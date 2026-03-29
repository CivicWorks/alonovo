# Breadth-First Data Source Coverage — Pilot Phase

**Date:** 2026-03-13
**Direction from George:** Get coverage on all attributes with reasonable data.
Be transparent about sources and grades. This is for demonstration/pilot purposes
to gain investor/donor interest. We will replace datasets with better sources as
we acquire funding and resources.

## Current Values (11 total after this work)

### Already Imported (8 values)

| # | Value | Slug | Source | Companies | Data Quality |
|---|-------|------|--------|-----------|--------------|
| 1 | Corporate Lobbying | `corporate_lobbying` | OpenSecrets/Statista 2024 | 20 | Good — federal disclosure data |
| 2 | Farm Animal Welfare | `farm_animal_welfare` | BBFAW 2024 report | 13 | Good — independent benchmark |
| 3 | Cage-Free Eggs | `cage_free_eggs` | EggTrack (Humane League) | 9 | Good — verified commitments |
| 4 | ICE/CBP Contracts | `ice_contracts` | USASpending.gov | 9 | Good — federal data |
| 5 | ICE Detention | `ice_detention` | The Intercept | 2 | Fair — investigative journalism |
| 6 | ESG Score | `esg_score` | Yahoo/Sustainalytics + S&P Global | ~245 | Good — established rating agencies |
| 7 | Cruelty-Free | `cruelty_free` | PETA certification list | 50+ | Good — official certifications |
| 8 | Tobacco | (disqualifying) | Internal | 3 | N/A |

### GHG Emissions (built, ready to run)

| # | Value | Slug | Source | Companies | Data Quality |
|---|-------|------|--------|-----------|--------------|
| 9 | GHG Emissions | `ghg_emissions` | NZDPU (Net-Zero Data Public Utility) | ~100+ matched | Good — official corporate disclosures, sector-relative grading |

### NEW — Breadth Expansion (5 values)

| # | Value | Slug | Source | Companies | Data Quality | Upgrade Path |
|---|-------|------|--------|-----------|--------------|--------------|
| 10 | LGBTQ+ Equality | `lgbtq_equality` | HRC Corporate Equality Index 2024 | 48 | Good — established annual report, 1300+ employers rated | Expand to full CEI list |
| 11 | Supply Chain Labor | `forced_labor` | KnowTheChain 2023 benchmarks | 31 | Good — independent benchmark, 0-100 scoring | Add 2025 benchmark when published |
| 12 | CEO Pay Ratio | `exec_pay_ratio` | SEC proxy filings / AFL-CIO Paywatch | 32 | Good — legally required disclosure | Expand to full S&P 500 from SEC EDGAR |
| 13 | Tax Fairness | `tax_fairness` | ITEP Corporate Tax Tracker | 29 | Good — analysis of SEC 10-K filings | ITEP covers 300+ companies |
| 14 | Gun Safety | `gun_safety` | Guns Down America scorecard | 18 | Fair — advocacy org scorecard | Cross-reference with NRA donation data |

## Data Quality Notes (for investor transparency)

**Strengths of current dataset:**
- Every data point traces to a named public source via `source_uri`
- Each claim records provenance (`how_known`, `author`, `effective_date`)
- Scoring rules are versioned — when better data arrives, we create v2 rules
- Immutable claims mean we never lose the audit trail

**Known limitations (honest assessment):**
- Coverage is uneven: ESG covers ~245 companies but gun safety only 18
- Some data is 1-2 years old (KnowTheChain 2023, ITEP 2018-2022 averages)
- HRC CEI and gun safety scores cover different company universes — not all overlap
- CEO pay ratios vary year to year; we use single-year proxies
- We use curated subsets of larger datasets — full coverage requires API access or partnerships

**Upgrade plan (with funding):**
1. **CDP Partnership** — replace Yahoo environmentScore with CDP climate scores
2. **ITEP Full Dataset** — expand from 29 to 300+ companies
3. **SEC EDGAR API** — automate CEO pay ratio extraction for all S&P 500
4. **HRC Full CEI** — import all 1300+ rated employers
5. **KnowTheChain 2025** — update when new benchmarks publish
6. **Real-time data** — OpenSecrets API for lobbying, USASpending API for contracts

## Running the Imports

**IMPORTANT: Back up the database first!**
```bash
cd /opt/shared/repos/alonovo/backend
source venv/bin/activate
python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/pre_breadth_$(date +%Y%m%d_%H%M%S).json
```

**Run each import (do small batch verification first):**
```bash
python manage.py import_hrc_data
python manage.py import_supply_chain_data
python manage.py import_exec_pay_data
python manage.py import_tax_fairness_data
python manage.py import_gun_safety_data
python manage.py import_ghg_data --dry-run  # verify before real run
python manage.py import_ghg_data
```
