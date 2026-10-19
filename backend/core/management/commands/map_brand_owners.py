"""Map each USDA brand owner name to the graded company that owns it, through Wikidata.

For each owner name in the USDA FoodData Central Branded Foods file (busiest owners first), find the
Wikidata organizations whose English label, alias or Wikipedia title is that exact name (legal suffixes
like Inc. and LLC ignored), then follow their current parents (P749 parent organization, P127 owned by;
statements with an end date or deprecated are skipped) up to six levels until one is a graded company
listed in data/company_wikidata.json.

Each owner's result is appended to the output file the moment it is known, and owners already in the
file are skipped, so the command can be stopped and rerun at any time. Requests go one at a time with
a pause between them, per https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits.

Usage:
    python manage.py map_brand_owners --fdc-file FoodData_Central_branded_food_json_2026-04-30.zip
    python manage.py map_brand_owners --fdc-file ... --min-products 25
"""
import collections
import json
import os
import re
import time
import unicodedata

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from core.barcode_providers import USER_AGENT
from core.management.commands.fill_product_attributes import records

API = 'https://www.wikidata.org/w/api.php'
DATA_DIR = os.path.join(settings.BASE_DIR, '..', 'data')
COMPANIES_FILE = os.path.join(DATA_DIR, 'company_wikidata.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'brand_owner_companies.jsonl')
SECONDS_BETWEEN_REQUESTS = 2
MAX_LEVELS = 6

# Words that differ between a company's legal name and how it is listed elsewhere
LEGAL_WORDS = {'inc', 'incorporated', 'llc', 'co', 'company', 'corp', 'corporation', 'ltd', 'limited', 'plc',
               'the', 'sales', 'usa', 'us', 'operations', 'lp', 'llp', 'l', 'p', 'na', 'sa', 'ag', 'nv', 'se', 'gmbh'}


def norm(name):
    s = unicodedata.normalize('NFKD', name or '').encode('ascii', 'ignore').decode().lower()
    s = s.replace("'", '').replace('&', ' and ')
    return ' '.join(w for w in re.findall(r'[a-z0-9]+', s) if w not in LEGAL_WORDS)


class Wikidata:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USER_AGENT
        self.entities = {}

    def call(self, params):
        """One API request, waiting out rate limits instead of failing."""
        for attempt in range(8):
            time.sleep(SECONDS_BETWEEN_REQUESTS)
            try:
                resp = self.session.get(API, params={**params, 'format': 'json', 'maxlag': 5}, timeout=60)
                if resp.status_code == 429:
                    time.sleep(int(resp.headers.get('Retry-After', 60)))
                    continue
                data = resp.json()
                if 'error' in data:
                    raise RuntimeError(data['error'].get('code'))
                return data
            except (requests.RequestException, ValueError, RuntimeError):
                time.sleep(10 * (attempt + 1))
        raise RuntimeError(f'Wikidata request failed: {params}')

    def search(self, text):
        return [h['id'] for h in self.call({'action': 'wbsearchentities', 'search': text, 'language': 'en',
                                            'type': 'item', 'limit': 10}).get('search', [])]

    def load(self, ids):
        missing = [i for i in ids if i not in self.entities]
        for k in range(0, len(missing), 50):
            data = self.call({'action': 'wbgetentities', 'ids': '|'.join(missing[k:k + 50]),
                              'props': 'labels|aliases|claims|sitelinks', 'languages': 'en', 'sitefilter': 'enwiki'})
            for qid, e in data.get('entities', {}).items():
                names = [e.get('labels', {}).get('en', {}).get('value', '')]
                names += [a['value'] for a in e.get('aliases', {}).get('en', [])]
                title = e.get('sitelinks', {}).get('enwiki', {}).get('title')
                if title:
                    names.append(re.sub(r' \(.*\)$', '', title))
                parents = []
                for prop in ('P749', 'P127'):
                    for st in e.get('claims', {}).get(prop, []):
                        if st.get('rank') == 'deprecated' or 'P582' in st.get('qualifiers', {}):
                            continue
                        value = st['mainsnak'].get('datavalue', {}).get('value', {})
                        if isinstance(value, dict) and value.get('id'):
                            parents.append(value['id'])
                self.entities[qid] = {'names': names, 'parents': parents}
        return [self.entities.get(i, {'names': [], 'parents': []}) for i in ids]


class Command(BaseCommand):
    help = 'Map USDA brand owner names to graded companies through Wikidata, saving as it goes'

    def add_arguments(self, parser):
        parser.add_argument('--fdc-file', required=True)
        parser.add_argument('--min-products', type=int, default=5,
                            help='Only owners with at least this many products in the USDA file')
        parser.add_argument('--output', default=OUTPUT_FILE)

    def handle(self, *args, **opts):
        companies = json.load(open(COMPANIES_FILE))
        graded = {v['qid']: ticker for ticker, v in companies.items()}

        counts = collections.Counter(
            (r.get('brandOwner') or '').strip() for r in records(opts['fdc_file']))
        counts.pop('', None)
        owners = [(o, c) for o, c in counts.most_common() if c >= opts['min_products']]

        done = set()
        if os.path.exists(opts['output']):
            with open(opts['output']) as f:
                done = {json.loads(line)['owner'] for line in f if line.strip()}
        todo = [(o, c) for o, c in owners if o not in done]
        self.stdout.write(f'{len(owners)} owners with {opts["min_products"]}+ products; {len(done)} already saved; {len(todo)} to do')

        wd = Wikidata()
        with open(opts['output'], 'a') as out:
            for n, (owner, count) in enumerate(todo, 1):
                row = self.resolve(wd, graded, companies, owner, count)
                out.write(json.dumps(row, ensure_ascii=False) + '\n')
                out.flush()
                if n % 100 == 0:
                    self.stdout.write(f'{n} of {len(todo)} done')
        self.stdout.write(self.style.SUCCESS(f'Saved to {opts["output"]}'))

    def resolve(self, wd, graded, companies, owner, count):
        target = norm(owner)
        row = {'owner': owner, 'products': count, 'source_file': 'usda_fdc'}
        try:
            # Search the name as written, without its legal suffix, and normalized
            bare = re.sub(r'[,.]?\s*\b(inc|incorporated|llc|co|company|corp|corporation|ltd|limited|plc)\b\.?\s*$', '', owner, flags=re.I).strip()
            candidates = list(dict.fromkeys(wd.search(owner) + wd.search(bare) + wd.search(target)))
            exact = [q for q, e in zip(candidates, wd.load(candidates)) if any(norm(n) == target for n in e['names'])]
            paths = {}
            for start in exact:
                path = self.climb(wd, graded, start)
                if path:
                    paths[start] = path
        except RuntimeError as e:
            row['error'] = str(e)
            return row
        row['wikidata_matches'] = exact
        tickers = {graded[p[-1]] for p in paths.values()}
        if len(tickers) == 1:
            path = next(iter(paths.values()))
            ticker = tickers.pop()
            row.update(ticker=ticker, company=companies[ticker]['name'],
                       path=[{'qid': q, 'name': wd.entities.get(q, {}).get('names', [''])[0]} for q in path])
        elif tickers:
            row['ambiguous'] = {start: graded[p[-1]] for start, p in paths.items()}
        return row

    def climb(self, wd, graded, start):
        """Chain of Wikidata ids from start up to the first graded company, or None."""
        chain = {start: [start]}
        level = [start]
        for _ in range(MAX_LEVELS):
            hit = next((q for q in level if q in graded), None)
            if hit:
                return chain[hit]
            nxt = []
            for q, e in zip(level, wd.load(level)):
                for parent in e['parents']:
                    if parent not in chain:
                        chain[parent] = chain[q] + [parent]
                        nxt.append(parent)
            if not nxt:
                return None
            level = nxt
        return None
