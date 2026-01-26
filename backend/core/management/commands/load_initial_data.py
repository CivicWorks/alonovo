import json
import uuid
from pathlib import Path
from django.core.management.base import BaseCommand
from core.models import Claim, Company, CompanyScore


class Command(BaseCommand):
    help = 'Load initial company data from scored_companies.json'

    def handle(self, *args, **options):
        data_path = Path(__file__).resolve().parent.parent.parent.parent.parent / 'data' / 'scored_companies.json'

        with open(data_path) as f:
            data = json.load(f)

        companies_created = 0
        claims_created = 0
        scores_created = 0

        for company_data in data['companies']:
            ticker = company_data['ticker']
            company_uri = f"urn:alonovo:company:{ticker.lower()}"

            company, created = Company.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'uri': company_uri,
                    'name': company_data['name'],
                    'sector': company_data['sector'],
                }
            )
            if created:
                companies_created += 1

            claim_uri = f"urn:alonovo:claim:lobbying:{ticker.lower()}:2024:{uuid.uuid4().hex[:8]}"
            claim, created = Claim.objects.update_or_create(
                subject=company_uri,
                claim='LOBBYING_SPEND',
                effective_date='2024-01-01',
                defaults={
                    'uri': claim_uri,
                    'amt': company_data['lobbying_spend_2024'],
                    'unit': 'USD',
                    'source_uri': 'https://www.opensecrets.org/',
                    'how_known': 'WEB_DOCUMENT',
                    'statement': f"{company_data['name']} lobbying spend for 2024",
                }
            )
            if created:
                claims_created += 1

            CompanyScore.objects.filter(company=company).delete()
            CompanyScore.objects.create(
                company=company,
                score=company_data['lobbying_score'],
                grade=company_data['lobbying_grade'],
                raw_value=company_data['lobbying_spend_2024'],
                reason=company_data['grade_reason'],
                source_claim_uris=[claim.uri],
            )
            scores_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {companies_created} companies, {claims_created} claims, {scores_created} scores'
        ))
