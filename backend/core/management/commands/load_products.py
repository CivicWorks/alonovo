"""Load top ~250 grocery products with brand→company mapping and category."""
from django.core.management.base import BaseCommand
from core.models import Company, Product

# Companies that may need to be created (name, ticker, sector)
NEW_COMPANIES = [
    ("General Mills", "GIS", "Consumer Staples"),
    ("Kellogg's", "K", "Consumer Staples"),
    ("Mars Inc.", None, "Consumer Staples"),
    ("Mondelez International", "MDLZ", "Consumer Staples"),
    ("Campbell Soup", "CPB", "Consumer Staples"),
    ("J.M. Smucker", "SJM", "Consumer Staples"),
    ("Hormel Foods", "HRL", "Consumer Staples"),
    ("Del Monte Foods", None, "Consumer Staples"),
    ("Ocean Spray", None, "Consumer Staples"),
    ("Chobani", None, "Consumer Staples"),
    ("Lactalis", None, "Consumer Staples"),
    ("Dole", "DOLE", "Consumer Staples"),
    ("Keurig Dr Pepper", "KDP", "Consumer Staples"),
    ("TreeTop", None, "Consumer Staples"),
    ("Bob Evans", None, "Consumer Staples"),
    ("Pilgrim's Pride", "PPC", "Consumer Staples"),
    ("Perdue Farms", None, "Consumer Staples"),
    ("Land O'Lakes", None, "Consumer Staples"),
    ("Sargento", None, "Consumer Staples"),
    ("Tillamook", None, "Consumer Staples"),
    ("Bimbo Bakeries", None, "Consumer Staples"),
    ("Flowers Foods", "FLO", "Consumer Staples"),
    ("Frito-Lay", None, "Consumer Staples"),  # subsidiary of PepsiCo, but brand recognition
    ("Post Holdings", "POST", "Consumer Staples"),
    ("McCormick & Company", "MKC", "Consumer Staples"),
    ("Bumble Bee Foods", None, "Consumer Staples"),
    ("Thai Union Group", None, "Consumer Staples"),  # Chicken of the Sea
    ("TreeHouse Foods", "THS", "Consumer Staples"),
    ("Goya Foods", None, "Consumer Staples"),
    ("B&G Foods", "BGS", "Consumer Staples"),
    ("Kikkoman", None, "Consumer Staples"),
    ("Annie's Homegrown", None, "Consumer Staples"),  # owned by General Mills
    ("Newman's Own", None, "Consumer Staples"),
    ("Clif Bar", None, "Consumer Staples"),  # owned by Mondelez
    ("KIND Snacks", None, "Consumer Staples"),  # owned by Mars
    ("Nature Valley", None, "Consumer Staples"),  # owned by General Mills
    ("Stonyfield Farm", None, "Consumer Staples"),  # owned by Lactalis
    ("Applegate Farms", None, "Consumer Staples"),  # owned by Hormel
    ("Oatly", "OTLY", "Consumer Staples"),
    ("Beyond Meat", "BYND", "Consumer Staples"),
    ("Impossible Foods", None, "Consumer Staples"),
    ("Seventh Generation", None, "Consumer Staples"),  # owned by Unilever
    ("Dr. Bronner's", None, "Consumer Staples"),
    ("Method Products", None, "Consumer Staples"),  # owned by S.C. Johnson
    ("Energizer Holdings", "ENR", "Consumer Staples"),
    ("Spectrum Brands", "SPB", "Consumer Staples"),
    ("Georgia-Pacific", None, "Consumer Staples"),  # Koch Industries
    ("Kimberly-Clark", "KMB", "Consumer Staples"),
    ("Anheuser-Busch InBev", "BUD", "Consumer Staples"),
    ("Constellation Brands", "STZ", "Consumer Staples"),
    ("Brown-Forman", "BF.B", "Consumer Staples"),
    ("Diageo", "DEO", "Consumer Staples"),
    ("Boston Beer Company", "SAM", "Consumer Staples"),
]

