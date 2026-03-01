from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


# Tobacco companies by ticker — add more as they enter the database
TOBACCO_COMPANIES = {
    'MO': 'Altria Group Inc',
    'PM': 'Philip Morris International',
    'BTI': 'British American Tobacco',
}


class Command(BaseCommand):
    help = "Add tobacco_products disqualifying value and grade known tobacco companies F"

    def handle(self, *args, **options):
        # 1. Create the Value via raw SQL since DB has display_group columns not in model
        from django.db import connection
        from django.utils import timezone
        try:
            value = Value.objects.get(slug='tobacco_products')
            created = False
        except Value.DoesNotExist:
            now = timezone.now()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO core_value (slug, name, description, value_type, is_fixed,
                        is_disqualifying, min_weight, card_display_template, card_icon,
                        created_at, updated_at, display_group, display_group_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    'tobacco_products', 'Tobacco Products',
                    'Company manufactures or primarily distributes tobacco/nicotine products',
                    'label', True, True, 1, 'Tobacco manufacturer', 'cigarette',
                    now, now, '', 7
                ])
            value = Value.objects.get(slug='tobacco_products')
            created = True
        action = "Created" if created else "Updated"
        self.stdout.write(f"{action} Value: tobacco_products")

        # 2. Create ScoringRule
        rule, created = ScoringRule.objects.update_or_create(
            value=value,
            version=1,
            defaults={
                'config': {
                    'type': 'label_map',
                    'labels': {
                        'tobacco_manufacturer': {'grade': 'F', 'score': -1.0},
                        'not_tobacco': {'grade': 'A', 'score': 1.0},
                    }
                }
            }
        )
        self.stdout.write(f"ScoringRule v1 {'created' if created else 'updated'}")

        # 3. Create claims and snapshots for known tobacco companies
        for ticker, name in TOBACCO_COMPANIES.items():
            company = Company.objects.filter(ticker=ticker).first()
            if not company:
                self.stdout.write(f"  Skipping {name} ({ticker}) — not in database")
                continue

            # Create claim
            claim_uri = f'urn:alonovo:tobacco:{ticker.lower()}'
            if not Claim.objects.filter(uri=claim_uri).exists():
                Claim.objects.create(
                    uri=claim_uri,
                    subject=company.uri,
                    claim_type='tobacco_manufacturer',
                    statement=f'{name} manufactures tobacco products',
                    label='tobacco_manufacturer',
                    source_uri='https://en.wikipedia.org/wiki/Tobacco_industry',
                    how_known='research',
                    author='alonovo-system',
                )
                self.stdout.write(f"  Created claim for {name}")

            # Create/update snapshot — F grade, disqualifying
            snap, created = CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value=value,
                defaults={
                    'score': -1.0,
                    'grade': 'F',
                    'claim_uris': [claim_uri],
                    'highlight_on_card': True,
                    'highlight_priority': 100,
                    'display_text': 'Tobacco manufacturer',
                    'display_icon': 'cigarette',
                    'scoring_rule_version': 1,
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} snapshot for {name}: F")

            # Create badge
            badge, created = CompanyBadge.objects.get_or_create(
                company=company,
                label='Tobacco',
                defaults={
                    'badge_type': 'negative',
                    'value': value,
                    'source_claim_uri': claim_uri,
                    'priority': 100,
                }
            )
            if created:
                self.stdout.write(f"  Created badge for {name}")

        self.stdout.write(self.style.SUCCESS("Done! Tobacco companies now get F overall."))
