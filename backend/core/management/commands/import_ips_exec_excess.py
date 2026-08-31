"""Import company data from the IPS Executive Excess 2026 report.

Data source: Institute for Policy Studies, Executive Excess 2026 (32nd annual
edition, released 2026-08-27), Appendix 1: the "Low-Wage 100" — the 100 S&P 500
companies with the lowest median worker pay in 2025. Underlying figures come
from SEC proxy statements (DEF 14A) and 10-K/10-Q filings.
https://ips-dc.org/report-executive-excess-2026/

IPS publishes the report as PDF only (no CSV/API). This command downloads the
PDF, parses the Appendix 1 table, resolves company names to tickers against the
S&P 500 constituents list (data/sp500_constituents.csv, vendored from
https://github.com/datasets/s-and-p-500-companies), and creates claims:

  CEO_PAY_RATIO      2025 CEO-to-median-worker pay ratio
  CEO_COMPENSATION   2025 CEO total compensation ($ million)
  MEDIAN_WORKER_PAY  2025 median worker pay ($/year)
  STOCK_BUYBACKS     2025 stock buyback expenditures ($ million)
  LOW_WAGE_100       membership in the Low-Wage 100

It then recomputes exec_pay_ratio snapshots for affected companies using the
newest CEO_PAY_RATIO claim per company, and creates/updates the low_wage_100
label value, snapshots, and badges.

Run with --dry-run to parse and resolve without touching the database.
"""
import csv
import re
import unicodedata
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from core.models import (
    Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge,
)

REPORT_URL = 'https://ips-dc.org/wp-content/uploads/2026/08/executive_excess_2026_report.pdf'
REPORT_PAGE = 'https://ips-dc.org/report-executive-excess-2026/'
APPENDIX_PAGES = (22, 23, 24)  # 0-based page indexes of Appendix 1
EFFECTIVE_DATE = '2025-12-31'  # figures are for fiscal 2025
AUTHOR = 'Institute for Policy Studies, Executive Excess 2026 (from SEC proxy statements)'

DATA_DIR = Path(__file__).resolve().parents[4] / 'data'
DEFAULT_CONSTITUENTS = DATA_DIR / 'sp500_constituents.csv'
DEFAULT_PDF_CACHE = DATA_DIR / 'ips_executive_excess_2026.pdf'

# One table row: 8 numeric cells after the company/CEO names.
# `\$?` on ratio: the Wabtec row is misprinted "$509" in the PDF.
# `bb` optional: the Lumentum row has no 2025 buyback figure, only the total.
ROW = re.compile(
    r'\$(?P<ceo>[\d,.]+)\s+(?P<ceoch>-?[\d,.]+%|n/a)\s+'
    r'\$(?P<median>[\d,]+)\s+(?P<medch>-?[\d,.]+%|n/a)\s+'
    r'\$?(?P<ratio>[\d,]+)\s+(?P<ratioch>-?[\d,.]+%|n/a)\s+'
    r'(?:\$(?P<bb>[\d,]+)\s+)?\$(?P<bbtot>[\d,]+)')

# Column-header fragments that pypdf interleaves with the first row of each page.
JUNK = re.compile(
    r'^((2025|% ?change,?|\(\$million\)|\(nominal\)|2019-2025( total)?|CEO compensation|'
    r'Median worker pay|CEO-worker pay ratio|Stock buyback expenditures|Low-Wage 100 firm,?|'
    r'ranked alphabetically|CEO in 2025|Appendix 1:.*?|The 100 S&P 500 companies with the|'
    r'lowest median worker wages in 2025|\d{1,2})\s+)+')

STOP = {'inc', 'corp', 'corporation', 'company', 'companies', 'co', 'plc', 'intl',
        'international', 'holdings', 'group', 'the', 'cos'}

# Report label (normalized) -> ticker, where name matching cannot resolve it.
ALIASES = {
    'caseys general stores': 'CASY',   # listed as "Casey's"
    'cognizant tech solutions': 'CTSH',  # listed as "Cognizant"
    'smith': 'AOS',                    # printed as "Smith (A.O.)"
    'cooper': 'COO',                   # Cooper Companies
}

