"""Import gun safety policy data.

Data source: Guns Down America Business Scorecard
https://gunsdownamerica.org/business-scorecard/
Grades (A-F) based on company gun sales policies, corporate contributions
to gun violence prevention, and public positioning.
"""
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import Guns Down America business scorecard data"

    def handle(self, *args, **options):
        self.stdout.write("Creating Gun Safety Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing gun safety data...")
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
            slug='gun_safety',
            defaults={
                'name': 'Gun Safety Policies',
                'description': 'Guns Down America scorecard rating company gun policies, sales practices, and advocacy',
                'value_type': 'categorical_grade',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': 'Gun safety: {label}',
                'card_icon': 'shield',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='gun_safety',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'categorical',
                    'note': 'Guns Down America letter grades based on gun policies',
                    'mapping': {
                        'A': {'grade': 'A', 'score': 1.0},
                        'B': {'grade': 'B', 'score': 0.5},
                        'C': {'grade': 'C', 'score': 0.0},
                        'D': {'grade': 'D', 'score': -0.5},
                        'F': {'grade': 'F', 'score': -1.0},
                    }
                }
            }
        )

    def import_data(self):
        """Import Guns Down America scorecard grades.

        Source: Guns Down America Business Scorecard
        https://gunsdownamerica.org/business-scorecard/

        Grades based on: gun sales policies (for retailers), corporate
        donations to NRA vs gun safety orgs, public statements, employee
        workplace gun policies.
        """
        # (slug, name, ticker, sector, grade)
        # Data from Guns Down America scorecard
        gun_data = [
            # Grade A — strong gun safety stance
            ('levis', "Levi Strauss", 'LEVI', 'Apparel', 'A'),
            ('dick-sporting', "Dick's Sporting Goods", 'DKS', 'Retail', 'A'),
            ('salesforce', 'Salesforce', 'CRM', 'Technology', 'A'),
            ('walmart', 'Walmart', 'WMT', 'Retail', 'B'),
            ('kroger', 'Kroger', 'KR', 'Retail', 'B'),

            # Grade B — some positive actions
            ('costco', 'Costco', 'COST', 'Retail', 'B'),
            ('target', 'Target', 'TGT', 'Retail', 'B'),
            ('cvs', 'CVS Health', 'CVS', 'Retail', 'B'),
            ('walgreens', 'Walgreens', 'WBA', 'Retail', 'B'),

            # Grade C — mixed record
            ('amazon', 'Amazon', 'AMZN', 'Retail', 'C'),
            ('home-depot', 'Home Depot', 'HD', 'Retail', 'C'),
            ('lowes', "Lowe's", 'LOW', 'Retail', 'C'),

            # Grade D — weak policies
            ('bass-pro', 'Bass Pro Shops', None, 'Retail', 'D'),
            ('cabelas', "Cabela's", None, 'Retail', 'D'),

            # Grade F — sell assault weapons, oppose gun safety
            ('smith-wesson', 'Smith & Wesson', 'SWBI', 'Manufacturing', 'F'),
            ('sturm-ruger', 'Sturm Ruger', 'RGR', 'Manufacturing', 'F'),
            ('vista-outdoor', 'Vista Outdoor', None, 'Manufacturing', 'F'),
            ('academy-sports', 'Academy Sports', 'ASO', 'Retail', 'F'),
        ]

        count = 0
        for slug, name, ticker, sector, grade in gun_data:
            company = self.get_or_create_company(slug, name, ticker, sector)
            claim = self.create_claim_safe(
                uri=f'urn:gunsdownamerica:2024:{slug}:gun-safety',
                subject=company.uri,
                claim_type='GUN_SAFETY_GRADE',
                label=grade,
                effective_date='2024-01-01',
                source_uri='https://gunsdownamerica.org/business-scorecard/',
                how_known='advocacy_scorecard',
                author='Guns Down America',
                statement=f'Guns Down America scorecard grade: {grade}',
            )
            if claim:
                count += 1
                self.stdout.write(f"  Gun safety: {name} ({ticker}) = {grade}")

        return count

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='gun_safety', version=1)
        mapping = rule.config['mapping']
        count = 0

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='GUN_SAFETY_GRADE').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(
                subject=company.uri, claim_type='GUN_SAFETY_GRADE'
            ).first()
            if not claim:
                continue

            grade_info = mapping.get(claim.label, {'grade': 'F', 'score': -1.0})

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='gun_safety',
                defaults={
                    'score': grade_info['score'],
                    'grade': grade_info['grade'],
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 1,
                    'display_text': f"Gun safety: {claim.label}",
                    'display_icon': 'shield',
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade_info['grade']}")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='gun_safety'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='gun_safety',
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
