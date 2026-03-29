"""Import CEO-to-worker pay ratio data.

Data source: AFL-CIO Executive Paywatch / SEC proxy filings
https://aflcio.org/paywatch
CEO-to-median-worker pay ratios from SEC-mandated disclosures.
Required since 2018 in proxy statements (DEF 14A).
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import CEO-to-worker pay ratio data from SEC proxy filings"

    def handle(self, *args, **options):
        self.stdout.write("Creating Executive Pay Ratio Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing pay ratio data...")
        count = self.import_data()

        self.stdout.write("Computing snapshots...")
        snap_count = self.compute_snapshots()

        self.stdout.write("Creating badges...")
        badge_count = self.create_badges()

        self.stdout.write(self.style.SUCCESS(
            f"Done! {count} claims, {snap_count} snapshots, {badge_count} badges"
        ))

    def get_or_create_company(self, slug, name, ticker, sector):
        if ticker:
            existing = Company.objects.filter(ticker=ticker).first()
            if existing:
                if sector and not existing.sector:
                    existing.sector = sector
                    existing.save()
                return existing
        uri = f'urn:company:{slug}'
        company, _ = Company.objects.update_or_create(
            uri=uri,
            defaults={'name': name, 'ticker': ticker, 'sector': sector}
        )
        return company

    def create_claim_safe(self, **kwargs):
        if Claim.objects.filter(uri=kwargs['uri']).exists():
            return None
        return Claim.objects.create(**kwargs)

    def create_value(self):
        Value.objects.update_or_create(
            slug='exec_pay_ratio',
            defaults={
                'name': 'CEO Pay Ratio',
                'description': 'CEO-to-median-worker compensation ratio from SEC proxy filings. Lower ratio = more equitable.',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'CEO pay: {amt}:1',
                'card_icon': 'dollar-sign',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='exec_pay_ratio',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold_inverse',
                    'note': 'CEO pay ratio — lower is more equitable. S&P 500 average is ~270:1.',
                    'thresholds': [
                        {'min': 1000, 'grade': 'F', 'score': -1.0},
                        {'min': 500, 'grade': 'D', 'score': -0.5},
                        {'min': 200, 'grade': 'C', 'score': 0.0},
                        {'min': 50, 'grade': 'B', 'score': 0.5},
                        {'min': 0, 'grade': 'A', 'score': 1.0},
                    ]
                }
            }
        )

    def import_data(self):
        """Import CEO pay ratio data.

        Source: SEC DEF 14A proxy filings, aggregated by AFL-CIO Executive Paywatch
        https://aflcio.org/paywatch

        Pay ratios are CEO total compensation / median worker compensation.
        Required disclosure since 2018. Data below is from 2023-2024 proxy filings.
        """
        # (slug, name, ticker, sector, pay_ratio)
        # Data from 2023-2024 SEC proxy filings / AFL-CIO Paywatch
        pay_data = [
            # Highest ratios (>1000:1)
            ('expedia', 'Expedia', 'EXPE', 'Technology', 2897),
            ('aptiv', 'Aptiv', 'APTV', 'Automotive', 5294),
            ('nike', 'Nike', 'NKE', 'Apparel', 968),
            ('starbucks', 'Starbucks', 'SBUX', 'Restaurants', 1579),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', 1213),
            ('chipotle', 'Chipotle', 'CMG', 'Restaurants', 2898),
            ('walmart', 'Walmart', 'WMT', 'Retail', 933),
            ('amazon', 'Amazon', 'AMZN', 'Retail', 105),
            ('coca-cola', 'Coca-Cola', 'KO', 'Beverages', 1594),
            ('pepsico', 'PepsiCo', 'PEP', 'Beverages', 526),

            # High ratios (200-1000:1)
            ('apple', 'Apple', 'AAPL', 'Technology', 672),
            ('jpmorgan', 'JPMorgan Chase', 'JPM', 'Banking', 386),
            ('disney', 'Disney', 'DIS', 'Entertainment', 628),
            ('comcast', 'Comcast', 'CMCSA', 'Telecommunications', 413),
            ('procter-gamble', 'Procter & Gamble', 'PG', 'Consumer Goods', 355),
            ('johnson-johnson', 'Johnson & Johnson', 'JNJ', 'Healthcare', 283),
            ('target', 'Target', 'TGT', 'Retail', 692),
            ('costco', 'Costco', 'COST', 'Retail', 310),
            ('home-depot', 'Home Depot', 'HD', 'Retail', 486),
            ('lowes', "Lowe's", 'LOW', 'Retail', 628),
            ('honeywell', 'Honeywell', 'HON', 'Industrials', 299),
            ('3m', '3M', 'MMM', 'Industrials', 218),
            ('general-motors', 'General Motors', 'GM', 'Automotive', 312),
            ('ford', 'Ford Motor', 'F', 'Automotive', 310),

            # Moderate ratios (50-200:1)
            ('alphabet', 'Alphabet', 'GOOGL', 'Technology', 67),
            ('microsoft', 'Microsoft', 'MSFT', 'Technology', 289),
            ('meta', 'Meta Platforms', 'META', 'Technology', 120),
            ('intel', 'Intel', 'INTC', 'Technology', 184),
            ('salesforce', 'Salesforce', 'CRM', 'Technology', 185),
            ('cisco', 'Cisco', 'CSCO', 'Technology', 167),

            # Lower ratios (<50:1)
            ('nvidia', 'NVIDIA', 'NVDA', 'Technology', 42),
            ('berkshire', 'Berkshire Hathaway', 'BRK.B', 'Conglomerate', 5),
        ]

        count = 0
        for slug, name, ticker, sector, ratio in pay_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            claim = self.create_claim_safe(
                uri=f'urn:sec-proxy:2024:{slug}:pay-ratio',
                subject=company.uri,
                claim_type='CEO_PAY_RATIO',
                amt=Decimal(str(ratio)),
                unit='ratio_to_1',
                effective_date='2024-04-01',
                source_uri='https://aflcio.org/paywatch',
                how_known='sec_filing',
                author='SEC DEF 14A / AFL-CIO Paywatch',
                statement=f'CEO-to-median-worker pay ratio: {ratio:,}:1',
            )
            if claim:
                count += 1
                self.stdout.write(f"  Pay ratio: {name} ({ticker}) = {ratio:,}:1")

        return count

    def _apply_threshold_inverse(self, thresholds, value):
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='exec_pay_ratio', version=1)
        count = 0

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='CEO_PAY_RATIO').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(
                subject=company.uri, claim_type='CEO_PAY_RATIO'
            ).first()
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
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade} ({int(ratio):,}:1)")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='exec_pay_ratio'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='exec_pay_ratio',
                defaults={
                    'label': snapshot.display_text,
                    'badge_type': badge_type,
                    'source_claim_uri': snapshot.claim_uris[0] if snapshot.claim_uris else '',
                    'priority': snapshot.highlight_priority,
                }
            )
            if created:
                count += 1
        return count
