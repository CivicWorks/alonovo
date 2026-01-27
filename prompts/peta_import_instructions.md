# PETA Cruelty-Free Import Instructions

Import animal testing data from PETA's Ultimate Cruelty-Free List.

---

## 1. Add Cruelty-Free Value

Add to `create_values()`:

```python
{
    'slug': 'cruelty_free',
    'name': 'Cruelty-Free (Animal Testing)',
    'description': 'PETA certification for companies that do not test on animals',
    'value_type': 'label',
    'is_fixed': False,
    'is_disqualifying': False,
    'card_display_template': '{label}',
    'card_icon': 'rabbit',
},
```

---

## 2. Add Cruelty-Free ScoringRule

Add to `create_scoring_rules()`:

```python
ScoringRule.objects.update_or_create(
    value_id='cruelty_free',
    version=1,
    defaults={
        'effective_date': '2026-01-01',
        'config': {
            'type': 'label',
            'mapping': {
                'cruelty_free_vegan': {'grade': 'A', 'score': 1.0},
                'cruelty_free': {'grade': 'A-', 'score': 0.85},
                'working_toward': {'grade': 'C', 'score': 0.0},
                'tests_on_animals': {'grade': 'F', 'score': -1.0},
            }
        }
    }
)
```

---

## 3. Data Source

**PETA Ultimate Cruelty-Free List**
- Cruelty-free companies: https://crueltyfree.peta.org/companies-dont-test/
- Companies that test: https://crueltyfree.peta.org/companies-test/
- Search/browse: https://crueltyfree.peta.org/company/

**Categories:**
| Label | Meaning |
|-------|---------|
| `cruelty_free_vegan` | No animal testing + 100% vegan products |
| `cruelty_free` | No animal testing |
| `working_toward` | Still tests but working on regulatory change |
| `tests_on_animals` | Known to test on animals |

---

## 4. Import Script

