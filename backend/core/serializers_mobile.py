"""Serializers for mobile API endpoints."""
from rest_framework import serializers
from .models import Company, CompanyValueSnapshot, CompanyBadge, BrandMapping


class MobileValueSnapshotSerializer(serializers.ModelSerializer):
    value_slug = serializers.SlugField(source='value.slug', read_only=True)
    value_name = serializers.CharField(source='value.name', read_only=True)

    class Meta:
        model = CompanyValueSnapshot
        fields = ['value_slug', 'value_name', 'score', 'grade',
                  'display_text', 'display_icon', 'claim_uris', 'computed_at']


class MobileBadgeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='badge_type')

    class Meta:
        model = CompanyBadge
        fields = ['label', 'type', 'priority']


class MobileCompanySerializer(serializers.ModelSerializer):
    value_snapshots = MobileValueSnapshotSerializer(many=True, read_only=True)
    badges = MobileBadgeSerializer(many=True, read_only=True)
    overall_grade = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'uri', 'ticker', 'name', 'sector',
                  'value_snapshots', 'badges', 'overall_grade']

    def get_overall_grade(self, obj):
        return compute_overall_grade_server(obj)


class BrandMappingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = BrandMapping
        fields = ['brand_name', 'company_name', 'company_ticker',
                  'source', 'confidence']


def compute_overall_grade_server(company):
    """Server-side overall grade computation.

    Mirrors frontend/src/lib/utils.ts:computeOverallGrade().
    """
    from .models import Value
    snapshots = list(company.value_snapshots.all())
    if not snapshots:
        return None

    disqualifying_slugs = set(
        Value.objects.filter(is_disqualifying=True).values_list('slug', flat=True)
    )

    # If any disqualifying value has F grade -> overall F
    for snap in snapshots:
        if snap.value_id in disqualifying_slugs and snap.grade.startswith('F'):
            return 'F'

    # Average scores, map to grade
    avg = sum(s.score for s in snapshots) / len(snapshots)
    if avg >= 0.8:
        return 'A'
    if avg >= 0.3:
        return 'B'
    if avg >= -0.1:
        return 'C'
    if avg >= -0.5:
        return 'D'
    return 'F'
