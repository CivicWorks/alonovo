import json
import uuid
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import Claim, Company, CompanyScore


class Command(BaseCommand):
    help = 'Load initial company data from scored_companies.json'

    def handle(self, *args, **options):
        data_path = Path(__file__).resolve().parent.parent.parent.parent.parent / 'data' / 'scored_companies.json'

        with open(data_path) as f:
            data = json.load(f)

        companies_loaded = 0
        claims_loaded = 0
        scores_loaded = 0

        for company_data in data['companies']:
            ticker = company_data['ticker']
            company_uri = f"urn:alonovo:company:{ticker.lower()}"

            company, _ = Company.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'uri': company_uri,
                    'name': company_data['name'],
                    'sector': company_data['sector'],
                }
            )
            companies_loaded += 1

            claim_uri = f"urn:alonovo:claim:lobbying:{ticker.lower()}:2024:{uuid.uuid4().hex[:8]}"
            if not Claim.objects.filter(subject=company_uri, claim_type='LOBBYING_SPEND').exists():
                Claim.objects.create(
                    uri=claim_uri,
                    subject=company_uri,
                    claim_type='LOBBYING_SPEND',
                    effective_date='2024-01-01',
                    amt=Decimal(str(company_data['lobbying_spend_2024'])),
                    unit='USD',
                    source_uri='https://www.opensecrets.org/',
                    how_known='WEB_DOCUMENT',
                    statement=f"{company_data['name']} lobbying spend for 2024",
                )
                claims_loaded += 1

            claim = Claim.objects.filter(subject=company_uri, claim_type='LOBBYING_SPEND').first()

            CompanyScore.objects.update_or_create(
                company=company,
                defaults={
                    'score': company_data['lobbying_score'],
                    'grade': company_data['lobbying_grade'],
                    'raw_value': company_data['lobbying_spend_2024'],
                    'reason': company_data['grade_reason'],
                    'source_claim_uris': [claim.uri] if claim else [],
                }
            )
            scores_loaded += 1

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {companies_loaded} companies, {claims_loaded} claims, {scores_loaded} scores'
        ))
