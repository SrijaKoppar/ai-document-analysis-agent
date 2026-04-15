"""
Form field extractor skill — extracts structured form fields from documents.
"""
from app.skills.base import Skill
from app.skills.registry import registry
from app.services.llm import llm_service
from app.config import MAX_TEXT_FOR_SINGLE_CALL
from app.prompts.question_prompt import FORM_FIELD_EXTRACTION_PROMPT


def extract_form_fields(text: str):
    """Extract form fields with labels, types, and values."""
    try:
        trimmed = text[:MAX_TEXT_FOR_SINGLE_CALL]
        prompt = FORM_FIELD_EXTRACTION_PROMPT.format(document_text=trimmed)
        response = llm_service.generate_strict_json(prompt)

        return {"form_fields": response}

    except Exception as e:
        return {"form_fields": f"Error: {str(e)}"}


registry.register(
    Skill(
        "extract_form_fields",
        "Extract structured form fields from document with field names, types, and sections",
        {"text": "str"},
        {"form_fields": "str"},
        extract_form_fields,
    )
)