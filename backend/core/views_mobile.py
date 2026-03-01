"""API views for the mobile barcode scanner app."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Company, Value, BrandMapping
from .barcode_providers import lookup_barcode
from .brand_matcher import match_brand_to_company
from .serializers_mobile import (
    MobileCompanySerializer,
    BrandMappingSerializer,
    compute_overall_grade_server,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def barcode_scan(request):
    """Scan a barcode and return product info + company ratings + alternatives.

    POST /api/scan/
    Body: {"barcode": "3017620422003"}
    """
    barcode = request.data.get('barcode', '').strip()
    if not barcode:
        return Response(
            {'error': 'barcode is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Step 1: Look up product from barcode
    product_info = lookup_barcode(barcode)
    if not product_info:
        return Response({
            'barcode': barcode,
            'product': None,
            'company': None,
            'alternatives': [],
            'match_confidence': 0,
            'match_method': 'product_not_found',
        })

    product_data = {
        'name': product_info.product_name,
        'brands': product_info.brands,
        'categories': product_info.categories,
        'image_url': product_info.image_url,
        'ecoscore_grade': product_info.ecoscore_grade,
        'provider': product_info.provider,
    }

    # Step 2: Match brand to company
    company, confidence, method = match_brand_to_company(product_info)

    if not company:
        return Response({
            'barcode': barcode,
            'product': product_data,
            'company': None,
            'alternatives': [],
            'match_confidence': 0,
            'match_method': method,
        })

    # Prefetch related data for serialization
    company = Company.objects.prefetch_related(
        'value_snapshots', 'value_snapshots__value', 'badges'
    ).get(pk=company.pk)

    company_data = MobileCompanySerializer(company).data

    # Step 3: Find better alternatives
    alternatives = _get_alternatives(company)
    alternatives_data = MobileCompanySerializer(alternatives, many=True).data

    return Response({
        'barcode': barcode,
        'product': product_data,
        'company': company_data,
        'alternatives': alternatives_data,
        'match_confidence': confidence,
        'match_method': method,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def alternatives_for_company(request, ticker):
    """Get better-rated alternatives for a company.

    GET /api/alternatives/{ticker}/
    """
    company = Company.objects.prefetch_related(
        'value_snapshots', 'value_snapshots__value', 'badges'
    ).filter(ticker=ticker).first()

    if not company:
        return Response(
            {'error': 'Company not found'},
            status=status.HTTP_404_NOT_FOUND,
        )

    company_data = MobileCompanySerializer(company).data
    alternatives = _get_alternatives(company)
    alternatives_data = MobileCompanySerializer(alternatives, many=True).data

    # Animal welfare highlight
    animal_welfare = _animal_welfare_highlight(company, alternatives)

    return Response({
        'company': company_data,
        'alternatives': alternatives_data,
        'animal_welfare_highlight': animal_welfare,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def brand_mappings_list(request):
    """List all brand mappings. Useful for debugging and admin.

    GET /api/brands/
    """
    mappings = BrandMapping.objects.select_related('company').all()
    data = BrandMappingSerializer(mappings, many=True).data
    return Response(data)


# --- helpers ---

ANIMAL_WELFARE_VALUES = {'farm_animal_welfare', 'cage_free_eggs', 'cruelty_free'}


def _get_alternatives(company, limit=5):
    """Find better-rated companies in the same sector.

    Prioritizes companies with better animal welfare scores.
    """
    if not company.sector:
        return []

    same_sector = Company.objects.filter(
        sector=company.sector
    ).exclude(
        pk=company.pk
    ).prefetch_related('value_snapshots', 'value_snapshots__value', 'badges')

    input_snapshots = list(company.value_snapshots.all())
    if not input_snapshots:
        input_avg = 0
    else:
        input_avg = sum(s.score for s in input_snapshots) / len(input_snapshots)

    candidates = []
    for alt in same_sector:
        alt_snapshots = list(alt.value_snapshots.all())
        if not alt_snapshots:
            continue
        alt_avg = sum(s.score for s in alt_snapshots) / len(alt_snapshots)
        if alt_avg <= input_avg:
            continue

        # Bonus for animal welfare values
        animal_bonus = 0
        for snap in alt_snapshots:
            if snap.value_id in ANIMAL_WELFARE_VALUES and snap.score > 0.3:
                animal_bonus += 0.2

        candidates.append((alt, alt_avg, animal_bonus))

    # Sort by animal welfare bonus first, then overall score
    candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)
    return [c[0] for c in candidates[:limit]]


def _animal_welfare_highlight(company, alternatives):
    """Build animal welfare comparison data."""
    def _aw_grades(comp):
        grades = {}
        for snap in comp.value_snapshots.all():
            if snap.value_id in ANIMAL_WELFARE_VALUES:
                grades[snap.value_id] = snap.grade
        return grades

    result = {'this_company': _aw_grades(company)}

    if alternatives:
        best = alternatives[0]
        result['best_alternative'] = {
            'name': best.name,
            'ticker': best.ticker,
            'grades': _aw_grades(best),
        }

    return result
