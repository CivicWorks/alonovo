# SOURCE_import_instructions.md

## Data Sources — Research Findings (2026-05-18)

---

### 1. HRC Corporate Equality Index (CEI)

**What it measures:** LGBTQ+ workplace equality — non-discrimination policies, equitable benefits, inclusive culture, corporate social responsibility. 0–100 scale.

**Coverage:** ~48 companies in the Alonovo command (subset of the full 1,400+ rated by HRC). Full CEI covers Fortune 1000 + AmLaw 200 firms.

**Data availability:**
- Full dataset: **Not publicly downloadable as CSV.** PDF report at hrc.org/resources/corporate-equality-index. Individual scores browsable one-by-one at hrc.org/cei-search. 2024 report: 1,400+ employers rated.
- Alonovo command uses a **hardcoded subset** (48 companies, curated S&P 500 + notable employers).

**Licensing:** HRC Foundation 501(c)(3). Report is publicly accessible. No formal license found for redistribution of bulk data — using a curated subset with source attribution is reasonable for a pilot.

**Upgrade path:** Contact HRC for bulk data access if coverage expands.

---

### 2. KnowTheChain

**What it measures:** Forced labor / human trafficking in supply chains across Apparel & Footwear, Food & Beverage, and ICT sectors.

**Coverage:** 60 companies (Food & Beverage) + 65 companies (Apparel & Footwear) + 60 companies (ICT) per benchmark cycle. Alonovo command covers a subset via `import_supply_chain_data.py`.

**Data availability:**
- Full dataset: **Not publicly downloadable.** PDF reports + "Access data" sign-up form at knowthechain.org. No bulk CSV. The data requires requesting access.
- Alonovo command uses a **hardcoded subset** of benchmarked companies.

**Licensing:** No formal license identified. Use as research/attribution basis for a pilot is defensible.

**Upgrade path:** Request full data access via the form at knowthechain.org when expanding coverage.

---

### 3. ITEP Corporate Tax Tracker

**What it measures:** Effective vs. statutory (21%) corporate tax rate. Based on SEC 10-K filings and ITEP analysis. Companies paying below their share score worse.

**Coverage:** ITEP covers 300+ companies. Alonovo command uses a subset.

**Data availability:**
- itep.org/corporate-tax-tracker — data is browsable on the site. No bulk download found. Data is derived from SEC 10-K filings.
- Alonovo command uses a **hardcoded subset** (hardcoded effective rates from the ITEP analysis).

**Licensing:** ITEP is a non-profit. Attributive use for a pilot is reasonable.

**Upgrade path:** Automate extraction from SEC EDGAR API for full S&P 500 coverage.

---

### 4. Guns Down America Scorecard

**What it measures:** Company gun policies, sales practices, and advocacy. Letter grades (A–F).

**Coverage:** ~18 companies in Alonovo command.

**Data availability:**
- gunsdownamerica.org/business-scorecard/ — data is on the website. No bulk download.
- Alonovo command uses a **hardcoded subset**.

**Licensing:** Advocacy organization. Attributive use for a pilot is reasonable.

**Upgrade path:** Cross-reference with NRA donation data for broader coverage.

---

## Import Commands (ready to run with team lead approval)

```bash
cd /opt/shared/repos/alonovo/backend
source venv/bin/activate

# Backup first
python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/pre_breadth_$(date +%Y%m%d_%H%M%S).json

# Run imports
python manage.py import_hrc_data          # LGBTQ+ Equality — 48 companies
python manage.py import_supply_chain_data  # Forced Labor — ~31 companies
python manage.py import_exec_pay_data      # CEO Pay Ratio — ~32 companies
python manage.py import_tax_fairness_data # Tax Fairness — ~29 companies
python manage.py import_gun_safety_data   # Gun Safety — ~18 companies
python manage.py import_ghg_data          # GHG Emissions — ~100 companies
```

**All commands use `Claim.objects.get_or_create()` — safe to re-run, won't duplicate data.**

---

## Recommendation

All four sources are suitable for the pilot given:
- All use publicly available research data with clear attribution
- No scraping or API key required (data is hardcoded as a curated subset)
- Commands are already written and follow the established import pattern

**Action needed:** Team lead approval before running any imports.