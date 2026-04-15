CLASSIFIER_PROMPT = """
You are a document classification AI.

Your task is to classify the given document into ONE of the following categories:

- report
- questionnaire
- invoice
- spreadsheet
- form
- research_paper
- other

Return ONLY a valid JSON object in this format:
{
  "document_type": "one_of_the_above"
}

Do NOT explain anything.
Do NOT add extra text.

Document content:
{document_text}
"""