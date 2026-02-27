"""Receipt OCR module.

Uses EasyOCR (open source, runs locally) to extract text from receipt images.
Text parsing will be handled by Claude AI in a separate step.
"""

import base64

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


def extract_text_from_image(image_base64: str) -> str:
    """Use EasyOCR to extract text from receipt image.

    Args:
        image_base64: Base64-encoded JPEG or PNG image

    Returns:
        Full text extracted from the image

    Raises:
        ValueError: If image is invalid or OCR fails
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_base64)

        # Get EasyOCR reader
        reader = _get_easyocr_reader()

        # Perform text detection
        # detail=0 returns just text, detail=1 returns [bbox, text, confidence]
        result = reader.readtext(image_bytes, detail=0)

        if not result:
            raise ValueError("No text detected in image")

        # Join all text lines with newlines
        full_text = '\n'.join(result)
        return full_text

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")
