from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Claim, Company, Value, UserValueWeight, Product
from .serializers import ClaimSerializer, CompanySerializer, ValueSerializer, UserValueWeightSerializer, ProductSerializer


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
    return Response(None, status=204)


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


@api_view(['GET'])
@permission_classes([AllowAny])
def products_list(request):
    """Search products by name, brand, or category.

    Query params:
      ?q=cheerios       - search name or brand_name (case-insensitive)
      ?category=cereal  - filter by category
      ?brand=Tide       - exact brand match
    """
    qs = Product.objects.select_related('company').all()
    q = request.query_params.get('q')
    category = request.query_params.get('category')
    brand = request.query_params.get('brand')
    if q:
        qs = qs.filter(
            models.Q(name__icontains=q) |
            models.Q(brand_name__icontains=q)
        )
    if category:
        qs = qs.filter(category=category)
    if brand:
        qs = qs.filter(brand_name__iexact=brand)
    serializer = ProductSerializer(qs[:100], many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_categories(request):
    """Return list of product categories with counts."""
    from django.db.models import Count
    cats = Product.objects.values('category').annotate(
        count=Count('id')).order_by('-count')
    return Response(list(cats))
