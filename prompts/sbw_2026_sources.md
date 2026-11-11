# Shopping for a Better World 2026: additional sources, research findings (2026-11-10)

These are the sources listed in the "add additional data sources" ticket (SBW 2026 additional source).
Ticket 003 says to research first and get approval. The team lead's decisions and the import and rollback
steps are at the end of this file. **Nothing has been imported into production yet.**

"Overlap" counts list companies that are already among the 427 companies on the live site
(`/api/companies/`, checked 2026-11-10). Names were matched by hand after an automatic first pass.

## Summary

| # | Source | Latest edition | Full list free? | Overlap | Recommendation |
|---|---|---|---|---|---|
| I | Fortune Best Workplaces for Women | **2026** (Oct 2026) | Yes, at fortune.com (large companies, 100) | 16 | Import as a positive-only value |
| II | Fortune Best Workplaces for Diversity | **2019** (last edition) | No | n/a | Drop: the list is discontinued |
| III | Fortune 100 Best Companies to Work For | 2026 (Apr 2026) | Top 10 only | n/a | Skip unless someone has the issue |
| III-b | Newsweek America's Greatest Workplaces for Women | 2026 (Feb 2026) | Not tested: blocked to automated fetch (HTTP 402) | ? | Someone checks it in a browser |
| IV | Catalyst (women's advancement) | Catalyst Award 2025 | Yes, but only about 5 winners a year | ~0 | Don't import; see board diversity note |
| V | BBFAW farm animal welfare | **2025 Benchmark** (published May 2026) | Yes, PDF | 30 (13 already graded from 2024) | Import as new 2025 claims on existing `farm_animal_welfare` |
| VI | Chronicle of Philanthropy corporate giving | 2012 top 10 (newer editions paywalled) | No | ? | Don't import: data is 14 years old |
| VII | Fortune Best Workplaces for Parents | 2025 (Nov 2025) | Yes (large companies, 70) | 14 | Import as a positive-only value |
| VIII | Fortune Best Workplaces for Millennials | **2024** (no 2025 edition; no Gen Z list) | Yes (large companies, 100) | 17 | Low priority: data is 2 years old |
| IX | Newsweek America's Greenest Companies | **2027** (Oct 2026, 650 companies) | Not tested: blocked to automated fetch (HTTP 402) | ? | Promising; someone checks it in a browser |

Lists saved to `data/sbw2026/` (each row carries its source URL):
- `fortune_best_large_workplaces_women_2026.csv` (100)
- `fortune_best_large_workplaces_parents_2025.csv` (70)
- `fortune_best_large_workplaces_millennials_2024.csv` (100)
- `bbfaw_2025_tiers.csv` (149 companies, tier and Impact Rating)

## Design point for all the "best workplace" lists

These lists only name winners. Leaving a company off doesn't mean it is a bad workplace: most
companies never apply (Great Place To Work certification is opt-in and paid). So:
- A listed company gets a claim and a positive grade.
- An unlisted company gets **no claim and no snapshot**. It must not be graded F.
- Proposed scoring: `label` type, `listed` = A (or rank bands: top 25 = A, 26-100 = A-).

Rather than adding three values, these could share one value, `workplace_recognition`, holding one
claim per list. That needs a decision.

---

## I. Fortune Best Workplaces for Women 2026

- **Source:** https://fortune.com/ranking/best-workplaces-for-women/ (Great Place To Work, published October 2026)
- **What it measures:** Women's answers to the Great Place To Work Trust Index survey (about 60
  questions). To qualify, a company needs at least 50 women employees, at least 20% women among
  non-executive managers, and at least one woman in the C-suite.
- **Coverage:** 100 large companies (1,000+ employees) plus a separate small and medium list. We saved the large list.
- **Overlap (16):** Hilton (HLT) #1, Cisco (CSCO) #2, Accenture (ACN) #6, Marriott (MAR) #7, American Express (AXP) #10,
  Synchrony (SYF) #14, Robert Half (RHI) #22, AbbVie (ABBV) #30, Stryker (SYK) #31, Dick's (DKS) #34,
  Nvidia (NVDA) #40, Bank of America (BAC) #44, Ross Stores (ROST) #67, Salesforce (CRM) #82, MetLife (MET) #97, Target (TGT) #99
- **Not yet graded (examples):** Progressive #4, Delta #16, Wegmans #20, Elevance #42, Publix #75
- **Suggested slug:** `workplace_women`. Claim URI: `urn:fortune-gptw:2026:{slug}:best-workplaces-women`
- **Licensing:** Fortune's terms limit reproducing the list. Storing rank and list name as a fact,
  with a link back, matches how we already handle HRC and Guns Down America. Don't copy Fortune's text.
