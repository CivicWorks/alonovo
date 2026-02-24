from django.contrib import admin
from .models import Claim, Company, CompanyScore, CompanyBadge, CompanyVote, Value, ScoringRule, CompanyValueSnapshot, UserValueWeight


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


@admin.register(CompanyVote)
class CompanyVoteAdmin(admin.ModelAdmin):
    list_display = ['company', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['company__ticker', 'company__name']
