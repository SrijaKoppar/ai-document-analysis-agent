"""
Dynamic LLM-based planner — selects skills based on document type and user query.
Falls back to keyword-based routing if LLM response is malformed.
"""
import json
from app.constants.skill_descriptions import get_skill_list_text


PLANNER_PROMPT = """You are a planning agent for a document analysis system.

Given a document type and a user query, select which skills to execute and in what order.

Available skills:
{skill_list}

Document type: {doc_type}
User query: {user_query}

Rules:
- Return ONLY a JSON array of skill names to execute in order
- Do NOT include "extract_text_pdf" or "classify_document_type" — those are already done
- Choose the most relevant skills for the query
- If the query asks for a summary, include "summarize_long_document"
- If the query asks about questions or questionnaire, include "extract_questions"
- If the query asks about form fields, include "extract_form_fields"
- If the query asks about tables, include "extract_tables"
- You can include multiple skills if the query requires it

Example response:
["summarize_long_document"]

Another example:
["extract_questions", "summarize_long_document"]

Return ONLY the JSON array, nothing else.
"""


def create_plan(doc_type, user_query, skills, llm):
    """
    Create an execution plan using LLM-based dynamic planning.
    Falls back to keyword matching if LLM output is malformed.
    """
    try:
        skill_list = get_skill_list_text()
        prompt = PLANNER_PROMPT.format(
            skill_list=skill_list,
            doc_type=doc_type,
            user_query=user_query,
        )

        response = llm(prompt)

        # Try to parse JSON array from response
        plan = _parse_plan(response, skills)
        if plan:
            return plan

    except Exception:
        pass

    # Fallback: keyword-based routing
    return _keyword_fallback(doc_type, user_query)


def _parse_plan(response, available_skills):
    """Try to extract a valid skill list from LLM response."""
    response = response.strip()

    # Try direct JSON parse
    try:
        plan = json.loads(response)
        if isinstance(plan, list) and all(isinstance(s, str) for s in plan):
            # Validate all skills exist
            valid = [s for s in plan if available_skills.get(s)]
            if valid:
                return valid
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find JSON array in the response text
    import re
    match = re.search(r'\[.*?\]', response, re.DOTALL)
    if match:
        try:
            plan = json.loads(match.group())
            if isinstance(plan, list):
                valid = [s for s in plan if isinstance(s, str) and available_skills.get(s)]
                if valid:
                    return valid
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def _keyword_fallback(doc_type, user_query):
    """Keyword-based skill selection as fallback."""
    query = user_query.lower()
    plan = []

    if "question" in query or doc_type == "questionnaire":
        plan.append("extract_questions")

    if "form" in query or "field" in query or doc_type == "form":
        plan.append("extract_form_fields")

    if "table" in query:
        plan.append("extract_tables")

    if "summary" in query or "summarize" in query or not plan:
        plan.append("summarize_long_document")

    return plan