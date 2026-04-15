"""
Verifier sub-agent — cross-checks agent output against source text.
Flags potential hallucinations or omissions.
"""
from app.services.llm import llm_service

VERIFIER_PROMPT = """You are a verification agent. Your job is to check the quality of a document analysis.

Original document text (truncated):
{original_text}

Agent's output:
{agent_output}

Evaluate the output on these criteria:
1. ACCURACY: Does the output accurately reflect the document content? Are there any hallucinated facts?
2. COMPLETENESS: Are any important points from the document missing?
3. QUALITY: Is the output well-structured and useful?

Return ONLY valid JSON in this format:
{{
  "accuracy_score": <1-10>,
  "completeness_score": <1-10>,
  "quality_score": <1-10>,
  "overall_score": <1-10>,
  "issues_found": ["list of specific issues if any"],
  "verification_status": "PASS" or "NEEDS_REVIEW",
  "suggestions": "brief suggestion for improvement if needed"
}}
"""


def verify_output(original_text: str, agent_output: str) -> dict:
    """
    Run verification on agent output against original document.
    Returns verification scores and any flagged issues.
    """
    try:
        # Truncate inputs to fit context
        truncated_text = original_text[:2000]
        truncated_output = str(agent_output)[:2000]

        prompt = VERIFIER_PROMPT.format(
            original_text=truncated_text,
            agent_output=truncated_output,
        )

        response = llm_service.generate_strict_json(prompt)

        # Try to parse
        import json
        try:
            verification = json.loads(response)
            return verification
        except (json.JSONDecodeError, TypeError):
            return {
                "accuracy_score": None,
                "completeness_score": None,
                "quality_score": None,
                "overall_score": None,
                "issues_found": [],
                "verification_status": "PARSE_ERROR",
                "raw_response": response[:500],
            }

    except Exception as e:
        return {
            "verification_status": "ERROR",
            "error": str(e),
        }