# (product_name, brand_name, company_name, category, typical_price)
# company_name must match either existing DB name or NEW_COMPANIES name
PRODUCTS = [
    # === CEREAL ===
    ("Cheerios Original", "Cheerios", "General Mills", "cereal", 5.49),
    ("Honey Nut Cheerios", "Cheerios", "General Mills", "cereal", 5.49),
    ("Lucky Charms", "Lucky Charms", "General Mills", "cereal", 5.29),
    ("Cinnamon Toast Crunch", "Cinnamon Toast Crunch", "General Mills", "cereal", 5.29),
    ("Frosted Flakes", "Frosted Flakes", "Kellogg's", "cereal", 5.19),
    ("Froot Loops", "Froot Loops", "Kellogg's", "cereal", 5.19),
    ("Raisin Bran", "Raisin Bran", "Kellogg's", "cereal", 4.79),
    ("Rice Krispies", "Rice Krispies", "Kellogg's", "cereal", 5.29),
    ("Frosted Mini-Wheats", "Mini-Wheats", "Kellogg's", "cereal", 5.49),
    ("Grape-Nuts", "Grape-Nuts", "Post Holdings", "cereal", 5.99),
    ("Honey Bunches of Oats", "Honey Bunches of Oats", "Post Holdings", "cereal", 4.99),
    ("Life Cereal", "Life", "PepsiCo", "cereal", 4.99),
    ("Cap'n Crunch", "Cap'n Crunch", "PepsiCo", "cereal", 4.79),
    ("Cocoa Puffs", "Cocoa Puffs", "General Mills", "cereal", 5.29),

    # === SNACKS / CHIPS ===
    ("Lay's Classic Potato Chips", "Lay's", "PepsiCo", "snacks", 4.99),
    ("Doritos Nacho Cheese", "Doritos", "PepsiCo", "snacks", 5.49),
    ("Cheetos Crunchy", "Cheetos", "PepsiCo", "snacks", 4.99),
    ("Tostitos Scoops", "Tostitos", "PepsiCo", "snacks", 5.29),
    ("Ruffles Original", "Ruffles", "PepsiCo", "snacks", 4.99),
    ("Fritos Original", "Fritos", "PepsiCo", "snacks", 4.99),
    ("SunChips Original", "SunChips", "PepsiCo", "snacks", 4.49),
    ("Pringles Original", "Pringles", "Kellogg's", "snacks", 5.79),
    ("Goldfish Crackers", "Goldfish", "Campbell Soup", "snacks", 3.99),
    ("Cheez-It Original", "Cheez-It", "Kellogg's", "snacks", 4.99),
    ("Ritz Crackers", "Ritz", "Mondelez International", "snacks", 4.49),
    ("Triscuit Original", "Triscuit", "Mondelez International", "snacks", 4.49),
    ("Wheat Thins", "Wheat Thins", "Mondelez International", "snacks", 4.49),
    ("Oreo Cookies", "Oreo", "Mondelez International", "snacks", 5.49),
    ("Chips Ahoy!", "Chips Ahoy!", "Mondelez International", "snacks", 4.99),
    ("Nutter Butter", "Nutter Butter", "Mondelez International", "snacks", 4.29),
    ("Clif Bar", "Clif Bar", "Mondelez International", "snacks", 1.79),
    ("KIND Bar Nuts & Spices", "KIND", "Mars Inc.", "snacks", 1.79),
    ("Nature Valley Granola Bar", "Nature Valley", "General Mills", "snacks", 4.29),
    ("Snickers Bar", "Snickers", "Mars Inc.", "snacks", 2.19),
    ("M&M's Peanut", "M&M's", "Mars Inc.", "snacks", 4.99),
    ("Reese's Peanut Butter Cups", "Reese's", "The Hershey Company", "snacks", 2.19),
    ("Hershey's Milk Chocolate Bar", "Hershey's", "The Hershey Company", "snacks", 2.09),
    ("Kit Kat", "Kit Kat", "The Hershey Company", "snacks", 2.09),
    ("Skittles", "Skittles", "Mars Inc.", "snacks", 1.99),
    ("Twix", "Twix", "Mars Inc.", "snacks", 2.19),
    ("SkinnyPop Popcorn", "SkinnyPop", "The Hershey Company", "snacks", 4.49),

    # === BEVERAGES (non-alcohol) ===
    ("Coca-Cola 12pk", "Coca-Cola", "Coca-Cola", "beverages", 7.99),
    ("Diet Coke 12pk", "Diet Coke", "Coca-Cola", "beverages", 7.99),
    ("Sprite 12pk", "Sprite", "Coca-Cola", "beverages", 7.99),
    ("Fanta Orange 12pk", "Fanta", "Coca-Cola", "beverages", 7.99),
    ("Minute Maid Orange Juice", "Minute Maid", "Coca-Cola", "beverages", 4.49),
    ("Dasani Water 24pk", "Dasani", "Coca-Cola", "beverages", 4.99),
    ("Smartwater 1L", "Smartwater", "Coca-Cola", "beverages", 2.49),
    ("Pepsi 12pk", "Pepsi", "PepsiCo", "beverages", 7.99),
    ("Mountain Dew 12pk", "Mountain Dew", "PepsiCo", "beverages", 7.99),
    ("Gatorade Original", "Gatorade", "PepsiCo", "beverages", 2.29),
    ("Tropicana Orange Juice", "Tropicana", "PepsiCo", "beverages", 4.99),
    ("Aquafina Water 24pk", "Aquafina", "PepsiCo", "beverages", 4.49),
    ("Nestle Pure Life Water 24pk", "Nestle Pure Life", "Nestlé", "beverages", 4.99),
    ("Poland Spring Water 24pk", "Poland Spring", "Nestlé", "beverages", 5.49),
    ("S.Pellegrino Sparkling Water", "S.Pellegrino", "Nestlé", "beverages", 2.49),
    ("Dr Pepper 12pk", "Dr Pepper", "Keurig Dr Pepper", "beverages", 7.49),
    ("7UP 12pk", "7UP", "Keurig Dr Pepper", "beverages", 7.49),
    ("Snapple Iced Tea", "Snapple", "Keurig Dr Pepper", "beverages", 2.29),
    ("Monster Energy", "Monster", "Monster Beverage", "beverages", 2.99),
    ("Red Bull", "Red Bull", "Monster Beverage", "beverages", 3.49),
    ("Oatly Oat Milk", "Oatly", "Oatly", "beverages", 5.49),
    ("Folgers Coffee", "Folgers", "J.M. Smucker", "beverages", 9.99),
    ("Maxwell House Coffee", "Maxwell House", "Kraft Heinz", "beverages", 8.99),
    ("Starbucks Ground Coffee", "Starbucks", "Nestlé", "beverages", 10.99),
    ("Keurig K-Cups Variety", "Keurig", "Keurig Dr Pepper", "beverages", 12.99),
    ("Lipton Iced Tea Mix", "Lipton", "Unilever", "beverages", 4.99),

    # === DAIRY & EGGS ===
    ("Chobani Greek Yogurt", "Chobani", "Chobani", "dairy", 1.69),
    ("Yoplait Original Yogurt", "Yoplait", "General Mills", "dairy", 0.89),
    ("Dannon Activia", "Dannon", "Danone", "dairy", 5.49),
    ("Stonyfield Organic Yogurt", "Stonyfield", "Lactalis", "dairy", 1.49),
    ("Philadelphia Cream Cheese", "Philadelphia", "Kraft Heinz", "dairy", 4.49),
    ("Kraft Singles", "Kraft", "Kraft Heinz", "dairy", 4.99),
    ("Sargento Shredded Cheese", "Sargento", "Sargento", "dairy", 4.49),
    ("Tillamook Cheddar", "Tillamook", "Tillamook", "dairy", 5.99),
    ("Land O'Lakes Butter", "Land O'Lakes", "Land O'Lakes", "dairy", 5.49),
    ("Horizon Organic Milk", "Horizon", "Danone", "dairy", 6.49),
    ("Organic Valley Milk", "Organic Valley", "Organic Valley", "dairy", 6.99),
    ("Eggland's Best Eggs 12ct", "Eggland's Best", "Eggland's Best", "dairy", 4.49),
    ("Vital Farms Pasture-Raised Eggs", "Vital Farms", "Vital Farms", "dairy", 7.99),

    # === BREAD & BAKERY ===
    ("Wonder Bread White", "Wonder Bread", "Flowers Foods", "bread", 3.99),
    ("Nature's Own Whole Wheat", "Nature's Own", "Flowers Foods", "bread", 4.49),
    ("Dave's Killer Bread", "Dave's Killer Bread", "Flowers Foods", "bread", 5.99),
    ("Sara Lee Artesano", "Sara Lee", "Bimbo Bakeries", "bread", 4.29),
    ("Arnold Whole Grains", "Arnold", "Bimbo Bakeries", "bread", 5.49),
    ("Thomas' English Muffins", "Thomas'", "Bimbo Bakeries", "bread", 4.99),
    ("Pepperidge Farm Farmhouse", "Pepperidge Farm", "Campbell Soup", "bread", 5.49),

    # === MEAT & PROTEIN ===
    ("Tyson Chicken Breast", "Tyson", "Tyson Foods", "meat", 8.29),
    ("Tyson Chicken Nuggets", "Tyson", "Tyson Foods", "meat", 7.99),
    ("Perdue Chicken Breast", "Perdue", "Perdue Farms", "meat", 8.49),
    ("Pilgrim's Pride Chicken", "Pilgrim's", "Pilgrim's Pride", "meat", 7.49),
    ("Hillshire Farm Lunch Meat", "Hillshire Farm", "Tyson Foods", "meat", 5.49),
    ("Oscar Mayer Bologna", "Oscar Mayer", "Kraft Heinz", "meat", 4.29),
    ("Oscar Mayer Hot Dogs", "Oscar Mayer", "Kraft Heinz", "meat", 4.99),
    ("Ball Park Franks", "Ball Park", "Tyson Foods", "meat", 4.99),
    ("Hormel Black Label Bacon", "Hormel", "Hormel Foods", "meat", 7.49),
    ("Jimmy Dean Sausage", "Jimmy Dean", "Tyson Foods", "meat", 5.49),
    ("Applegate Naturals Turkey", "Applegate", "Hormel Foods", "meat", 6.99),
    ("Beyond Burger 2pk", "Beyond Meat", "Beyond Meat", "meat", 6.99),
    ("Impossible Burger", "Impossible", "Impossible Foods", "meat", 7.49),
    ("SPAM Classic", "SPAM", "Hormel Foods", "meat", 3.99),
    ("Jennie-O Ground Turkey", "Jennie-O", "Hormel Foods", "meat", 5.49),
    ("Bob Evans Mashed Potatoes", "Bob Evans", "Bob Evans", "meat", 4.49),

    # === FROZEN ===
    ("DiGiorno Rising Crust Pizza", "DiGiorno", "Nestlé", "frozen", 7.49),
    ("Stouffer's Lasagna", "Stouffer's", "Nestlé", "frozen", 4.29),
    ("Hot Pockets", "Hot Pockets", "Nestlé", "frozen", 3.49),
    ("Lean Cuisine Cafe Steamers", "Lean Cuisine", "Nestlé", "frozen", 3.99),
    ("Tombstone Pizza", "Tombstone", "Nestlé", "frozen", 5.99),
    ("Ben & Jerry's Ice Cream Pint", "Ben & Jerry's", "Unilever", "frozen", 5.99),
    ("Haagen-Dazs Ice Cream Pint", "Haagen-Dazs", "Nestlé", "frozen", 5.99),
    ("Breyers Ice Cream", "Breyers", "Unilever", "frozen", 5.49),
    ("Talenti Gelato", "Talenti", "Unilever", "frozen", 5.99),
    ("Eggo Waffles", "Eggo", "Kellogg's", "frozen", 4.29),
    ("Banquet Frozen Meals", "Banquet", "Conagra Brands", "frozen", 1.99),
    ("Marie Callender's Pot Pie", "Marie Callender's", "Conagra Brands", "frozen", 3.99),
    ("Healthy Choice Power Bowls", "Healthy Choice", "Conagra Brands", "frozen", 4.29),
    ("Birds Eye Steamfresh Veggies", "Birds Eye", "Conagra Brands", "frozen", 3.29),
    ("Green Giant Frozen Veggies", "Green Giant", "B&G Foods", "frozen", 2.99),
    ("Totino's Pizza Rolls", "Totino's", "General Mills", "frozen", 4.49),
    ("Pillsbury Frozen Biscuits", "Pillsbury", "General Mills", "frozen", 3.99),

    # === CANNED & PANTRY ===
    ("Campbell's Condensed Tomato Soup", "Campbell's", "Campbell Soup", "canned", 1.79),
    ("Campbell's Chunky Soup", "Campbell's", "Campbell Soup", "canned", 3.29),
    ("Progresso Soup", "Progresso", "General Mills", "canned", 2.99),
    ("SpaghettiOs", "SpaghettiOs", "Campbell Soup", "canned", 1.49),
    ("Chef Boyardee Ravioli", "Chef Boyardee", "Conagra Brands", "canned", 1.69),
    ("Chicken of the Sea Tuna", "Chicken of the Sea", "Thai Union Group", "canned", 1.49),
    ("Bumble Bee Tuna", "Bumble Bee", "Bumble Bee Foods", "canned", 1.59),
    ("StarKist Tuna Pouch", "StarKist", "Thai Union Group", "canned", 1.79),
    ("Bush's Baked Beans", "Bush's", "Bush Brothers", "canned", 2.99),
    ("Goya Black Beans", "Goya", "Goya Foods", "canned", 1.29),
    ("Del Monte Canned Fruit", "Del Monte", "Del Monte Foods", "canned", 2.49),
    ("Dole Pineapple Chunks", "Dole", "Dole", "canned", 2.29),
    ("Hunt's Tomato Sauce", "Hunt's", "Conagra Brands", "canned", 1.29),
    ("Ro-Tel Diced Tomatoes", "Ro-Tel", "Conagra Brands", "canned", 1.49),
    ("Prego Pasta Sauce", "Prego", "Campbell Soup", "canned", 3.49),
    ("Ragu Pasta Sauce", "Ragu", "Kraft Heinz", "canned", 3.29),
    ("Barilla Pasta", "Barilla", "Barilla", "canned", 1.99),
    ("Kraft Mac & Cheese", "Kraft", "Kraft Heinz", "canned", 1.49),
    ("Annie's Mac & Cheese", "Annie's", "General Mills", "canned", 2.49),
    ("Velveeta Shells & Cheese", "Velveeta", "Kraft Heinz", "canned", 3.99),

    # === CONDIMENTS & SAUCES ===
    ("Heinz Ketchup", "Heinz", "Kraft Heinz", "condiments", 4.99),
    ("French's Mustard", "French's", "McCormick & Company", "condiments", 2.99),
    ("Hellmann's Mayonnaise", "Hellmann's", "Unilever", "condiments", 5.99),
    ("Duke's Mayonnaise", "Duke's", "Sauer Brands", "condiments", 4.99),
    ("Hidden Valley Ranch", "Hidden Valley", "Clorox", "condiments", 4.49),
    ("Soy Vay Teriyaki", "Soy Vay", "Clorox", "condiments", 4.99),
    ("Kikkoman Soy Sauce", "Kikkoman", "Kikkoman", "condiments", 3.99),
    ("Tabasco Hot Sauce", "Tabasco", "McIlhenny Company", "condiments", 4.49),
    ("Frank's RedHot", "Frank's RedHot", "McCormick & Company", "condiments", 3.99),
    ("Sriracha (Huy Fong)", "Huy Fong Sriracha", "Huy Fong Foods", "condiments", 4.49),
    ("A1 Steak Sauce", "A1", "Kraft Heinz", "condiments", 4.99),
    ("Sweet Baby Ray's BBQ", "Sweet Baby Ray's", "Kraft Heinz", "condiments", 2.99),
    ("McCormick Spices", "McCormick", "McCormick & Company", "condiments", 4.99),
    ("Newman's Own Salad Dressing", "Newman's Own", "Newman's Own", "condiments", 4.49),

    # === PEANUT BUTTER & SPREADS ===
    ("Jif Peanut Butter", "Jif", "J.M. Smucker", "spreads", 4.49),
    ("Skippy Peanut Butter", "Skippy", "Hormel Foods", "spreads", 4.29),
    ("Smucker's Strawberry Jam", "Smucker's", "J.M. Smucker", "spreads", 4.49),
    ("Nutella", "Nutella", "Barilla", "spreads", 5.99),

    # === BABY & INFANT ===
    ("Gerber Baby Food Pouches", "Gerber", "Nestlé", "baby", 1.79),
    ("Enfamil Infant Formula", "Enfamil", "Reckitt Benckiser", "baby", 39.99),
    ("Similac Infant Formula", "Similac", "Abbott Laboratories", "baby", 37.99),

    # === HOUSEHOLD CLEANING ===
    ("Tide Liquid Detergent", "Tide", "Procter & Gamble", "cleaning", 12.99),
    ("Gain Liquid Detergent", "Gain", "Procter & Gamble", "cleaning", 11.99),
    ("All Free & Clear Detergent", "All", "Henkel", "cleaning", 9.99),
    ("Seventh Generation Detergent", "Seventh Generation", "Unilever", "cleaning", 13.49),
    ("Cascade Dishwasher Pods", "Cascade", "Procter & Gamble", "cleaning", 14.99),
    ("Dawn Dish Soap", "Dawn", "Procter & Gamble", "cleaning", 4.49),
    ("Palmolive Dish Soap", "Palmolive", "Colgate-Palmolive", "cleaning", 3.49),
    ("Clorox Bleach", "Clorox", "Clorox", "cleaning", 4.99),
    ("Lysol Disinfecting Spray", "Lysol", "Reckitt Benckiser", "cleaning", 6.49),
    ("Windex Glass Cleaner", "Windex", "S.C. Johnson", "cleaning", 4.99),
    ("Mr. Clean Multi-Surface", "Mr. Clean", "Procter & Gamble", "cleaning", 4.49),
    ("Pine-Sol Cleaner", "Pine-Sol", "Clorox", "cleaning", 4.99),
    ("Swiffer WetJet Pads", "Swiffer", "Procter & Gamble", "cleaning", 9.99),
    ("Method All-Purpose Cleaner", "Method", "S.C. Johnson", "cleaning", 4.99),
    ("Mrs. Meyer's Clean Day", "Mrs. Meyer's", "S.C. Johnson", "cleaning", 5.99),
    ("Dr. Bronner's Castile Soap", "Dr. Bronner's", "Dr. Bronner's", "cleaning", 12.99),
    ("OxiClean Stain Remover", "OxiClean", "Church & Dwight", "cleaning", 9.99),
    ("Arm & Hammer Baking Soda", "Arm & Hammer", "Church & Dwight", "cleaning", 1.49),

    # === PAPER & HOUSEHOLD ===
    ("Charmin Ultra Soft Toilet Paper", "Charmin", "Procter & Gamble", "paper", 12.99),
    ("Cottonelle Toilet Paper", "Cottonelle", "Kimberly-Clark", "paper", 11.99),
    ("Scott 1000 Toilet Paper", "Scott", "Kimberly-Clark", "paper", 9.99),
    ("Bounty Paper Towels", "Bounty", "Procter & Gamble", "paper", 14.99),
    ("Viva Paper Towels", "Viva", "Kimberly-Clark", "paper", 11.99),
    ("Kleenex Facial Tissue", "Kleenex", "Kimberly-Clark", "paper", 3.49),
    ("Puffs Plus Lotion", "Puffs", "Procter & Gamble", "paper", 3.99),
    ("Glad Trash Bags", "Glad", "Clorox", "paper", 9.99),
    ("Hefty Ultra Strong Trash Bags", "Hefty", "Reynolds Consumer Products", "paper", 10.99),
    ("Ziploc Bags", "Ziploc", "S.C. Johnson", "paper", 5.49),
    ("Reynolds Wrap Aluminum Foil", "Reynolds", "Reynolds Consumer Products", "paper", 6.99),
    ("Saran Wrap", "Saran", "S.C. Johnson", "paper", 4.49),

    # === PERSONAL CARE ===
    ("Colgate Total Toothpaste", "Colgate", "Colgate-Palmolive", "personal_care", 5.49),
    ("Crest 3D White Toothpaste", "Crest", "Procter & Gamble", "personal_care", 5.49),
    ("Sensodyne Toothpaste", "Sensodyne", "Henkel", "personal_care", 7.49),
    ("Listerine Mouthwash", "Listerine", "Johnson & Johnson", "personal_care", 7.99),
    ("Dove Body Wash", "Dove", "Unilever", "personal_care", 7.99),
    ("Irish Spring Bar Soap", "Irish Spring", "Colgate-Palmolive", "personal_care", 5.99),
    ("Dial Bar Soap", "Dial", "Henkel", "personal_care", 5.49),
    ("Old Spice Body Wash", "Old Spice", "Procter & Gamble", "personal_care", 7.99),
    ("Axe Body Spray", "Axe", "Unilever", "personal_care", 6.99),
    ("Head & Shoulders Shampoo", "Head & Shoulders", "Procter & Gamble", "personal_care", 8.99),
    ("Pantene Pro-V Shampoo", "Pantene", "Procter & Gamble", "personal_care", 7.99),
    ("Suave Shampoo", "Suave", "Unilever", "personal_care", 3.49),
    ("TRESemme Shampoo", "TRESemme", "Unilever", "personal_care", 5.99),
    ("Neutrogena Face Wash", "Neutrogena", "Johnson & Johnson", "personal_care", 9.99),
    ("Aveeno Daily Moisturizer", "Aveeno", "Johnson & Johnson", "personal_care", 12.99),
    ("Olay Moisturizer", "Olay", "Procter & Gamble", "personal_care", 11.99),
    ("Vaseline Lotion", "Vaseline", "Unilever", "personal_care", 7.49),
    ("Band-Aid Bandages", "Band-Aid", "Johnson & Johnson", "personal_care", 5.99),
    ("Tylenol Extra Strength", "Tylenol", "Johnson & Johnson", "personal_care", 10.99),
    ("Advil Ibuprofen", "Advil", "Pfizer Inc.", "personal_care", 10.99),
    ("Benadryl Allergy", "Benadryl", "Johnson & Johnson", "personal_care", 9.99),
    ("Zyrtec Allergy", "Zyrtec", "Johnson & Johnson", "personal_care", 24.99),
    ("Degree Deodorant", "Degree", "Unilever", "personal_care", 5.99),
    ("Secret Deodorant", "Secret", "Procter & Gamble", "personal_care", 6.99),
    ("Gillette Razors", "Gillette", "Procter & Gamble", "personal_care", 12.99),
    ("Schick Hydro Razors", "Schick", "Energizer Holdings", "personal_care", 11.99),

    # === PET ===
    ("Purina Dog Chow", "Purina", "Nestlé", "pet", 14.99),
    ("Purina Cat Chow", "Purina", "Nestlé", "pet", 12.99),
    ("Pedigree Dog Food", "Pedigree", "Mars Inc.", "pet", 12.99),
    ("Whiskas Cat Food", "Whiskas", "Mars Inc.", "pet", 1.29),
    ("Meow Mix", "Meow Mix", "J.M. Smucker", "pet", 11.99),
    ("Blue Buffalo Dog Food", "Blue Buffalo", "General Mills", "pet", 19.99),
    ("Milk-Bone Dog Treats", "Milk-Bone", "J.M. Smucker", "pet", 5.99),
    ("Greenies Dog Treats", "Greenies", "Mars Inc.", "pet", 9.99),
    ("Fancy Feast Cat Food", "Fancy Feast", "Nestlé", "pet", 1.09),
    ("Iams Dog Food", "Iams", "Mars Inc.", "pet", 16.99),

    # === BATTERIES ===
    ("Duracell AA Batteries 8pk", "Duracell", "Procter & Gamble", "batteries", 9.99),
    ("Energizer AA Batteries 8pk", "Energizer", "Energizer Holdings", "batteries", 9.49),

    # === ALCOHOL ===
    ("Budweiser 12pk", "Budweiser", "Anheuser-Busch InBev", "alcohol", 14.99),
    ("Bud Light 12pk", "Bud Light", "Anheuser-Busch InBev", "alcohol", 14.99),
    ("Coors Light 12pk", "Coors Light", "Molson Coors Beverage Company", "alcohol", 14.99),
    ("Miller Lite 12pk", "Miller Lite", "Molson Coors Beverage Company", "alcohol", 14.99),
    ("Corona Extra 12pk", "Corona", "Constellation Brands", "alcohol", 17.99),
    ("Modelo Especial 12pk", "Modelo", "Constellation Brands", "alcohol", 17.99),
    ("Samuel Adams Boston Lager 6pk", "Samuel Adams", "Boston Beer Company", "alcohol", 11.99),
    ("Jack Daniel's Whiskey 750ml", "Jack Daniel's", "Brown-Forman", "alcohol", 27.99),
    ("Smirnoff Vodka 750ml", "Smirnoff", "Diageo", "alcohol", 14.99),
    ("Johnnie Walker Black 750ml", "Johnnie Walker", "Diageo", "alcohol", 35.99),
]

