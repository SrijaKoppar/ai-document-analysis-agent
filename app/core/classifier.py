import json
from app.services.llm import llm_service
from app.prompts.classifier_prompt import CLASSIFIER_PROMPT


def classify_document(text: str) -> str:
    """
    Classify document into predefined categories using LLM.
    Returns: document_type (str)
    """

    trimmed_text = text[:2000]

    prompt = CLASSIFIER_PROMPT.format(document_text=trimmed_text)

    response = llm_service.generate(prompt)

    try:
        result = json.loads(response)
        return result.get("document_type", "other")
    except Exception:
        return "other"