```python
def import_peta_cruelty_free_data(self):
    """
    Import PETA cruelty-free data.
    
    Data manually compiled or scraped from https://crueltyfree.peta.org/
    """
    
    # Companies that ARE cruelty-free (and vegan)
    cruelty_free_vegan = [
        ('lush', 'Lush', 'Consumer Goods'),
        ('the-body-shop', 'The Body Shop', 'Consumer Goods'),
        ('elf-cosmetics', 'e.l.f. Cosmetics', 'Consumer Goods'),
        ('pacifica', 'Pacifica', 'Consumer Goods'),
        ('tarte', 'Tarte Cosmetics', 'Consumer Goods'),
        ('too-faced', 'Too Faced', 'Consumer Goods'),
        ('urban-decay', 'Urban Decay', 'Consumer Goods'),
        ('nyx', 'NYX Cosmetics', 'Consumer Goods'),
        ('milani', 'Milani', 'Consumer Goods'),
        ('wet-n-wild', 'Wet n Wild', 'Consumer Goods'),
        ('physicians-formula', 'Physicians Formula', 'Consumer Goods'),
        ('alba-botanica', 'Alba Botanica', 'Consumer Goods'),
        ('jasons-natural', "Jason's Natural", 'Consumer Goods'),
        ('seventh-generation', 'Seventh Generation', 'Consumer Goods'),
        ('method', 'Method', 'Consumer Goods'),
        ('mrs-meyers', "Mrs. Meyer's", 'Consumer Goods'),
        ('toms-of-maine', "Tom's of Maine", 'Consumer Goods'),
        ('burts-bees', "Burt's Bees", 'Consumer Goods'),
        ('derma-e', 'Derma E', 'Consumer Goods'),
        ('acure', 'Acure', 'Consumer Goods'),
    ]
    
    # Companies that ARE cruelty-free (not fully vegan)
    cruelty_free = [
        ('bath-body-works', 'Bath & Body Works', 'Consumer Goods'),
        ('beautycounter', 'Beautycounter', 'Consumer Goods'),
        ('the-honest-company', 'The Honest Company', 'Consumer Goods'),
        ('mario-badescu', 'Mario Badescu', 'Consumer Goods'),
        ('paula-choice', "Paula's Choice", 'Consumer Goods'),
        ('first-aid-beauty', 'First Aid Beauty', 'Consumer Goods'),
        ('tatcha', 'Tatcha', 'Consumer Goods'),
        ('drunk-elephant', 'Drunk Elephant', 'Consumer Goods'),
        ('glossier', 'Glossier', 'Consumer Goods'),
        ('fenty-beauty', 'Fenty Beauty', 'Consumer Goods'),
    ]
    
    # Companies working toward cruelty-free (still test but making changes)
    working_toward = [
        ('colgate-palmolive', 'Colgate-Palmolive', 'CL', 'Consumer Goods'),
        ('henkel', 'Henkel', 'HENKY', 'Consumer Goods'),
    ]
    
    # Major companies that DO test on animals
    tests_on_animals = [
        ('loreal', "L'Oréal", 'OR.PA', 'Consumer Goods'),
        ('estee-lauder', 'Estée Lauder', 'EL', 'Consumer Goods'),
        ('procter-gamble', 'Procter & Gamble', 'PG', 'Consumer Goods'),
        ('johnson-johnson', 'Johnson & Johnson', 'JNJ', 'Healthcare'),
        ('unilever', 'Unilever', 'UL', 'Consumer Goods'),
        ('clorox', 'Clorox', 'CLX', 'Consumer Goods'),
        ('sc-johnson', 'S.C. Johnson', None, 'Consumer Goods'),
        ('reckitt', 'Reckitt Benckiser', 'RKT.L', 'Consumer Goods'),
        ('church-dwight', 'Church & Dwight', 'CHD', 'Consumer Goods'),
        ('revlon', 'Revlon', 'REV', 'Consumer Goods'),
        ('avon', 'Avon', None, 'Consumer Goods'),
        ('mary-kay', 'Mary Kay', None, 'Consumer Goods'),
        ('maybelline', 'Maybelline', None, 'Consumer Goods'),  # owned by L'Oréal
        ('lancome', 'Lancôme', None, 'Consumer Goods'),  # owned by L'Oréal
        ('clinique', 'Clinique', None, 'Consumer Goods'),  # owned by Estée Lauder
        ('mac', 'MAC Cosmetics', None, 'Consumer Goods'),  # owned by Estée Lauder
        ('olay', 'Olay', None, 'Consumer Goods'),  # owned by P&G
        ('pantene', 'Pantene', None, 'Consumer Goods'),  # owned by P&G
        ('head-shoulders', 'Head & Shoulders', None, 'Consumer Goods'),  # owned by P&G
        ('dove', 'Dove', None, 'Consumer Goods'),  # owned by Unilever
        ('axe', 'Axe', None, 'Consumer Goods'),  # owned by Unilever
        ('neutrogena', 'Neutrogena', None, 'Consumer Goods'),  # owned by J&J
        ('aveeno', 'Aveeno', None, 'Consumer Goods'),  # owned by J&J
    ]
    
    # Import cruelty-free vegan
    for slug, name, sector in cruelty_free_vegan:
        self._create_peta_claim(slug, name, None, sector, 'cruelty_free_vegan')
    
    # Import cruelty-free (not vegan)
    for slug, name, sector in cruelty_free:
        self._create_peta_claim(slug, name, None, sector, 'cruelty_free')
    
    # Import working toward
    for slug, name, ticker, sector in working_toward:
        self._create_peta_claim(slug, name, ticker, sector, 'working_toward')
    
    # Import tests on animals
    for slug, name, ticker, sector in tests_on_animals:
        self._create_peta_claim(slug, name, ticker, sector, 'tests_on_animals')


def _create_peta_claim(self, slug, name, ticker, sector, label):
    uri = f'urn:company:{slug}'
    
    Company.objects.update_or_create(
        uri=uri,
        defaults={'name': name, 'ticker': ticker, 'sector': sector}
    )
    
    claim_uri = f'urn:peta:2026:{slug}:cruelty-free'
    try:
        Claim.objects.create(
            uri=claim_uri,
            subject=uri,
            claim_type='CRUELTY_FREE_STATUS',
            label=label,
            effective_date='2026-01-01',
            source_uri='https://crueltyfree.peta.org/',
            how_known='official_certification'
        )
    except ValueError:
        pass
```

