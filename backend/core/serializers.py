from rest_framework import serializers
from .models import Claim, Company, CompanyScore, CompanyBadge, CompanyValueSnapshot, Value, ScoringRule, UserValueWeight


class CompanyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyScore
        fields = '__all__'


class CompanyBadgeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='badge_type')

    class Meta:
        model = CompanyBadge
        fields = ['label', 'type', 'priority']


class CompanyValueSnapshotSerializer(serializers.ModelSerializer):
    value_slug = serializers.SlugField(source='value.slug', read_only=True)
    value_name = serializers.CharField(source='value.name', read_only=True)

    class Meta:
        model = CompanyValueSnapshot
        fields = ['value_slug', 'value_name', 'score', 'grade',
                  'highlight_on_card', 'highlight_priority',
                  'display_text', 'display_icon', 'claim_uris', 'computed_at']


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['uri', 'subject', 'claim_type', 'amt', 'unit', 'label',
                  'effective_date', 'source_uri', 'how_known', 'statement',
                  'created_at']


class CompanySerializer(serializers.ModelSerializer):
    scores = CompanyScoreSerializer(many=True, read_only=True)
    badges = CompanyBadgeSerializer(many=True, read_only=True)
    value_snapshots = CompanyValueSnapshotSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__'


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ['slug', 'name', 'description', 'value_type',
                  'is_fixed', 'is_disqualifying', 'min_weight',
                  'display_group', 'display_group_order',
                  'card_display_template', 'card_icon']


class UserValueWeightSerializer(serializers.ModelSerializer):
    value_slug = serializers.SlugField(source='value.slug', read_only=True)
    value_name = serializers.CharField(source='value.name', read_only=True)

    class Meta:
        model = UserValueWeight
        fields = ['id', 'value_slug', 'value_name', 'weight']
