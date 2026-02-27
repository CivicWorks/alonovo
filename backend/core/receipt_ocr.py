"""Receipt OCR module.

Supports both images (EasyOCR) and PDFs (pypdf) for receipt text extraction.
Text parsing will be handled by Claude AI in a separate step.
"""

import base64
import io

# Global EasyOCR reader (initialized once)
_easyocr_reader = None


def _get_easyocr_reader():
    """Get or initialize the EasyOCR reader (singleton pattern)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
        except ImportError:
            raise ImportError(
                "easyocr not installed. "
                "Run: pip install easyocr"
            )
        # Initialize reader for English (add other languages if needed: ['en', 'es', 'fr'])
        _easyocr_reader = easyocr.Reader(['en'], gpu=False)
    return _easyocr_reader


def _is_pdf(file_bytes: bytes) -> bool:
    """Check if file is a PDF by looking at magic bytes."""
    return file_bytes.startswith(b'%PDF')


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using pypdf.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        Full text extracted from all pages

    Raises:
        ValueError: If PDF is invalid or text extraction fails
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "pypdf not installed. "
            "Run: pip install pypdf"
        )

    try:
        # Create PDF reader from bytes
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)

        # Extract text from all pages
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)

        if not full_text:
            raise ValueError("No text found in PDF")

        return '\n'.join(full_text)

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def _extract_text_from_image_ocr(image_bytes: bytes) -> str:
    """Extract text from image using EasyOCR.

    Args:
        image_bytes: Raw image file bytes (JPEG, PNG, etc.)

    Returns:
        Full text extracted from the image

    Raises:
        ValueError: If OCR fails
    """
    try:
        # Get EasyOCR reader
        reader = _get_easyocr_reader()

        # Perform text detection
        # detail=0 returns just text, detail=1 returns [bbox, text, confidence]
        result = reader.readtext(image_bytes, detail=0)

        if not result:
            raise ValueError("No text detected in image")

        # Join all text lines with newlines
        return '\n'.join(result)

    except Exception as e:
        raise ValueError(f"Failed to process image with OCR: {str(e)}")


def extract_text_from_image(image_base64: str) -> str:
    """Extract text from receipt (supports both images and PDFs).

    Automatically detects file type and uses appropriate extraction method:
    - PDF files: pypdf text extraction
    - Image files: EasyOCR

    Args:
        image_base64: Base64-encoded file (JPEG, PNG, or PDF)

    Returns:
        Full text extracted from the file

    Raises:
        ValueError: If file is invalid or extraction fails
    """
    try:
        # Decode base64
        file_bytes = base64.b64decode(image_base64)

        # Check if PDF or image
        if _is_pdf(file_bytes):
            # Extract text from PDF
            return _extract_text_from_pdf(file_bytes)
        else:
            # Extract text from image using OCR
            return _extract_text_from_image_ocr(file_bytes)

    except Exception as e:
        raise ValueError(f"Failed to process file: {str(e)}")
