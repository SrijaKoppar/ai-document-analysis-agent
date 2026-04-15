"""
Table parser skill — detects and extracts tables from document text.
"""
from app.skills.base import Skill
from app.skills.registry import registry
import re


def extract_tables(text: str):
    """Detect and extract tabular data from text."""
    try:
        tables = []
        lines = text.split("\n")
        current_table = []
        table_count = 0

        for line in lines:
            stripped = line.strip()

            # Detect table-like lines (pipe-delimited, tab-delimited, or consistent spacing)
            is_table_line = (
                "|" in stripped
                or "\t" in line
                or bool(re.match(r"^[\w\s]+\s{2,}[\w\s]+", stripped))
            )
            is_separator = bool(re.match(r"^[\-\+\|=\s]+$", stripped)) and len(stripped) > 3

            if is_table_line or is_separator:
                current_table.append(stripped)
            else:
                if len(current_table) >= 2:  # minimum 2 lines to be a table
                    table_count += 1
                    parsed = _parse_table_lines(current_table, table_count)
                    if parsed:
                        tables.append(parsed)
                current_table = []

        # Don't forget the last table if file ends with one
        if len(current_table) >= 2:
            table_count += 1
            parsed = _parse_table_lines(current_table, table_count)
            if parsed:
                tables.append(parsed)

        return {
            "tables": tables,
            "total_tables": len(tables),
        }

    except Exception as e:
        return {"tables": [], "total_tables": 0, "error": str(e)}


def _parse_table_lines(lines, table_number):
    """Parse a block of table-like lines into structured data."""
    # Filter out separator lines
    data_lines = [l for l in lines if not re.match(r"^[\-\+\|=\s]+$", l)]

    if not data_lines:
        return None

    # Determine delimiter
    if "|" in data_lines[0]:
        delimiter = "|"
    elif "\t" in data_lines[0]:
        delimiter = "\t"
    else:
        delimiter = None  # whitespace

    rows = []
    for line in data_lines:
        if delimiter:
            cells = [c.strip() for c in line.split(delimiter) if c.strip()]
        else:
            cells = line.split()
        if cells:
            rows.append(cells)

    if not rows:
        return None

    # First row as headers if it looks like one
    headers = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []

    return {
        "table_number": table_number,
        "headers": headers,
        "rows": data_rows,
        "row_count": len(data_rows),
    }


registry.register(
    Skill(
        "extract_tables",
        "Detect and extract tables from document text into structured format",
        {"text": "str"},
        {"tables": "list", "total_tables": "int"},
        extract_tables,
    )
)