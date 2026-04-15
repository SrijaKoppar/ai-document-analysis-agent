"""
Document classifier skill — classifies documents into categories using LLM.
"""
from app.skills.base import Skill
from app.skills.registry import registry
from app.services.llm import llm_service
from app.prompts.classifier_prompt import CLASSIFIER_PROMPT
from app.config import MAX_TEXT_FOR_CLASSIFIER
import json


def classify_document_type(text: str):
    """Classify document into a category using LLM."""
    try:
        trimmed = text[:MAX_TEXT_FOR_CLASSIFIER]
        prompt = CLASSIFIER_PROMPT.format(document_text=trimmed)
        response = llm_service.generate_strict_json(prompt)

        try:
            result = json.loads(response)
            doc_type = result.get("document_type", "other")
        except (json.JSONDecodeError, TypeError):
            # Fallback: try to extract type from raw text
            response_lower = response.lower().strip()
            valid_types = ["report", "questionnaire", "invoice", "spreadsheet",
                          "form", "research_paper", "other"]
            doc_type = "other"
            for vt in valid_types:
                if vt in response_lower:
                    doc_type = vt
                    break

        return {"doc_type": doc_type}

    except Exception as e:
        return {"doc_type": "other", "classification_error": str(e)}


registry.register(
    Skill(
        "classify_document_type",
        "Classify document type (report, questionnaire, invoice, form, etc.)",
        {"text": "str"},
        {"doc_type": "str"},
        classify_document_type,
    )
)