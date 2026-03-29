"""Import KnowTheChain forced labor / supply chain benchmark data.

Data source: KnowTheChain Benchmarks
https://knowthechain.org/benchmark/
Scores 0-100, published every 2 years. Covers food/beverage, ICT, apparel sectors.
2023 benchmarks cover ~60 companies per sector.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import KnowTheChain supply chain / forced labor benchmark data"

    def handle(self, *args, **options):
        self.stdout.write("Creating Supply Chain / Forced Labor Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing KnowTheChain data...")
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
            slug='forced_labor',
            defaults={
                'name': 'Supply Chain Labor Rights',
                'description': 'KnowTheChain benchmark measuring company efforts to address forced labor risks in supply chains (0-100)',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'Labor: {amt}/100',
                'card_icon': 'users',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='forced_labor',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold',
                    'note': 'KnowTheChain 0-100 scale. Most companies score below 50. Average is ~25.',
                    'thresholds': [
                        {'min': 60, 'grade': 'A', 'score': 1.0},
                        {'min': 40, 'grade': 'B', 'score': 0.5},
                        {'min': 25, 'grade': 'C', 'score': 0.0},
                        {'min': 10, 'grade': 'D', 'score': -0.5},
                        {'min': 0, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

    def import_data(self):
        """Import KnowTheChain benchmark scores.

        Source: KnowTheChain 2023 Benchmarks
        https://knowthechain.org/benchmark/

        Covers three sectors: Food & Beverage, ICT, Apparel & Footwear.
        Scores evaluate: commitment & governance, traceability & risk assessment,
        purchasing practices, recruitment, worker voice, monitoring, and remedy.
        """
        # (slug, name, ticker, sector, score, benchmark_sector)
        # Scores from KnowTheChain 2022-2023 benchmarks
        ktc_data = [
            # Food & Beverage Benchmark 2023
            ('nestle', 'Nestlé', 'NESN.SW', 'Food Manufacturing', 51, 'food_bev'),
            ('unilever', 'Unilever', 'UL', 'Consumer Goods', 60, 'food_bev'),
            ('coca-cola', 'Coca-Cola', 'KO', 'Beverages', 46, 'food_bev'),
            ('pepsico', 'PepsiCo', 'PEP', 'Beverages', 42, 'food_bev'),
            ('mars', 'Mars', None, 'Food Manufacturing', 39, 'food_bev'),
            ('mondelez', 'Mondelez', 'MDLZ', 'Food Manufacturing', 34, 'food_bev'),
            ('kraft-heinz', 'Kraft Heinz', 'KHC', 'Food Manufacturing', 14, 'food_bev'),
            ('tyson-foods', 'Tyson Foods', 'TSN', 'Food Manufacturing', 10, 'food_bev'),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', 20, 'food_bev'),
            ('starbucks', 'Starbucks', 'SBUX', 'Restaurants', 27, 'food_bev'),
            ('walmart', 'Walmart', 'WMT', 'Retail', 37, 'food_bev'),
            ('costco', 'Costco', 'COST', 'Retail', 19, 'food_bev'),
            ('kroger', 'Kroger', 'KR', 'Retail', 11, 'food_bev'),
            ('general-mills', 'General Mills', 'GIS', 'Food Manufacturing', 26, 'food_bev'),
            ('kelloggs', "Kellogg's", 'K', 'Food Manufacturing', 31, 'food_bev'),

            # ICT Benchmark 2022
            ('apple', 'Apple', 'AAPL', 'Technology', 51, 'ict'),
            ('hp', 'HP Inc.', 'HPQ', 'Technology', 57, 'ict'),
            ('intel', 'Intel', 'INTC', 'Technology', 41, 'ict'),
            ('microsoft', 'Microsoft', 'MSFT', 'Technology', 38, 'ict'),
            ('samsung', 'Samsung', '005930.KS', 'Technology', 29, 'ict'),
            ('dell', 'Dell', 'DELL', 'Technology', 28, 'ict'),
            ('amazon', 'Amazon', 'AMZN', 'Retail', 18, 'ict'),
            ('alphabet', 'Alphabet', 'GOOGL', 'Technology', 15, 'ict'),
            ('meta', 'Meta Platforms', 'META', 'Technology', 10, 'ict'),
            ('tesla', 'Tesla', 'TSLA', 'Automotive', 7, 'ict'),

            # Apparel & Footwear Benchmark 2023
            ('adidas', 'Adidas', 'ADS.DE', 'Apparel', 65, 'apparel'),
            ('nike', 'Nike', 'NKE', 'Apparel', 45, 'apparel'),
            ('gap', 'Gap Inc.', 'GAP', 'Apparel', 44, 'apparel'),
            ('vf-corp', 'VF Corporation', 'VFC', 'Apparel', 42, 'apparel'),
            ('ralph-lauren', 'Ralph Lauren', 'RL', 'Apparel', 33, 'apparel'),
            ('pvh', 'PVH Corp.', 'PVH', 'Apparel', 50, 'apparel'),
        ]

        count = 0
        for slug, name, ticker, sector, score, bench_sector in ktc_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            claim = self.create_claim_safe(
                uri=f'urn:knowthechain:2023:{slug}:forced-labor',
                subject=company.uri,
                claim_type='FORCED_LABOR_SCORE',
                amt=Decimal(str(score)),
                unit='ktc_benchmark_score',
                effective_date='2023-06-01',
                source_uri='https://knowthechain.org/benchmark/',
                how_known='official_benchmark',
                author='KnowTheChain',
                statement=f'KnowTheChain {bench_sector} benchmark score: {score}/100',
            )
            if claim:
                count += 1
                self.stdout.write(f"  KnowTheChain: {name} ({ticker}) = {score}/100 [{bench_sector}]")

        return count

    def _apply_threshold(self, thresholds, value):
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='forced_labor', version=1)
        count = 0

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='FORCED_LABOR_SCORE').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(
                subject=company.uri, claim_type='FORCED_LABOR_SCORE'
            ).first()
            if not claim:
                continue

            score_val = float(claim.amt)
            grade, score = self._apply_threshold(rule.config['thresholds'], score_val)

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='forced_labor',
                defaults={
                    'score': score,
                    'grade': grade,
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 2,
                    'display_text': f"Supply chain labor: {int(score_val)}/100",
                    'display_icon': 'users',
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade} ({int(score_val)}/100)")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='forced_labor'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='forced_labor',
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
