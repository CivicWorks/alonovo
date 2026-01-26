from django.contrib import admin
from .models import Claim, Company, CompanyScore


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['uri', 'subject', 'claim', 'amt', 'created_at']
    list_filter = ['claim', 'how_known']
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
