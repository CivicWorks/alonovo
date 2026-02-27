from django.contrib import admin
from .models import (Claim, Company, CompanyScore, CompanyBadge, Value, ScoringRule,
                     CompanyValueSnapshot, UserValueWeight, BrandMapping, BarcodeCache,
                     Product, UnmatchedProduct)


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


@admin.register(BrandMapping)
class BrandMappingAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'company', 'source', 'confidence']
    list_filter = ['source']
    search_fields = ['brand_name', 'company__name', 'company__ticker']


@admin.register(BarcodeCache)
class BarcodeCacheAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'product_name', 'brands', 'provider', 'created_at']
    list_filter = ['provider']
    search_fields = ['barcode', 'product_name', 'brands']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand_name', 'company', 'category', 'typical_price', 'source']
    list_filter = ['category', 'source', 'company']
    search_fields = ['name', 'brand_name', 'company__name', 'barcode']
    raw_id_fields = ['company']


@admin.register(UnmatchedProduct)
class UnmatchedProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'brand_name', 'parent_company_guess', 'seen_count', 'reviewed', 'last_seen_at']
    list_filter = ['reviewed', 'category_guess']
    search_fields = ['product_name', 'brand_name', 'parent_company_guess']
    ordering = ['-seen_count', '-last_seen_at']
    readonly_fields = ['created_at', 'last_seen_at']
    actions = ['mark_as_reviewed']

    def mark_as_reviewed(self, request, queryset):
        """Mark selected items as reviewed."""
        queryset.update(reviewed=True)
    mark_as_reviewed.short_description = "Mark selected as reviewed"
