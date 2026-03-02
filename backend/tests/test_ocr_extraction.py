#!/usr/bin/env python
"""Test text extraction from receipt images and PDFs.

Supports both image files (JPEG, PNG) via EasyOCR and PDF files via pypdf.

Usage:
    python tests/test_ocr_extraction.py path/to/receipt.jpg
    python tests/test_ocr_extraction.py path/to/receipt.pdf
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


def test_ocr_extraction(file_path):
    """Test text extraction with a real receipt file (image or PDF)."""
    print("=" * 60)
    print(f"Testing Receipt Text Extraction")
    print(f"File: {file_path}")
    print("=" * 60)

    # Detect file type
    file_ext = os.path.splitext(file_path)[1].lower()
    file_type = "PDF" if file_ext == '.pdf' else "Image"
    print(f"\nDetected file type: {file_type}")

    # Read and encode file
    print(f"Reading {file_type.lower()}...")
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        print(f"   File size: {len(file_bytes)} bytes")
    except Exception as e:
        print(f"Failed to read file: {e}")
        return False

    # Extract text
    print(f"\n Extracting text ({file_type})...")
    try:
        extracted_text = extract_text_from_image(file_base64)
        print("Text extraction successful!")
        print(f"\n Extracted Text ({len(extracted_text)} characters):")
        print("-" * 60)
        print(extracted_text)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"Text extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tests/test_ocr_extraction.py path/to/receipt.[jpg|png|pdf]")
        print("\n Examples:")
        print("  python tests/test_ocr_extraction.py example-receipts/receipt.png")
        print("  python tests/test_ocr_extraction.py example-receipts/receipt.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    print("\n Receipt Text Extraction Test\n")

    success = test_ocr_extraction(file_path)

    if success:
        print("\n" + "=" * 60)
        print("TEXT EXTRACTION TEST PASSED!")
        print("=" * 60)
        print("\n Next step: Add Claude AI parsing to understand this text")
    else:
        print("\n TEXT EXTRACTION TEST FAILED")
        sys.exit(1)
