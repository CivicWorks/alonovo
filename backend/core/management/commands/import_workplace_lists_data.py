"""Import Fortune / Great Place To Work best-workplace lists into one value: workplace_recognition.

Data sources (lists saved under data/sbw2026/, one row per company with rank):
- Fortune Best Large Workplaces for Women 2026 (published October 2026)
  https://fortune.com/ranking/best-workplaces-for-women/
- Fortune Best Large Workplaces for Parents 2025 (published November 2025)
  https://fortune.com/ranking/best-large-workplaces-parents/
Research notes: prompts/sbw_2026_sources.md

These lists only name winners, and companies opt in to the survey. A listed company gets a
claim and a positive grade; an unlisted company gets NO claim and NO snapshot (never an F).

Grade: best rank on any list <= 25 -> A (1.0), otherwise A- (0.85).
Only companies already on Alonovo are imported (matched by ticker below).
To add a list (e.g. Parents 2026): save the CSV, add it to LISTS, add any new tickers to TICKERS.

Usage:
    python manage.py import_workplace_lists_data --dry-run
    python manage.py import_workplace_lists_data --limit 10
    python manage.py import_workplace_lists_data
"""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge

DATA_DIR = os.path.join(settings.BASE_DIR, '..', 'data', 'sbw2026')
VALUE = 'workplace_recognition'
CLAIM_TYPE = 'WORKPLACE_LIST_RANK'

# key, short label for display, file, year, publication date, source URL
LISTS = [
    ('women', 'Women', 'fortune_best_large_workplaces_women_2026.csv', 2026, '2026-10-23',
     'https://fortune.com/ranking/best-workplaces-for-women/'),
    ('parents', 'Parents', 'fortune_best_large_workplaces_parents_2025.csv', 2025, '2025-11-18',
     'https://fortune.com/ranking/best-large-workplaces-parents/'),
]

# Fortune list name -> ticker of the company already on Alonovo (checked 2026-11-10).
# Names not listed here are skipped. Do not add look-alikes (e.g. Hilton Food Group,
# American Fidelity, Cardinal Financial are different companies).
TICKERS = {
    'Hilton Worldwide Holdings': 'HLT',
    'Cisco Systems': 'CSCO',
    'Accenture': 'ACN',
    'Marriott International': 'MAR',
    'American Express': 'AXP',
    'Synchrony Financial': 'SYF',
    'Robert Half': 'RHI',
    'AbbVie': 'ABBV',
    'Stryker': 'SYK',
    "Dick's Sporting Goods": 'DKS',
    'Nvidia': 'NVDA',
    'Bank of America': 'BAC',
    'Ross Stores': 'ROST',
    'Salesforce': 'CRM',
    'MetLife': 'MET',
    'Target': 'TGT',
    'CarMax': 'KMX',
    'Hewlett Packard Enterprise': 'HPE',
    'Intuit': 'INTU',
    'Mastercard': 'MA',
}


