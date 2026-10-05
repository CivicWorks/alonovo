# Product data sources

What the shop needs per product: barcode (GTIN/UPC), name, brand, who owns the brand, category,
ingredients, nutrition, package size, image. Sources below were checked 2026-10-05.

## Products

| Source | What it has | Licence | Access | Refresh |
|---|---|---|---|---|
| USDA FoodData Central, Branded Foods | 455,458 US packaged foods in the 2026-04-30 file: GTIN/UPC, description, brand name, brand owner, category (`brandedFoodCategory`), ingredients, full nutrition, serving and package size. No images. | Public domain (CC0) | Bulk JSON/CSV zip (204 MB zipped, 3.3 GB JSON) at https://fdc.nal.usda.gov/download-datasets/ ; REST API with a free data.gov key (`DEMO_KEY` allows about 30 requests an hour) | API monthly, bulk file about every six months |
| Open Food Facts | Barcode, name, brands, category tags, labels (organic, gluten free), ingredients, nutrition, NOVA group, Nutri-Score, images. Worldwide, crowd-sourced, gaps per product. | ODbL (data), CC BY-SA (images) | Free API, no key; daily exports (CSV, JSONL, Parquet) at https://world.openfoodfacts.org/data | Continuous |
| Open Beauty Facts / Open Products Facts / Open Pet Food Facts | Same shape as Open Food Facts for personal care, household and pet products | ODbL | Same as Open Food Facts | Continuous |
| Open Prices | Shelf prices by barcode and store, with a discount flag. Thin US coverage. | ODbL | Public API, https://prices.openfoodfacts.org/api/docs | Continuous |
| Kroger Products API | Kroger's catalog: UPC, brand, images, nutrition, local price and promotions | Kroger terms, not open | OAuth app credentials, https://developer.kroger.com/ | Live |
| GS1 US Data Hub | GTIN to the company that licensed the barcode | Paid ($500+/year), 30 free lookups a day | https://www.gs1us.org/tools/gs1-us-data-hub | Brand-owner supplied |

## Brand to owner

| Source | What it has | Licence |
|---|---|---|
| USDA `brandOwner` | The US brand owner on each food record, e.g. Cheerios -> General Mills Sales Inc., Life -> The Quaker Oats Company | Public domain |
| Wikidata | Brand -> owner (P127), company -> parent (P749), with dates and references, e.g. The Quaker Oats Company -> PepsiCo | CC0 |
| SEC EDGAR 10-K Exhibit 21 | Each public company's listed subsidiaries | Public |
| OpenCorporates | Legal entities and parent relationships | Open licence, API terms apply |

A brand can have different owners by region. Cheerios is General Mills in the US (USDA `brandOwner`)
and Cereal Partners Worldwide (General Mills and Nestlé) elsewhere. Philadelphia cream cheese is
Kraft Heinz in the US (USDA `brandOwner`) and Mondelez elsewhere.

## Local producers

| Source | What it has | Access |
|---|---|---|
| Arizona DHS cottage food registrants | 8,791 home food makers (Dec 2024), with county, zip and a free-text product list | PDF, https://www.azdhs.gov/documents/preparedness/epidemiology-disease-control/food-safety-environmental-services/cottage-food-program/cottage-food-participants.pdf |
| USDA Local Food Directories | Farmers markets, CSAs, food hubs, on-farm markets by zip and radius. Markets, not vendors. | API key, https://www.usdalocalfoodportal.com/fe/datasharing/ |
| Open Food Network (US) | About 1,000 producers and their products | https://openfoodnetwork.net/ |
| Market vendor pages | e.g. Heirloom Farmers Markets (Tucson) lists vendors by type | https://www.heirloomfm.org/vendors/food-vendors/ |

## Coupons

No free source gives manufacturer coupons by product. Ibotta, Quotient/coupons.com, Fetch and
Checkout 51 have no public API. Flipp shows weekly sale prices by zip through an undocumented
endpoint. Open Prices has discounted shelf prices where people have recorded them.

## Scripts (run to refresh)

| Command | What it does |
|---|---|
| `python manage.py fill_product_images` | Product image and missing barcode from Open Food Facts and related databases |
| `python manage.py fill_product_attributes --fdc-file <USDA branded foods zip>` | Attaches the matching USDA record to `Product.attributes['usda_fdc']`, by barcode or by brand and name |

## Known gaps in the shop's data (2026-10-05)

- 345 hand-entered products. Most name a brand or line, not one product: "Cap'n Crunch", "Special K Original", "Powerade Sports Drink". Matching them to one USDA record by name picks an arbitrary flavor (Special K Original matched Raspberry; 7UP 12pk matched a candy cane pack).
- 238 of 345 have no barcode. Some barcodes point at a different item: Cap'n Crunch's is Crunch Berries; Cheerios Original's is an Australian listing.
- `product_type` is one label per product ("cold cereal" for 18 cereals), so Cheerios and Cap'n Crunch count as the same thing.
- Brands made by graded companies are missing, e.g. Cascadian Farm (General Mills), and makers we do not grade, e.g. Three Wishes.
