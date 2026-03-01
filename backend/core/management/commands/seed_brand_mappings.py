"""Seed brand-to-company mappings for barcode scanning.

Maps well-known product brands to their parent companies in the Alonovo database.
Only creates mappings for companies that already exist in the DB.

Usage:
    python manage.py seed_brand_mappings
"""
from django.core.management.base import BaseCommand
from core.models import Company, BrandMapping


# (brand_name, company_ticker, source)
# Ticker must match a Company already in the database
BRAND_MAPPINGS = [
    # Nestlé
    ("Nestlé", "NESN.SW", "manual"),
    ("Nescafé", "NESN.SW", "manual"),
    ("Nespresso", "NESN.SW", "manual"),
    ("KitKat", "NESN.SW", "manual"),
    ("Häagen-Dazs", "NESN.SW", "manual"),
    ("Purina", "NESN.SW", "manual"),
    ("Gerber", "NESN.SW", "manual"),
    ("Perrier", "NESN.SW", "manual"),
    ("S.Pellegrino", "NESN.SW", "manual"),
    ("Stouffer's", "NESN.SW", "manual"),
    ("DiGiorno", "NESN.SW", "manual"),
    ("Hot Pockets", "NESN.SW", "manual"),
    ("Coffee-mate", "NESN.SW", "manual"),
    ("Cheerios", "NESN.SW", "manual"),
    ("Dreyer's", "NESN.SW", "manual"),
    ("Lean Cuisine", "NESN.SW", "manual"),
    ("Maggi", "NESN.SW", "manual"),

    # Procter & Gamble
    ("Tide", "PG", "manual"),
    ("Pampers", "PG", "manual"),
    ("Gillette", "PG", "manual"),
    ("Oral-B", "PG", "manual"),
    ("Charmin", "PG", "manual"),
    ("Bounty", "PG", "manual"),
    ("Dawn", "PG", "manual"),
    ("Febreze", "PG", "manual"),
    ("Swiffer", "PG", "manual"),
    ("Olay", "PG", "manual"),
    ("Pantene", "PG", "manual"),
    ("Head & Shoulders", "PG", "manual"),
    ("Old Spice", "PG", "manual"),
    ("Crest", "PG", "manual"),
    ("Downy", "PG", "manual"),
    ("Mr. Clean", "PG", "manual"),

    # Unilever
    ("Dove", "UL", "manual"),
    ("Axe", "UL", "manual"),
    ("Ben & Jerry's", "UL", "manual"),
    ("Hellmann's", "UL", "manual"),
    ("Knorr", "UL", "manual"),
    ("Lipton", "UL", "manual"),
    ("Magnum", "UL", "manual"),
    ("Breyers", "UL", "manual"),
    ("Degree", "UL", "manual"),
    ("TRESemmé", "UL", "manual"),
    ("Vaseline", "UL", "manual"),
    ("Suave", "UL", "manual"),
    ("Seventh Generation", "UL", "manual"),

    # Johnson & Johnson
    ("Band-Aid", "JNJ", "manual"),
    ("Tylenol", "JNJ", "manual"),
    ("Neutrogena", "JNJ", "manual"),
    ("Aveeno", "JNJ", "manual"),
    ("Listerine", "JNJ", "manual"),
    ("Benadryl", "JNJ", "manual"),
    ("Johnson's", "JNJ", "manual"),

    # Coca-Cola
    ("Coca-Cola", "KO", "manual"),
    ("Sprite", "KO", "manual"),
    ("Fanta", "KO", "manual"),
    ("Dasani", "KO", "manual"),
    ("Minute Maid", "KO", "manual"),
    ("Smartwater", "KO", "manual"),
    ("Vitaminwater", "KO", "manual"),
    ("Powerade", "KO", "manual"),
    ("Simply", "KO", "manual"),

    # PepsiCo
    ("Pepsi", "PEP", "manual"),
    ("Lay's", "PEP", "manual"),
    ("Doritos", "PEP", "manual"),
    ("Cheetos", "PEP", "manual"),
    ("Gatorade", "PEP", "manual"),
    ("Tropicana", "PEP", "manual"),
    ("Quaker", "PEP", "manual"),
    ("Mountain Dew", "PEP", "manual"),
    ("Aquafina", "PEP", "manual"),
    ("Frito-Lay", "PEP", "manual"),
    ("Tostitos", "PEP", "manual"),
    ("Ruffles", "PEP", "manual"),

    # Kraft Heinz
    ("Heinz", "KHC", "manual"),
    ("Oscar Mayer", "KHC", "manual"),
    ("Philadelphia", "KHC", "manual"),
    ("Kraft", "KHC", "manual"),
    ("Velveeta", "KHC", "manual"),
    ("Jell-O", "KHC", "manual"),
    ("Capri Sun", "KHC", "manual"),
    ("Planters", "KHC", "manual"),

    # McDonald's
    ("McDonald's", "MCD", "manual"),

    # Walmart
    ("Great Value", "WMT", "manual"),
    ("Sam's Choice", "WMT", "manual"),
    ("Equate", "WMT", "manual"),

    # Costco
    ("Kirkland Signature", "COST", "manual"),
    ("Kirkland", "COST", "manual"),

    # Amazon
    ("Amazon Basics", "AMZN", "manual"),
    ("365 Everyday Value", "AMZN", "manual"),
    ("Whole Foods", "AMZN", "manual"),

    # Hershey
    ("Hershey's", "HSY", "manual"),
    ("Reese's", "HSY", "manual"),
    ("Twizzlers", "HSY", "manual"),
    ("Jolly Rancher", "HSY", "manual"),
    ("Ice Breakers", "HSY", "manual"),

    # Colgate-Palmolive
    ("Colgate", "CL", "manual"),
    ("Palmolive", "CL", "manual"),
    ("Ajax", "CL", "manual"),
    ("Speed Stick", "CL", "manual"),
    ("Irish Spring", "CL", "manual"),
    ("Softsoap", "CL", "manual"),

    # Mars
    ("M&M's", "MARS", "manual"),
    ("Snickers", "MARS", "manual"),
    ("Twix", "MARS", "manual"),
    ("Skittles", "MARS", "manual"),
    ("Pedigree", "MARS", "manual"),
    ("Whiskas", "MARS", "manual"),
    ("Uncle Ben's", "MARS", "manual"),

    # Ferrero
    ("Nutella", "FERRERO", "manual"),
    ("Ferrero Rocher", "FERRERO", "manual"),
    ("Kinder", "FERRERO", "manual"),
    ("Tic Tac", "FERRERO", "manual"),

    # Danone
    ("Danone", "BN.PA", "manual"),
    ("Dannon", "BN.PA", "manual"),
    ("Evian", "BN.PA", "manual"),
    ("Volvic", "BN.PA", "manual"),
    ("Activia", "BN.PA", "manual"),
    ("Silk", "BN.PA", "manual"),
    ("Alpro", "BN.PA", "manual"),

    # Kellogg's
    ("Kellogg's", "K", "manual"),
    ("Pringles", "K", "manual"),
    ("Cheez-It", "K", "manual"),
    ("Pop-Tarts", "K", "manual"),
    ("Eggo", "K", "manual"),

    # General Mills
    ("General Mills", "GIS", "manual"),
    ("Cheerios", "GIS", "manual"),
    ("Nature Valley", "GIS", "manual"),
    ("Yoplait", "GIS", "manual"),
    ("Betty Crocker", "GIS", "manual"),
    ("Häagen-Dazs", "GIS", "manual"),  # US license

    # Mondelēz
    ("Oreo", "MDLZ", "manual"),
    ("Cadbury", "MDLZ", "manual"),
    ("Toblerone", "MDLZ", "manual"),
    ("Ritz", "MDLZ", "manual"),
    ("Trident", "MDLZ", "manual"),
    ("Philadelphia", "MDLZ", "manual"),

    # Tyson Foods
    ("Tyson", "TSN", "manual"),
    ("Jimmy Dean", "TSN", "manual"),
    ("Hillshire Farm", "TSN", "manual"),
    ("Ball Park", "TSN", "manual"),

    # Starbucks
    ("Starbucks", "SBUX", "manual"),
]


class Command(BaseCommand):
    help = "Seed brand-to-company mappings for barcode scanning"

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        not_found = set()

        for brand_name, ticker, source in BRAND_MAPPINGS:
            company = Company.objects.filter(ticker=ticker).first()
            if not company:
                # Also try by name
                company = Company.objects.filter(name__iexact=ticker).first()
            if not company:
                not_found.add(ticker)
                skipped += 1
                continue

            _, was_created = BrandMapping.objects.update_or_create(
                brand_name_normalized=brand_name.lower().strip(),
                company=company,
                defaults={
                    'brand_name': brand_name,
                    'source': source,
                    'confidence': 1.0,
                }
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} brand mappings, skipped {skipped}"
        ))
        if not_found:
            self.stdout.write(self.style.WARNING(
                f"Companies not in DB (add them first): {', '.join(sorted(not_found))}"
            ))
