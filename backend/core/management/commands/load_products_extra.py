"""Load additional products to bring total to 300+."""
from django.core.management.base import BaseCommand
from core.models import Company, Product

NEW_COMPANIES = [
    ("Starbucks", "SBUX", "Consumer Staples"),
    ("Grupo Bimbo", None, "Consumer Staples"),
    ("Welch's", None, "Consumer Staples"),
    ("Ocean Spray Cranberries", None, "Consumer Staples"),
    ("Sun-Maid", None, "Consumer Staples"),
    ("Blue Diamond Growers", None, "Consumer Staples"),
    ("Diamond Foods", None, "Consumer Staples"),
    ("Wonderful Company", None, "Consumer Staples"),
    ("Simply Orange", None, "Consumer Staples"),
    ("Amy's Kitchen", None, "Consumer Staples"),
    ("Annie Chun's", None, "Consumer Staples"),
    ("Bob's Red Mill", None, "Consumer Staples"),
    ("Chosen Foods", None, "Consumer Staples"),
    ("Siete Foods", None, "Consumer Staples"),
    ("Celsius Holdings", "CELH", "Consumer Staples"),
    ("Vita Coco", None, "Consumer Staples"),
    ("La Croix", None, "Consumer Staples"),
    ("National Beverage Corp", "FIZZ", "Consumer Staples"),
    ("White Claw", None, "Consumer Staples"),
    ("Mark Anthony Brands", None, "Consumer Staples"),
    ("Smithfield Foods", None, "Consumer Staples"),
    ("JBS USA", None, "Consumer Staples"),
    ("Cargill", None, "Consumer Staples"),
    ("Quaker Oats", None, "Consumer Staples"),
    ("Old El Paso", None, "Consumer Staples"),
    ("Green Mountain Coffee", None, "Consumer Staples"),
    ("Kodiak Cakes", None, "Consumer Staples"),
    ("Rxbar", None, "Consumer Staples"),
    ("Banza", None, "Consumer Staples"),
    ("Rao's Homemade", None, "Consumer Staples"),
    ("Primal Kitchen", None, "Consumer Staples"),
    ("Sir Kensington's", None, "Consumer Staples"),
    ("Justin's", None, "Consumer Staples"),
    ("SunButter", None, "Consumer Staples"),
    ("Kettle Brand", None, "Consumer Staples"),
    ("Cape Cod Chips", None, "Consumer Staples"),
    ("Utz Quality Foods", None, "Consumer Staples"),
    ("Snyder's of Hanover", None, "Consumer Staples"),
    ("Late July", None, "Consumer Staples"),
    ("Enjoy Life Foods", None, "Consumer Staples"),
    ("Hu Kitchen", None, "Consumer Staples"),
    ("Lily's Sweets", None, "Consumer Staples"),
    ("Endangered Species Chocolate", None, "Consumer Staples"),
    ("Alter Eco", None, "Consumer Staples"),
    ("Horizon Organic", None, "Consumer Staples"),
    ("Happy Egg Co", None, "Consumer Staples"),
    ("Nellie's Free Range", None, "Consumer Staples"),
    ("Simple Truth", None, "Consumer Staples"),
    ("365 by Whole Foods", None, "Consumer Staples"),
    ("Trader Joe's", None, "Consumer Staples"),
]

