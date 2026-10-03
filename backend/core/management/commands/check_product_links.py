"""Check that every product image link still loads, so shoppers never see a broken picture.

Requests each Product.image_url and reports the ones that fail or are not images.
With --clear, broken image links (404, not an image) are removed (fill_product_images can then look again).

Usage:
    python manage.py check_product_links
    python manage.py check_product_links --clear
Exit status is 1 when any link is broken, so a scheduled job or CI step can alert on it.
"""
import sys

import requests
from django.core.management.base import BaseCommand

from core.barcode_providers import REQUEST_TIMEOUT, USER_AGENT
from core.models import Product


def check(url):
    """Return (reason, definite): reason is None when the link serves an image.

    definite is False for timeouts, connection errors and server errors, which may pass on a
    later run; those are reported but never cleared.
    """
    try:
        resp = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT, stream=True)
        resp.close()
    except requests.RequestException as e:
        return f'unreachable: {e.__class__.__name__}', False
    if resp.status_code >= 500:
        return f'unreachable: HTTP {resp.status_code}', False
    if resp.status_code != 200:
        return f'HTTP {resp.status_code}', True
    if not resp.headers.get('Content-Type', '').startswith('image/'):
        return f'not an image ({resp.headers.get("Content-Type", "no type")})', True
    return None, True


class Command(BaseCommand):
    help = 'Check product image links; report or clear broken ones'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Remove broken image links')

    def handle(self, *args, **opts):
        products = list(Product.objects.exclude(image_url__isnull=True).order_by('id'))
        broken = unreachable = 0
        for product in products:
            reason, definite = check(product.image_url)
            if not reason:
                continue
            self.stdout.write(f'{product.id} {product.name}: {reason} {product.image_url}')
            if not definite:
                unreachable += 1
            else:
                broken += 1
                if opts['clear']:
                    product.image_url = None
                    product.save(update_fields=['image_url', 'updated_at'])
        self.stdout.write(f'{len(products)} checked, {broken} broken, {unreachable} unreachable this run')
        if broken:
            sys.exit(1)
