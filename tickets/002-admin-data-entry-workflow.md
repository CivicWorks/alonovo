# Ticket: Improve Admin Workflow for Adding Data

## Status: Ready

## Summary

Adding new companies, values, and claims through Django Admin is possible but not obvious. A new team member wouldn't know what order to create things, what fields matter, or how to get from "I have a data source" to "it shows up on the site." This ticket is about making that path clear — either through better admin configuration, documentation inside the admin, or both.

## Current State

The data entry flow is:

1. Create a **Value** (e.g., "Cruelty-Free") with slug, type, flags
2. Create a **ScoringRule** for that value (thresholds or label mappings)
3. Create **Company** entries (need URI, ticker, name, sector)
4. Create **Claim** entries (need URI, subject=company URI, claim_type, amt/label, source_uri)
5. Run a management command or script to compute **CompanyValueSnapshot** from claims
6. Badges get created from snapshots

The problems:
- Steps 1-4 can be done in Django Admin but it's not obvious what order or what fields matter
- Step 5 requires running a management command — there's no "recompute" button in admin
- The Claim model requires knowing the company's URI (not just picking from a dropdown)
- ScoringRule config is raw JSON — easy to get wrong
- There's no guidance in the admin about what claim_type values exist or what units to use

## Goals

Make it so someone can answer: **"I found a data source about X for company Y. How do I add it?"**

## Suggested Improvements (pick any combination)

### A. Better Admin Configuration (recommended first step)

**File:** `backend/core/admin.py`

1. **Add help text and fieldsets** to group related fields visually
2. **Add list_display** so the admin list views show useful columns (not just `__str__`)
3. **Add list_filter** on Claim for claim_type, and on Company for sector
4. **Add search_fields** on Company (name, ticker) and Claim (subject, claim_type)
5. **Make Claim.subject a searchable field** or add a raw_id_field so you don't have to type URIs
6. **Add readonly_fields** for computed/auto fields like created_at, uri patterns

Example for Company admin:
```python
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'ticker', 'sector', 'uri']
    list_filter = ['sector']
    search_fields = ['name', 'ticker']
    readonly_fields = ['created_at', 'updated_at']
```

Example for Claim admin:
```python
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_type', 'subject', 'amt', 'label', 'effective_date', 'source_uri']
    list_filter = ['claim_type', 'how_known']
    search_fields = ['subject', 'claim_type', 'label']
    readonly_fields = ['created_at']
```

### B. Admin Action to Recompute Snapshots

Add a Django admin action on Company that recomputes snapshots for selected companies. This removes the need to SSH in and run management commands after adding claims.

**File:** `backend/core/admin.py`

```python
@admin.action(description="Recompute value snapshots for selected companies")
def recompute_snapshots(modeladmin, request, queryset):
    # Call the snapshot computation logic for each selected company
    ...
```

This is the biggest quality-of-life improvement. Without it, adding data through admin is incomplete — you add claims but nothing shows up until someone runs a command.

### C. Add a "How to Add Data" Page in Admin

Add a simple view at `/admin/data-guide/` that explains the workflow with examples. Link it from the admin index page.

This could just be a Django template with static content explaining:
- What each model is for
- The order to create things
- What claim_type values exist (LOBBYING_SPEND, ESG_SCORE, CRUELTY_FREE_STATUS, etc.)
- What units to use (USD, percent, sustainalytics_risk, severity_scale, etc.)
- Example: "To add lobbying data for Apple..."

## DO NOT

- Do not change any models or add new fields
- Do not change serializers, API views, or frontend code
- Do not change or delete any existing data
- Do not change the management commands (they still work and are the bulk import path)
- Do not add new dependencies

## Files Involved

| File | Change |
|------|--------|
| `backend/core/admin.py` | Main file — admin classes, actions, help text |
| `backend/templates/admin/data_guide.html` | Optional — data entry guide page |
| `backend/core/urls.py` | Optional — if adding the guide page as a view |

## How to Test

1. Log into Django Admin at `/admin/` (credentials: ask team lead)
2. Verify Company list shows name, ticker, sector columns with search and filter
3. Verify Claim list shows claim_type, subject, amt with filters
4. Add a test Claim through admin for an existing company — verify it saves
5. If you added the recompute action: select a company, run "Recompute snapshots", verify the snapshot updates
6. Delete your test claim when done

## Reference

- Existing management commands show the full data flow: `backend/core/management/commands/import_initial_data.py`
- Current claim_types in use: LOBBYING_SPEND, FARM_WELFARE_TIER, CAGE_FREE_PERCENT, ICE_CONTRACT, ICE_DETENTION_OPERATOR, ICE_COLLABORATOR, ESG_SCORE, CRUELTY_FREE_STATUS, EXEC_ETHICS_SCORE, STOOD_UP
- Current units in use: USD, percent, million_usd, sustainalytics_risk, spglobal_score, severity_scale
