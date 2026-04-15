"""Prompts for document summarization — supports map-reduce pattern."""

# Used per-chunk in map-reduce
CHUNK_SUMMARY_PROMPT = """You are an expert document analyst.

Summarize the following section of a document concisely. Capture all key facts, figures, names, dates, and conclusions.

Section:
{chunk_text}

Summary:"""

# Used to synthesize chunk summaries into final output
SYNTHESIS_PROMPT = """You are an expert document analyst.

Below are summaries of different sections of a document. Combine them into a single, coherent, detailed summary.

Structure your response EXACTLY like this:
## Overview
(2-3 sentence overview of what the document is about)

## Key Points
(bulleted list of the most important points)

## Important Details
(specific figures, dates, names, or data worth noting)

## Conclusion
(final takeaway or conclusion from the document)

Section Summaries:
{section_summaries}

Final Summary:"""

# For short documents that fit in one call
SINGLE_PASS_SUMMARY_PROMPT = """You are an expert document analyst.

Provide a detailed, structured summary of the following document.

Structure your response EXACTLY like this:
## Overview
(2-3 sentence overview of what the document is about)

## Key Points
(bulleted list of the most important points)

## Important Details
(specific figures, dates, names, or data worth noting)

## Conclusion
(final takeaway or conclusion from the document)

Document:
{document_text}

Detailed Summary:"""

# For Excel / spreadsheet data
EXCEL_SUMMARY_PROMPT = """You are an expert data analyst.

Summarize the following spreadsheet data. Describe:
1. What the data represents
2. Key columns and their meaning
3. Notable patterns, totals, or outliers
4. Number of records and data quality observations

Data Schema: {schema}
Sample Data (first rows):
{sample_data}
Total Rows: {total_rows}
Sheet Name: {sheet_name}

Summary:"""
