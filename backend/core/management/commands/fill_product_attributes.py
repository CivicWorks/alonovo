"""Attach each product's USDA FoodData Central record to Product.attributes['usda_fdc'].

Reads the Branded Foods JSON download (public domain, https://fdc.nal.usda.gov/download-datasets/),
one record per line, and keeps the whole record. A product matches a record:
  1. by barcode, when the product has one and the record's GTIN/UPC is the same number, else
  2. by name: the record's brand name and description together carry our brand and every word
     of our product name. Among several, the newest US record with the fewest extra words wins.
How each product was matched is stored next to the record, so a wrong match can be traced.

Usage:
    python manage.py fill_product_attributes --fdc-file FoodData_Central_branded_food_json_2026-04-30.zip
    python manage.py fill_product_attributes --fdc-file ... --dry-run
"""
import json
import re
import zipfile
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import Product

# Words shelf names carry that USDA descriptions often leave out
IGNORED_WORDS = {'original', 'classic', 'pk', 'ct', 'oz', 'the'}


def tokens(text):
    words = re.findall(r"[a-z]+|[0-9]+", (text or '').lower().replace("'", ''))
    return {w[:-1] if w.endswith('s') and len(w) > 3 else w for w in words} - IGNORED_WORDS


def digits(code):
    return (code or '').lstrip('0')


def records(path):
    """Yield each food record from the download, zipped or not."""
    if path.endswith('.zip'):
        with zipfile.ZipFile(path) as z:
            name = z.namelist()[0]
            with z.open(name) as f:
                yield from parse_lines(line.decode('utf-8') for line in f)
    else:
        with open(path, encoding='utf-8') as f:
            yield from parse_lines(f)


def parse_lines(lines):
    """Each record is one line; the last one is followed by the closing ]} of the file."""
    decoder = json.JSONDecoder()
    for line in lines:
        line = line.strip()
        if line.startswith('{"foodClass"'):
            yield decoder.raw_decode(line)[0]


def published(rec):
    try:
        return datetime.strptime(rec.get('publicationDate', ''), '%m/%d/%Y')
    except ValueError:
        return datetime.min


class Command(BaseCommand):
    help = 'Attach USDA FoodData Central records to products'

    def add_arguments(self, parser):
        parser.add_argument('--fdc-file', required=True)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        products = list(Product.objects.all())
        by_barcode = {digits(p.barcode): p for p in products if digits(p.barcode)}
        wanted = {p.id: (tokens(p.brand_name), tokens(p.name) - tokens(p.brand_name) or tokens(p.name)) for p in products}
        best = {}  # product id -> (rank, method, record)

        seen = 0
        for rec in records(opts['fdc_file']):
            seen += 1
            code = digits(rec.get('gtinUpc'))
            if code in by_barcode:
                p = by_barcode[code]
                rank = (2, published(rec))
                if p.id not in best or best[p.id][0] < rank:
                    best[p.id] = (rank, 'barcode', rec)
            desc = tokens(rec.get('description'))
            brand = tokens(rec.get('brandName')) | tokens(rec.get('subbrandName')) | desc
            for pid, (our_brand, our_name) in wanted.items():
                if our_brand <= brand and our_name <= brand:
                    extra = len(desc - our_name - our_brand)
                    rank = (1, rec.get('marketCountry') == 'United States', -extra, published(rec))
                    if pid not in best or best[pid][0] < rank:
                        best[pid] = (rank, 'brand and name', rec)
            if seen % 100000 == 0:
                self.stderr.write(f'{seen} records read, {len(best)} products matched')

        for p in products:
            if p.id not in best:
                self.stdout.write(f'{p.id} {p.name}: no match')
                continue
            _, method, rec = best[p.id]
            self.stdout.write(f'{p.id} {p.name} -> {rec.get("description")} [{rec.get("brandOwner")}] by {method}')
            if not opts['dry_run']:
                attrs = p.attributes or {}
                attrs['usda_fdc'] = {'matched_by': method, 'source_file': opts['fdc_file'].split('/')[-1], 'record': rec}
                p.attributes = attrs
                p.save(update_fields=['attributes', 'updated_at'])

        self.stdout.write(self.style.SUCCESS(f'{len(best)} of {len(products)} products matched from {seen} records'))
