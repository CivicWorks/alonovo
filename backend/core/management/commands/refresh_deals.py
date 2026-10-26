"""Refresh live deals from store APIs into Deal.

Best Buy (https://bestbuyapis.github.io/api-documentation/): every product on sale with at least
--min-percent off. Needs BESTBUY_API_KEY in the environment; BESTBUY_AFFILIATE_ID (Impact) is optional
and only fills Deal.affiliate_url.

Each deal is saved the moment it is read. A deal this source listed before but not in this refresh gets
an end time, so it drops off the page. The maker is matched by brand to a graded company (brand list,
then company names and Wikidata names in data/company_wikidata.json); the store is Best Buy.

Run daily until Thanksgiving and every 2 hours from Thanksgiving to Cyber Monday, e.g. cron:
    0 6 * * *      cd backend && .venv/bin/python manage.py refresh_deals
    0 */2 26-30 11 * cd backend && .venv/bin/python manage.py refresh_deals
"""
import json
import os
import time
from decimal import Decimal, InvalidOperation

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.barcode_providers import USER_AGENT
from core.management.commands.map_brand_owners import COMPANIES_FILE, DATA_DIR, norm
from core.models import BrandMapping, Company, Deal

BESTBUY_URL = 'https://api.bestbuy.com/v1/products(onSale=true&percentSavings>={min_percent})'
BESTBUY_FIELDS = ('sku,name,manufacturer,salePrice,regularPrice,percentSavings,url,affiliateUrl,image,upc,'
                  'categoryPath.name,priceUpdateDate,offers.startDate,offers.endDate')
BESTBUY_TICKER = 'BBY'
SECONDS_BETWEEN_REQUESTS = 1  # Best Buy allows 5 a second
CATEGORIES_FILE = os.path.join(DATA_DIR, 'deal_categories.json')


def money(value):
    try:
        return Decimal(str(value)) if value is not None else None
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = 'Refresh live deals from store APIs, saving each as it is read'

    def add_arguments(self, parser):
        parser.add_argument('--min-percent', type=int, default=15, help='Smallest discount to keep')
        parser.add_argument('--max-pages', type=int, default=200, help='Stop after this many pages of 100')

    def handle(self, *args, **opts):
        key = os.environ.get('BESTBUY_API_KEY')
        if not key:
            raise CommandError('BESTBUY_API_KEY is not set (free key at https://developer.bestbuy.com)')
        self.makers = self.maker_names()
        self.categories = json.load(open(CATEGORIES_FILE))['bestbuy']
        store = Company.objects.filter(ticker=BESTBUY_TICKER).first()
        started = timezone.now()

        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        params = {'apiKey': key, 'format': 'json', 'show': BESTBUY_FIELDS, 'pageSize': 100}
        if os.environ.get('BESTBUY_AFFILIATE_ID'):
            params['PID'] = os.environ['BESTBUY_AFFILIATE_ID']
        url = BESTBUY_URL.format(min_percent=opts['min_percent'])
        saved, page, pages = 0, 1, 1
        while page <= min(pages, opts['max_pages']):
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            resp = session.get(url, params={**params, 'page': page}, timeout=60)
            if resp.status_code != 200:
                raise CommandError(f'Best Buy page {page}: HTTP {resp.status_code} {resp.text[:200]}')
            data = resp.json()
            pages = data.get('totalPages', 1)
            for item in data.get('products', []):
                self.save_bestbuy(item, store)
                saved += 1
            self.stdout.write(f'page {page} of {pages}: {saved} deals saved')
            page += 1

        if page > pages:  # a full refresh: whatever it did not see has ended
            ended = Deal.objects.filter(source='bestbuy_api', ends_at__isnull=True, last_seen_at__lt=started) \
                .update(ends_at=started)
            self.stdout.write(f'{ended} deals no longer listed, marked ended')
        self.stdout.write(self.style.SUCCESS(f'{saved} Best Buy deals refreshed'))

    def save_bestbuy(self, item, store):
        offers = item.get('offers') or [{}]
        path = [c.get('name', '') for c in item.get('categoryPath') or []]
        brand = item.get('manufacturer') or ''
        Deal.objects.update_or_create(source='bestbuy_api', source_id=str(item['sku']), defaults={
            'title': item.get('name', '')[:500],
            'brand_name': brand[:200],
            'company': self.maker(brand),
            'store_name': 'Best Buy',
            'store': store,
            'category': self.category(path),
            'price': money(item.get('salePrice')),
            'regular_price': money(item.get('regularPrice')),
            'url': item.get('url') or '',
            'affiliate_url': item.get('affiliateUrl') or '',
            'image_url': item.get('image') or '',
            'barcode': item.get('upc') or '',
            'starts_at': offers[0].get('startDate') or None,
            'ends_at': offers[0].get('endDate') or None,
            'attributes': item,
            'last_seen_at': timezone.now(),
        })

    def category(self, path):
        """Our deal category from the first Best Buy category name that the mapping knows."""
        for name in path:
            if name in self.categories:
                return self.categories[name]
        return ''

    def maker_names(self):
        """Normalized brand or company name -> Company, from the brand list and company names."""
        by_ticker = {c.ticker: c for c in Company.objects.exclude(ticker=None).exclude(ticker='')}
        names = {}
        for ticker, entry in json.load(open(COMPANIES_FILE)).items():
            if ticker in by_ticker:
                names.setdefault(norm(entry['name']), by_ticker[ticker])
        for c in by_ticker.values():
            names.setdefault(norm(c.name), c)
        for b in BrandMapping.objects.select_related('company'):
            names.setdefault(norm(b.brand_name), b.company)
        names.pop('', None)
        return names

    def maker(self, brand):
        return self.makers.get(norm(brand))
