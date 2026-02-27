#!/usr/bin/env python
"""Test full receipt analysis pipeline: OCR → Claude AI → Company matching.

Usage: python tests/test_claude_parsing.py path/to/receipt.jpg
"""

import sys
import os
import base64
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Django BEFORE any core imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alonovo.settings')
import django
django.setup()

# NOW we can import from core
from core.receipt_ocr import extract_text_from_image
from core.receipt_parser import parse_receipt_with_claude, match_company_to_database


def test_full_pipeline(image_path):
    """Test full receipt analysis pipeline."""
    print("=" * 60)
    print(f"Testing Full Receipt Analysis Pipeline")
    print(f"Image: {image_path}")
    print("=" * 60)

    # Step 1: Read and encode image
    print("\n📸 Reading image...")
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        print(f"   Image size: {len(image_bytes)} bytes")
    except Exception as e:
        print(f"❌ Failed to read image: {e}")
        return False

    # Step 2: OCR extraction
    print("\n🔍 Step 1: Running EasyOCR...")
    try:
        extracted_text = extract_text_from_image(image_base64)
        print("✅ OCR successful!")
        print(f"\n📄 Extracted Text ({len(extracted_text)} characters):")
        print("-" * 60)
        print(extracted_text)
        print("-" * 60)
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Claude AI parsing
    print("\n🤖 Step 2: Parsing with Claude AI...")
    try:
        parsed_data = parse_receipt_with_claude(extracted_text)
        print("✅ Claude AI parsing successful!")
        print(f"\n📋 Parsed Data:")
        print("-" * 60)
        print(json.dumps(parsed_data, indent=2))
        print("-" * 60)
    except Exception as e:
        print(f"❌ Claude AI parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Company matching
    print("\n🔗 Step 3: Matching companies to database...")
    matched_count = 0
    total_items = len(parsed_data.get('items', []))

    for item in parsed_data.get('items', []):
        parent_company = item.get('parent_company', '')
        brand = item.get('brand', '')
        product_name = item.get('product_name', '')

        company, confidence, method = match_company_to_database(parent_company, brand)

        if company and confidence >= 0.8:
            matched_count += 1
            print(f"   ✅ {product_name}")
            print(f"      Brand: {brand} → Company: {company.name}")
            print(f"      Confidence: {confidence:.0%} ({method})")
        else:
            print(f"   ❌ {product_name}")
            print(f"      Brand: {brand}, Parent: {parent_company}")
            print(f"      Reason: {method} (confidence: {confidence:.0%})")

    print("\n" + "=" * 60)
    print(f"📊 Results: {matched_count}/{total_items} items matched ({matched_count/total_items*100:.0%}%)")
    print("=" * 60)

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tests/test_claude_parsing.py path/to/receipt.jpg")
        print("\nExample:")
        print("  python tests/test_claude_parsing.py example-receipts/receipt.png")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    print("\n🧪 Phase 2: Full Receipt Analysis Test\n")
    print("⚠️  Make sure you have:")
    print("   1. Installed: pip install anthropic")
    print("   2. Added ANTHROPIC_API_KEY to your .env file")
    print("")

    success = test_full_pipeline(image_path)

    if success:
        print("\n" + "=" * 60)
        print("✅ PHASE 2 TEST PASSED!")
        print("=" * 60)
        print("\nNext step: Commit Phase 2 and move to mobile app integration")
    else:
        print("\n❌ PHASE 2 TEST FAILED")
        sys.exit(1)
