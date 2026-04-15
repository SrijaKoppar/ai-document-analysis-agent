"""Skill descriptions used by the dynamic planner to select skills."""

SKILL_DESCRIPTIONS = {
    "extract_text_pdf": (
        "Extract text content from a PDF document. "
        "Use this as the first step for any PDF file."
    ),
    "extract_text_scanned_pdf": (
        "Extract text from scanned/image-based PDFs using OCR. "
        "Use when regular PDF text extraction returns empty or minimal text."
    ),
    "parse_excel_sheet": (
        "Parse an Excel (.xlsx) or CSV file into structured data. "
        "Returns sheet names, column schemas, row counts, and sample data."
    ),
    "classify_document_type": (
        "Classify a document into a category: report, questionnaire, invoice, "
        "spreadsheet, form, research_paper, or other. Use after text extraction."
    ),
    "summarize_long_document": (
        "Generate a detailed structured summary of a document using map-reduce. "
        "Handles long documents by chunking. Best for reports and research papers."
    ),
    "structured_summary": (
        "Produce a JSON-structured summary with sections, key entities, dates, "
        "and important figures. Good for invoices and data-heavy documents."
    ),
    "extract_questions": (
        "Extract all questions from a questionnaire or exam document. "
        "Returns structured JSON with question text, type, options, and section."
    ),
    "extract_form_fields": (
        "Extract form fields, labels, and expected input types from a form document. "
        "Returns structured JSON with field names, types, and sections."
    ),
    "extract_tables": (
        "Detect and extract tables from document text. "
        "Parses tabular data into structured list-of-dict format."
    ),
}

# Used by the planner prompt
def get_skill_list_text():
    """Format skill descriptions for the planner LLM prompt."""
    lines = []
    for name, desc in SKILL_DESCRIPTIONS.items():
        lines.append(f"  - {name}: {desc}")
    return "\n".join(lines)
