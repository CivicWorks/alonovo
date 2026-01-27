# ESG Score Import Instructions

Import ESG scores from multiple sources. Multiple claims from different sources for the same company/value is intentional—shows consensus or disagreement.

---

## 1. Add ESG Value

Add to `create_values()` in the import command:

```python
{
    'slug': 'esg_score',
    'name': 'ESG Score',
    'description': 'Environmental, Social, and Governance score from multiple rating agencies',
    'value_type': 'metric',
    'is_fixed': False,
    'is_disqualifying': False,
    'card_display_template': 'ESG: {amt}',
    'card_icon': 'leaf',
},
```

---

## 2. Add ESG ScoringRule

Add to `create_scoring_rules()`:

```python
# ESG Score (Sustainalytics-style: lower = better, 0-40+ scale)
ScoringRule.objects.update_or_create(
    value_id='esg_score',
    version=1,
    defaults={
        'effective_date': '2026-01-01',
        'config': {
            'type': 'threshold_inverse',  # lower is better
            'thresholds': [
                {'max': 10, 'grade': 'A', 'score': 1.0},    # Negligible risk
                {'max': 20, 'grade': 'B', 'score': 0.6},    # Low risk
                {'max': 30, 'grade': 'C', 'score': 0.0},    # Medium risk
                {'max': 40, 'grade': 'D', 'score': -0.5},   # High risk
                {'max': 100, 'grade': 'F', 'score': -1.0},  # Severe risk
            ]
        }
    }
)
```

---

## 3. Source 1: GitHub CSV (Pre-scraped S&P 500)

**Source:** https://github.com/sburstein/ESG-Stock-Data
**File:** `sp_esg_stock_data.csv` (245 companies)

```bash
wget -O data/sp_esg_stock_data.csv https://raw.githubusercontent.com/sburstein/ESG-Stock-Data/main/sp_esg_stock_data.csv
```

```python
import csv
from decimal import Decimal

def import_github_esg_data(self):
    """
    Import ESG data from sburstein/ESG-Stock-Data GitHub repo.
    CSV columns: ticker, totalEsg, environmentScore, socialScore, governanceScore, etc.
    """
    csv_path = 'data/sp_esg_stock_data.csv'
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row.get('ticker') or row.get('Ticker')
            total_esg = row.get('totalEsg') or row.get('Total ESG')
            
            if not ticker or not total_esg:
                continue
            
            try:
                esg_value = Decimal(str(total_esg))
            except:
                continue
            
            slug = ticker.lower()
            uri = f'urn:company:{slug}'
            
            Company.objects.update_or_create(
                uri=uri,
                defaults={
                    'name': row.get('company', ticker),
                    'ticker': ticker,
                    'sector': row.get('sector', None),
                }
            )
            
            claim_uri = f'urn:yahoo-sustainalytics:2024:{slug}:esg'
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='ESG_SCORE',
                    amt=esg_value,
                    unit='sustainalytics_risk',
                    effective_date='2024-01-01',
                    source_uri='https://github.com/sburstein/ESG-Stock-Data',
                    how_known='scraped_yahoo_finance'
                )
            except ValueError:
                pass
```

---

## 4. Source 2: Yahoo Finance via yfinance (Live Pull)

**Source:** https://finance.yahoo.com/ (Sustainalytics data)

```bash
pip install yfinance
```

```python
import yfinance as yf
from decimal import Decimal

def import_yfinance_esg_data(self, tickers: list):
    """
    Pull live ESG data from Yahoo Finance using yfinance library.
    tickers: list of ticker symbols, e.g., ['AAPL', 'MSFT', 'GOOGL']
    """
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            sustainability = stock.sustainability
            
            if sustainability is None:
                continue
            
            total_esg = sustainability.loc['totalEsg'].values[0] if 'totalEsg' in sustainability.index else None
            env_score = sustainability.loc['environmentScore'].values[0] if 'environmentScore' in sustainability.index else None
            social_score = sustainability.loc['socialScore'].values[0] if 'socialScore' in sustainability.index else None
            gov_score = sustainability.loc['governanceScore'].values[0] if 'governanceScore' in sustainability.index else None
            
            if total_esg is None:
                continue
            
            slug = ticker.lower()
            uri = f'urn:company:{slug}'
            
            info = stock.info
            Company.objects.update_or_create(
                uri=uri,
                defaults={
                    'name': info.get('longName', ticker),
                    'ticker': ticker,
                    'sector': info.get('sector', None),
                }
            )
            
            claim_uri = f'urn:yfinance:2026:{slug}:esg'
            statement = f"E:{env_score} S:{social_score} G:{gov_score}" if all([env_score, social_score, gov_score]) else None
            
            try:
                Claim.objects.create(
                    uri=claim_uri,
                    subject=uri,
                    claim_type='ESG_SCORE',
                    amt=Decimal(str(total_esg)),
                    unit='sustainalytics_risk',
                    statement=statement,
                    effective_date='2026-01-01',
                    source_uri='https://finance.yahoo.com/',
                    how_known='yfinance_api'
                )
            except ValueError:
                pass
                
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue
```

---

## 5. Source 3: S&P Global ESG Scores

**Source:** https://www.spglobal.com/esg/scores/
**Scale:** 0-100, higher = better (opposite of Sustainalytics)

