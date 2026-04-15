"""Prompts for extracting questions from questionnaire/form documents."""

QUESTION_EXTRACTION_PROMPT = """You are an AI that extracts questions from documents.

Analyze the document text below and extract ALL questions found.

For each question, provide:
- question_number: sequential number
- text: the full question text
- type: one of "MCQ", "descriptive", "yes_no", "likert_scale", "numeric", "fill_in_blank"
- options: list of answer choices if MCQ/likert, otherwise empty list
- section: the section or heading the question falls under (if identifiable), otherwise "General"
- required: true if the question appears mandatory, false otherwise

Return ONLY valid JSON in this format:
{{
  "total_questions": <number>,
  "questions": [
    {{
      "question_number": 1,
      "text": "What is your name?",
      "type": "descriptive",
      "options": [],
      "section": "Personal Information",
      "required": true
    }}
  ]
}}

Document text:
{document_text}
"""

FORM_FIELD_EXTRACTION_PROMPT = """You are an AI that extracts form fields from documents.

Analyze the document and extract all form fields, labels, and their expected values.

Return ONLY valid JSON in this format:
{{
  "total_fields": <number>,
  "fields": [
    {{
      "field_name": "Full Name",
      "field_type": "text",
      "current_value": "",
      "section": "Personal Details",
      "required": true
    }}
  ]
}}

Field types can be: "text", "number", "date", "email", "phone", "checkbox", "dropdown", "textarea"

Document text:
{document_text}
"""