---

## 5. Compute Cruelty-Free Snapshots

```python
def compute_cruelty_free_snapshot(self, company, claims):
    """Compute cruelty-free snapshot from PETA data."""
    cf_claims = claims.filter(claim_type='CRUELTY_FREE_STATUS')
    if not cf_claims.exists():
        return
    
    claim = cf_claims.first()
    rule = ScoringRule.objects.get(value_id='cruelty_free', version=1)
    mapping = rule.config['mapping'].get(claim.label, {'grade': 'F', 'score': -1.0})
    
    display_text_map = {
        'cruelty_free_vegan': 'Cruelty-free & Vegan',
        'cruelty_free': 'Cruelty-free',
        'working_toward': 'Working toward cruelty-free',
        'tests_on_animals': 'Tests on animals',
    }
    
    display_icon_map = {
        'cruelty_free_vegan': 'rabbit',
        'cruelty_free': 'rabbit',
        'working_toward': 'clock',
        'tests_on_animals': 'alert',
    }
    
    CompanyValueSnapshot.objects.update_or_create(
        company=company,
        value_id='cruelty_free',
        defaults={
            'score': mapping['score'],
            'grade': mapping['grade'],
            'claim_uris': [claim.uri],
            'highlight_on_card': True,
            'highlight_priority': 2,
            'display_text': display_text_map.get(claim.label, claim.label),
            'display_icon': display_icon_map.get(claim.label, 'rabbit'),
            'scoring_rule_version': 1,
        }
    )
```

---

## 6. Scraping PETA (Optional)

If you want to scrape the full list:

```python
import requests
from bs4 import BeautifulSoup

def scrape_peta_cruelty_free():
    """
    Scrape PETA's cruelty-free list.
    Note: Be respectful of rate limits.
    """
    base_url = 'https://crueltyfree.peta.org/companies-dont-test/'
    
    # This is a simplified example - actual scraping may need pagination
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    companies = []
    # Find company entries - structure may vary
    for entry in soup.select('.company-entry'):  # adjust selector as needed
        name = entry.select_one('.company-name').text.strip()
        is_vegan = 'vegan' in entry.get('class', [])
        companies.append({
            'name': name,
            'label': 'cruelty_free_vegan' if is_vegan else 'cruelty_free'
        })
    
    return companies
```

---

## 7. Additional Source: Cruelty Free Kitty

**URL:** https://www.crueltyfreekitty.com/companies-that-test-on-animals/

Maintains a list of 268+ companies that test on animals, cross-referenced with PETA. Good for the "tests_on_animals" category.

---

## 8. Run Order

```bash
# If scraping
pip install beautifulsoup4 requests

# Run import
python manage.py import_peta_data
```

---

## Data Summary

| Source | URL | Data Type |
|--------|-----|-----------|
| PETA Cruelty-Free | https://crueltyfree.peta.org/companies-dont-test/ | Companies that don't test |
| PETA Tests on Animals | https://crueltyfree.peta.org/companies-test/ | Companies that do test |
| Cruelty Free Kitty | https://www.crueltyfreekitty.com/companies-that-test-on-animals/ | Supplemental list |

---

## Notes

- PETA list is primarily cosmetics/personal care/household products
- Many parent companies (L'Oréal, P&G, etc.) test while some subsidiaries don't
- "Working toward" status means they still test but are lobbying for regulatory change
- China sales often require animal testing (changing as of 2024)
