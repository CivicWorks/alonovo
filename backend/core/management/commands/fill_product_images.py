"""Fill Product.image_url (and barcode, when empty) from the Open *Facts databases.

Searches by product name, accepts a hit only when its brands field contains the
product's brand and its name contains every word of the product's name, and stores the front-of-pack image. Food products use the Open
Food Facts search service; the other databases only offer the older search page,
which allows about 10 requests a minute, so those requests are spaced out.

Usage:
    python manage.py fill_product_images            # products with no image yet
    python manage.py fill_product_images --dry-run --limit 5
"""
import re
import time

import requests
from django.core.management.base import BaseCommand

from core.barcode_providers import REQUEST_TIMEOUT, USER_AGENT
from core.models import Product

FOOD = 'https://world.openfoodfacts.org'
FOOD_SEARCH = 'https://search.openfoodfacts.org/search'
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


# Pack sizes and filler words that shelf names carry but database names often omit
IGNORED_WORDS = {'original', 'classic', 'pk', 'ct', 'ml', 'l', 'oz'}


def tokens(text):
    words = re.findall(r"[a-z]+|[0-9]+", text.lower().replace("'", ''))
    return {w[:-1] if w.endswith('s') and len(w) > 3 else w for w in words} - IGNORED_WORDS


# A hit may add one word (a maker's name, "cereal"); more usually means another product
MAX_EXTRA_WORDS = 1


def name_matches(product, hit):
    """Every word of our product name appears in the hit's name, with at most one extra."""
    ours, theirs = tokens(product.name), tokens(hit.get('product_name') or '')
    return ours <= theirs and len(theirs - ours) <= MAX_EXTRA_WORDS


def closeness(product, hit):
    """Higher is better: the fewest extra words in the hit's name, then a US listing."""
    us = 'en:united-states' in (hit.get('countries_tags') or [])
    extra = len(tokens(hit.get('product_name') or '') - tokens(product.name))
    return (-extra, us)


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
                continue

            # Products are US shelf items: prefer a US listing of the same brand and closest name
            candidates = [h for h in hits if h.get('image_front_small_url')
                          and brand_matches(product, h) and name_matches(product, h)]
            hit = max(candidates, key=lambda h: closeness(product, h), default=None)
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
            if host != FOOD:
                time.sleep(SECONDS_BETWEEN_REQUESTS)

        self.stdout.write(self.style.SUCCESS(f'{found} of {len(products)} matched'))

    def search(self, host, name):
        """Return a list of hits with brands as a comma-separated string, or None on failure."""
        fields = 'code,product_name,brands,image_front_small_url,countries_tags'
        if host == FOOD:
            url, params = FOOD_SEARCH, {'q': name, 'page_size': 10, 'fields': fields}
        else:
            url, params = f'{host}/cgi/search.pl', {
                'search_terms': name, 'search_simple': 1, 'json': 1, 'page_size': 10, 'fields': fields}
        for wait in [0, *RETRY_WAITS]:
            time.sleep(wait)
            try:
                resp = requests.get(url, params=params, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
            except (requests.RequestException, ValueError) as e:
                self.stderr.write(f'{name}: {e}')
                continue
            hits = data.get('hits') if host == FOOD else data.get('products')
            for h in hits or []:
                if isinstance(h.get('brands'), list):
                    h['brands'] = ', '.join(h['brands'])
            return hits or []
        return None
