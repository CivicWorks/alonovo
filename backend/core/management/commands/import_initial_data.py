from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import values, scoring rules, and new company/claim data"

    def handle(self, *args, **options):
        self.stdout.write("Creating Values...")
        self.create_values()

        self.stdout.write("Creating ScoringRules...")
        self.create_scoring_rules()

        self.stdout.write("Importing companies and claims...")
        self.import_companies_and_claims()

        self.stdout.write("Computing snapshots...")
        self.compute_snapshots()

        self.stdout.write("Creating badges...")
        self.create_badges()

        self.stdout.write(self.style.SUCCESS("Done!"))

    def get_or_create_company(self, slug, name, ticker, sector):
        """Find existing company by ticker or create new one."""
        if ticker:
            existing = Company.objects.filter(ticker=ticker).first()
            if existing:
                return existing
        uri = f'urn:company:{slug}'
        company, _ = Company.objects.update_or_create(
            uri=uri,
            defaults={'name': name, 'ticker': ticker, 'sector': sector}
        )
        return company

    def create_claim_safe(self, **kwargs):
        """Create a claim if it doesn't already exist."""
        if Claim.objects.filter(uri=kwargs['uri']).exists():
            return Claim.objects.get(uri=kwargs['uri'])
        return Claim.objects.create(**kwargs)

    def create_values(self):
        values_data = [
            {
                'slug': 'corporate_lobbying',
                'name': 'Corporate Lobbying',
                'description': 'Total lobbying expenditure reported to Congress',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'Lobbying: ${amt}',
                'card_icon': 'megaphone',
            },
            {
                'slug': 'cage_free_eggs',
                'name': 'Cage-Free Egg Commitment',
                'description': 'Progress toward 100% cage-free egg sourcing',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': '{amt}% cage-free',
                'card_icon': 'egg',
            },
            {
                'slug': 'farm_animal_welfare',
                'name': 'Farm Animal Welfare Rating',
                'description': 'BBFAW tier rating (1-6, lower is better)',
                'value_type': 'categorical_grade',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'BBFAW Tier {label}',
                'card_icon': 'cow',
            },
            {
                'slug': 'ice_contracts',
                'name': 'ICE/CBP Contracts',
                'description': 'Active contracts with Immigration and Customs Enforcement or Customs and Border Protection',
                'value_type': 'metric',
                'is_fixed': True,
                'is_disqualifying': False,
                'min_weight': 1,
                'card_display_template': 'ICE contracts: ${amt}M',
                'card_icon': 'warning',
            },
            {
                'slug': 'ice_detention',
                'name': 'ICE Detention Operations',
                'description': 'Operates or directly supports immigrant detention facilities',
                'value_type': 'label',
                'is_fixed': True,
                'is_disqualifying': True,
                'min_weight': 5,
                'card_display_template': 'Detention operator',
                'card_icon': 'alert',
            },
        ]

        for data in values_data:
            Value.objects.update_or_create(slug=data['slug'], defaults=data)
            self.stdout.write(f"  Value: {data['name']}")

    def create_scoring_rules(self):
        # Corporate lobbying scoring (inverse - lower spend is better)
        ScoringRule.objects.update_or_create(
            value_id='corporate_lobbying',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold_inverse',
                    'thresholds': [
                        {'min': 10000000, 'grade': 'F', 'score': -1.0},
                        {'min': 5000000, 'grade': 'D', 'score': -0.6},
                        {'min': 2000000, 'grade': 'C', 'score': -0.2},
                        {'min': 500000, 'grade': 'B', 'score': 0.4},
                        {'min': 0, 'grade': 'A', 'score': 1.0},
                    ]
                }
            }
        )

        # Cage-free scoring
        ScoringRule.objects.update_or_create(
            value_id='cage_free_eggs',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold',
                    'thresholds': [
                        {'min': 95, 'grade': 'A', 'score': 1.0},
                        {'min': 80, 'grade': 'B', 'score': 0.6},
                        {'min': 50, 'grade': 'C', 'score': 0.2},
                        {'min': 25, 'grade': 'D', 'score': -0.2},
                        {'min': 0, 'grade': 'F', 'score': -1.0},
                    ]
                }
            }
        )

        # BBFAW tier scoring
        ScoringRule.objects.update_or_create(
            value_id='farm_animal_welfare',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'categorical',
                    'mapping': {
                        '1': {'grade': 'A', 'score': 1.0},
                        '2': {'grade': 'A-', 'score': 0.85},
                        '3': {'grade': 'B', 'score': 0.6},
                        '4': {'grade': 'C', 'score': 0.2},
                        '5': {'grade': 'D', 'score': -0.4},
                        '6': {'grade': 'F', 'score': -1.0},
                    }
                }
            }
        )

        # ICE contracts scoring (any amount is bad, only zero is A)
        ScoringRule.objects.update_or_create(
            value_id='ice_contracts',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'threshold_inverse',
                    'thresholds': [
                        {'min': 50, 'grade': 'F', 'score': -1.0},
                        {'min': 10, 'grade': 'D', 'score': -0.6},
                        {'min': 1, 'grade': 'D', 'score': -0.4},
                        {'min': 0.001, 'grade': 'D', 'score': -0.3},
                        {'min': 0, 'grade': 'A', 'score': 1.0},
                    ]
                }
            }
        )

        # ICE detention scoring
        ScoringRule.objects.update_or_create(
            value_id='ice_detention',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'label',
                    'mapping': {
                        'detention_operator': {'grade': 'F', 'score': -1.0},
                        'major_contractor': {'grade': 'F', 'score': -1.0},
                        'none': {'grade': 'A', 'score': 1.0},
                    }
                }
            }
        )

    def import_companies_and_claims(self):
        # Migrate existing lobbying claims into value system
        self.migrate_lobbying_data()

        # BBFAW Data (source: https://www.bbfaw.com/media/2190/bbfaw-2024-report.pdf)
        bbfaw_data = [
            ('marks-and-spencer', 'Marks & Spencer', 'MKS.L', 'Retail', '2'),
            ('waitrose', 'Waitrose', None, 'Retail', '2'),
            ('premier-foods', 'Premier Foods', 'PFD.L', 'Food Manufacturing', '2'),
            ('greggs', 'Greggs', 'GRG.L', 'Restaurants', '2'),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', '5'),
            ('tyson-foods', 'Tyson Foods', 'TSN', 'Food Manufacturing', '5'),
            ('amazon-whole-foods', 'Amazon/Whole Foods', 'AMZN', 'Retail', '5'),
            ('dominos-pizza', "Domino's Pizza", 'DPZ', 'Restaurants', '5'),
            ('nestle', 'Nestlé', 'NESN.SW', 'Food Manufacturing', '5'),
            ('walmart', 'Walmart', 'WMT', 'Retail', '5'),
            ('tesco', 'Tesco', 'TSCO.L', 'Retail', '4'),
            ('costco', 'Costco', 'COST', 'Retail', '5'),
            ('kroger', 'Kroger', 'KR', 'Retail', '5'),
        ]

        for slug, name, ticker, sector, tier in bbfaw_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            self.create_claim_safe(
                uri=f'urn:bbfaw:2024:{slug}:tier',
                subject=company.uri,
                claim_type='FARM_WELFARE_TIER',
                label=tier,
                effective_date='2024-04-25',
                source_uri='https://www.bbfaw.com/media/2190/bbfaw-2024-report.pdf',
                how_known='official_report',
            )
            self.stdout.write(f"  BBFAW: {name} Tier {tier}")

        # EggTrack Data (source: https://www.eggtrack.com/en/)
        eggtrack_data = [
            ('danone', 'Danone', 'BN.PA', 'Food Manufacturing', 100),
            ('barilla', 'Barilla', None, 'Food Manufacturing', 100),
            ('mcdonalds', "McDonald's", 'MCD', 'Restaurants', 33),
            ('walmart', 'Walmart', 'WMT', 'Retail', 14),
            ('raleys', "Raley's", None, 'Retail', 100),
            ('sprouts', 'Sprouts Farmers Market', 'SFM', 'Retail', 100),
            ('hershey', 'The Hershey Company', 'HSY', 'Food Manufacturing', 100),
            ('kraft-heinz', 'Kraft Heinz', 'KHC', 'Food Manufacturing', 85),
            ('kfc-europe', 'KFC Europe', None, 'Restaurants', 100),
        ]

        for slug, name, ticker, sector, pct in eggtrack_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            self.create_claim_safe(
                uri=f'urn:eggtrack:2024:{slug}:cagefree',
                subject=company.uri,
                claim_type='CAGE_FREE_PERCENT',
                amt=Decimal(str(pct)),
                unit='percent',
                effective_date='2024-01-01',
                source_uri='https://www.eggtrack.com/en/',
                how_known='official_tracker',
            )
            self.stdout.write(f"  EggTrack: {name} {pct}%")

        # ICE Contracts Data (source: Fortune June 2025, USASpending.gov)
        ice_contracts_data = [
            ('dell', 'Dell', 'DELL', 'Technology', Decimal('18.8')),
            ('motorola-solutions', 'Motorola Solutions', 'MSI', 'Technology', Decimal('15.6')),
            ('l3harris', 'L3Harris', 'LHX', 'Defense', Decimal('4.4')),
            ('comcast', 'Comcast', 'CMCSA', 'Telecommunications', Decimal('0.061')),
            ('ecolab', 'Ecolab', 'ECL', 'Manufacturing', Decimal('0.137')),
            ('ups', 'UPS', 'UPS', 'Logistics', Decimal('0.061')),
            ('sosi', 'SOSi', None, 'Defense', Decimal('123')),
            ('gravitas', 'Gravitas Investigations', None, 'Services', Decimal('32')),
            ('government-support-services', 'Government Support Services', None, 'Services', Decimal('55')),
        ]

        for slug, name, ticker, sector, amt in ice_contracts_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            self.create_claim_safe(
                uri=f'urn:usaspending:2025:{slug}:ice',
                subject=company.uri,
                claim_type='ICE_CONTRACT',
                amt=amt,
                unit='million_usd',
                effective_date='2025-06-01',
                source_uri='https://www.usaspending.gov/',
                how_known='federal_spending_data',
            )
            self.stdout.write(f"  ICE Contract: {name} ${amt}M")

        # ICE Detention Operators (source: The Intercept Dec 2025)
        detention_data = [
            ('geo-group', 'GEO Group', 'GEO', 'Private Prisons'),
            ('corecivic', 'CoreCivic', 'CXW', 'Private Prisons'),
        ]

        for slug, name, ticker, sector in detention_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            self.create_claim_safe(
                uri=f'urn:ice:2025:{slug}:detention',
                subject=company.uri,
                claim_type='ICE_DETENTION_OPERATOR',
                label='detention_operator',
                effective_date='2025-12-01',
                source_uri='https://theintercept.com/2025/12/23/ice-bounty-hunters-track-immigrant-surveillance/',
                how_known='investigative_journalism',
            )
            self.stdout.write(f"  ICE Detention: {name}")

    def migrate_lobbying_data(self):
        """Convert existing lobbying claims into the corporate_lobbying value system."""
        lobbying_claims = Claim.objects.filter(claim_type='LOBBYING_SPEND')
        self.stdout.write(f"  Migrating {lobbying_claims.count()} lobbying claims...")
        # These get picked up in compute_snapshots

    def compute_snapshots(self):
        """Compute CompanyValueSnapshot for each company/value pair with claims."""
        for company in Company.objects.all():
            claims = Claim.objects.filter(subject=company.uri)

            # Corporate lobbying
            lobbying_claims = claims.filter(claim_type='LOBBYING_SPEND')
            if lobbying_claims.exists():
                claim = lobbying_claims.first()
                rule = ScoringRule.objects.get(value_id='corporate_lobbying', version=1)
                amt_float = float(claim.amt)
                grade, score = self._apply_threshold_inverse(rule.config['thresholds'], amt_float)

                # Format display amount
                if amt_float >= 1000000:
                    display_amt = f"${amt_float / 1000000:.1f}M"
                elif amt_float >= 1000:
                    display_amt = f"${amt_float / 1000:.0f}K"
                else:
                    display_amt = f"${amt_float:,.0f}"

                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='corporate_lobbying',
                    defaults={
                        'score': score,
                        'grade': grade,
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 3,
                        'display_text': f"Lobbying: {display_amt} (2024)",
                        'display_icon': 'megaphone',
                        'scoring_rule_version': 1,
                    }
                )
                self.stdout.write(f"  Lobbying snapshot: {company.name} = {grade}")

            # BBFAW tier
            bbfaw_claims = claims.filter(claim_type='FARM_WELFARE_TIER')
            if bbfaw_claims.exists():
                claim = bbfaw_claims.first()
                rule = ScoringRule.objects.get(value_id='farm_animal_welfare', version=1)
                mapping = rule.config['mapping'].get(claim.label, {'grade': 'F', 'score': -1.0})

                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='farm_animal_welfare',
                    defaults={
                        'score': mapping['score'],
                        'grade': mapping['grade'],
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 1,
                        'display_text': f"BBFAW Tier {claim.label}",
                        'display_icon': 'cow',
                        'scoring_rule_version': 1,
                    }
                )
                self.stdout.write(f"  BBFAW snapshot: {company.name} = {mapping['grade']}")

            # Cage-free
            cage_claims = claims.filter(claim_type='CAGE_FREE_PERCENT')
            if cage_claims.exists():
                claim = cage_claims.first()
                rule = ScoringRule.objects.get(value_id='cage_free_eggs', version=1)
                amt_float = float(claim.amt)
                grade, score = self._apply_threshold(rule.config['thresholds'], amt_float)

                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='cage_free_eggs',
                    defaults={
                        'score': score,
                        'grade': grade,
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 2,
                        'display_text': f"{int(claim.amt)}% cage-free",
                        'display_icon': 'egg',
                        'scoring_rule_version': 1,
                    }
                )
                self.stdout.write(f"  Cage-free snapshot: {company.name} = {grade}")

            # ICE contracts
            ice_claims = claims.filter(claim_type='ICE_CONTRACT')
            if ice_claims.exists():
                claim = ice_claims.first()
                rule = ScoringRule.objects.get(value_id='ice_contracts', version=1)
                amt_float = float(claim.amt)
                grade, score = self._apply_threshold_inverse(rule.config['thresholds'], amt_float)

                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='ice_contracts',
                    defaults={
                        'score': score,
                        'grade': grade,
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 0,
                        'display_text': f"ICE contracts: ${claim.amt}M",
                        'display_icon': 'warning',
                        'scoring_rule_version': 1,
                    }
                )
                self.stdout.write(f"  ICE contract snapshot: {company.name} = {grade}")

            # ICE detention
            detention_claims = claims.filter(claim_type='ICE_DETENTION_OPERATOR')
            if detention_claims.exists():
                claim = detention_claims.first()

                CompanyValueSnapshot.objects.update_or_create(
                    company=company,
                    value_id='ice_detention',
                    defaults={
                        'score': -1.0,
                        'grade': 'F',
                        'claim_uris': [claim.uri],
                        'highlight_on_card': True,
                        'highlight_priority': 0,
                        'display_text': 'ICE detention operator',
                        'display_icon': 'alert',
                        'scoring_rule_version': 1,
                    }
                )
                self.stdout.write(f"  ICE detention snapshot: {company.name} = F")

    def _apply_threshold(self, thresholds, value):
        """Higher value = better grade."""
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def _apply_threshold_inverse(self, thresholds, value):
        """Higher value = worse grade."""
        for t in thresholds:
            if value >= t['min']:
                return t['grade'], t['score']
        last = thresholds[-1]
        return last['grade'], last['score']

    def create_badges(self):
        """Create badges from computed snapshots."""
        for snapshot in CompanyValueSnapshot.objects.filter(highlight_on_card=True):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                label=snapshot.display_text,
                defaults={
                    'badge_type': badge_type,
                    'value': snapshot.value,
                    'source_claim_uri': snapshot.claim_uris[0] if snapshot.claim_uris else '',
                    'priority': snapshot.highlight_priority,
                }
            )
            self.stdout.write(f"  Badge: {snapshot.company.name} - {snapshot.display_text} ({badge_type})")
