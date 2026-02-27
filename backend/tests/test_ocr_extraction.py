#!/usr/bin/env python
"""Test EasyOCR text extraction with a real image file.

Usage: python tests/test_ocr_extraction.py path/to/receipt.jpg
"""

import sys
import os
import base64

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Django BEFORE any core imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alonovo.settings')
import django
django.setup()

# NOW we can import from core
from core.receipt_ocr import extract_text_from_image


def test_ocr_extraction(image_path):
    """Test OCR text extraction with a real receipt image."""
    print("=" * 60)
    print(f"Testing EasyOCR Text Extraction")
    print(f"Image: {image_path}")
    print("=" * 60)

    # Read and encode image
    print("\n📸 Reading image...")
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        print(f"   Image size: {len(image_bytes)} bytes")
    except Exception as e:
        print(f"❌ Failed to read image: {e}")
        return False

    # Run OCR
    print("\n🔍 Running EasyOCR...")
    try:
        extracted_text = extract_text_from_image(image_base64)
        print("✅ OCR successful!")
        print(f"\n📄 Extracted Text ({len(extracted_text)} characters):")
        print("-" * 60)
        print(extracted_text)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tests/test_ocr_extraction.py path/to/receipt.jpg")
        print("\nExample:")
        print("  python tests/test_ocr_extraction.py example-receipts/receipt.png")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    print("\n🧪 EasyOCR Text Extraction Test\n")

    success = test_ocr_extraction(image_path)

    if success:
        print("\n" + "=" * 60)
        print("✅ OCR EXTRACTION TEST PASSED!")
        print("=" * 60)
        print("\nNext step: Add Claude AI parsing to understand this text")
    else:
        print("\n❌ OCR TEST FAILED")
        sys.exit(1)
