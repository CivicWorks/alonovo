from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Claim, Company, CompanyVote, Value, UserValueWeight
from .serializers import ClaimSerializer, CompanySerializer, ValueSerializer, UserValueWeightSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def sectors_list(request):
    """Return distinct sectors."""
    sectors = Company.objects.values_list('sector', flat=True).distinct().order_by('sector')
    return Response([s for s in sectors if s])


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    lookup_field = 'ticker'
    pagination_class = None

    def get_queryset(self):
        qs = Company.objects.prefetch_related('scores', 'badges', 'value_snapshots', 'value_snapshots__value')
        sector = self.request.query_params.get('sector')
        value = self.request.query_params.get('value')
        if sector:
            qs = qs.filter(sector=sector)
        if value:
            qs = qs.filter(value_snapshots__value__slug=value).distinct()
        return qs


class ValueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer
    lookup_field = 'slug'


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """Get current user info, or null if not authenticated."""
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'email': request.user.email,
            'username': request.user.username,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        })
    return Response(None)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_weights(request):
    """Get or set user's value weights."""
    if request.method == 'GET':
        weights = UserValueWeight.objects.filter(user=request.user).select_related('value')
        serializer = UserValueWeightSerializer(weights, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Expects: [{"value_slug": "lobbying", "weight": 7}, ...]
        for item in request.data:
            try:
                value = Value.objects.get(slug=item['value_slug'])
                weight = float(item['weight'])

                # Enforce min_weight for fixed values
                if value.is_fixed and weight < value.min_weight:
                    weight = value.min_weight

                UserValueWeight.objects.update_or_create(
                    user=request.user,
                    value=value,
                    defaults={'weight': weight}
                )
            except (Value.DoesNotExist, KeyError, ValueError):
                continue

        return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def company_claims(request, ticker):
    """Get all claims for a company by ticker."""
    company = Company.objects.filter(ticker=ticker).first()
    if not company:
        return Response([], status=404)
    claims = Claim.objects.filter(subject=company.uri).order_by('-effective_date')
    serializer = ClaimSerializer(claims, many=True)
    return Response(serializer.data)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def vote_for_company(request, ticker):
    """Vote/unvote for a company to prioritize data acquisition."""
    company = Company.objects.filter(ticker=ticker).first()
    if not company:
        return Response({'error': 'Company not found'}, status=404)

    if request.method == 'POST':
        if request.user.is_authenticated:
            vote, created = CompanyVote.objects.get_or_create(
                company=company, user=request.user)
            if not created:
                return Response({'status': 'already_voted', 'vote_count': company.votes.count()})
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            if CompanyVote.objects.filter(company=company, session_key=session_key).exists():
                return Response({'status': 'already_voted', 'vote_count': company.votes.count()})
            CompanyVote.objects.create(company=company, session_key=session_key)

        return Response({'status': 'voted', 'vote_count': company.votes.count()})

    elif request.method == 'DELETE':
        if request.user.is_authenticated:
            CompanyVote.objects.filter(company=company, user=request.user).delete()
        elif request.session.session_key:
            CompanyVote.objects.filter(
                company=company, session_key=request.session.session_key).delete()
        return Response({'status': 'unvoted', 'vote_count': company.votes.count()})


@api_view(['GET'])
@permission_classes([AllowAny])
def vote_leaderboard(request):
    """Companies with no data, sorted by vote count."""
    from django.db.models import Count
    companies = (Company.objects
        .filter(value_snapshots__isnull=True)
        .annotate(vote_count=Count('votes'))
        .filter(vote_count__gt=0)
        .order_by('-vote_count')[:50])
    result = [{'ticker': c.ticker, 'name': c.name, 'sector': c.sector,
               'vote_count': c.vote_count} for c in companies]
    return Response(result)
