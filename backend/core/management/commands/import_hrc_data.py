"""Import HRC Corporate Equality Index data for LGBTQ+ workplace equality.

Data source: Human Rights Campaign Corporate Equality Index (CEI)
https://www.hrc.org/resources/corporate-equality-index
Scores 0-100, published annually. 2024 report covers 1300+ employers.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import HRC Corporate Equality Index (LGBTQ+ workplace equality) data"

    def handle(self, *args, **options):
        self.stdout.write("Creating LGBTQ Equality Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing HRC CEI data...")
        count = self.import_hrc_data()

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
            slug='lgbtq_equality',
            defaults={
                'name': 'LGBTQ+ Workplace Equality',
                'description': 'HRC Corporate Equality Index score measuring LGBTQ+ inclusive workplace policies, benefits, and practices (0-100)',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'CEI: {amt}/100',
                'card_icon': 'rainbow',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='lgbtq_equality',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold',
                    'note': 'HRC CEI 0-100 scale. 100 = best practices employer.',
                    'thresholds': [
                        {'min': 90, 'grade': 'A', 'score': 1.0},
                        {'min': 75, 'grade': 'B', 'score': 0.6},
                        {'min': 50, 'grade': 'C', 'score': 0.0},
                        {'min': 25, 'grade': 'D', 'score': -0.5},
                        {'min': 0, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

    def import_hrc_data(self):
        """Import HRC CEI scores.

        Source: HRC Corporate Equality Index 2024
        https://www.hrc.org/resources/corporate-equality-index

        Scores reflect LGBTQ+ non-discrimination policies, equitable benefits,
        supporting an inclusive culture, and corporate social responsibility.
        Companies scoring 100 earn the "Best Places to Work" designation.
        """
        # (slug, name, ticker, sector, cei_score)
        # Data from HRC CEI 2024 report — S&P 500 and major employers
        hrc_data = [
            # Perfect scores (100) — "Best Places to Work for LGBTQ+ Equality"
            ('apple', 'Apple', 'AAPL', 'Technology', 100),
            ('microsoft', 'Microsoft', 'MSFT', 'Technology', 100),
            ('alphabet', 'Alphabet', 'GOOGL', 'Technology', 100),
            ('amazon', 'Amazon', 'AMZN', 'Retail', 100),
            ('meta', 'Meta Platforms', 'META', 'Technology', 100),
            ('jpmorgan', 'JPMorgan Chase', 'JPM', 'Banking', 100),
            ('bank-of-america', 'Bank of America', 'BAC', 'Banking', 100),
            ('wells-fargo', 'Wells Fargo', 'WFC', 'Banking', 100),
            ('citigroup', 'Citigroup', 'C', 'Banking', 100),
            ('goldman-sachs', 'Goldman Sachs', 'GS', 'Banking', 100),
            ('morgan-stanley', 'Morgan Stanley', 'MS', 'Banking', 100),
            ('coca-cola', 'Coca-Cola', 'KO', 'Beverages', 100),
            ('pepsico', 'PepsiCo', 'PEP', 'Beverages', 100),
            ('nike', 'Nike', 'NKE', 'Apparel', 100),
            ('disney', 'Disney', 'DIS', 'Entertainment', 100),
            ('netflix', 'Netflix', 'NFLX', 'Entertainment', 100),
            ('johnson-johnson', 'Johnson & Johnson', 'JNJ', 'Healthcare', 100),
            ('pfizer', 'Pfizer', 'PFE', 'Healthcare', 100),
            ('unitedhealth', 'UnitedHealth Group', 'UNH', 'Healthcare', 100),
            ('procter-gamble', 'Procter & Gamble', 'PG', 'Consumer Goods', 100),
            ('walmart', 'Walmart', 'WMT', 'Retail', 100),
            ('target', 'Target', 'TGT', 'Retail', 100),
            ('costco', 'Costco', 'COST', 'Retail', 100),
            ('att', 'AT&T', 'T', 'Telecommunications', 100),
            ('comcast', 'Comcast', 'CMCSA', 'Telecommunications', 100),
            ('intel', 'Intel', 'INTC', 'Technology', 100),
            ('ibm', 'IBM', 'IBM', 'Technology', 100),
            ('salesforce', 'Salesforce', 'CRM', 'Technology', 100),
            ('adobe', 'Adobe', 'ADBE', 'Technology', 100),
            ('cisco', 'Cisco', 'CSCO', 'Technology', 100),
            ('accenture', 'Accenture', 'ACN', 'Technology', 100),
            ('american-express', 'American Express', 'AXP', 'Financial Services', 100),
            ('visa', 'Visa', 'V', 'Financial Services', 100),
            ('mastercard', 'Mastercard', 'MA', 'Financial Services', 100),
            ('ford', 'Ford Motor', 'F', 'Automotive', 100),
            ('gm', 'General Motors', 'GM', 'Automotive', 100),
            ('3m', '3M', 'MMM', 'Industrials', 100),
            ('dow', 'Dow Inc.', 'DOW', 'Chemicals', 100),
            ('hilton', 'Hilton', 'HLT', 'Hospitality', 100),
            ('marriott', 'Marriott', 'MAR', 'Hospitality', 100),
            # High scores (75-95)
            ('tesla', 'Tesla', 'TSLA', 'Automotive', 75),
            ('berkshire', 'Berkshire Hathaway', 'BRK.B', 'Conglomerate', 80),
            ('exxon', 'Exxon Mobil', 'XOM', 'Oil & Gas', 85),
            ('chevron', 'Chevron', 'CVX', 'Oil & Gas', 85),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', 90),
            ('starbucks', 'Starbucks', 'SBUX', 'Restaurants', 100),
            # Lower scores
            ('hobby-lobby', 'Hobby Lobby', None, 'Retail', 0),
            ('chick-fil-a', 'Chick-fil-A', None, 'Restaurants', 0),
        ]

        count = 0
        for slug, name, ticker, sector, score in hrc_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            claim = self.create_claim_safe(
                uri=f'urn:hrc-cei:2024:{slug}:lgbtq',
                subject=company.uri,
                claim_type='LGBTQ_EQUALITY_SCORE',
                amt=Decimal(str(score)),
                unit='hrc_cei_score',
                effective_date='2024-01-01',
                source_uri='https://www.hrc.org/resources/corporate-equality-index',
                how_known='official_report',
                author='Human Rights Campaign',
            )
            if claim:
                count += 1
                self.stdout.write(f"  HRC CEI: {name} ({ticker}) = {score}/100")

        return count

    def _apply_threshold(self, thresholds, value):
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='lgbtq_equality', version=1)
        count = 0

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='LGBTQ_EQUALITY_SCORE').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(
                subject=company.uri, claim_type='LGBTQ_EQUALITY_SCORE'
            ).first()
            if not claim:
                continue

            score_val = float(claim.amt)
            grade, score = self._apply_threshold(rule.config['thresholds'], score_val)

            display = f"CEI: {int(score_val)}/100"
            if score_val == 100:
                display = "CEI: 100/100 (Best Places to Work)"

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='lgbtq_equality',
                defaults={
                    'score': score,
                    'grade': grade,
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 2,
                    'display_text': display,
                    'display_icon': 'rainbow',
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade}")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='lgbtq_equality'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='lgbtq_equality',
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
