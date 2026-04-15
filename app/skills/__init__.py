"""
Skill registration — imports all skill modules so they self-register
with the global SkillRegistry on startup.
"""
from app.skills.ingestion import pdf_reader, ocr_reader, excel_reader
from app.skills.processing import table_parser
from app.skills.understanding import (
    summarizer,
    structured_summarizer,
    question_extractor,
    classifier,
    form_extractor,
)