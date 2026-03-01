from django.contrib import admin
from .models import (Claim, Company, CompanyScore, CompanyBadge, CompanyVote, Value, ScoringRule,
                     CompanyValueSnapshot, UserValueWeight, BrandMapping, BarcodeCache)


# ── Inlines ──────────────────────────────────────────────────────────

class CompanyValueSnapshotInline(admin.TabularInline):
    model = CompanyValueSnapshot
    extra = 0
    fields = ['value', 'grade', 'score', 'highlight_on_card', 'display_text', 'computed_at']
    readonly_fields = ['computed_at']
    show_change_link = True


class CompanyBadgeInline(admin.TabularInline):
    model = CompanyBadge
    extra = 0
    fields = ['label', 'badge_type', 'value', 'priority']


class BrandMappingInline(admin.TabularInline):
    model = BrandMapping
    extra = 0
    fields = ['brand_name', 'source', 'confidence']


class ScoringRuleInline(admin.StackedInline):
    model = ScoringRule
    extra = 0
    readonly_fields = ['created_at']


# ── Model Admins ─────────────────────────────────────────────────────

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['uri', 'subject', 'claim_type', 'amt', 'label', 'effective_date', 'created_at']
    list_filter = ['claim_type', 'how_known', 'effective_date']
    search_fields = ['uri', 'subject', 'statement', 'label']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = [
        'uri', 'subject', 'object', 'claim_type', 'statement', 'effective_date',
        'source_uri', 'how_known', 'date_observed', 'digest_multibase',
        'amt', 'unit', 'label', 'author', 'curator', 'issuer_id', 'issuer_id_type',
        'proof', 'created_at',
    ]

    def has_change_permission(self, request, obj=None):
        return False  # Claims are immutable

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'name', 'sector', 'snapshot_count', 'badge_count', 'created_at']
    list_filter = ['sector']
    search_fields = ['ticker', 'name', 'uri']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    inlines = [CompanyValueSnapshotInline, CompanyBadgeInline, BrandMappingInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        from django.db.models import Count
        return qs.annotate(
            _snapshot_count=Count('value_snapshots', distinct=True),
            _badge_count=Count('badges', distinct=True),
        )

    @admin.display(description='Snapshots', ordering='_snapshot_count')
    def snapshot_count(self, obj):
        return obj._snapshot_count

    @admin.display(description='Badges', ordering='_badge_count')
    def badge_count(self, obj):
        return obj._badge_count


@admin.register(CompanyScore)
class CompanyScoreAdmin(admin.ModelAdmin):
    list_display = ['company', 'grade', 'score', 'raw_value', 'computed_at']
    list_filter = ['grade']
    search_fields = ['company__ticker', 'company__name']
    list_select_related = ['company']
    raw_id_fields = ['company']
    readonly_fields = ['computed_at']
    date_hierarchy = 'computed_at'


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = [
        'slug', 'name', 'value_type', 'display_group',
        'is_fixed', 'is_disqualifying', 'min_weight',
    ]
    list_filter = ['value_type', 'is_fixed', 'is_disqualifying']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ScoringRuleInline]
    fieldsets = (
        (None, {
            'fields': ('slug', 'name', 'description', 'value_type'),
        }),
        ('Policy', {
            'fields': ('is_fixed', 'is_disqualifying', 'min_weight'),
        }),
        ('Display', {
            'fields': ('display_group', 'display_group_order', 'card_display_template', 'card_icon'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ['value', 'version', 'effective_date', 'created_at']
    list_filter = ['value']
    list_select_related = ['value']
    readonly_fields = ['created_at']


@admin.register(CompanyValueSnapshot)
class CompanyValueSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'value', 'grade', 'score',
        'highlight_on_card', 'display_text', 'computed_at',
    ]
    list_filter = ['value', 'grade', 'highlight_on_card']
    search_fields = ['company__ticker', 'company__name', 'display_text']
    list_select_related = ['company', 'value']
    raw_id_fields = ['company']
    readonly_fields = ['computed_at']
    date_hierarchy = 'computed_at'
    list_per_page = 50


@admin.register(UserValueWeight)
class UserValueWeightAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'weight']
    list_filter = ['value']
    search_fields = ['user__username', 'user__email']
    list_select_related = ['user', 'value']
    raw_id_fields = ['user']


@admin.register(CompanyBadge)
class CompanyBadgeAdmin(admin.ModelAdmin):
    list_display = ['company', 'label', 'badge_type', 'value', 'priority']
    list_filter = ['badge_type', 'value']
    search_fields = ['company__ticker', 'company__name', 'label']
    list_select_related = ['company', 'value']
    raw_id_fields = ['company']


@admin.register(CompanyVote)
class CompanyVoteAdmin(admin.ModelAdmin):
    list_display = ['company', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['company__ticker', 'company__name']


@admin.register(BrandMapping)
class BrandMappingAdmin(admin.ModelAdmin):
    """
    Maps product brands to parent companies.
    Workflow: Scan barcode -> Get brand -> Map to company -> Add claims
    """
    list_display = ['brand_name', 'get_company', 'source', 'confidence', 'created_at']
    list_filter = ['source', 'confidence', 'created_at']
    search_fields = ['brand_name', 'brand_name_normalized', 'company__name', 'company__ticker']
    list_select_related = ['company']
    raw_id_fields = ['company']
    readonly_fields = ['brand_name_normalized', 'created_at', 'updated_at']
    fieldsets = (
        ('Brand Information', {
            'fields': ('brand_name', 'company'),
        }),
        ('Metadata', {
            'fields': ('source', 'confidence'),
        }),
    )

    @admin.display(description='Company')
    def get_company(self, obj):
        return f"{obj.company.ticker} - {obj.company.name}" if obj.company else '-'


@admin.register(BarcodeCache)
class BarcodeCacheAdmin(admin.ModelAdmin):
    """Cached barcode lookups from external APIs."""
    list_display = ['barcode', 'product_name', 'brands', 'owner', 'provider', 'created_at']
    list_filter = ['provider']
    search_fields = ['barcode', 'product_name', 'brands', 'owner']
    readonly_fields = ['raw_response', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
