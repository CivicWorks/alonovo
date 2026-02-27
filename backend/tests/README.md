# Receipt Scanner Tests

## Test Files

### `test_ocr_extraction.py`
Tests text extraction from receipt images and PDFs (Phase 1).

**Usage:**
```bash
python tests/test_ocr_extraction.py example-receipts/receipt.png
python tests/test_ocr_extraction.py example-receipts/receipt.pdf
```

**What it tests:**
- File loading and base64 encoding
- Automatic format detection (PDF vs image)
- PDF text extraction (using pypdf)
- Image OCR text extraction (using EasyOCR)
- Returns raw extracted text

---

### `test_claude_parsing.py`
Tests full receipt analysis pipeline: OCR → Claude AI → Company matching (Phase 2).

**Usage:**
```bash
python tests/test_claude_parsing.py example-receipts/receipt.png
```

**Prerequisites:**
- Install: `pip install anthropic`
- Add `ANTHROPIC_API_KEY` to your `.env` file

**What it tests:**
- EasyOCR text extraction
- Claude AI parsing (extracts products, brands, parent companies)
- Company matching to database (4-strategy fallback)
- Shows match confidence and method for each item

---

## Running Tests

**Prerequisites:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Run OCR test (Phase 1):**
```bash
python tests/test_ocr_extraction.py path/to/receipt.jpg
```

**Run full pipeline test (Phase 2):**
```bash
# Make sure you have ANTHROPIC_API_KEY in .env
python tests/test_claude_parsing.py path/to/receipt.jpg
```

---

## Next Phase

- **Phase 3:** Mobile app integration - Data models and API service
- **Phase 4:** Mobile app - Receipt scanner screen with camera
- **Phase 5:** Mobile app - Receipt results screen
