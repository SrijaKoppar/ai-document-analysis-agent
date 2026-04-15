"""
Question extractor skill — extracts structured questions from questionnaire/exam docs.
Returns JSON with question text, type, options, section, and required status.
"""
from app.skills.base import Skill
from app.skills.registry import registry
from app.services.llm import llm_service
from app.config import MAX_TEXT_FOR_SINGLE_CALL
from app.prompts.question_prompt import QUESTION_EXTRACTION_PROMPT


def extract_questions(text: str):
    """Extract all questions from a document with structured metadata."""
    try:
        trimmed_text = text[:MAX_TEXT_FOR_SINGLE_CALL]
        prompt = QUESTION_EXTRACTION_PROMPT.format(document_text=trimmed_text)
        response = llm_service.generate_strict_json(prompt)

        return {"questions": response}

    except Exception as e:
        return {"questions": f"Error extracting questions: {str(e)}"}


question_extractor_skill = Skill(
    name="extract_questions",
    description="Extract all questions from a questionnaire/exam with type, options, and section info",
    input_schema={"text": "string"},
    output_schema={"questions": "str"},
    func=extract_questions,
)

registry.register(question_extractor_skill)