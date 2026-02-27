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


def match_company_to_database(parent_company_name: str, brand_name: str):
    """Match extracted company/brand to existing database.

    Tries multiple strategies:
    1. Direct company name match
    2. BrandMapping lookup
    3. Fuzzy company name match

    Args:
        parent_company_name: Company name from Claude
        brand_name: Brand name from Claude

    Returns:
        tuple: (Company object or None, confidence: float, method: str)
    """
    from .models import Company, BrandMapping

    parent_company_name_lower = parent_company_name.lower().strip()
    brand_name_lower = brand_name.lower().strip()

    # Strategy 1: Direct company name match (exact)
    company = Company.objects.filter(name__iexact=parent_company_name).first()
    if company:
        return company, 0.95, 'exact_company_name'

    # Strategy 2: BrandMapping lookup (exact brand match)
    brand_mapping = BrandMapping.objects.filter(
        brand_name_normalized=brand_name_lower
    ).select_related('company').first()
    if brand_mapping:
        return brand_mapping.company, brand_mapping.confidence, 'brand_mapping_exact'

    # Strategy 3: Fuzzy company name match (contains)
    if len(parent_company_name) >= 3:
        company = Company.objects.filter(
            name__icontains=parent_company_name
        ).first()
        if company:
            return company, 0.7, 'fuzzy_company_name'

    # Strategy 4: Fuzzy brand match
    if len(brand_name) >= 3:
        brand_mapping = BrandMapping.objects.filter(
            brand_name_normalized__icontains=brand_name_lower
        ).select_related('company').first()
        if brand_mapping:
            return brand_mapping.company, brand_mapping.confidence * 0.7, 'brand_mapping_fuzzy'

    # No match found
    return None, 0.0, 'not_found'
