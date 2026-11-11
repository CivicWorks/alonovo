"""Import BBFAW 2025 Benchmark tiers into the existing farm_animal_welfare value.

Data source: Business Benchmark on Farm Animal Welfare, 2025 Report (launched 2026-05-05)
https://www.bbfaw.com/media/2209/bbfaw-benchmark-2025.pdf
Tiers 1 (leadership) to 6 (no evidence), Figure 1.1 of the report.
Full table for all 149 companies: data/sbw2026/bbfaw_2025_tiers.csv
Research notes: prompts/sbw_2026_sources.md

Only companies already on Alonovo are imported (matched by company URI below); the
rest of the 149 are reported as skipped. The 2024 claims stay; the snapshot uses the
newest claim by effective_date. The value and ScoringRule v1 are not changed.

Usage:
    python manage.py import_bbfaw_2025_data --dry-run
    python manage.py import_bbfaw_2025_data --limit 10
    python manage.py import_bbfaw_2025_data
"""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Claim, Company, ScoringRule, CompanyValueSnapshot, CompanyBadge

DATA_FILE = os.path.join(settings.BASE_DIR, '..', 'data', 'sbw2026', 'bbfaw_2025_tiers.csv')
SOURCE_URI = 'https://www.bbfaw.com/media/2209/bbfaw-benchmark-2025.pdf'
EFFECTIVE_DATE = '2026-05-05'
VALUE = 'farm_animal_welfare'

# BBFAW company name (as in the CSV) -> (claim slug, Alonovo company URI)
# URIs checked against https://alonovo.cooperation.org/api/companies/ on 2026-11-10.
COMPANY_MAP = {
    # Already graded from the 2024 report (slugs match the 2024 claim URIs)
    "Marks & Spencer PLC": ('marks-and-spencer', 'urn:company:marks-and-spencer'),
    "Waitrose": ('waitrose', 'urn:company:waitrose'),
    "Premier Foods PLC": ('premier-foods', 'urn:company:premier-foods'),
    "Greggs PLC": ('greggs', 'urn:company:greggs'),
    "McDonald’s Corporation": ('mcdonalds', 'urn:alonovo:company:mcd'),
    "Tyson Foods Inc": ('tyson-foods', 'urn:company:tyson-foods'),
    "Amazon/Whole Foods Market": ('amazon-whole-foods', 'urn:alonovo:company:amzn'),
    "Domino’s Pizza Inc": ('dominos-pizza', 'urn:company:dominos-pizza'),
    "Nestlé SA": ('nestle', 'urn:company:nestle'),
    "Walmart Inc": ('walmart', 'urn:alonovo:company:wmt'),
    "Tesco PLC": ('tesco', 'urn:company:tesco'),
    "Costco Wholesale Corporation": ('costco', 'urn:alonovo:company:cost'),
    "(The) Kroger Company": ('kroger', 'urn:company:kroger'),
    # On Alonovo but not yet graded for farm animal welfare
    "Chipotle Mexican Grill": ('chipotle', 'urn:company:chipotle'),
    "ConAgra": ('conagra', 'urn:company:cag'),
    "Kraft Heinz Company": ('kraft-heinz', 'urn:company:kraft-heinz'),
    "Unilever NV": ('unilever', 'urn:company:unilever'),
    "Yum! Brands Inc": ('yum-brands', 'urn:company:yum-brands'),
    "Hershey Co": ('hershey', 'urn:company:hershey'),
    "Barilla SpA": ('barilla', 'urn:company:barilla'),
    "Campbell Soup Company": ('campbell-soup', 'https://alonovo.cooperation.org/company/campbell-soup'),
    "Chick-fil-A": ('chick-fil-a', 'urn:company:chick-fil-a'),
    "Darden Restaurants PLC": ('darden-restaurants', 'urn:company:darden-restaurants'),
    "General Mills Inc": ('general-mills', 'https://alonovo.cooperation.org/company/general-mills'),
    "Mars Inc": ('mars', 'urn:company:mars'),
    "Starbucks Corporation": ('starbucks', 'urn:alonovo:company:sbux'),
    "Sysco Corporation": ('sysco', 'urn:company:syy'),
    "Target Corporation": ('target', 'urn:alonovo:company:tgt'),
    "Mondelēz International": ('mondelez', 'https://alonovo.cooperation.org/company/mondelez-international'),
    "Groupe Danone SA": ('danone', 'urn:company:danone'),
}


