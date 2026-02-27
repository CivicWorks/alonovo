"""Receipt parsing using Claude AI.

Uses Claude to intelligently extract products and deduce parent companies
from receipt text, then matches to existing database.
"""

import json
from typing import List, Dict, Optional
from decouple import config
import anthropic


def parse_receipt_with_claude(receipt_text: str) -> Dict:
    """Use Claude AI to extract products and companies from receipt text.

    Args:
        receipt_text: Raw text extracted from receipt (OCR output)

    Returns:
        {
            'store_name': str,
            'date': str or None,
            'total': float or None,
            'items': [
                {
                    'product_name': str,
                    'brand': str,
                    'parent_company': str,
                    'price': float or None
                },
                ...
            ]
        }

    Raises:
        ValueError: If Claude API call fails or returns invalid data
    """
    # Get API key from environment
    api_key = config('ANTHROPIC_API_KEY', default=None)
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment. "
            "Add it to your .env file or set as environment variable."
        )

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)

    # Construct prompt for Claude
    prompt = f"""You are analyzing a receipt to extract product information and identify parent companies.

Receipt text:
{receipt_text}

Your task:
1. Identify the store name
2. Extract the date (if visible)
3. Extract the total amount (if visible)
4. For each product line item:
   - Extract the product name
   - Identify the brand
   - Deduce the parent company (the corporation that owns the brand)
   - Extract the price (if visible)

Important:
- For brands like "Tide", "Pampers", "Bounty" → parent company is "Procter & Gamble"
- For brands like "Cheerios", "Häagen-Dazs" → parent company is "General Mills"
- For brands like "Coca-Cola", "Sprite" → parent company is "The Coca-Cola Company"
- For store brands (Kroger brand, Target brand, etc.) → parent company is the store
- If unsure about parent company, use the brand name itself

Return ONLY a JSON object (no markdown, no explanation) in this exact format:
{{
    "store_name": "Store Name",
    "date": "YYYY-MM-DD" or null,
    "total": 123.45 or null,
    "items": [
        {{
            "product_name": "Product Name",
            "brand": "Brand Name",
            "parent_company": "Parent Company Name",
            "price": 12.99 or null
        }}
    ]
}}"""

    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Claude 3 Haiku (available with current API key)
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract response text
        response_text = message.content[0].text.strip()

        # Parse JSON response
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Sometimes Claude wraps JSON in markdown code blocks
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
                parsed_data = json.loads(json_str)
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
                parsed_data = json.loads(json_str)
            else:
                raise ValueError(f"Could not parse Claude response as JSON: {response_text}")

        # Validate structure
        if not isinstance(parsed_data, dict):
            raise ValueError("Claude response is not a dictionary")

        if 'items' not in parsed_data or not isinstance(parsed_data['items'], list):
            raise ValueError("Claude response missing 'items' array")

        return parsed_data

    except anthropic.APIError as e:
        raise ValueError(f"Claude API error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse receipt with Claude: {str(e)}")


def match_company_to_database(parent_company_name: str, brand_name: str, product_name: str = '', price: float = None):
    """Match extracted company/brand to existing database.

    Tries multiple strategies (in order):
    1. Exact product name match (Product model)
    2. Brand name match (Product model)
    3. Direct company name match
    4. BrandMapping lookup
    5. Fuzzy company/brand match

    If no match found or confidence < 80%, saves to UnmatchedProduct for review.

    Args:
        parent_company_name: Company name from Claude
        brand_name: Brand name from Claude
        product_name: Product name from receipt (optional)
        price: Product price (optional, for tracking typical price)

    Returns:
        tuple: (Company object or None, confidence: float, method: str)
    """
    from .models import Company, BrandMapping, Product, UnmatchedProduct
    from django.db.models import F

    parent_company_name = parent_company_name.strip()
    brand_name = brand_name.strip()
    product_name = product_name.strip()

    parent_company_name_lower = parent_company_name.lower()
    brand_name_lower = brand_name.lower()

    # Strategy 1: Exact product name match (BEST - 95% confidence)
    if product_name:
        product = Product.objects.filter(
            name__iexact=product_name
        ).select_related('company').first()
        if product:
            return product.company, 0.95, 'exact_product_name'

    # Strategy 2: Brand name match in Product model (90% confidence)
    if brand_name:
        product = Product.objects.filter(
            brand_name__iexact=brand_name
        ).select_related('company').first()
        if product:
            return product.company, 0.90, 'product_brand_match'

    # Strategy 3: Direct company name match (85% confidence)
    if parent_company_name:
        company = Company.objects.filter(name__iexact=parent_company_name).first()
        if company:
            return company, 0.85, 'exact_company_name'

    # Strategy 4: BrandMapping lookup (exact brand match)
    if brand_name:
        brand_mapping = BrandMapping.objects.filter(
            brand_name_normalized=brand_name_lower
        ).select_related('company').first()
        if brand_mapping:
            return brand_mapping.company, brand_mapping.confidence, 'brand_mapping_exact'

    # Strategy 5: Fuzzy company name match (70% confidence)
    if len(parent_company_name) >= 3:
        company = Company.objects.filter(
            name__icontains=parent_company_name
        ).first()
        if company:
            # Save to unmatched (low confidence)
            _save_unmatched_product(product_name, brand_name, parent_company_name, price)
            return company, 0.70, 'fuzzy_company_name'

    # Strategy 6: Fuzzy brand match (lower confidence)
    if len(brand_name) >= 3:
        brand_mapping = BrandMapping.objects.filter(
            brand_name_normalized__icontains=brand_name_lower
        ).select_related('company').first()
        if brand_mapping:
            # Save to unmatched (low confidence)
            _save_unmatched_product(product_name, brand_name, parent_company_name, price)
            return brand_mapping.company, brand_mapping.confidence * 0.7, 'brand_mapping_fuzzy'

    # No match found - save to unmatched for review
    _save_unmatched_product(product_name, brand_name, parent_company_name, price)
    return None, 0.0, 'not_found'


def _save_unmatched_product(product_name: str, brand_name: str, parent_company_guess: str, price: float = None):
    """Save unmatched product for admin review, or increment seen_count if exists."""
    from .models import UnmatchedProduct
    from django.db.models import F

    if not product_name or not brand_name:
        return  # Skip if missing critical info

    # Check if this product already exists
    unmatched, created = UnmatchedProduct.objects.get_or_create(
        product_name=product_name,
        brand_name=brand_name,
        defaults={
            'parent_company_guess': parent_company_guess or '',
            'typical_price': price,
        }
    )

    if not created:
        # Already exists - increment seen count and update price
        unmatched.seen_count = F('seen_count') + 1
        if price and (not unmatched.typical_price or abs(price - unmatched.typical_price) < 2):
            # Update typical price if close to existing
            unmatched.typical_price = price
        unmatched.save(update_fields=['seen_count', 'typical_price', 'last_seen_at'])
