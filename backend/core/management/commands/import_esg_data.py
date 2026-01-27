import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import ESG scores from multiple sources"

    def handle(self, *args, **options):
        self.stdout.write("Creating ESG Value...")
        self.create_value()

        self.stdout.write("Creating ESG ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing GitHub CSV ESG data...")
        csv_count = self.import_github_csv()

        self.stdout.write("Importing S&P Global ESG data...")
        sp_count = self.import_spglobal_data()

        self.stdout.write("Computing ESG snapshots...")
        snap_count = self.compute_esg_snapshots()

        self.stdout.write("Creating badges...")
        badge_count = self.create_badges()

        self.stdout.write(self.style.SUCCESS(
            f"Done! CSV: {csv_count} claims, S&P: {sp_count} claims, "
            f"{snap_count} snapshots, {badge_count} badges"
        ))

    def get_or_create_company(self, slug, name, ticker, sector):
        if ticker:
            existing = Company.objects.filter(ticker=ticker).first()
            if existing:
                # Update sector if we have one and they don't
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
            slug='esg_score',
            defaults={
                'name': 'ESG Score',
                'description': 'Environmental, Social, and Governance score from multiple rating agencies',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'ESG: {amt}',
                'card_icon': 'leaf',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='esg_score',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold_inverse',
                    'thresholds': [
                        {'max': 10, 'grade': 'A', 'score': 1.0},
                        {'max': 20, 'grade': 'B', 'score': 0.6},
                        {'max': 30, 'grade': 'C', 'score': 0.0},
                        {'max': 40, 'grade': 'D', 'score': -0.5},
                        {'max': 100, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

    def import_github_csv(self):
        csv_path = '/home/ec2-user/alonovo2/data/sp_esg_stock_data.csv'
        count = 0
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get('ticker', '').strip()
                total_esg = row.get('esgScore.tot', '').strip()
                company_name = row.get('company', '').strip()
                sector = row.get('sector', '').strip()

                if not ticker or not total_esg:
                    continue

                try:
                    esg_value = Decimal(str(total_esg))
                except Exception:
                    continue

                slug = ticker.lower().replace('-', '_')
                company = self.get_or_create_company(slug, company_name or ticker, ticker, sector or None)

                claim = self.create_claim_safe(
                    uri=f'urn:yahoo-sustainalytics:2021:{slug}:esg',
                    subject=company.uri,
                    claim_type='ESG_SCORE',
                    amt=esg_value,
                    unit='sustainalytics_risk',
                    effective_date='2021-03-01',
                    source_uri='https://github.com/sburstein/ESG-Stock-Data',
                    how_known='scraped_yahoo_finance',
                )
                if claim:
                    count += 1
                    self.stdout.write(f"  CSV: {company_name} ({ticker}) ESG={esg_value}")

        return count

    def import_spglobal_data(self):
        spglobal_data = [
            ('AAPL', 'Apple', 'Technology', 31),
            ('MSFT', 'Microsoft', 'Technology', 35),
            ('GOOGL', 'Alphabet', 'Technology', 29),
            ('AMZN', 'Amazon', 'Retail', 22),
            ('META', 'Meta Platforms', 'Technology', 26),
            ('TSLA', 'Tesla', 'Automotive', 37),
            ('JPM', 'JPMorgan Chase', 'Banking', 51),
            ('V', 'Visa', 'Financial Services', 42),
            ('JNJ', 'Johnson & Johnson', 'Healthcare', 55),
            ('WMT', 'Walmart', 'Retail', 48),
            ('PG', 'Procter & Gamble', 'Consumer Goods', 56),
            ('XOM', 'Exxon Mobil', 'Oil & Gas', 41),
            ('CVX', 'Chevron', 'Oil & Gas', 43),
            ('KO', 'Coca-Cola', 'Beverages', 52),
            ('PEP', 'PepsiCo', 'Beverages', 58),
            ('MCD', "McDonald's", 'Restaurants', 34),
            ('NKE', 'Nike', 'Apparel', 45),
            ('DIS', 'Disney', 'Entertainment', 39),
            ('NFLX', 'Netflix', 'Entertainment', 28),
            ('COST', 'Costco', 'Retail', 44),
        ]

        count = 0
        for ticker, name, sector, sp_score in spglobal_data:
            slug = ticker.lower()
            company = self.get_or_create_company(slug, name, ticker, sector)

            claim = self.create_claim_safe(
                uri=f'urn:spglobal:2025:{slug}:esg',
                subject=company.uri,
                claim_type='ESG_SCORE',
                amt=Decimal(str(sp_score)),
                unit='spglobal_score',
                effective_date='2025-01-01',
                source_uri='https://www.spglobal.com/esg/scores/',
                how_known='official_rating',
            )
            if claim:
                count += 1
                self.stdout.write(f"  S&P Global: {name} ({ticker}) score={sp_score}")

        return count

    def compute_esg_snapshots(self):
        rule = ScoringRule.objects.get(value_id='esg_score', version=1)
        count = 0

        companies_with_esg = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='ESG_SCORE').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_esg:
            esg_claims = Claim.objects.filter(subject=company.uri, claim_type='ESG_SCORE')
            if not esg_claims.exists():
                continue

            normalized_scores = []
            claim_uris = []

            for claim in esg_claims:
                claim_uris.append(claim.uri)
                if claim.unit == 'spglobal_score':
                    # S&P: 0-100, higher = better -> invert to sustainalytics-like scale
                    normalized = (100 - float(claim.amt)) / 2
                else:
                    # Sustainalytics-style: lower = better, already on 0-50 scale
                    normalized = float(claim.amt)
                normalized_scores.append(normalized)

            avg_score = sum(normalized_scores) / len(normalized_scores)

            grade = 'F'
            score = -1.0
            for threshold in rule.config['thresholds']:
                if avg_score <= threshold['max']:
                    grade = threshold['grade']
                    score = threshold['score']
                    break

            display_text = f"ESG Risk: {avg_score:.1f}"
            if len(claim_uris) > 1:
                display_text += f" ({len(claim_uris)} sources)"

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='esg_score',
                defaults={
                    'score': score,
                    'grade': grade,
                    'claim_uris': claim_uris,
                    'highlight_on_card': True,
                    'highlight_priority': 3,
                    'display_text': display_text,
                    'display_icon': 'leaf',
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade} (risk: {avg_score:.1f})")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='esg_score'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='esg_score',
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