class Command(BaseCommand):
    help = "Import BBFAW 2025 Benchmark tiers (farm_animal_welfare) for companies already on Alonovo"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Show what would be imported without saving")
        parser.add_argument('--limit', type=int, default=0, help="Only import the first N matched companies (0 = all)")

    def handle(self, *args, **options):
        dry_run, limit = options['dry_run'], options['limit']
        rule = ScoringRule.objects.filter(value_id=VALUE, version=1).first()
        if not rule:
            raise CommandError(f"ScoringRule {VALUE} v1 not found; run import_initial_data first")
        mapping = rule.config['mapping']

        rows = self.read_rows()
        matched, skipped = [], []
        for row in rows:
            entry = COMPANY_MAP.get(row['company'])
            if not entry:
                skipped.append(row['company'])
                continue
            slug, company_uri = entry
            company = Company.objects.filter(uri=company_uri).first()
            if not company:
                skipped.append(f"{row['company']} (company {company_uri} not in database)")
                continue
            matched.append((row, slug, company))

        if len(matched) != len(COMPANY_MAP):
            found = {r['company'] for r, _, _ in matched}
            missing = sorted(set(COMPANY_MAP) - found)
            self.stdout.write(self.style.WARNING(f"Mapped but not imported: {missing}"))
        if limit:
            matched = matched[:limit]

        self.stdout.write(f"{len(rows)} companies in the report, {len(matched)} to import, "
                          f"{len(skipped)} not on Alonovo (skipped)")

        claims = snaps = 0
        with transaction.atomic():
            for row, slug, company in matched:
                tier = row['tier_2025']
                grade = mapping.get(tier, {}).get('grade', '?')
                previous = self.current_snapshot_text(company)
                self.stdout.write(f"  {company.name}: Tier {tier} -> {grade}  (was: {previous})")
                if dry_run:
                    continue
                if self.create_claim(slug, company, row):
                    claims += 1
                self.update_snapshot_and_badge(company, mapping)
                snaps += 1
            if dry_run:
                self.stdout.write(self.style.WARNING("Dry run: nothing saved"))
                return

        self.stdout.write(self.style.SUCCESS(f"Done! {claims} new claims, {snaps} snapshots updated"))

    def read_rows(self):
        path = os.path.abspath(DATA_FILE)
        if not os.path.exists(path):
            raise CommandError(f"Data file not found: {path}")
        with open(path, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        bad = [r for r in rows if r['tier_2025'] not in {'1', '2', '3', '4', '5', '6'}]
        if bad:
            raise CommandError(f"Rows with an invalid tier: {bad[:5]}")
        return rows

    def current_snapshot_text(self, company):
        snap = CompanyValueSnapshot.objects.filter(company=company, value_id=VALUE).first()
        return f"{snap.display_text} = {snap.grade}" if snap else "not graded"

    def create_claim(self, slug, company, row):
        uri = f'urn:bbfaw:2025:{slug}:tier'
        if Claim.objects.filter(uri=uri).exists():
            return None
        return Claim.objects.create(
            uri=uri,
            subject=company.uri,
            claim_type='FARM_WELFARE_TIER',
            label=row['tier_2025'],
            statement=f"BBFAW 2025 Benchmark: {row['company']} is in Tier {row['tier_2025']} "
                      f"(Impact Rating {row['impact_rating']})",
            effective_date=EFFECTIVE_DATE,
            source_uri=SOURCE_URI,
            how_known='official_report',
            author='Business Benchmark on Farm Animal Welfare',
        )

    def update_snapshot_and_badge(self, company, mapping):
        # Claim has no default ordering, so pick the newest benchmark explicitly.
        claim = (Claim.objects.filter(subject=company.uri, claim_type='FARM_WELFARE_TIER')
                 .order_by('-effective_date', '-created_at').first())
        grade = mapping.get(claim.label, {'grade': 'F', 'score': -1.0})
        year = claim.uri.split(':')[2]  # report year from urn:bbfaw:YEAR:slug:tier
        text = f"BBFAW Tier {claim.label} ({year})"
        snap, _ = CompanyValueSnapshot.objects.update_or_create(
            company=company,
            value_id=VALUE,
            defaults={
                'score': grade['score'],
                'grade': grade['grade'],
                'claim_uris': [claim.uri],
                'highlight_on_card': True,
                'highlight_priority': 1,
                'display_text': text,
                'display_icon': 'cow',
                'scoring_rule_version': 1,
            }
        )
        badge_type = 'positive' if snap.score > 0.3 else ('negative' if snap.score < -0.3 else 'neutral')
        # Older badges were keyed by label ("BBFAW Tier 5"), so replace rather than update.
        CompanyBadge.objects.filter(company=company, value_id=VALUE).delete()
        CompanyBadge.objects.create(
            company=company,
            value_id=VALUE,
            label=text,
            badge_type=badge_type,
            source_claim_uri=claim.uri,
            priority=snap.highlight_priority,
        )