PRODUCTS = [
    # === MORE CEREAL & BREAKFAST ===
    ("Quaker Oats Old Fashioned", "Quaker", "PepsiCo", "cereal", 5.29),
    ("Quaker Instant Oatmeal Variety", "Quaker", "PepsiCo", "cereal", 5.49),
    ("Bob's Red Mill Rolled Oats", "Bob's Red Mill", "Bob's Red Mill", "cereal", 6.49),
    ("Kodiak Cakes Power Cakes Mix", "Kodiak Cakes", "Kodiak Cakes", "cereal", 5.99),
    ("Special K Original", "Special K", "Kellogg's", "cereal", 5.29),
    ("Grape-Nuts Flakes", "Grape-Nuts", "Post Holdings", "cereal", 5.49),
    ("Great Grains", "Great Grains", "Post Holdings", "cereal", 4.99),
    ("Kashi GoLean", "Kashi", "Kellogg's", "cereal", 5.49),

    # === MORE SNACKS ===
    ("Kettle Brand Sea Salt Chips", "Kettle Brand", "Campbell Soup", "snacks", 4.99),
    ("Cape Cod Original Chips", "Cape Cod", "Campbell Soup", "snacks", 4.99),
    ("Utz Original Chips", "Utz", "Utz Quality Foods", "snacks", 4.49),
    ("Snyder's Pretzels", "Snyder's", "Campbell Soup", "snacks", 3.99),
    ("Late July Sea Salt Tortilla Chips", "Late July", "Campbell Soup", "snacks", 4.49),
    ("Siete Grain Free Tortilla Chips", "Siete", "PepsiCo", "snacks", 5.99),
    ("RXBAR Chocolate Sea Salt", "RXBAR", "Kellogg's", "snacks", 2.49),
    ("Larabar Cashew Cookie", "Larabar", "General Mills", "snacks", 1.79),
    ("PopCorners Sea Salt", "PopCorners", "PepsiCo", "snacks", 4.49),
    ("Pirate's Booty Aged White Cheddar", "Pirate's Booty", "The Hershey Company", "snacks", 4.99),
    ("Hu Dark Chocolate Bar", "Hu", "Mondelez International", "snacks", 5.49),
    ("Lily's Dark Chocolate Chips", "Lily's", "The Hershey Company", "snacks", 5.49),
    ("Endangered Species Dark Chocolate", "Endangered Species", "Endangered Species Chocolate", "snacks", 3.99),
    ("Enjoy Life Chocolate Chips", "Enjoy Life", "Mondelez International", "snacks", 5.49),
    ("Blue Diamond Almonds", "Blue Diamond", "Blue Diamond Growers", "snacks", 5.99),
    ("Wonderful Pistachios", "Wonderful", "Wonderful Company", "snacks", 7.99),
    ("Sun-Maid Raisins", "Sun-Maid", "Sun-Maid", "snacks", 4.49),
    ("Welch's Fruit Snacks", "Welch's", "Welch's", "snacks", 4.99),

    # === MORE BEVERAGES ===
    ("Celsius Energy Drink", "Celsius", "Celsius Holdings", "beverages", 2.49),
    ("Vita Coco Coconut Water", "Vita Coco", "Vita Coco", "beverages", 2.99),
    ("LaCroix Sparkling Water 12pk", "LaCroix", "National Beverage Corp", "beverages", 5.49),
    ("Perrier Sparkling Water", "Perrier", "Nestlé", "beverages", 2.29),
    ("Simply Orange Juice", "Simply", "Coca-Cola", "beverages", 4.99),
    ("Honest Tea Organic", "Honest Tea", "Coca-Cola", "beverages", 2.29),
    ("Gold Peak Iced Tea", "Gold Peak", "Coca-Cola", "beverages", 2.49),
    ("V8 Original Vegetable Juice", "V8", "Campbell Soup", "beverages", 4.49),
    ("Ocean Spray Cranberry Juice", "Ocean Spray", "Ocean Spray", "beverages", 4.29),
    ("Welch's Grape Juice", "Welch's", "Welch's", "beverages", 4.49),
    ("Arizona Iced Tea", "Arizona", "Arizona Beverages", "beverages", 1.29),
    ("Starbucks Frappuccino Bottle", "Starbucks", "PepsiCo", "beverages", 3.29),
    ("Body Armor Sports Drink", "Body Armor", "Coca-Cola", "beverages", 2.49),
    ("Powerade Sports Drink", "Powerade", "Coca-Cola", "beverages", 1.99),

    # === MORE DAIRY ===
    ("Oikos Greek Yogurt", "Oikos", "Danone", "dairy", 1.49),
    ("Siggi's Icelandic Yogurt", "Siggi's", "Lactalis", "dairy", 2.29),
    ("Fage Total Greek Yogurt", "Fage", "Fage", "dairy", 2.49),
    ("Happy Egg Co Free Range Eggs", "Happy Egg", "Happy Egg Co", "dairy", 5.99),
    ("Nellie's Free Range Eggs", "Nellie's", "Nellie's Free Range", "dairy", 6.49),
    ("Cabot Sharp Cheddar", "Cabot", "Cabot Creamery", "dairy", 5.49),
    ("Laughing Cow Cheese Wedges", "Laughing Cow", "Lactalis", "dairy", 4.49),
    ("Babybel Mini Cheese", "Babybel", "Lactalis", "dairy", 5.99),
    ("Silk Almond Milk", "Silk", "Danone", "dairy", 4.49),
    ("Almond Breeze Almond Milk", "Almond Breeze", "Blue Diamond Growers", "dairy", 3.99),

    # === MORE BREAD ===
    ("King's Hawaiian Rolls", "King's Hawaiian", "King's Hawaiian", "bread", 4.99),
    ("Mission Flour Tortillas", "Mission", "Bimbo Bakeries", "bread", 3.99),
    ("Old El Paso Taco Shells", "Old El Paso", "General Mills", "bread", 2.49),
    ("Banza Chickpea Pasta", "Banza", "Banza", "bread", 3.99),

    # === MORE MEAT & PROTEIN ===
    ("Smithfield Bacon", "Smithfield", "Smithfield Foods", "meat", 6.99),
    ("Nathan's Famous Hot Dogs", "Nathan's", "Smithfield Foods", "meat", 5.99),
    ("Foster Farms Chicken", "Foster Farms", "Foster Farms", "meat", 8.49),
    ("Boar's Head Turkey Breast", "Boar's Head", "Boar's Head", "meat", 9.99),
    ("Land O'Frost Premium Lunch Meat", "Land O'Frost", "Land O'Frost", "meat", 4.99),
    ("Hebrew National Hot Dogs", "Hebrew National", "Conagra Brands", "meat", 5.49),

    # === MORE FROZEN ===
    ("Amy's Organic Burritos", "Amy's", "Amy's Kitchen", "frozen", 3.99),
    ("Trader Joe's Mandarin Chicken", "Trader Joe's", "Trader Joe's", "frozen", 4.99),
    ("El Monterey Burritos", "El Monterey", "Ruiz Foods", "frozen", 5.49),
    ("TGI Friday's Appetizers", "TGI Friday's", "Conagra Brands", "frozen", 7.99),
    ("Ore-Ida French Fries", "Ore-Ida", "Kraft Heinz", "frozen", 4.99),
    ("Häagen-Dazs Bars", "Häagen-Dazs", "Nestlé", "frozen", 5.99),
    ("Magnum Ice Cream Bars", "Magnum", "Unilever", "frozen", 5.99),
    ("Halo Top Ice Cream", "Halo Top", "Halo Top", "frozen", 5.49),

    # === MORE CANNED & PANTRY ===
    ("Rao's Marinara Sauce", "Rao's", "Campbell Soup", "canned", 8.49),
    ("Classico Pasta Sauce", "Classico", "Kraft Heinz", "canned", 3.49),
    ("Pace Salsa", "Pace", "Campbell Soup", "canned", 3.99),
    ("Tostitos Salsa", "Tostitos", "PepsiCo", "canned", 4.49),
    ("Old El Paso Refried Beans", "Old El Paso", "General Mills", "canned", 1.79),
    ("Manwich Sloppy Joe Sauce", "Manwich", "Conagra Brands", "canned", 1.99),
    ("Hormel Chili", "Hormel", "Hormel Foods", "canned", 2.99),
    ("Uncle Ben's Ready Rice", "Uncle Ben's", "Mars Inc.", "canned", 2.99),
    ("Minute Rice White", "Minute Rice", "Kraft Heinz", "canned", 3.49),
    ("Near East Rice Pilaf", "Near East", "PepsiCo", "canned", 2.49),

    # === MORE CONDIMENTS ===
    ("Primal Kitchen Avocado Mayo", "Primal Kitchen", "Kraft Heinz", "condiments", 9.99),
    ("Sir Kensington's Ketchup", "Sir Kensington's", "Unilever", "condiments", 5.49),
    ("Justin's Almond Butter", "Justin's", "Hormel Foods", "condiments", 8.99),
    ("SunButter Sunflower Butter", "SunButter", "SunButter", "condiments", 6.99),
    ("Cholula Hot Sauce", "Cholula", "McCormick & Company", "condiments", 3.99),
    ("Stubb's BBQ Sauce", "Stubb's", "McCormick & Company", "condiments", 3.99),
    ("Kraft Ranch Dressing", "Kraft", "Kraft Heinz", "condiments", 4.49),
    ("Wish-Bone Italian Dressing", "Wish-Bone", "Conagra Brands", "condiments", 3.49),
    ("Ken's Steak House Dressing", "Ken's", "Ken's Foods", "condiments", 3.99),

    # === MORE CLEANING ===
    ("Persil Laundry Detergent", "Persil", "Henkel", "cleaning", 12.99),
    ("Purex Laundry Detergent", "Purex", "Henkel", "cleaning", 7.99),
    ("Finish Dishwasher Tabs", "Finish", "Reckitt Benckiser", "cleaning", 13.99),
    ("Scrub Daddy Sponge", "Scrub Daddy", "Scrub Daddy", "cleaning", 4.49),
    ("S.O.S Steel Wool Pads", "S.O.S", "Clorox", "cleaning", 3.49),
    ("Febreze Air Freshener", "Febreze", "Procter & Gamble", "cleaning", 5.99),
    ("Glade Air Freshener", "Glade", "S.C. Johnson", "cleaning", 4.49),
    ("Pledge Furniture Polish", "Pledge", "S.C. Johnson", "cleaning", 5.99),

    # === MORE PERSONAL CARE ===
    ("Cetaphil Face Cleanser", "Cetaphil", "Galderma", "personal_care", 11.99),
    ("CeraVe Moisturizing Cream", "CeraVe", "L'Oréal", "personal_care", 16.99),
    ("Aquaphor Healing Ointment", "Aquaphor", "Henkel", "personal_care", 7.99),
    ("Gold Bond Lotion", "Gold Bond", "Sanofi", "personal_care", 9.99),
    ("Burt's Bees Lip Balm", "Burt's Bees", "Clorox", "personal_care", 4.49),
    ("Carmex Lip Balm", "Carmex", "Carma Labs", "personal_care", 2.49),
    ("Chapstick Original", "Chapstick", "Haleon", "personal_care", 2.99),
    ("Tom's of Maine Toothpaste", "Tom's of Maine", "Colgate-Palmolive", "personal_care", 5.99),
    ("Arm & Hammer Toothpaste", "Arm & Hammer", "Church & Dwight", "personal_care", 3.99),
    ("Oral-B Toothbrush", "Oral-B", "Procter & Gamble", "personal_care", 6.99),
    ("Eucerin Moisturizer", "Eucerin", "Henkel", "personal_care", 12.99),
]

