"""
OCR reader skill — extracts text from scanned/image-based PDFs.
Uses pytesseract + pdf2image if available, otherwise graceful fallback.
"""
from app.skills.base import Skill
from app.skills.registry import registry


def extract_text_scanned_pdf(file_path: str):
    """Extract text from scanned PDFs using OCR."""
    try:
        # Try importing OCR dependencies
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        return {
            "text": (
                "[OCR Not Available] pytesseract and pdf2image are not installed. "
                "Install with: pip install pytesseract pdf2image\n"
                "Also requires Tesseract binary: brew install tesseract"
            ),
            "ocr_available": False,
        }

    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path, dpi=200)
        all_text = []

        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            if page_text.strip():
                all_text.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

        full_text = "\n\n".join(all_text)

        if not full_text.strip():
            return {
                "text": "OCR could not extract any text from this document.",
                "ocr_available": True,
                "pages_processed": len(images),
            }

        return {
            "text": full_text,
            "ocr_available": True,
            "pages_processed": len(images),
        }

    except Exception as e:
        return {
            "text": f"OCR Error: {str(e)}",
            "ocr_available": True,
        }


registry.register(
    Skill(
        "extract_text_scanned_pdf",
        "Extract text from scanned/image-based PDFs using OCR (Tesseract)",
        {"file_path": "str"},
        {"text": "str", "ocr_available": "bool"},
        extract_text_scanned_pdf,
    )
)