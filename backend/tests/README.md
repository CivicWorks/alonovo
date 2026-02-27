# Receipt Scanner Tests

## Test Files

### `test_ocr_extraction.py`
Tests EasyOCR text extraction from receipt images.

**Usage:**
```bash
python tests/test_ocr_extraction.py example-receipts/receipt.png
```

**What it tests:**
- Image loading and base64 encoding
- EasyOCR text extraction
- Returns raw extracted text

---

## Running Tests

**Prerequisites:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Run OCR test:**
```bash
python tests/test_ocr_extraction.py path/to/receipt.jpg
```

---

## Next Phase

- **Phase 2:** Add Claude AI parsing to understand extracted text
- **Phase 3:** Add mobile app integration tests