# Extra companies that might be referenced but not in NEW_COMPANIES
EXTRA_COMPANIES = [
    ("Bush Brothers", None, "Consumer Staples"),
    ("Sauer Brands", None, "Consumer Staples"),
    ("McIlhenny Company", None, "Consumer Staples"),
    ("Huy Fong Foods", None, "Consumer Staples"),
    ("Reynolds Consumer Products", "REYN", "Consumer Staples"),
    ("Organic Valley", None, "Consumer Staples"),
    ("Eggland's Best", None, "Consumer Staples"),
    ("Vital Farms", "VITL", "Consumer Staples"),
]


class Command(BaseCommand):
    help = "Load top ~250 grocery products into the Product model"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
            help='Clear existing products before loading')

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing products")

        # Ensure all companies exist
        all_companies = NEW_COMPANIES + EXTRA_COMPANIES
        companies_created = 0
        for name, ticker, sector in all_companies:
            obj, created = Company.objects.get_or_create(
                name=name,
                defaults={
                    'uri': f"https://alonovo.cooperation.org/company/{name.lower().replace(' ', '-').replace('.', '').replace('&', 'and')}",
                    'ticker': ticker or '',
                    'sector': sector,
                }
            )
            if created:
                companies_created += 1
                self.stdout.write(f"  Created company: {name} ({ticker or 'private'})")

        # Build company lookup by name
        company_map = {}
        for c in Company.objects.all():
            company_map[c.name] = c
            # Also index without trailing punctuation etc
            company_map[c.name.strip()] = c

        # Load products
        loaded = 0
        skipped = 0
        errors = []
        for product_name, brand_name, company_name, category, price in PRODUCTS:
            company = company_map.get(company_name)
            if not company:
                errors.append(f"Company not found: '{company_name}' (for {product_name})")
                continue

            _, created = Product.objects.get_or_create(
                name=product_name,
                company=company,
                defaults={
                    'brand_name': brand_name,
                    'category': category,
                    'typical_price': price,
                    'source': 'top_grocery_products_2026',
                }
            )
            if created:
                loaded += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {loaded} products loaded, {skipped} already existed, "
            f"{companies_created} companies created"
        ))
        if errors:
            self.stdout.write(self.style.WARNING(f"\n{len(errors)} errors:"))
            for e in errors:
                self.stdout.write(f"  {e}")

        # Summary by category
        self.stdout.write("\nProducts by category:")
        from django.db.models import Count
        cats = Product.objects.values('category').annotate(
            count=Count('id')).order_by('-count')
        for c in cats:
            self.stdout.write(f"  {c['category']:20s} {c['count']}")
