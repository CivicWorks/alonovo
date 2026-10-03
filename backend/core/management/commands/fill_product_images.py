"""Fill Product.image_url (and barcode, when empty) from the Open *Facts databases.

Searches by product name, accepts a hit only when its brands field contains the
product's brand, and stores the front-of-pack image. Open Food Facts allows about
10 search requests a minute, so requests are spaced out.

Usage:
    python manage.py fill_product_images            # products with no image yet
    python manage.py fill_product_images --dry-run --limit 5
"""
import time

import requests
from django.core.management.base import BaseCommand

from core.barcode_providers import REQUEST_TIMEOUT, USER_AGENT
from core.models import Product

FOOD = 'https://world.openfoodfacts.org'
BEAUTY = 'https://world.openbeautyfacts.org'
PET = 'https://world.openpetfoodfacts.org'
PRODUCTS = 'https://world.openproductsfacts.org'

# Which database to search for each product category
HOST_BY_CATEGORY = {
    'personal_care': BEAUTY,
    'pet': PET,
    'cleaning': PRODUCTS,
    'paper': PRODUCTS,
    'batteries': PRODUCTS,
}

SECONDS_BETWEEN_REQUESTS = 7
RETRY_WAITS = [30, 90]  # seconds to wait before retrying a failed search


def brand_matches(product, hit):
    brand = product.brand_name.lower().replace("'", '')
    brands = (hit.get('brands') or '').lower().replace("'", '')
    return brand in brands


class Command(BaseCommand):
    help = 'Fill product images and barcodes from Open Food Facts and related databases'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--limit', type=int, help='Stop after this many products')

    def handle(self, *args, **opts):
        products = list(Product.objects.filter(image_url__isnull=True).order_by('id')[:opts['limit']])
        found = 0
        for product in products:
            host = HOST_BY_CATEGORY.get(product.category, FOOD)
            hits = self.search(host, product.name)
            if hits is None:
                self.stderr.write(f'{product.id} {product.name}: search failed')
                time.sleep(SECONDS_BETWEEN_REQUESTS)
                continue

            # Products are US shelf items: prefer a US listing of the same brand
            hits.sort(key=lambda h: 'en:united-states' not in (h.get('countries_tags') or []))
            hit = next((h for h in hits if h.get('image_front_small_url') and brand_matches(product, h)), None)
            if hit:
                found += 1
                self.stdout.write(f'{product.id} {product.name} -> {hit.get("product_name")} [{hit.get("code")}]')
                if not opts['dry_run']:
                    product.image_url = hit['image_front_small_url']
                    if not product.barcode and hit.get('code'):
                        product.barcode = hit['code']
                    product.save(update_fields=['image_url', 'barcode', 'updated_at'])
            else:
                self.stdout.write(f'{product.id} {product.name}: no match')
            time.sleep(SECONDS_BETWEEN_REQUESTS)

        self.stdout.write(self.style.SUCCESS(f'{found} of {len(products)} matched'))

    def search(self, host, name):
        for wait in [0, *RETRY_WAITS]:
            time.sleep(wait)
            try:
                resp = requests.get(
                    f'{host}/cgi/search.pl',
                    params={
                        'search_terms': name,
                        'search_simple': 1,
                        'json': 1,
                        'page_size': 10,
                        'fields': 'code,product_name,brands,image_front_small_url,countries_tags',
                    },
                    headers={'User-Agent': USER_AGENT},
                    timeout=REQUEST_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json().get('products', [])
            except (requests.RequestException, ValueError) as e:
                self.stderr.write(f'{name}: {e}')
        return None