- **Correction to the ticket text:** the ticket's top 4 (Hilton, Cisco, East West Bank, Progressive) is the 2026 list.

## II. Fortune Best Workplaces for Diversity

- The newest Fortune page is the **2019** edition (https://fortune.com/ranking/best-workplaces-for-diversity/), top 10 only.
  The Great Place To Work list directory has no diversity list now.
- **Recommendation:** drop it. Possible replacements to research: Newsweek "America's Greatest Workplaces
  for Diversity" (published January 2025, same publisher as III-b) or Comparably Best Companies for Diversity.

## III. Fortune 100 Best Companies to Work For 2026

- https://fortune.com/ranking/best-companies/ (April 2026, 29th edition). Only the top 10 is visible
  without a subscription: Synchrony, Hilton, Cisco, American Express, Wegmans, Nvidia, Marriott,
  Accenture, Delta, World Wide Technology.
- **Recommendation:** skip, unless someone has the print issue or a subscription. The top companies are
  already on the women and parents lists.

## III-b. Newsweek America's Greatest Workplaces for Women 2026

- https://rankings.newsweek.com/americas-greatest-workplaces-for-women-2026 (published 2026-02-05, with
  Plant-A Insights; 1,000 companies, 1,000+ employees, star ratings by size band).
- The page returned HTTP 402 to our automated fetch. It may still open in a normal browser.
- **Next step:** someone opens it in a browser and confirms (a) the full list is free to view and (b) the score format (stars or points).
- With 1,000 companies, overlap with our 427 is likely high. This could be the best women-workplace source.

## IV. Catalyst / women's advancement

- The Catalyst Award picks only a few initiatives a year: CIBC, JDE Peet's, KPMG, McCarthy Tétrault and Sanofi in 2025;
  Sephora and Zoetis in 2024. Most winners are not US-listed. No 2026 winners found yet.
- No member list for CEO Champions for Change was found. Catalyst doesn't rank or score companies.
- **Recommendation:** don't import Catalyst. For women on boards, the cleaner source is the board
  makeup each company discloses in its SEC proxy (DEF 14A), or 50/50 Women on Boards (not checked).
  That would be a new value (`board_gender_diversity`, % women directors) and deserves its own ticket.

## V. BBFAW 2025 Benchmark (farm animal welfare)

- **Report:** https://www.bbfaw.com/media/2209/bbfaw-benchmark-2025.pdf (launched 2026-05-05; 149 companies, 6 tiers)
- **Already in Alonovo:** `farm_animal_welfare` value, ScoringRule v1 (tier 1 = A ... tier 6 = F), with 13
  companies from the 2024 report in `import_initial_data.py`.
- **2025 tiers:** Tier 1: none; Tier 2: Greggs, M&S, Premier Foods, Waitrose; Tier 3: 8 companies; Tier 4: 18; Tiers 5 and 6: the rest.
  Almost every US company is in tier 5 or 6.
- **Overlap (30):** the 13 already graded plus Chipotle, Conagra, Kraft Heinz, Unilever, Yum!, Hershey, Barilla,
  Campbell, Chick-fil-A, Darden, General Mills, Mars, Starbucks, Sysco, Target, Mondelez, Danone.
- **How `bbfaw_2025_tiers.csv` was made:** parsed from Figure 1.1 of the PDF. Tier boundaries were checked against
  Table 1.2 (tier movements), and all 19 moved companies landed in the right tier. Still check it visually against the PDF before import.
- **Discrepancy to check:** our 2024 claims give Walmart, Costco and Domino's **tier 5**. In the 2025 report they are
  **tier 6**, and they are not in the "falling" table, so they were probably tier 6 in 2024 too. The 2024 entries
  may be wrong. Claims are immutable, so a correction would mean a new claim, not an edit.
- **Import notes:**
  - New claims `urn:bbfaw:2025:{slug}:tier`, `effective_date` 2026-05-05. Keep the 2024 claims.
  - The snapshot code in `import_initial_data.py` uses `bbfaw_claims.first()`. `Claim` has no default
    ordering, so that can pick the old 2024 claim. The new command must use `.order_by('-effective_date').first()`.
  - Don't touch the existing value or scoring rule.

## VI. Charity: Chronicle of Philanthropy

