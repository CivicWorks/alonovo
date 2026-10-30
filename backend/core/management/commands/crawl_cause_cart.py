"""Read the public product pages of cause-cart.com, a curated marketplace of mission-driven sellers.

Starts from the store's home page, its seller list and every category, cause and impact page linked from
them; any page with a schema.org Product block is a product. Each product's name, seller, price, image,
description and categories are appended to the products file the moment they are read, and each
cause or impact page's products to the listings file, and products already in the file are skipped, so the command can be stopped and
rerun at any time. Pages from the store template's demo catalog (books, computers, video games...) are
not linked from the store and are not followed.

Usage:
    python manage.py crawl_cause_cart
"""
import html
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from core.barcode_providers import USER_AGENT

STORE = 'https://cause-cart.com/'
START_PAGES = [STORE, urljoin(STORE, 'index.php?dispatch=companies.catalog'),
               urljoin(STORE, 'shop-by-impact/'), urljoin(STORE, 'shop-by-cause/')]
DATA_DIR = os.path.join(settings.BASE_DIR, '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'cause_cart_products.jsonl')
LISTINGS_FILE = os.path.join(DATA_DIR, 'cause_cart_listings.jsonl')
SECONDS_BETWEEN_REQUESTS = 1
MAX_PAGES = 1500
# Links that are not catalog pages
SKIP = re.compile(r'/(cart|wishlist|profiles|orders|compare|login|blog|images|var|js|design)(/|$)|'
                  r'dispatch=(?!companies\.(catalog|products))|selected_section=|[?&](sort_by|features_hash|layout|items_per_page)=')
LISTING = re.compile(r'/(shop-by-impact|shop-by-cause)/([^/]+)/')


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


class Command(BaseCommand):
    help = 'Read cause-cart.com product pages into data/cause_cart_products.jsonl and cause_cart_listings.jsonl'

    def handle(self, *args, **opts):
        seen_products, seen_listings = set(), set()
        if os.path.exists(LISTINGS_FILE):
            with open(LISTINGS_FILE) as f:
                seen_listings = {(d['listing'], d['url']) for d in map(json.loads, filter(str.strip, f))}
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE) as f:
                seen_products = {json.loads(line)['url'] for line in f if line.strip()}
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        queue, visited = list(START_PAGES), set()
        written = 0
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                r = session.get(url, timeout=30)
            except requests.RequestException as e:
                self.stderr.write(f'{url}: {e}')
                continue
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            if r.status_code != 200 or 'text/html' not in r.headers.get('content-type', ''):
                continue
            page = r.text
            listing = LISTING.search(url)
            m = re.search(r'<title>[^<]*::\s*([^<]+)</title>', page) if listing else None
            listing_name = text(m.group(1)) if m else ''
            for href in re.findall(r'href="([^"#]+)"', page):
                link = urljoin(url, html.unescape(href)).split('#')[0]
                if urlparse(link).netloc != urlparse(STORE).netloc or SKIP.search(link):
                    continue
                key = (f'{listing.group(1)}/{listing.group(2)}', link) if listing else None
                if key and key not in seen_listings and re.search(r'/[^/]+/[^/]+/', urlparse(link).path):
                    with open(LISTINGS_FILE, 'a') as f:
                        f.write(json.dumps({'listing': key[0], 'name': listing_name, 'url': link}) + '\n')
                    seen_listings.add(key)
                if link not in visited and link not in queue:
                    queue.append(link)
            product = self.product(url, page)
            if product and url not in seen_products:
                with open(OUTPUT_FILE, 'a') as f:
                    f.write(json.dumps(product) + '\n')
                seen_products.add(url)
                written += 1
                self.stdout.write(f'{product["seller"] or "?"}: {product["name"]} ${product["price"]}')
                self.stdout.flush()
        self.stdout.write(f'{written} new products, {len(visited)} pages read')

    def product(self, url, page):
        info, crumbs = None, []
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            try:
                data = json.loads(block)
            except ValueError:
                continue
            kind = str(data.get('@type', ''))
            if kind.endswith('Product'):
                info = data
            elif kind.endswith('BreadcrumbList'):
                crumbs = [i.get('name') for i in data.get('itemListElement', [])][1:-1]
        if not info:
            return None
        offers = info.get('offers') or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price = offers.get('price')
        if price is None:
            m = re.search(r'class="ty-price-num">([\d,.]+)<', page)
            price = m.group(1).replace(',', '') if m else None
        seller = re.search(r'Vendor:\s*</[^>]+>\s*(?:<[^>]+>\s*)*([^<]+)<', page)
        image = info.get('image')
        if isinstance(image, list):
            image = image[0] if image else None
        if not image:
            m = re.search(r'property="og:image" content="([^"]+)"', page)
            image = m.group(1) if m else None
        return {
            'url': url,
            'name': text(info.get('name')),
            'seller': text(seller.group(1)) if seller else '',
            'price': str(price) if price is not None else None,
            'currency': offers.get('priceCurrency') or 'USD',
            'image_url': image,
            'description': text(info.get('description'))[:2000],
            'sku': info.get('sku'),
            'categories': crumbs,
            'read_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }
