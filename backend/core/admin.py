from django.contrib import admin
from .models import (Claim, Company, CompanyScore, CompanyBadge, Value, ScoringRule,
                     CompanyValueSnapshot, UserValueWeight, BrandMapping, BarcodeCache)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['uri', 'subject', 'claim_type', 'amt', 'label', 'created_at']
    list_filter = ['claim_type', 'how_known']
    search_fields = ['uri', 'subject', 'statement']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'name', 'sector']
    list_filter = ['sector']
    search_fields = ['ticker', 'name']


@admin.register(CompanyScore)
class CompanyScoreAdmin(admin.ModelAdmin):
    list_display = ['company', 'grade', 'score', 'raw_value', 'computed_at']
    list_filter = ['grade']
    search_fields = ['company__ticker', 'company__name']


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'value_type', 'is_fixed', 'is_disqualifying']
    list_filter = ['value_type', 'is_fixed', 'is_disqualifying']
    search_fields = ['name', 'description']


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ['value', 'version', 'effective_date', 'created_at']
    list_filter = ['value']


@admin.register(CompanyValueSnapshot)
class CompanyValueSnapshotAdmin(admin.ModelAdmin):
    list_display = ['company', 'value', 'grade', 'score', 'highlight_on_card', 'computed_at']
    list_filter = ['value', 'grade', 'highlight_on_card']
    search_fields = ['company__ticker', 'company__name']


@admin.register(UserValueWeight)
class UserValueWeightAdmin(admin.ModelAdmin):
    list_display = ['user', 'value', 'weight']
    list_filter = ['value']
    search_fields = ['user__username', 'user__email']


@admin.register(CompanyBadge)
class CompanyBadgeAdmin(admin.ModelAdmin):
    list_display = ['company', 'label', 'badge_type', 'priority']
    list_filter = ['badge_type', 'value']
    search_fields = ['company__ticker', 'company__name', 'label']



# ===========================
# BRAND MAPPING ADMIN
# ===========================
@admin.register(BrandMapping)
class BrandMappingAdmin(admin.ModelAdmin):
    """
    Maps product brands to parent companies.
    Workflow: Scan barcode -> Get brands -> Map to company -> Add claims
    """
    list_display = ['brand_name', 'get_company', 'confidence', 'source', 'created_at']
    list_filter = ['source', 'confidence', 'created_at']
    search_fields = ['brand_name', 'brand_name_normalized', 'company__name', 'company__ticker']

    fieldsets = (
        ('Brand Information', {
            'fields': ('brand_name', 'company'),
        }),
        ('Metadata', {
            'fields': ('source', 'confidence'),
        }),
    )

    readonly_fields = ['brand_name_normalized', 'created_at', 'updated_at']

    def get_company(self, obj):
        return f"{obj.company.ticker} - {obj.company.name}" if obj.company else '-'
    get_company.short_description = 'Company'


# ===========================
# BARCODE CACHE ADMIN
# ===========================
@admin.register(BarcodeCache)
class BarcodeCacheAdmin(admin.ModelAdmin):
    """
    Cached barcode lookups from external APIs.
    """
    list_display = ['barcode', 'product_name', 'brands', 'provider', 'created_at']
    list_filter = ['provider', 'created_at']
    search_fields = ['barcode', 'product_name', 'brands', 'owner']
    readonly_fields = ['created_at', 'raw_response']
    list_per_page = 50
