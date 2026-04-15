"""
Excel & CSV reader skill — handles .xlsx, .xls, and .csv files.
Enumerates sheets, detects column types, returns structured data.
"""
from app.skills.base import Skill
from app.skills.registry import registry
import pandas as pd
import json


def parse_excel_sheet(file_path: str):
    """Parse Excel or CSV file into structured sheet-level summaries."""
    try:
        ext = file_path.rsplit(".", 1)[-1].lower()

        if ext == "csv":
            sheets = {"Sheet1": pd.read_csv(file_path)}
        elif ext in ("xlsx", "xls"):
            xls = pd.ExcelFile(file_path)
            sheets = {name: xls.parse(name) for name in xls.sheet_names}
        else:
            return {"error": f"Unsupported file type: .{ext}"}

        result = {
            "file_path": file_path,
            "total_sheets": len(sheets),
            "sheets": [],
        }

        all_text_parts = []

        for sheet_name, df in sheets.items():
            # Clean up: drop fully empty rows/cols
            df = df.dropna(how="all").dropna(axis=1, how="all")

            columns = list(df.columns)
            dtypes = {col: str(df[col].dtype) for col in columns}
            row_count = len(df)

            # Sample data (first 5 rows)
            sample = df.head(5).fillna("").to_dict(orient="records")

            # Basic stats for numeric columns
            stats = {}
            for col in df.select_dtypes(include=["number"]).columns:
                stats[col] = {
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "mean": round(float(df[col].mean()), 2) if not df[col].isna().all() else None,
                    "missing": int(df[col].isna().sum()),
                }

            # Missing value count per column
            missing = {col: int(df[col].isna().sum()) for col in columns if df[col].isna().sum() > 0}

            sheet_info = {
                "sheet_name": sheet_name,
                "row_count": row_count,
                "column_count": len(columns),
                "columns": columns,
                "column_types": dtypes,
                "sample_data": sample,
                "numeric_stats": stats,
                "missing_values": missing,
            }
            result["sheets"].append(sheet_info)

            # Build text representation for LLM summarization
            text_repr = f"Sheet: {sheet_name} ({row_count} rows, {len(columns)} columns)\n"
            text_repr += f"Columns: {', '.join(columns)}\n"
            if stats:
                text_repr += f"Numeric stats: {json.dumps(stats, default=str)}\n"
            if missing:
                text_repr += f"Missing values: {json.dumps(missing)}\n"
            text_repr += f"Sample data:\n{df.head(5).to_string(index=False)}\n"
            all_text_parts.append(text_repr)

        # Provide a "text" key so downstream skills (summarizer) can consume it
        result["text"] = "\n\n".join(all_text_parts)
        result["data"] = sheets[list(sheets.keys())[0]].fillna("").to_dict(orient="records")

        return result

    except Exception as e:
        return {"error": f"Excel parsing error: {str(e)}"}


registry.register(
    Skill(
        "parse_excel_sheet",
        "Parse Excel (.xlsx) or CSV file into structured data with per-sheet analysis",
        {"file_path": "str"},
        {"sheets": "list", "text": "str", "data": "list"},
        parse_excel_sheet,
    )
)