```python
def import_spglobal_esg_data(self):
    """
    Import S&P Global ESG scores.
    S&P uses 0-100 scale (higher = better), opposite of Sustainalytics.
    """
    # Manually compiled data - S&P scale: 0-100, higher is better
    spglobal_data = [
        ('AAPL', 'Apple', 'Technology', 31),
        ('MSFT', 'Microsoft', 'Technology', 35),
        ('GOOGL', 'Alphabet', 'Technology', 29),
        ('AMZN', 'Amazon', 'Retail', 22),
        ('META', 'Meta Platforms', 'Technology', 26),
        ('TSLA', 'Tesla', 'Automotive', 37),
        ('JPM', 'JPMorgan Chase', 'Banking', 51),
        ('V', 'Visa', 'Financial Services', 42),
        ('JNJ', 'Johnson & Johnson', 'Healthcare', 55),
        ('WMT', 'Walmart', 'Retail', 48),
        ('PG', 'Procter & Gamble', 'Consumer Goods', 56),
        ('XOM', 'Exxon Mobil', 'Oil & Gas', 41),
        ('CVX', 'Chevron', 'Oil & Gas', 43),
        ('KO', 'Coca-Cola', 'Beverages', 52),
        ('PEP', 'PepsiCo', 'Beverages', 58),
        ('MCD', "McDonald's", 'Restaurants', 34),
        ('NKE', 'Nike', 'Apparel', 45),
        ('DIS', 'Disney', 'Entertainment', 39),
        ('NFLX', 'Netflix', 'Entertainment', 28),
        ('COST', 'Costco', 'Retail', 44),
    ]
    
    for ticker, name, sector, sp_score in spglobal_data:
        slug = ticker.lower()
        uri = f'urn:company:{slug}'
        
        Company.objects.update_or_create(
            uri=uri,
            defaults={'name': name, 'ticker': ticker, 'sector': sector}
        )
        
        claim_uri = f'urn:spglobal:2025:{slug}:esg'
        try:
            Claim.objects.create(
                uri=claim_uri,
                subject=uri,
                claim_type='ESG_SCORE',
                amt=Decimal(str(sp_score)),
                unit='spglobal_score',  # 0-100, higher = better
                effective_date='2025-01-01',
                source_uri='https://www.spglobal.com/esg/scores/',
                how_known='official_rating'
            )
        except ValueError:
            pass
```

---

## 6. Compute ESG Snapshots (Multiple Sources)

Handle multiple claims from different sources, normalize scales, average:

```python
def compute_esg_snapshot(self, company, claims):
    """
    Compute ESG snapshot from potentially multiple source claims.
    Normalizes different scales and averages across sources.
    """
    esg_claims = claims.filter(claim_type='ESG_SCORE')
    if not esg_claims.exists():
        return
    
    normalized_scores = []
    claim_uris = []
    
    for claim in esg_claims:
        claim_uris.append(claim.uri)
        
        if claim.unit == 'spglobal_score':
            # S&P: 0-100, higher = better -> invert and scale to 0-50
            normalized = (100 - float(claim.amt)) / 2
        else:
            # Sustainalytics-style: already lower = better
            normalized = float(claim.amt)
        
        normalized_scores.append(normalized)
    
    avg_score = sum(normalized_scores) / len(normalized_scores)
    
    rule = ScoringRule.objects.get(value_id='esg_score', version=1)
    grade = 'F'
    score = -1.0
    for threshold in rule.config['thresholds']:
        if avg_score <= threshold['max']:
            grade = threshold['grade']
            score = threshold['score']
            break
    
    display_text = f"ESG Risk: {avg_score:.1f}"
    if len(claim_uris) > 1:
        display_text += f" ({len(claim_uris)} sources)"
    
    CompanyValueSnapshot.objects.update_or_create(
        company=company,
        value_id='esg_score',
        defaults={
            'score': score,
            'grade': grade,
            'claim_uris': claim_uris,
            'highlight_on_card': True,
            'highlight_priority': 3,
            'display_text': display_text,
            'display_icon': 'leaf',
            'scoring_rule_version': 1,
        }
    )
```

---

## 7. S&P 500 Ticker List

Common tickers to seed:

```python
SP500_SAMPLE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'BRK-B', 'NVDA', 'JPM', 'JNJ',
    'V', 'UNH', 'HD', 'PG', 'MA', 'DIS', 'PYPL', 'ADBE', 'NFLX', 'CMCSA',
    'PFE', 'KO', 'PEP', 'TMO', 'COST', 'ABT', 'CSCO', 'AVGO', 'ACN', 'MRK',
    'NKE', 'MCD', 'WMT', 'CVX', 'XOM', 'LLY', 'DHR', 'TXN', 'NEE', 'BMY',
    'UPS', 'QCOM', 'HON', 'LOW', 'UNP', 'ORCL', 'PM', 'IBM', 'SBUX', 'CAT',
]
```

---

## 8. Run Order

```bash
pip install yfinance

wget -O data/sp_esg_stock_data.csv https://raw.githubusercontent.com/sburstein/ESG-Stock-Data/main/sp_esg_stock_data.csv

python manage.py import_esg_data
```

---

## Data Sources Reference

| Source | Scale | Direction | Coverage |
|--------|-------|-----------|----------|
| GitHub/Yahoo/Sustainalytics | 0-50+ | Lower = better | 245 S&P 500 |
| yfinance (live) | 0-50+ | Lower = better | Any ticker |
| S&P Global | 0-100 | Higher = better | Manual lookup |
