"""Import GHG Scope 1 emissions from NZDPU API.

Data source: https://nzdpu.com (Net-Zero Data Public Utility)
Grades are sector-relative using a curved grading mechanism so that
energy companies aren't all F and fintech aren't all A.
"""
import json
import math
import urllib.request
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import Claim, Company, Value, ScoringRule, CompanyValueSnapshot, CompanyBadge


NZDPU_SEARCH_URL = "https://nzdpu.com/wis/search"

# Name normalization suffixes
SUFFIXES = [
    ' inc.', ' inc', ' corp.', ' corp', ' corporation', ' company',
    ' co.', ' co', ' ltd.', ' ltd', ' llc', ' plc', ' group',
    ' holdings', ' enterprises', ' international', ' technologies',
    ',', '.', ' the',
]


class Command(BaseCommand):
    help = "Import GHG Scope 1 emissions from NZDPU and grade relative to sector"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Show what would be imported without saving")
        parser.add_argument('--limit', type=int, default=0, help="Limit number of companies to process (0=all)")

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        self.stdout.write("Step 1: Fetching emissions data from NZDPU...")
        nzdpu_data = self.fetch_nzdpu_data()
        self.stdout.write(f"  Got {len(nzdpu_data)} unique companies from NZDPU")

        self.stdout.write("Step 2: Matching against our companies...")
        matches = self.match_companies(nzdpu_data, limit)
        self.stdout.write(f"  Matched {len(matches)} companies")

        if not matches:
            self.stdout.write(self.style.WARNING("No matches found."))
            return

        self.stdout.write("Step 3: Computing sector-relative grades...")
        graded = self.compute_sector_grades(matches)

        if dry_run:
            self.stdout.write("\n[DRY RUN] Would create:")
            for item in sorted(graded, key=lambda x: x['s1_emissions'], reverse=True):
                self.stdout.write(
                    f"  {item['company'].name:40s} | "
                    f"S1: {item['s1_emissions']:>12,.0f} tCO2e | "
                    f"Sector: {item['sector']:30s} | "
                    f"Percentile: {item['percentile']:5.1f}% | "
                    f"Grade: {item['grade']}"
                )
            self.stdout.write(self.style.SUCCESS(f"\n[DRY RUN] Would update {len(graded)} companies"))
            return

        self.stdout.write("Step 4: Creating Value and ScoringRule...")
        self.create_value_and_rule()

        self.stdout.write("Step 5: Creating claims and snapshots...")
        claim_count, snap_count = self.create_claims_and_snapshots(graded)

        self.stdout.write(self.style.SUCCESS(
            f"Done! {claim_count} claims, {snap_count} snapshots"
        ))

    def fetch_nzdpu_data(self):
        """Fetch all companies with Scope 1 emissions from NZDPU."""
        all_companies = {}
        start = 0
        limit = 500
        total = None

        while total is None or start < total:
            body = json.dumps({
                "meta": {},
                "fields": [
                    "company_name", "sics_sector", "total_s1_emissions_ghg",
                    "reporting_year", "jurisdiction", "legal_entity_identifier"
                ]
            }).encode()

            req = urllib.request.Request(
                f"{NZDPU_SEARCH_URL}?mode=easy&start={start}&limit={limit}",
                data=body,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            if total is None:
                total = data["total_disclosures"]

            for item in data["items"]:
                name = item["company_name"]
                yr = item.get("reporting_year", 0)
                # Keep most recent year's data
                if name not in all_companies or yr > all_companies[name].get("reporting_year", 0):
                    all_companies[name] = item

            start += limit

        return all_companies

    def normalize_name(self, name):
        """Normalize company name for matching."""
        n = name.lower().strip()
        for s in SUFFIXES:
            n = n.removesuffix(s)
        n = n.strip(' ,.')
        return n

    def match_companies(self, nzdpu_data, limit=0):
        """Match our companies against NZDPU data."""
        nzdpu_by_norm = {}
        for name, data in nzdpu_data.items():
            key = self.normalize_name(name)
            nzdpu_by_norm[key] = (name, data)

        our_companies = Company.objects.all()
        if limit:
            our_companies = our_companies[:limit]

        matches = []
        for company in our_companies:
            our_norm = self.normalize_name(company.name)

            # Direct match
            if our_norm in nzdpu_by_norm:
                nz_name, nz_data = nzdpu_by_norm[our_norm]
                s1 = nz_data.get("total_s1_emissions_ghg")
                if s1 is not None:
                    matches.append({
                        'company': company,
                        'nzdpu_name': nz_name,
                        's1_emissions': float(s1),
                        'nzdpu_sector': nz_data.get('sics_sector', ''),
                        'reporting_year': nz_data.get('reporting_year'),
                        'nz_id': nz_data.get('nz_id'),
                    })
                continue

            # Fuzzy: one contains the other (min length 5 to avoid false positives)
            if len(our_norm) >= 5:
                for nz_norm, (nz_name, nz_data) in nzdpu_by_norm.items():
                    if len(nz_norm) >= 5 and (our_norm in nz_norm or nz_norm in our_norm):
                        s1 = nz_data.get("total_s1_emissions_ghg")
                        if s1 is not None:
                            matches.append({
                                'company': company,
                                'nzdpu_name': nz_name,
                                's1_emissions': float(s1),
                                'nzdpu_sector': nz_data.get('sics_sector', ''),
                                'reporting_year': nz_data.get('reporting_year'),
                                'nz_id': nz_data.get('nz_id'),
                            })
                        break

        return matches

    def compute_sector_grades(self, matches):
        """Grade companies relative to their sector using a curved mechanism.

        Uses the company's own sector from our DB (more complete than NZDPU).
        Within each sector, grades on a percentile curve:
          A = bottom 20% (lowest emissions in sector)
          B = 20-40%
          C = 40-60%
          D = 60-80%
          F = top 20% (highest emissions in sector)
        """
        # Group by sector (use our sector, fall back to NZDPU sector)
        by_sector = {}
        for match in matches:
            sector = match['company'].sector or match['nzdpu_sector'] or 'Unknown'
            if sector == 'Information Not Available':
                sector = match['company'].sector or 'Unknown'
            match['sector'] = sector
            by_sector.setdefault(sector, []).append(match)

        graded = []
        for sector, sector_matches in by_sector.items():
            # Sort by emissions within sector
            sector_matches.sort(key=lambda x: x['s1_emissions'])
            n = len(sector_matches)

            for i, match in enumerate(sector_matches):
                if n == 1:
                    percentile = 50.0
                else:
                    percentile = (i / (n - 1)) * 100

                match['percentile'] = percentile

                if percentile <= 20:
                    match['grade'] = 'A'
                    match['score'] = 1.0
                elif percentile <= 40:
                    match['grade'] = 'B'
                    match['score'] = 0.5
                elif percentile <= 60:
                    match['grade'] = 'C'
                    match['score'] = 0.0
                elif percentile <= 80:
                    match['grade'] = 'D'
                    match['score'] = -0.5
                else:
                    match['grade'] = 'F'
                    match['score'] = -1.0

                graded.append(match)

        return graded

    def create_value_and_rule(self):
        """Create the GHG emissions Value and ScoringRule."""
        Value.objects.update_or_create(
            slug='ghg_emissions',
            defaults={
                'name': 'GHG Emissions',
                'description': 'Greenhouse gas Scope 1 emissions, graded relative to sector peers',
                'value_type': 'metric',
                'is_fixed': False,
                'is_disqualifying': False,
                'card_display_template': '',
                'card_icon': 'factory',
            }
        )

        ScoringRule.objects.update_or_create(
            value_id='ghg_emissions',
            version=1,
            defaults={
                'effective_date': '2026-03-01',
                'config': {
                    'type': 'sector_relative_percentile',
                    'description': 'Curved grading within sector: A=bottom 20%, B=20-40%, C=40-60%, D=60-80%, F=top 20%',
                    'grades': {
                        'A': {'max_percentile': 20, 'score': 1.0},
                        'B': {'max_percentile': 40, 'score': 0.5},
                        'C': {'max_percentile': 60, 'score': 0.0},
                        'D': {'max_percentile': 80, 'score': -0.5},
                        'F': {'max_percentile': 100, 'score': -1.0},
                    }
                }
            }
        )

    def format_emissions(self, tco2e):
        """Format emissions for display."""
        if tco2e >= 1_000_000:
            return f"{tco2e / 1_000_000:.1f}M metric tons CO₂e"
        elif tco2e >= 1_000:
            return f"{tco2e / 1_000:.0f}K metric tons CO₂e"
        else:
            return f"{tco2e:,.0f} metric tons CO₂e"

    def create_claims_and_snapshots(self, graded):
        """Create Claims and CompanyValueSnapshots for matched companies."""
        claim_count = 0
        snap_count = 0

        for item in graded:
            company = item['company']
            s1 = item['s1_emissions']
            year = item.get('reporting_year', 2023)
            nz_id = item.get('nz_id', '')

            # Create claim
            claim_uri = f"urn:nzdpu:{year}:{company.uri.split(':')[-1]}:ghg_s1"
            if not Claim.objects.filter(uri=claim_uri).exists():
                Claim.objects.create(
                    uri=claim_uri,
                    subject=company.uri,
                    claim_type='GHG_SCOPE1_EMISSIONS',
                    amt=Decimal(str(s1)),
                    unit='tCO2e',
                    effective_date=f'{year}-12-31',
                    source_uri=f'https://nzdpu.com/external/by-nzid?nz_id={nz_id}' if nz_id else 'https://nzdpu.com',
                    how_known='official_disclosure',
                    statement=f'Scope 1 GHG emissions: {self.format_emissions(s1)}',
                    author='NZDPU / CDP',
                )
                claim_count += 1

            # Create snapshot (detail card shows emissions, not main card)
            CompanyValueSnapshot.objects.update_or_create(
                company=company,
                value_id='ghg_emissions',
                defaults={
                    'score': item['score'],
                    'grade': item['grade'],
                    'claim_uris': [claim_uri],
                    'highlight_on_card': False,
                    'highlight_priority': 2,
                    'display_text': f"Scope 1: {self.format_emissions(s1)} ({year})",
                    'display_icon': 'factory',
                    'scoring_rule_version': 1,
                }
            )
            snap_count += 1
            self.stdout.write(
                f"  {company.name}: {item['grade']} "
                f"({self.format_emissions(s1)}, sector: {item['sector']})"
            )

        return claim_count, snap_count
