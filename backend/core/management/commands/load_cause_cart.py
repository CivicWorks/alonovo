"""Load the Cause-Cart products read by crawl_cause_cart into Deal, source cause_cart.

Each product becomes one Deal at store Cause-Cart: the seller as brand, the store's first category, its
price and link, and the whole record in attributes along with the cause and impact pages that list it
(attributes['labels'], e.g. Women-Owned). Products no longer in the file are ended. Rerun after every
crawl; existing rows are updated in place.

Usage:
    python manage.py load_cause_cart
"""
import json
import os
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from core.management.commands.crawl_cause_cart import LISTINGS_FILE, OUTPUT_FILE
from core.models import Deal

SOURCE = 'cause_cart'
STORE_NAME = 'Cause-Cart'


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def price(value):
    try:
        return Decimal(value) if value not in (None, '') else None
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = 'Load data/cause_cart_products.jsonl into Deal (source cause_cart)'

    def handle(self, *args, **opts):
        labels = {}
        for row in read_jsonl(LISTINGS_FILE):
            if row.get('name'):
                labels.setdefault(row['url'], set()).add(row['name'])
        products = read_jsonl(OUTPUT_FILE)
        now = timezone.now()
        for p in products:
            record = dict(p, labels=sorted(labels.get(p['url'], [])))
            Deal.objects.update_or_create(source=SOURCE, source_id=p['url'], defaults={
                'title': p['name'][:500],
                'brand_name': p.get('seller', '')[:200],
                'store_name': STORE_NAME,
                'category': (p.get('categories') or [''])[0][:100],
                'price': price(p.get('price')),
                'regular_price': None,
                'currency': p.get('currency') or 'USD',
                'url': p['url'],
                'image_url': p.get('image_url') or '',
                'attributes': record,
                'ends_at': None,
                'last_seen_at': parse_datetime(p['read_at']) or now,
            })
        ended = Deal.objects.filter(source=SOURCE, ends_at__isnull=True) \
            .exclude(source_id__in=[p['url'] for p in products]).update(ends_at=now)
        self.stdout.write(f'{len(products)} Cause-Cart products loaded, {ended} ended')
