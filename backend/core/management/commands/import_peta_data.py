from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


class Command(BaseCommand):
    help = "Import PETA cruelty-free data"

    def handle(self, *args, **options):
        self.stdout.write("Creating Cruelty-Free Value...")
        self.create_value()

        self.stdout.write("Creating ScoringRule...")
        self.create_scoring_rule()

        self.stdout.write("Importing PETA data...")
        count = self.import_peta_data()

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
            slug='cruelty_free',
            defaults={
                'name': 'Cruelty-Free (Animal Testing)',
                'description': 'PETA certification for companies that do not test on animals',
                'value_type': 'label',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': '{label}',
                'card_icon': 'rabbit',
            }
        )

    def create_scoring_rule(self):
        ScoringRule.objects.update_or_create(
            value_id='cruelty_free',
            version=1,
            defaults={
                'effective_date': '2026-01-01',
                'config': {
                    'type': 'label',
                    'mapping': {
                        'cruelty_free_vegan': {'grade': 'A', 'score': 1.0},
                        'cruelty_free': {'grade': 'A-', 'score': 0.85},
                        'working_toward': {'grade': 'C', 'score': 0.0},
                        'tests_on_animals': {'grade': 'F', 'score': -1.0},
                    }
                }
            }
        )

    def import_peta_data(self):
        count = 0

        cruelty_free_vegan = [
            ('lush', 'Lush', None, 'Consumer Goods'),
            ('the-body-shop', 'The Body Shop', None, 'Consumer Goods'),
            ('elf-cosmetics', 'e.l.f. Cosmetics', None, 'Consumer Goods'),
            ('pacifica', 'Pacifica', None, 'Consumer Goods'),
            ('tarte', 'Tarte Cosmetics', None, 'Consumer Goods'),
            ('too-faced', 'Too Faced', None, 'Consumer Goods'),
            ('urban-decay', 'Urban Decay', None, 'Consumer Goods'),
            ('nyx', 'NYX Cosmetics', None, 'Consumer Goods'),
            ('milani', 'Milani', None, 'Consumer Goods'),
            ('wet-n-wild', 'Wet n Wild', None, 'Consumer Goods'),
            ('physicians-formula', 'Physicians Formula', None, 'Consumer Goods'),
            ('alba-botanica', 'Alba Botanica', None, 'Consumer Goods'),
            ('jasons-natural', "Jason's Natural", None, 'Consumer Goods'),
            ('seventh-generation', 'Seventh Generation', None, 'Consumer Goods'),
            ('method', 'Method', None, 'Consumer Goods'),
            ('mrs-meyers', "Mrs. Meyer's", None, 'Consumer Goods'),
            ('toms-of-maine', "Tom's of Maine", None, 'Consumer Goods'),
            ('burts-bees', "Burt's Bees", None, 'Consumer Goods'),
            ('derma-e', 'Derma E', None, 'Consumer Goods'),
            ('acure', 'Acure', None, 'Consumer Goods'),
        ]

        cruelty_free = [
            ('bath-body-works', 'Bath & Body Works', None, 'Consumer Goods'),
            ('beautycounter', 'Beautycounter', None, 'Consumer Goods'),
            ('the-honest-company', 'The Honest Company', None, 'Consumer Goods'),
            ('mario-badescu', 'Mario Badescu', None, 'Consumer Goods'),
            ('paula-choice', "Paula's Choice", None, 'Consumer Goods'),
            ('first-aid-beauty', 'First Aid Beauty', None, 'Consumer Goods'),
            ('tatcha', 'Tatcha', None, 'Consumer Goods'),
            ('drunk-elephant', 'Drunk Elephant', None, 'Consumer Goods'),
            ('glossier', 'Glossier', None, 'Consumer Goods'),
            ('fenty-beauty', 'Fenty Beauty', None, 'Consumer Goods'),
        ]

        working_toward = [
            ('colgate-palmolive', 'Colgate-Palmolive', 'CL', 'Consumer Goods'),
            ('henkel', 'Henkel', 'HENKY', 'Consumer Goods'),
        ]

        tests_on_animals = [
            ('loreal', "L'Oréal", 'OR.PA', 'Consumer Goods'),
            ('estee-lauder', 'Estée Lauder', 'EL', 'Consumer Goods'),
            ('procter-gamble', 'Procter & Gamble', 'PG', 'Consumer Goods'),
            ('johnson-johnson', 'Johnson & Johnson', 'JNJ', 'Healthcare'),
            ('unilever', 'Unilever', 'UL', 'Consumer Goods'),
            ('clorox', 'Clorox', 'CLX', 'Consumer Goods'),
            ('sc-johnson', 'S.C. Johnson', None, 'Consumer Goods'),
            ('reckitt', 'Reckitt Benckiser', 'RKT.L', 'Consumer Goods'),
            ('church-dwight', 'Church & Dwight', 'CHD', 'Consumer Goods'),
            ('revlon', 'Revlon', 'REV', 'Consumer Goods'),
            ('avon', 'Avon', None, 'Consumer Goods'),
            ('mary-kay', 'Mary Kay', None, 'Consumer Goods'),
            ('maybelline', 'Maybelline', None, 'Consumer Goods'),
            ('lancome', 'Lancôme', None, 'Consumer Goods'),
            ('clinique', 'Clinique', None, 'Consumer Goods'),
            ('mac', 'MAC Cosmetics', None, 'Consumer Goods'),
            ('olay', 'Olay', None, 'Consumer Goods'),
            ('pantene', 'Pantene', None, 'Consumer Goods'),
            ('head-shoulders', 'Head & Shoulders', None, 'Consumer Goods'),
            ('dove', 'Dove', None, 'Consumer Goods'),
            ('axe', 'Axe', None, 'Consumer Goods'),
            ('neutrogena', 'Neutrogena', None, 'Consumer Goods'),
            ('aveeno', 'Aveeno', None, 'Consumer Goods'),
        ]

        for slug, name, ticker, sector in cruelty_free_vegan:
            if self._create_peta_claim(slug, name, ticker, sector, 'cruelty_free_vegan'):
                count += 1

        for slug, name, ticker, sector in cruelty_free:
            if self._create_peta_claim(slug, name, ticker, sector, 'cruelty_free'):
                count += 1

        for slug, name, ticker, sector in working_toward:
            if self._create_peta_claim(slug, name, ticker, sector, 'working_toward'):
                count += 1

        for slug, name, ticker, sector in tests_on_animals:
            if self._create_peta_claim(slug, name, ticker, sector, 'tests_on_animals'):
                count += 1

        return count

    def _create_peta_claim(self, slug, name, ticker, sector, label):
        company = self.get_or_create_company(slug, name, ticker, sector)
        claim = self.create_claim_safe(
            uri=f'urn:peta:2026:{slug}:cruelty-free',
            subject=company.uri,
            claim_type='CRUELTY_FREE_STATUS',
            label=label,
            effective_date='2026-01-01',
            source_uri='https://crueltyfree.peta.org/',
            how_known='official_certification',
        )
        if claim:
            self.stdout.write(f"  PETA: {name} = {label}")
            return True
        return False

    def compute_snapshots(self):
        rule = ScoringRule.objects.get(value_id='cruelty_free', version=1)
        mapping = rule.config['mapping']
        count = 0

        display_text_map = {
            'cruelty_free_vegan': 'Cruelty-free & Vegan',
            'cruelty_free': 'Cruelty-free',
            'working_toward': 'Working toward cruelty-free',
            'tests_on_animals': 'Tests on animals',
        }

        display_icon_map = {
            'cruelty_free_vegan': 'rabbit',
            'cruelty_free': 'rabbit',
            'working_toward': 'clock',
            'tests_on_animals': 'alert',
        }

        companies_with_claims = Company.objects.filter(
            uri__in=Claim.objects.filter(claim_type='CRUELTY_FREE_STATUS').values_list('subject', flat=True)
        ).distinct()

        for company in companies_with_claims:
            claim = Claim.objects.filter(subject=company.uri, claim_type='CRUELTY_FREE_STATUS').first()
            if not claim:
                continue

            grade_info = mapping.get(claim.label, {'grade': 'F', 'score': -1.0})

            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='cruelty_free',
                defaults={
                    'score': grade_info['score'],
                    'grade': grade_info['grade'],
                    'claim_uris': [claim.uri],
                    'highlight_on_card': True,
                    'highlight_priority': 2,
                    'display_text': display_text_map.get(claim.label, claim.label),
                    'display_icon': display_icon_map.get(claim.label, 'rabbit'),
                    'scoring_rule_version': 1,
                }
            )
            count += 1
            self.stdout.write(f"  Snapshot: {company.name} = {grade_info['grade']}")

        return count

    def create_badges(self):
        count = 0
        for snapshot in CompanyValueSnapshot.objects.filter(value_id='cruelty_free'):
            badge_type = 'positive' if snapshot.score > 0.3 else ('negative' if snapshot.score < -0.3 else 'neutral')
            _, created = CompanyBadge.objects.update_or_create(
                company=snapshot.company,
                value_id='cruelty_free',
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