- The ticket's top-10 table (2011 giving as a share of 2010 pre-tax profits) **didn't come through in the
  paste**, so only the Kroger footnote survived. Later editions (2016, 2018) are for subscribers only.
  The 2018 article (https://www.philanthropy.com/news/corporate-cash-giving-rises-5-exclusive-chronicle-survey-shows/)
  covers 2017 giving and puts the full data behind a paywall.
- **Recommendation:** don't import. The data is too old to grade companies on in 2026. Better options to research:
  - each company's foundation Form 990-PF plus 10-K pre-tax income, so we compute the giving share ourselves, or
  - CECP Giving in Numbers (aggregate only, no company names).

## VII. Fortune Best Workplaces for Parents 2025

- https://fortune.com/ranking/best-large-workplaces-parents/ (published 2025-11-18). 70 large companies; about 606,000 survey
  answers from parents; companies need 50+ parent responses. The 2026 edition is likely due this month (November 2026).
- **Overlap (14):** American Express #1, Nvidia #2, Hilton #3, Cisco #7, Synchrony #10, Salesforce #16, Stryker #19,
  AbbVie #25, CarMax #32, Bank of America #33, Marriott #34, HPE #51, Intuit #52, Mastercard #60
- **Suggested slug:** `workplace_parents` (or a claim under `workplace_recognition`).
  **Wait a few weeks and import the 2026 list instead.**

## VIII. Fortune Best Workplaces for Millennials

- https://fortune.com/best-workplaces-millennials/ — the latest edition is **2024**. No 2025 edition, and no Gen Z list exists.
- **Overlap (17):** Cisco, Hilton, Nvidia, Marriott, Comcast, American Express, Synchrony, Adobe, Mastercard, Stryker,
  Robert Half, Intuit, Cadence, MetLife, **Altria** (#86; Altria is a tobacco company and tobacco is disqualifying), Bank of America, Grainger.
- **Recommendation:** low priority. It overlaps heavily with I and VII and is two years old.

## IX. Newsweek America's Greenest Companies 2027

- https://rankings.newsweek.com/americas-greenest-companies-2027 (published October 2026, with Plant-A Insights and GIST Impact).
  650 companies, out of about 1,700 that met the entry rules. Scored against their own industry: GHG 50%,
  water 20%, waste 20%, commitments and disclosure 10%. Lists by size band.
- The ticket expected a February issue; the 2027 list is already out.
- The page returned HTTP 402 to our automated fetch. **Next step:** someone opens it in a browser and checks
  whether the score column is free to view.
- **Fit:** this would complement our `ghg_emissions` value (NZDPU, 178 companies) rather than replace it.
  Suggested slug: `green_ranking`. Like the workplace lists, it names winners only, so unlisted companies are not graded.

---

## Decisions (team lead, 2026-11-10)

1. BBFAW 2025: **approved**. Command: `import_bbfaw_2025_data`.
2. Fortune lists: **one shared value**, `workplace_recognition`, holding Women 2026 and Parents 2025.
   It sits in the **Worker Rights** display group, so it is averaged with the other worker values instead of
   counting as a whole group of its own in the overall grade.
   Command: `import_workplace_lists_data`. Millennials 2024 is left out (2 years old, overlaps the other two).
3. Newsweek (III-b, IX): the pages didn't open for the team lead either. Parked.
4. **Dropped:** II Fortune Diversity (discontinued), IV Catalyst (no company scores), VI Chronicle (data too old).

## Running the imports (production)

What the two commands change: they add claims (they never edit or delete any), create or update
`farm_animal_welfare` and `workplace_recognition` snapshots, and **replace** those companies' badges for those two
values (the old badge is deleted and a new one created). `import_workplace_lists_data` also creates the
`workplace_recognition` Value and its ScoringRule v1. They only touch companies already on Alonovo, and
running either one twice is safe.

### 0. Before you start

- [ ] The branch is reviewed and merged (or checked out) on the server, so both commands and `data/sbw2026/` are there.
- [ ] Someone has compared `data/sbw2026/bbfaw_2025_tiers.csv` with Figure 1.1 (page 21) of the BBFAW PDF, especially
      Walmart, Costco and Domino's (tier 6).
- [ ] Confirm the production path. CLAUDE.md says `/home/ec2-user/alonovo2`; older notes say `/opt/shared/repos/alonovo`.

### 1. Back up (three files)

```bash
cd /home/ec2-user/alonovo2/backend
source venv/bin/activate
STAMP=$(date +%Y%m%d_%H%M%S)
# a. Full Django backup (house standard)
python manage.py dumpdata --natural-primary --natural-foreign -o ../backups/pre_sbw2026_full_$STAMP.json
# b. Grades and badges only: this is what the targeted rollback restores
python manage.py dumpdata core.CompanyValueSnapshot core.CompanyBadge --natural-primary --natural-foreign \
    -o ../backups/pre_sbw2026_scores_$STAMP.json
# c. Postgres dump: last-resort full restore
sudo -u postgres pg_dump alonovo > ../backups/pre_sbw2026_pgdump_$STAMP.sql
ls -la ../backups/*$STAMP*          # all three files exist and are not empty
echo $STAMP                         # write this down for the rollback
```

### 2. Import

```bash
python manage.py import_bbfaw_2025_data --dry-run      # 30 companies; check old -> new grade against "Expected" below
python manage.py import_bbfaw_2025_data --limit 10     # first 10 in report order (Kroger, Amazon, Chipotle ... all tier 5)
#   check e.g. https://alonovo.cooperation.org/api/companies/KR/ and /CMG/ show "BBFAW Tier 5 (2025)"
python manage.py import_bbfaw_2025_data                # the rest; the first 10 are skipped as already done

python manage.py import_workplace_lists_data --dry-run # 20 companies
python manage.py import_workplace_lists_data --limit 10
#   check /api/companies/HLT/ shows "Fortune Best Workplaces: Women #1, Parents #3", grade A
python manage.py import_workplace_lists_data
```

**No gunicorn restart needed.** These commands only write data. The API reads the database on every request
(no cache is configured), and the web code doesn't change. Restart only if the merge also changes code gunicorn serves.

### 3. Roll back (if the results look wrong)

Targeted rollback. It removes only what these imports added and puts the old grades back. Rehearsed on a test
copy of the database: afterwards every row matched the pre-import state (timestamps aside).

```bash
cd /home/ec2-user/alonovo2/backend && source venv/bin/activate
python manage.py shell <<'EOF'
from django.db import transaction
from core.models import Claim, Value, CompanyValueSnapshot, CompanyBadge
with transaction.atomic():
    n_claims = Claim.objects.filter(uri__startswith='urn:bbfaw:2025:').delete()[0]
    n_claims += Claim.objects.filter(uri__startswith='urn:fortune-gptw:').delete()[0]
    n_badges = CompanyBadge.objects.filter(value_id__in=['farm_animal_welfare', 'workplace_recognition']).delete()[0]
    n_snaps = CompanyValueSnapshot.objects.filter(value_id__in=['farm_animal_welfare', 'workplace_recognition']).delete()[0]
    n_value = Value.objects.filter(slug='workplace_recognition').delete()[0]  # also removes its ScoringRule and user weights
print(f"Deleted {n_claims} claims, {n_badges} badges, {n_snaps} snapshots, workplace value rows: {n_value}")
print("Now run loaddata on the pre_sbw2026_scores backup to restore the old farm_animal_welfare grades.")
EOF
python manage.py loaddata ../backups/pre_sbw2026_scores_<STAMP>.json
```

Notes:
- This deletes the claims the imports created (URIs starting `urn:bbfaw:2025:` and `urn:fortune-gptw:`). Claims are
  normally never deleted, so only do this to undo this import, with the team lead's OK.
- Deleting the `workplace_recognition` value also deletes any user weights set for it after the import.
- Use the `scores` backup taken just before the import. An older one would also roll back unrelated grade changes.
- **Last resort, if the database is in a bad state:** restore the Postgres dump (c). It replaces the whole database,
  so anything written after the backup (new users, votes, weights) is lost. Stop gunicorn, restore into the
  `alonovo` database, start gunicorn. Do this only with the team lead.
- The full JSON backup (a) is not a rollback by itself: `loaddata` adds and overwrites rows but never removes the
  rows the import created.

Expected grade changes (checked on a test copy of the database):
- BBFAW: 17 companies get a farm animal welfare grade for the first time.
- Walmart, Costco and Domino's go from D (tier 5, 2024) to **F (tier 6, 2025)**.
- Danone gets B, Hershey and Barilla C, and Starbucks, Target, General Mills, Mars, Mondelez, Campbell,
  Darden, Sysco and Chick-fil-A F.
- Workplace: 11 companies get A (best rank in the top 25) and 9 get A-. Unlisted companies are unchanged.

When Fortune Parents 2026 comes out: save it as `data/sbw2026/fortune_best_large_workplaces_parents_2026.csv`,
change the `parents` entry in `LISTS`, add any new tickers to `TICKERS`, and re-run. The newer claim then replaces the 2025 one.
