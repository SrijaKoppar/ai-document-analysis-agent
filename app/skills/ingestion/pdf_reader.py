"""
PDF reader skill — extracts text from PDFs with page tracking.
Auto-falls back to OCR when text extraction returns empty.
"""
from app.skills.base import Skill
from app.skills.registry import registry
import PyPDF2


def pdf_reader(file_path: str):
    """Extract text from a PDF, with page-level tracking for citations."""
    try:
        pages = []
        full_text = ""

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                pages.append({
                    "page_number": i + 1,
                    "text": page_text.strip(),
                    "char_count": len(page_text.strip()),
                })
                if page_text.strip():
                    full_text += f"\n--- Page {i + 1} ---\n{page_text.strip()}\n"

        # If no text extracted, this is likely a scanned PDF
        if not full_text.strip():
            # Try OCR fallback
            try:
                from app.skills.ingestion.ocr_reader import extract_text_scanned_pdf
                ocr_result = extract_text_scanned_pdf(file_path)
                return {
                    "text": ocr_result.get("text", ""),
                    "pages": pages,
                    "total_pages": len(pages),
                    "extraction_method": "ocr",
                }
            except Exception:
                return {
                    "text": "No text could be extracted. Document may be scanned/image-based.",
                    "pages": pages,
                    "total_pages": len(pages),
                    "extraction_method": "failed",
                }

        return {
            "text": full_text.strip(),
            "pages": pages,
            "total_pages": len(pages),
            "extraction_method": "text",
        }

    except Exception as e:
        return {"text": f"Error extracting PDF: {str(e)}", "extraction_method": "error"}


pdf_reader_skill = Skill(
    name="extract_text_pdf",
    description="Extract text from a PDF document with page tracking and OCR fallback",
    input_schema={"file_path": "string"},
    output_schema={"text": "string", "pages": "list", "total_pages": "int"},
    func=pdf_reader,
)

registry.register(pdf_reader_skill)