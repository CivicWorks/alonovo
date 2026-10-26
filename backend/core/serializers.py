from rest_framework import serializers
from .models import Claim, Deal, Company, CompanyScore, CompanyBadge, CompanyValueSnapshot, Value, ScoringRule, UserValueWeight, Product


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


class ProductSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_ticker = serializers.CharField(source='company.ticker', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand_name', 'category', 'typical_price',
                  'barcode', 'product_type', 'image_url', 'company_name', 'company_ticker']


class DealSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True, default=None)
    company_ticker = serializers.CharField(source='company.ticker', read_only=True, default=None)
    store_ticker = serializers.CharField(source='store.ticker', read_only=True, default=None)

    class Meta:
        model = Deal
        fields = ['id', 'title', 'brand_name', 'company_name', 'company_ticker', 'store_name', 'store_ticker',
                  'category', 'price', 'regular_price', 'currency', 'url', 'affiliate_url', 'image_url',
                  'starts_at', 'ends_at', 'source', 'last_seen_at']
