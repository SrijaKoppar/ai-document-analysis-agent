"""
Structured summarizer — produces JSON-formatted summary with sections,
key entities, dates, and figures. Ideal for invoices and data-heavy docs.
"""
from app.skills.base import Skill
from app.skills.registry import registry
from app.services.llm import llm_service
from app.config import MAX_TEXT_FOR_SINGLE_CALL


STRUCTURED_SUMMARY_PROMPT = """You are a document analysis AI.

Analyze the following document and produce a structured summary.

Return ONLY valid JSON in this exact format:
{{
  "title": "Document title or best guess",
  "document_type": "report/invoice/form/questionnaire/research_paper/other",
  "sections": [
    {{
      "heading": "Section name",
      "content": "Brief summary of this section"
    }}
  ],
  "key_entities": ["list of important names, organizations, products mentioned"],
  "key_dates": ["list of important dates mentioned"],
  "key_figures": ["list of important numbers, amounts, percentages"],
  "main_findings": "2-3 sentence summary of the main conclusions or purpose"
}}

Document text:
{document_text}
"""


def structured_summary(text: str):
    """Produce a JSON-structured summary with entities, dates, and figures."""
    try:
        trimmed = text[:MAX_TEXT_FOR_SINGLE_CALL]
        prompt = STRUCTURED_SUMMARY_PROMPT.format(document_text=trimmed)
        response = llm_service.generate_strict_json(prompt)

        return {
            "structured_summary": response,
        }

    except Exception as e:
        return {"structured_summary": f"Error: {str(e)}"}


registry.register(
    Skill(
        "structured_summary",
        "Produce a JSON-structured summary with sections, entities, dates, and figures",
        {"text": "str"},
        {"structured_summary": "str"},
        structured_summary,
    )
)