# In the report but no longer in the current S&P 500 constituents list.
EXTRA = {
    'epam systems': ('EPAM', 'EPAM Systems', 'Information Technology'),
}


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9& ]', ' ', s)
    return ' '.join(t for t in s.split() if t not in STOP)


class Command(BaseCommand):
    help = "Import Low-Wage 100 data (pay ratios, median pay, buybacks) from IPS Executive Excess 2026"

    def add_arguments(self, parser):
        parser.add_argument('--pdf', help=f'Path to the report PDF (default: download to {DEFAULT_PDF_CACHE})')
        parser.add_argument('--constituents', default=str(DEFAULT_CONSTITUENTS),
                            help='S&P 500 constituents CSV (Symbol,Security,GICS Sector,...)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Parse and resolve only; no database writes')

    def handle(self, *args, **options):
        pdf_path = self.get_pdf(options['pdf'])
        known = self.load_constituents(options['constituents'])
        rows = self.parse_appendix(pdf_path, known)

        if options['dry_run']:
            for r in rows:
                self.stdout.write(
                    f"{r['ticker']:6} {r['name']:40} ratio {r['ratio']:>6,}:1  "
                    f"median ${r['median']:>7,}  CEO ${r['ceo_m']}M  "
                    f"buybacks2025 {'$%s M' % format(r['bb_m'], ',') if r['bb_m'] is not None else 'n/a'}"
                )
            self.stdout.write(self.style.SUCCESS(f"Dry run: {len(rows)} companies parsed and resolved"))
            return

        self.stdout.write("Creating low_wage_100 Value and ScoringRule...")
        self.create_low_wage_value()

        self.stdout.write("Importing claims...")
        count = self.import_claims(rows)

        self.stdout.write("Recomputing exec_pay_ratio snapshots (newest claim per company)...")
        snap = self.compute_ratio_snapshots(rows)

        self.stdout.write("Creating low_wage_100 snapshots and badges...")
        lw = self.compute_low_wage_snapshots(rows)

        self.stdout.write(self.style.SUCCESS(
            f"Done. {count} claims, {snap} pay-ratio snapshots, {lw} low-wage-100 snapshots"
        ))

    # ---------- retrieval ----------

    def get_pdf(self, pdf_option):
        if pdf_option:
            path = Path(pdf_option)
            if not path.exists():
                raise CommandError(f"PDF not found: {path}")
            return path
        path = DEFAULT_PDF_CACHE
        if not path.exists():
            import requests
            self.stdout.write(f"Downloading {REPORT_URL} ...")
            resp = requests.get(REPORT_URL, timeout=60)
            resp.raise_for_status()
            if not resp.content.startswith(b'%PDF'):
                raise CommandError("Downloaded file is not a PDF")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(resp.content)
        return path

    def load_constituents(self, csv_path):
        path = Path(csv_path)
        if not path.exists():
            raise CommandError(f"Constituents CSV not found: {path}")
        known = {}
        with open(path) as f:
            for r in csv.DictReader(f):
                known[norm(r['Security'])] = (r['Symbol'], r['Security'], r.get('GICS Sector', ''))
        return known

    # ---------- parsing ----------

    def parse_appendix(self, pdf_path, known):
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        lines = []
        for i in APPENDIX_PAGES:
            lines += [l.strip() for l in reader.pages[i].extract_text().splitlines()
                      if l.strip() and 'n/a = did not exist' not in l]
        blob = ' '.join(lines)

        rows, pos = [], 0
        unresolved = []
        for m in ROW.finditer(blob):
            prefix = JUNK.sub('', blob[pos:m.start()].strip())
            pos = m.end()
            ticker, name = self.resolve(prefix, known)
            if not ticker:
                unresolved.append(prefix)
                continue
            d = m.groupdict()
            rows.append({
                'ticker': ticker,
                'name': name,
                'sector': known.get(norm(name), (None, None, ''))[2],
                'ceo_m': Decimal(d['ceo'].replace(',', '')),
                'median': int(d['median'].replace(',', '')),
                'ratio': int(d['ratio'].replace(',', '')),
                'bb_m': int(d['bb'].replace(',', '')) if d['bb'] else None,
                'bbtot_m': int(d['bbtot'].replace(',', '')),
            })

        if unresolved:
            raise CommandError(
                f"{len(unresolved)} unresolved company rows (add to ALIASES/EXTRA): {unresolved}")
        tickers = [r['ticker'] for r in rows]
        dupes = {t for t in tickers if tickers.count(t) > 1}
        if dupes:
            raise CommandError(f"Duplicate tickers resolved: {dupes}")
        if len(rows) != 100:
            raise CommandError(f"Expected 100 Low-Wage 100 rows, parsed {len(rows)}")
        return rows

    def resolve(self, prefix, known):
        toks = prefix.split()
        for k in range(min(6, len(toks)), 0, -1):
            cand = norm(' '.join(toks[:k]))
            if not cand:
                continue
            if cand in EXTRA:
                ticker, name, _ = EXTRA[cand]
                return ticker, name
            if cand in ALIASES:
                ticker = ALIASES[cand]
                row = next(v for v in known.values() if v[0] == ticker)
                return ticker, row[1]
            if cand in known:
                return known[cand][0], known[cand][1]
            starts = [v for nk, v in known.items() if nk.startswith(cand + ' ')]
            if len(starts) == 1 and len(cand) >= 3:
                return starts[0][0], starts[0][1]
        return None, None

    # ---------- import ----------

    def get_or_create_company(self, row):
        existing = Company.objects.filter(ticker=row['ticker']).first()
        if existing:
            if row['sector'] and not existing.sector:
                existing.sector = row['sector']
                existing.save()
            return existing
        slug = slugify(row['name'])
        company, _ = Company.objects.update_or_create(
            uri=f"urn:company:{slug}",
            defaults={'name': row['name'], 'ticker': row['ticker'], 'sector': row['sector']},
        )
        return company

    def create_claim_safe(self, **kwargs):
        if Claim.objects.filter(uri=kwargs['uri']).exists():
            return None
        return Claim.objects.create(**kwargs)

    def import_claims(self, rows):
        count = 0
        for row in rows:
            company = self.get_or_create_company(row)
            slug = slugify(row['name'])
            claims = [
                dict(
                    uri=f'urn:ips-ee:2026:{slug}:pay-ratio',
                    claim_type='CEO_PAY_RATIO',
                    amt=Decimal(row['ratio']),
                    unit='ratio_to_1',
                    statement=f"CEO-to-median-worker pay ratio: {row['ratio']:,}:1 (2025)",
                ),
                dict(
                    uri=f'urn:ips-ee:2026:{slug}:ceo-comp',
                    claim_type='CEO_COMPENSATION',
                    amt=row['ceo_m'],
                    unit='usd_million',
                    statement=f"CEO total compensation: ${row['ceo_m']} million (2025)",
                ),
                dict(
                    uri=f'urn:ips-ee:2026:{slug}:median-pay',
                    claim_type='MEDIAN_WORKER_PAY',
                    amt=Decimal(row['median']),
                    unit='usd_per_year',
                    statement=f"Median worker pay: ${row['median']:,} (2025)",
                ),
                dict(
                    uri=f'urn:ips-ee:2026:{slug}:low-wage-100',
                    claim_type='LOW_WAGE_100',
                    label='low_wage_100',
                    statement="Among the 100 S&P 500 companies with the lowest median worker pay in 2025 (IPS Low-Wage 100)",
                ),
            ]
            if row['bb_m'] is not None:
                claims.append(dict(
                    uri=f'urn:ips-ee:2026:{slug}:buybacks-2025',
                    claim_type='STOCK_BUYBACKS',
                    amt=Decimal(row['bb_m']),
                    unit='usd_million',
                    statement=(f"Stock buybacks: ${row['bb_m']:,} million in 2025; "
                               f"${row['bbtot_m']:,} million total 2019-2025"),
                ))
            for c in claims:
                created = self.create_claim_safe(
                    subject=company.uri,
                    effective_date=EFFECTIVE_DATE,
                    source_uri=REPORT_URL,
                    how_known='published_report',
                    author=AUTHOR,
                    **c,
                )
                if created:
                    count += 1
            self.stdout.write(f"  {row['ticker']}: ratio {row['ratio']:,}:1, median ${row['median']:,}")
        return count

    # ---------- scoring ----------

    def create_low_wage_value(self):
        Value.objects.update_or_create(
            slug='low_wage_100',
            defaults={
                'name': 'Low-Wage 100',
                'description': ('Among the 100 S&P 500 companies with the lowest median worker pay, '
                                'per the Institute for Policy Studies annual Executive Excess report. '
                                f'Source: {REPORT_PAGE}'),
                'value_type': 'label',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'Low-Wage 100',
                'card_icon': 'trending-down',
            },
        )
        ScoringRule.objects.update_or_create(
            value_id='low_wage_100',
            version=1,
            defaults={
                'effective_date': '2026-08-27',
                'config': {
                    'type': 'label_map',
                    'note': 'Membership in the IPS Low-Wage 100. Score is an editable default.',
                    'labels': {
                        'low_wage_100': {'grade': 'D', 'score': -0.3},
                    },
                },
            },
        )

    def _apply_threshold_inverse(self, thresholds, value):
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def compute_ratio_snapshots(self, rows):
        rule = ScoringRule.objects.get(value_id='exec_pay_ratio', version=1)
        count = 0
        for row in rows:
            company = Company.objects.filter(ticker=row['ticker']).first()
            if not company:
                continue
            claim = (Claim.objects
                     .filter(subject=company.uri, claim_type='CEO_PAY_RATIO')
                     .order_by('-effective_date')
                     .first())
            if not claim:
                continue
            ratio = float(claim.amt)
            grade, score = self._apply_threshold_inverse(rule.config['thresholds'], ratio)
            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='exec_pay_ratio',
                defaults={
                    'score': score,
                    'grade': grade,
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 2,
                    'display_text': f"CEO pay: {int(ratio):,}:1",
                    'display_icon': 'dollar-sign',
                    'scoring_rule_version': 1,
                },
            )
            badge_type = 'positive' if score > 0.3 else ('negative' if score < -0.3 else 'neutral')
            CompanyBadge.objects.update_or_create(
                company=company,
                value_id='exec_pay_ratio',
                defaults={
                    'label': f"CEO pay: {int(ratio):,}:1",
                    'badge_type': badge_type,
                    'source_claim_uri': claim.uri,
                    'priority': 2,
                },
            )
            count += 1
        return count

    def compute_low_wage_snapshots(self, rows):
        rule = ScoringRule.objects.get(value_id='low_wage_100', version=1)
        cfg = rule.config['labels']['low_wage_100']
        count = 0
        for row in rows:
            company = Company.objects.filter(ticker=row['ticker']).first()
            if not company:
                continue
            claim_uri = f"urn:ips-ee:2026:{slugify(row['name'])}:low-wage-100"
            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='low_wage_100',
                defaults={
                    'score': cfg['score'],
                    'grade': cfg['grade'],
                    'claim_uris': [claim_uri],
                    'highlight_on_card': False,
                    'display_text': 'Low-Wage 100 (IPS 2026)',
                    'display_icon': 'trending-down',
                    'scoring_rule_version': 1,
                },
            )
            CompanyBadge.objects.update_or_create(
                company=company,
                value_id='low_wage_100',
                defaults={
                    'label': 'Low-Wage 100',
                    'badge_type': 'negative',
                    'source_claim_uri': claim_uri,
                    'priority': 1,
                },
            )
            count += 1
        return count
