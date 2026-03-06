import json
import time
import urllib.request
import urllib.error
import urllib.parse
from django.core.management.base import BaseCommand
from core.models import Company

# Manual overrides for companies that Clearbit gets wrong or misses
KNOWN_WEBSITES = {
    '3M Company': '3m.com',
    'Abbott Laboratories': 'abbott.com',
    'AbbVie Inc.': 'abbvie.com',
    'Albemarle Corporation': 'albemarle.com',
    'Alphabet (Google)': 'google.com',
    'Altria Group Inc': 'altria.com',
    'Ameren Corp': 'ameren.com',
    'Anheuser-Busch InBev': 'ab-inbev.com',
    'Ball Corp': 'ball.com',
    'Caterpillar Inc.': 'caterpillar.com',
    'Whirlpool Corp.': 'whirlpool.com',
    'Adobe Inc.': 'adobe.com',
    'AES Corp': 'aes.com',
    'Allstate Corp': 'allstate.com',
    'Apple Inc.': 'apple.com',
    'AT&T Inc.': 'att.com',
    'Bank of America': 'bankofamerica.com',
    'Berkshire Hathaway': 'berkshirehathaway.com',
    'Boeing Company': 'boeing.com',
    'Cisco Systems': 'cisco.com',
    'Citigroup Inc.': 'citigroup.com',
    'Coca-Cola Company': 'coca-colacompany.com',
    'Comcast Corp.': 'comcastcorporation.com',
    'CVS Health': 'cvshealth.com',
    'Dow Inc.': 'dow.com',
    'DuPont de Nemours': 'dupont.com',
    'Exxon Mobil': 'exxonmobil.com',
    'Ford Motor Company': 'ford.com',
    'General Electric': 'ge.com',
    'General Mills': 'generalmills.com',
    'General Motors': 'gm.com',
    'Goldman Sachs Group': 'goldmansachs.com',
    'Home Depot': 'homedepot.com',
    'Honeywell International': 'honeywell.com',
    'Intel Corp.': 'intel.com',
    'International Business Machines': 'ibm.com',
    'Johnson & Johnson': 'jnj.com',
    'JPMorgan Chase': 'jpmorganchase.com',
    'Kellogg Company': 'kelloggs.com',
    "Kellogg's": 'kelloggs.com',
    'Kraft Heinz': 'kraftheinzcompany.com',
    "Lowe's": 'lowes.com',
    'McDonald\'s Corp.': 'mcdonalds.com',
    'Meta Platforms (Facebook)': 'meta.com',
    'Microsoft Corp.': 'microsoft.com',
    'Morgan Stanley': 'morganstanley.com',
    'Nike Inc.': 'nike.com',
    'PepsiCo': 'pepsico.com',
    'Pfizer Inc.': 'pfizer.com',
    'Procter & Gamble': 'pg.com',
    'Target Corp.': 'target.com',
    'Tesla Inc.': 'tesla.com',
    'UnitedHealth Group': 'unitedhealthgroup.com',
    'Verizon Communications': 'verizon.com',
    'Visa Inc.': 'visa.com',
    'Walmart Inc.': 'walmart.com',
    'Walt Disney Company': 'thewaltdisneycompany.com',
    'Wells Fargo': 'wellsfargo.com',
    'American International Group': 'aig.com',
    'American Tower Corp.': 'americantower.com',
    'ANSYS, Inc.': 'ansys.com',
    'A.O. Smith Corp': 'aosmith.com',
    'APA Corporation': 'apacorp.com',
    'Applied Materials Inc.': 'appliedmaterials.com',
    'Aptiv PLC': 'aptiv.com',
    'Archer-Daniels-Midland Co': 'adm.com',
    'Autodesk Inc.': 'autodesk.com',
    'Automatic Data Processing': 'adp.com',
    'Avery Dennison Corp': 'averydennison.com',
    'Best Buy Co. Inc.': 'bestbuy.com',
    'Boston Beer Company': 'bostonbeer.com',
    'Boston Properties': 'bxp.com',
    'Cardinal Health Inc.': 'cardinalhealth.com',
    'Carmax Inc': 'carmax.com',
    'CF Industries Holdings Inc': 'cfindustries.com',
    'Citrix Systems': 'citrix.com',
    'CSX Corp.': 'csx.com',
    'Cummins Inc.': 'cummins.com',
    'Danaher Corp.': 'danaher.com',
    'Deere & Co.': 'deere.com',
    'Digital Realty Trust Inc': 'digitalrealty.com',
    'Discovery, Inc. (Series A)': 'discovery.com',
    'Emerson Electric Company': 'emerson.com',
    'Entergy Corp.': 'entergy.com',
    'Facebook, Inc.': 'meta.com',
    'Meta Platforms': 'meta.com',
    'Fidelity National Information Services': 'fisglobal.com',
    'Fiserv Inc': 'fiserv.com',
    'Flowserve Corporation': 'flowserve.com',
    'FMC Corporation': 'fmc.com',
    'Fortive Corp': 'fortive.com',
    'Freeport-McMoRan Inc.': 'fcx.com',
    'Garmin Ltd.': 'garmin.com',
    'Grainger (W.W.) Inc.': 'grainger.com',
    'Hanesbrands Inc': 'hanes.com',
    'Hartford Financial Svc.Gp.': 'thehartford.com',
    'Hasbro Inc.': 'hasbro.com',
    'Hilton Worldwide Holdings Inc': 'hilton.com',
    "Honeywell Int'l Inc.": 'honeywell.com',
    'Illumina Inc': 'illumina.com',
    'Intercontinental Exchange': 'ice.com',
    'Intuit Inc.': 'intuit.com',
    'Intuitive Surgical Inc.': 'intuitive.com',
    'Iron Mountain Incorporated': 'ironmountain.com',
    'J. B. Hunt Transport Services': 'jbhunt.com',
    'KLA Corporation': 'kla.com',
    'Laboratory Corp. of America Holding': 'labcorp.com',
    'L Brands Inc.': 'bbwinc.com',
    'Lilly (Eli) & Co.': 'lilly.com',
    'LKQ Corporation': 'lkqcorp.com',
    'Loews Corp.': 'loews.com',
    "Lowe's Cos.": 'lowes.com',
    'Martin Marietta Materials': 'martinmarietta.com',
    'Masco Corp.': 'masco.com',
    'Mastercard Inc.': 'mastercard.com',
    'McKesson Corp.': 'mckesson.com',
    'MetLife Inc.': 'metlife.com',
    'Molson Coors Beverage Company': 'molsoncoors.com',
    'Mondelez International': 'mondelezinternational.com',
    "Moody's Corp": 'moodys.com',
    'Nasdaq, Inc.': 'nasdaq.com',
    'Netflix Inc.': 'netflix.com',
    'News Corp (Class A)': 'newscorp.com',
    'Nike, Inc.': 'nike.com',
    'NiSource Inc.': 'nisource.com',
    'Nucor Corp.': 'nucor.com',
    'Nvidia Corporation': 'nvidia.com',
    'Oracle Corp.': 'oracle.com',
    "O'Reilly Automotive": 'oreillyauto.com',
    'Paychex Inc.': 'paychex.com',
    'Pentair plc': 'pentair.com',
    "Pilgrim's Pride": 'pilgrims.com',
    'PPL Corp.': 'pplweb.com',
    'PVH Corp.': 'pvh.com',
    'Quanta Services Inc.': 'quantaservices.com',
    'Ralph Lauren Corporation': 'ralphlauren.com',
    'Realty Income Corporation': 'realtyincome.com',
    'Reckitt Benckiser': 'reckitt.com',
    'Regency Centers Corporation': 'regencycenters.com',
    'Regions Financial Corp.': 'regions.com',
    'Ross Stores': 'rossstores.com',
    'Simon Property Group Inc': 'simon.com',
    'Sprouts Farmers Market': 'sprouts.com',
    'Stryker Corp.': 'stryker.com',
    'Synchrony Financial': 'synchrony.com',
    'Synopsys Inc.': 'synopsys.com',
    'Sysco Corp.': 'sysco.com',
    'TE Connectivity Ltd.': 'te.com',
    'Textron Inc.': 'textron.com',
    'TJX Companies Inc.': 'tjx.com',
    'Tractor Supply Company': 'tractorsupply.com',
    'T. Rowe Price Group': 'troweprice.com',
    'Under Armour (Class A)': 'underarmour.com',
    'United Rentals, Inc.': 'unitedrentals.com',
    'VF Corporation': 'vfc.com',
    'Waste Management Inc.': 'wm.com',
    'Waters Corporation': 'waters.com',
    'Xylem Inc.': 'xylem.com',
    'National Beverage Corp': 'nationalbeverage.com',
    'Mid-America Apartments': 'maac.com',
    'Duke Realty Corp': 'dukerealty.com',
    'Essex Property Trust, Inc.': 'essexapartmenthomes.com',
    'Everest Re Group Ltd.': 'everestre.com',
    'F5 Networks': 'f5.com',
}


