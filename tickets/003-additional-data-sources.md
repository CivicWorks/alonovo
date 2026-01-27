# Ticket: Research and Import Additional Data Sources

## Status: Ready (research first, then review before import)

## Summary

We need more data sources to fill out company ratings. Many companies currently only have ESG scores — we want coverage across multiple values so the grades are more meaningful. This ticket is about finding, validating, and importing new data.

## IMPORTANT: Process

**Do NOT write a scraper and run it.** Follow this process:

1. **Research** the data source — what does it cover, how many companies, what format, is it freely available?
2. **Write a summary** of what you found (add to this ticket or a new file in `prompts/`)
3. **Get approval** from the team lead before importing anything
4. **Write a management command** following the existing pattern (see below)
5. **Back up the database** before running it
6. **Run it on a small batch first** (5-10 companies) and verify the results look right
7. **Then run the full import** after the small batch is confirmed good

**Why this process:** Bad data is worse than no data. A wrong score on a real company is a credibility problem. We'd rather have 50 well-sourced companies than 500 with questionable data.

## Data Sources to Investigate

### High Priority (structured, reliable)

**1. Corporate Equality Index (HRC)**
- https://www.hrc.org/resources/corporate-equality-index
- LGBTQ+ workplace equality scores, 0-100 scale
- Covers 1300+ companies, published annually
- Value slug: `lgbtq_equality`
- Well-structured PDF/data, many S&P 500 companies

**2. KnowTheChain**
- https://knowthechain.org/benchmark/
- Forced labor / supply chain benchmarks
- Covers food & beverage, ICT, apparel sectors
- Value slug: `forced_labor`
- Scores 0-100, published every 2 years

**3. Corporate Tax Transparency**
- https://taxfoundation.org/data/all/global/corporate-tax-rates-by-country/
- Also: https://itep.org/corporate-tax-avoidance-in-the-first-year-of-the-tax-cuts-and-jobs-act/
- Effective tax rates vs statutory rates — shows who's paying their share
- Value slug: `tax_fairness`

**4. Gun Safety / Firearm Industry**
- https://gunsdownamerica.org/business-scorecard/
- Rates companies on gun safety policies
- Value slug: `gun_safety`

### Medium Priority (requires more work)

**5. Deforestation / Palm Oil**
- https://www.ran.org/the-issues/palm-oil/
- Palm oil sourcing scorecards
- Covers snack food, cosmetics, household goods companies

**6. Political Donations (beyond lobbying)**
- https://www.opensecrets.org/political-action-committees-pacs
- PAC contributions by company
- We already have lobbying spend — this would add PAC data

**7. Worker Safety (OSHA)**
- https://www.osha.gov/severeinjury
- OSHA severe injury reports by employer
- Public data, searchable by company name

### Lower Priority (harder to get clean data)

**8. Executive Compensation Ratio**
- CEO-to-median-worker pay ratio (required in SEC proxy filings)
- Available in company 10-K filings
- Value slug: `exec_pay_ratio`

**9. Carbon Emissions**
- CDP (formerly Carbon Disclosure Project) scores
- https://www.cdp.net/en
- Requires account to access data

## How to Write an Import Command

Follow the exact same pattern as the existing commands. Here's the template:

**File:** `backend/core/management/commands/import_SOURCE_data.py`

```python
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import DATA_SOURCE data"

    def handle(self, *args, **options):
        self.create_value()
        self.create_scoring_rule()
        self.import_data()
        self.compute_snapshots()
        self.create_badges()
        self.stdout.write(self.style.SUCCESS("Done!"))

    def get_or_create_company(self, slug, name, ticker, sector):
        """Always use this — deduplicates by ticker."""
        if ticker:
            existing = Company.objects.filter(ticker=ticker).first()
            if existing:
                return existing
        uri = f'urn:company:{slug}'
        company, _ = Company.objects.update_or_create(
            uri=uri,
            defaults={'name': name, 'ticker': ticker, 'sector': sector}
        )
        return company

    def create_claim_safe(self, **kwargs):
        """Always use this — won't create duplicates."""
        if Claim.objects.filter(uri=kwargs['uri']).exists():
            return None
        return Claim.objects.create(**kwargs)

    # ... rest follows the pattern in import_esg_data.py or import_peta_data.py
```

**Key rules:**
- Use `get_or_create_company()` — never create a company without checking ticker first
- Use `create_claim_safe()` — claims are immutable, duplicates will error
- Claim URIs must be globally unique — use format `urn:SOURCE:YEAR:SLUG:TYPE`
- Always set `source_uri` to the actual data source URL
- Always set `how_known` to describe provenance (official_report, public_data, etc.)

## DO NOT

- Do not scrape any website without approval — some have terms of service against it
- Do not import data you haven't manually spot-checked against the source
- Do not create claims without a `source_uri` — provenance is required
- Do not run imports without backing up first: `python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/pre_import_$(date +%Y%m%d).json`
- Do not modify existing values, scoring rules, or claims
- Do not change models, serializers, views, or frontend code
- Do not import more than 10 companies on first run — verify output, then run full batch
- Do not guess data — if a source doesn't have a company, skip it rather than estimate

## Deliverables

For each data source you research, create a file in `prompts/` with:

1. Source name and URL
2. What it measures
3. How many companies it covers (and which ones overlap with our existing data)
4. Data format (CSV, PDF, API, etc.)
5. Suggested value slug, scoring thresholds, and grade mapping
6. Any licensing or usage restrictions
7. Sample data for 5 companies so we can review before full import

Example: see `prompts/esg_import_instructions.md` and `prompts/peta_import_instructions.md`

## Files Involved

| File | Change |
|------|--------|
| `prompts/SOURCE_import_instructions.md` | Research document (create first, get approval) |
| `backend/core/management/commands/import_SOURCE_data.py` | Import command (after approval) |
| `data/` | Any downloaded CSV/data files |

## Reference

- Existing import commands: `backend/core/management/commands/import_*.py`
- Current values: corporate_lobbying, cage_free_eggs, farm_animal_welfare, ice_contracts, ice_detention, ice_collaborator, esg_score, stood_up, cruelty_free, ethics_of_executives
- Backup command: `cd backend && source venv/bin/activate && python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/alonovo_full_$(date +%Y%m%d_%H%M%S).json`