EXTRA_COMPANIES = [
    ("Arizona Beverages", None, "Consumer Staples"),
    ("Fage", None, "Consumer Staples"),
    ("Cabot Creamery", None, "Consumer Staples"),
    ("King's Hawaiian", None, "Consumer Staples"),
    ("Foster Farms", None, "Consumer Staples"),
    ("Boar's Head", None, "Consumer Staples"),
    ("Land O'Frost", None, "Consumer Staples"),
    ("Ruiz Foods", None, "Consumer Staples"),
    ("Halo Top", None, "Consumer Staples"),
    ("Ken's Foods", None, "Consumer Staples"),
    ("Scrub Daddy", None, "Consumer Staples"),
    ("Galderma", None, "Consumer Staples"),
    ("Sanofi", "SNY", "Healthcare"),
    ("Carma Labs", None, "Consumer Staples"),
    ("Haleon", "HLN", "Consumer Staples"),
]


class Command(BaseCommand):
    help = "Load additional products to reach 300+"

    def handle(self, *args, **options):
        # Create new companies
        all_new = NEW_COMPANIES + EXTRA_COMPANIES
        created = 0
        for name, ticker, sector in all_new:
            obj, was_created = Company.objects.get_or_create(
                name=name,
                defaults={
                    'uri': f"https://alonovo.cooperation.org/company/{name.lower().replace(' ', '-').replace('.', '').replace('&', 'and')}",
                    'ticker': ticker or '',
                    'sector': sector,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f"  Created company: {name}")

        company_map = {c.name: c for c in Company.objects.all()}

        loaded = 0
        skipped = 0
        errors = []
        for product_name, brand_name, company_name, category, price in PRODUCTS:
            company = company_map.get(company_name)
            if not company:
                errors.append(f"Company not found: '{company_name}' (for {product_name})")
                continue
            _, was_created = Product.objects.get_or_create(
                name=product_name,
                company=company,
                defaults={
                    'brand_name': brand_name,
                    'category': category,
                    'typical_price': price,
                    'source': 'top_grocery_products_2026_extra',
                }
            )
            if was_created:
                loaded += 1
            else:
                skipped += 1

        total = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {loaded} new products loaded, {skipped} already existed, "
            f"{created} companies created. Total products: {total}"
        ))
        if errors:
            self.stdout.write(self.style.WARNING(f"\n{len(errors)} errors:"))
            for e in errors:
                self.stdout.write(f"  {e}")

        from django.db.models import Count
        self.stdout.write("\nProducts by category:")
        for c in Product.objects.values('category').annotate(count=Count('id')).order_by('-count'):
            self.stdout.write(f"  {c['category']:20s} {c['count']}")