class Command(BaseCommand):
    help = "Prefill company website URLs using Clearbit autocomplete + known overrides"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Show what would be updated without saving")
        parser.add_argument('--delay', type=float, default=0.3, help="Seconds between API calls")
        parser.add_argument('--all', action='store_true', help="Include companies without tickers too")

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delay = options['delay']

        if options['all']:
            companies = list(Company.objects.filter(website__isnull=True) | Company.objects.filter(website=''))
        else:
            has_ticker = Company.objects.exclude(ticker__isnull=True).exclude(ticker='')
            companies = list(has_ticker.filter(website__isnull=True) | has_ticker.filter(website=''))

        self.stdout.write(f"Found {len(companies)} companies without website URLs")

        if not companies:
            self.stdout.write(self.style.SUCCESS("Nothing to do."))
            return

        updated = 0
        failed = 0

        for company in companies:
            # Check manual overrides first
            domain = KNOWN_WEBSITES.get(company.name)
            source = 'override'

            if not domain:
                domain = self.lookup_domain(company.name)
                source = 'clearbit'

            if domain:
                url = f"https://{domain}"
                if dry_run:
                    self.stdout.write(f"  [DRY RUN] {company.name}: {url} ({source})")
                else:
                    company.website = url
                    company.save(update_fields=['website', 'updated_at'])
                    self.stdout.write(f"  {company.name}: {url} ({source})")
                updated += 1
            else:
                self.stdout.write(f"  {company.name}: no domain found")
                failed += 1

            if source == 'clearbit':
                time.sleep(delay)

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}Done! Updated: {updated}, Not found: {failed}"
        ))

    def lookup_domain(self, company_name):
        """Look up domain for a company name via Clearbit autocomplete."""
        try:
            encoded = urllib.parse.quote(company_name)
            url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={encoded}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if not data:
                    return None
                # Look through results for a matching name, prefer .com domains
                best = None
                for result in data:
                    if self.names_match(company_name, result.get('name', '')):
                        domain = result.get('domain', '')
                        if domain.endswith('.com'):
                            return domain
                        if best is None:
                            best = domain
                return best
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
            pass
        return None

    def names_match(self, our_name, their_name):
        """Check if the Clearbit result name reasonably matches our company name."""
        ours = our_name.lower().strip()
        theirs = their_name.lower().strip()
        # Strip common suffixes for comparison
        for suffix in [' inc.', ' inc', ' corp.', ' corp', ' corporation', ' company',
                       ' co.', ' co', ' ltd.', ' ltd', ' llc', ' plc', ' group',
                       ' holdings', ' enterprises', ' international', ' technologies']:
            ours = ours.removesuffix(suffix)
            theirs = theirs.removesuffix(suffix)
        if ours == theirs:
            return True
        if ours in theirs or theirs in ours:
            return True
        return False
