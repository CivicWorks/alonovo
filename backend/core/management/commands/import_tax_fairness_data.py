"""Import corporate tax fairness data.

Data source: ITEP (Institute on Taxation and Economic Policy)
https://itep.org/corporate-tax-tracker/
Effective tax rates vs. 21% statutory rate. Companies paying less than
their share score worse. Based on SEC 10-K filings and ITEP analysis.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import ITEP corporate tax fairness data"

    def handle(self, *args, **options):
        self.stdout.write("Creating Tax Fairness Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing ITEP data...")
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
            slug='tax_fairness',
            defaults={
                'name': 'Corporate Tax Fairness',
                'description': 'Effective corporate tax rate vs. 21% statutory rate. Based on ITEP analysis of SEC filings.',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'Eff. tax: {amt}%',
                'card_icon': 'landmark',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='tax_fairness',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold',
                    'note': 'Effective tax rate. US statutory rate is 21%. Higher = paying fair share.',
                    'thresholds': [
                        {'min': 18, 'grade': 'A', 'score': 1.0},
                        {'min': 12, 'grade': 'B', 'score': 0.5},
                        {'min': 5, 'grade': 'C', 'score': 0.0},
                        {'min': 0, 'grade': 'D', 'score': -0.5},
                        {'min': -100, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

    def import_data(self):
        """Import effective tax rate data.

        Source: ITEP Corporate Tax Tracker + SEC 10-K filings
        https://itep.org/corporate-tax-tracker/

        Effective tax rates are calculated as federal income taxes paid as a
        percentage of pretax US profits over 2018-2022 (post-TCJA).
        Negative rates mean the company received net tax rebates.
        """
        # (slug, name, ticker, sector, effective_tax_rate_pct)
        # Data from ITEP Corporate Tax Tracker (2018-2022 average effective rates)
        tax_data = [
            # Paying close to or above statutory rate
            ('jpmorgan', 'JPMorgan Chase', 'JPM', 'Banking', 18.5),
            ('bank-of-america', 'Bank of America', 'BAC', 'Banking', 14.6),
            ('wells-fargo', 'Wells Fargo', 'WFC', 'Banking', 11.2),
            ('walmart', 'Walmart', 'WMT', 'Retail', 22.6),
            ('target', 'Target', 'TGT', 'Retail', 21.3),
            ('home-depot', 'Home Depot', 'HD', 'Retail', 22.8),
            ('costco', 'Costco', 'COST', 'Retail', 23.1),
            ('procter-gamble', 'Procter & Gamble', 'PG', 'Consumer Goods', 19.8),
            ('coca-cola', 'Coca-Cola', 'KO', 'Beverages', 17.9),
            ('pepsico', 'PepsiCo', 'PEP', 'Beverages', 20.1),
            ('johnson-johnson', 'Johnson & Johnson', 'JNJ', 'Healthcare', 12.4),

            # Moderate avoidance
            ('apple', 'Apple', 'AAPL', 'Technology', 14.4),
            ('microsoft', 'Microsoft', 'MSFT', 'Technology', 16.5),
            ('alphabet', 'Alphabet', 'GOOGL', 'Technology', 15.7),
            ('meta', 'Meta Platforms', 'META', 'Technology', 14.1),
            ('intel', 'Intel', 'INTC', 'Technology', 5.3),
            ('disney', 'Disney', 'DIS', 'Entertainment', 0.6),
            ('ford', 'Ford Motor', 'F', 'Automotive', 1.5),
            ('general-motors', 'General Motors', 'GM', 'Automotive', 0.2),

            # Significant avoidance — low or negative effective rate
            ('amazon', 'Amazon', 'AMZN', 'Retail', 5.1),
            ('nike', 'Nike', 'NKE', 'Apparel', 13.8),
            ('netflix', 'Netflix', 'NFLX', 'Entertainment', -0.4),
            ('salesforce', 'Salesforce', 'CRM', 'Technology', 0.7),
            ('tesla', 'Tesla', 'TSLA', 'Automotive', -1.0),
            ('exxon', 'Exxon Mobil', 'XOM', 'Oil & Gas', 2.0),
            ('chevron', 'Chevron', 'CVX', 'Oil & Gas', 5.8),

            # Duke Energy, FedEx, others noted by ITEP as paying $0 or less
            ('duke-energy', 'Duke Energy', 'DUK', 'Utilities', -0.1),
            ('fedex', 'FedEx', 'FDX', 'Logistics', -3.7),
            ('dish-network', 'DISH Network', 'DISH', 'Telecommunications', -4.0),
        ]

        count = 0
        for slug, name, ticker, sector, rate in tax_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            claim = self.create_claim_safe(
                uri=f'urn:itep:2023:{slug}:tax-rate',
                subject=company.uri,
                claim_type='EFFECTIVE_TAX_RATE',
                amt=Decimal(str(rate)),
                unit='percent',
                effective_date='2023-01-01',
                source_uri='https://itep.org/corporate-tax-tracker/',
                how_known='public_analysis',
                author='ITEP',
                statement=f'Avg. effective federal tax rate (2018-2022): {rate}% vs. 21% statutory',
            )
            if claim:
                count += 1
                self.stdout.write(f"  ITEP: {name} ({ticker}) = {rate}% effective rate")

        return count

    def _apply_threshold(self, thresholds, value):
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='tax_fairness', version=1)
        count = 0

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='EFFECTIVE_TAX_RATE').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(
                subject=company.uri, claim_type='EFFECTIVE_TAX_RATE'
            ).first()
            if not claim:
                continue

            rate = float(claim.amt)
            grade, score = self._apply_threshold(rule.config['thresholds'], rate)

            if rate < 0:
                display = f"Tax rate: {rate:.1f}% (net rebate)"
            else:
                display = f"Tax rate: {rate:.1f}% (vs. 21% statutory)"

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='tax_fairness',
                defaults={
                    'score': score,
                    'grade': grade,
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 2,
                    'display_text': display,
                    'display_icon': 'landmark',
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade} ({rate:.1f}%)")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='tax_fairness'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='tax_fairness',
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