class Command(BaseCommand):
    help = "Import Fortune best-workplace lists (women, parents) into workplace_recognition"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Show what would be imported without saving")
        parser.add_argument('--limit', type=int, default=0, help="Only import the first N matched companies (0 = all)")

    def handle(self, *args, **options):
        dry_run, limit = options['dry_run'], options['limit']

        # company -> list of (list key, label, rank, row info)
        entries = {}
        for key, label, filename, year, date, url in LISTS:
            rows = self.read_rows(filename)
            hits = 0
            for row in rows:
                ticker = TICKERS.get(row['company'])
                if not ticker:
                    continue
                company = Company.objects.filter(ticker=ticker).first()
                if not company:
                    self.stdout.write(self.style.WARNING(f"  {row['company']}: ticker {ticker} not in database, skipped"))
                    continue
                entries.setdefault(company, []).append(
                    dict(key=key, label=label, rank=int(row['rank']), year=year, date=date, url=url,
                         list_name=row['list']))
                hits += 1
            self.stdout.write(f"{label} {year}: {len(rows)} companies on the list, {hits} on Alonovo")

        companies = sorted(entries, key=lambda c: min(e['rank'] for e in entries[c]))
        if limit:
            companies = companies[:limit]
        self.stdout.write(f"{len(companies)} companies to import")

        for company in companies:
            self.stdout.write(f"  {company.name}: {self.display_text(entries[company])} -> "
                              f"{self.grade_for(entries[company])[0]}")
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: nothing saved"))
            return

        claims = 0
        with transaction.atomic():
            self.create_value()
            self.create_scoring_rule()
            for company in companies:
                for e in entries[company]:
                    if self.create_claim(company, e):
                        claims += 1
                self.update_snapshot_and_badge(company)

        self.stdout.write(self.style.SUCCESS(f"Done! {claims} new claims, {len(companies)} snapshots"))

    def read_rows(self, filename):
        path = os.path.abspath(os.path.join(DATA_DIR, filename))
        if not os.path.exists(path):
            raise CommandError(f"Data file not found: {path}")
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def create_value(self):
        Value.objects.update_or_create(
            slug=VALUE,
            defaults={
                'name': 'Great Workplace Recognition',
                'description': 'Named on a Fortune / Great Place To Work best-workplace list (women, parents), '
                               'based on employee surveys. Only listed companies are graded; '
                               'not being listed is not a negative.',
                'value_type': 'label',
                'is_fixed': False,
                'is_disqualifying': False,
                # Same group as forced_labor, exec_pay_ratio, employee_ownership, leadership_diversity
                'display_group': 'Worker Rights',
                'display_group_order': 1,
                'card_display_template': '{label}',
                'card_icon': 'briefcase',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id=VALUE,
            version=1,
            defaults={
                'effective_date': '2026-11-10',
                'config': {
                    'type': 'rank_band',
                    'note': 'Best rank across Fortune best-workplace lists. Unlisted companies are not graded.',
                    'bands': [
                        {'max_rank': 25, 'grade': 'A', 'score': 1.0},
                        {'max_rank': 100, 'grade': 'A-', 'score': 0.85},
                    ],
                }
            }
        )

    def grade_for(self, entries):
        best = min(e['rank'] for e in entries)
        return ('A', 1.0) if best <= 25 else ('A-', 0.85)

    def display_text(self, entries):
        parts = ', '.join(f"{e['label']} #{e['rank']}" for e in sorted(entries, key=lambda e: e['rank']))
        return f"Fortune Best Workplaces: {parts}"

    def claim_slug(self, company):
        return (company.ticker or company.uri.rsplit(':', 1)[-1]).lower().replace('.', '-')

    def create_claim(self, company, e):
        uri = f"urn:fortune-gptw:{e['year']}:{self.claim_slug(company)}:best-workplaces-{e['key']}"
        if Claim.objects.filter(uri=uri).exists():
            return None
        return Claim.objects.create(
            uri=uri,
            subject=company.uri,
            claim_type=CLAIM_TYPE,
            label=f"{e['key']}_{e['year']}",
            amt=e['rank'],
            unit='rank',
            statement=f"Ranked #{e['rank']} on {e['list_name']}",
            effective_date=e['date'],
            source_uri=e['url'],
            how_known='official_report',
            author='Fortune / Great Place To Work',
        )

    def update_snapshot_and_badge(self, company):
        # Use the newest claim per list key, so a 2026 list replaces the 2025 one.
        latest = {}
        for c in (Claim.objects.filter(subject=company.uri, claim_type=CLAIM_TYPE)
                  .order_by('-effective_date', '-created_at')):
            key = c.label.rsplit('_', 1)[0]
            latest.setdefault(key, c)
        labels = dict((k, lbl) for k, lbl, *_ in LISTS)
        entries = [dict(label=labels.get(k, k.title()), rank=int(c.amt)) for k, c in latest.items()]
        grade, score = self.grade_for(entries)
        text = self.display_text(entries)
        uris = [c.uri for c in latest.values()]
        CompanyValueSnapshot.objects.update_or_create(
            company=company,
            value_id=VALUE,
            defaults={
                'score': score,
                'grade': grade,
                'claim_uris': uris,
                'highlight_on_card': True,
                'highlight_priority': 2,
                'display_text': text,
                'display_icon': 'briefcase',
                'scoring_rule_version': 1,
            }
        )
        CompanyBadge.objects.filter(company=company, value_id=VALUE).delete()
        CompanyBadge.objects.create(
            company=company,
            value_id=VALUE,
            label=text,
            badge_type='positive',
            source_claim_uri=uris[0],
            priority=2,
        )
