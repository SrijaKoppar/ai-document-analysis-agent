"""
Summarizer skill — map-reduce summarization for long documents.
Short docs get single-pass; long docs get chunked → summarized → synthesized.
"""
from app.skills.base import Skill
from app.skills.registry import registry
from app.services.llm import llm
from app.config import MAX_CHUNK_SIZE, CHUNK_OVERLAP, MAX_TEXT_FOR_SINGLE_CALL
from app.prompts.summary_prompt import (
    CHUNK_SUMMARY_PROMPT,
    SYNTHESIS_PROMPT,
    SINGLE_PASS_SUMMARY_PROMPT,
)


def _chunk_text(text, chunk_size=MAX_CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def summarize_long_document(text: str):
    """Summarize a document using map-reduce for long texts."""
    try:
        text = text.strip()
        if not text:
            return {"summary": "No text provided for summarization."}

        # Short document: single pass
        if len(text) <= MAX_TEXT_FOR_SINGLE_CALL:
            prompt = SINGLE_PASS_SUMMARY_PROMPT.format(document_text=text)
            summary = llm(prompt)
            return {
                "summary": summary.strip(),
                "method": "single_pass",
                "chunks_processed": 1,
            }

        # Long document: map-reduce
        chunks = _chunk_text(text)
        chunk_summaries = []

        for i, chunk in enumerate(chunks):
            prompt = CHUNK_SUMMARY_PROMPT.format(chunk_text=chunk)
            chunk_summary = llm(prompt)
            chunk_summaries.append(f"Section {i + 1}:\n{chunk_summary.strip()}")

        # Synthesize all chunk summaries
        combined = "\n\n".join(chunk_summaries)

        # If combined summaries are still too long, do another round
        if len(combined) > MAX_TEXT_FOR_SINGLE_CALL:
            combined = combined[:MAX_TEXT_FOR_SINGLE_CALL]

        synthesis_prompt = SYNTHESIS_PROMPT.format(section_summaries=combined)
        final_summary = llm(synthesis_prompt)

        return {
            "summary": final_summary.strip(),
            "method": "map_reduce",
            "chunks_processed": len(chunks),
        }

    except Exception as e:
        return {"summary": f"Summarization error: {str(e)}"}


registry.register(
    Skill(
        "summarize_long_document",
        "Generate a detailed structured summary using map-reduce for long documents",
        {"text": "str"},
        {"summary": "str", "method": "str", "chunks_processed": "int"},
        summarize_long_document,
    )
)