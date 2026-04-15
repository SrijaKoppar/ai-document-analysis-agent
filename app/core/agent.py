"""
Main Agent — orchestrates the full document analysis pipeline.
Supports PDF, Excel, and CSV files.
Pipeline: Ingest → Classify → Plan → Execute → Verify
"""
import os

from app.core.executor import execute_plan
from app.skills.registry import registry
from app.core.planner import create_plan
from app.core.verifier import verify_output
from app.utils.logger import AgentLogger
from app.config import ENABLE_VERIFIER


class Agent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, file_path: str, user_query: str = "Summarize this document"):
        """
        Full agent pipeline:
        1. Detect file type & extract content
        2. Classify document type
        3. Plan which skills to run
        4. Execute the plan
        5. (Optional) Verify the output
        """
        logger = AgentLogger()
        logger.log_step("Agent started", f"File: {os.path.basename(file_path)}")
        logger.log_step("User query", user_query)

        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

        # ── Step 1: Extract content ─────────────────────────────
        if ext in ("xlsx", "xls", "csv"):
            logger.log_step("File type", f"Spreadsheet (.{ext})")
            extract_skill = registry.get("parse_excel_sheet")
            if not extract_skill:
                return {"error": "parse_excel_sheet skill not registered"}

            extract_output = extract_skill.run(file_path=file_path)
            text = extract_output.get("text", "")
            doc_type = "spreadsheet"

            if extract_output.get("error"):
                return {"error": extract_output["error"], "logs": logger.get_logs()}

            logger.log_result("Excel parsed",
                f"{extract_output.get('total_sheets', 0)} sheets found")

        elif ext == "pdf":
            logger.log_step("File type", "PDF")
            extract_skill = registry.get("extract_text_pdf")
            if not extract_skill:
                return {"error": "extract_text_pdf skill not registered"}

            extract_output = extract_skill.run(file_path=file_path)
            text = extract_output.get("text", "")
            extraction_method = extract_output.get("extraction_method", "unknown")

            logger.log_result("Text extracted",
                f"{len(text)} chars via {extraction_method}, "
                f"{extract_output.get('total_pages', '?')} pages")

            # Step 2: Classify
            logger.log_step("Classifying document", "")
            classify_skill = registry.get("classify_document_type")
            if classify_skill:
                classification = classify_skill.run(text=text)
                doc_type = classification.get("doc_type", "other")
            else:
                doc_type = "other"

            logger.log_result("Document classified", doc_type)

        else:
            return {"error": f"Unsupported file type: .{ext}", "logs": logger.get_logs()}

        # ── Step 3: Plan ─────────────────────────────────────────
        logger.log_step("Planning", f"doc_type={doc_type}, query={user_query}")

        plan = create_plan(
            doc_type=doc_type,
            user_query=user_query,
            skills=registry.list_skills(),
            llm=self.llm,
        )

        logger.log_result("Plan created", str(plan))

        # ── Step 4: Execute ──────────────────────────────────────
        logger.log_step("Executing plan", f"{len(plan)} skills")

        context = {"text": text, "file_path": file_path}

        # Merge additional data from extraction (sheets info, pages, etc.)
        if ext in ("xlsx", "xls", "csv"):
            context.update({
                k: v for k, v in extract_output.items()
                if k not in ("text",)
            })

        result = execute_plan(plan, context, logger)

        # ── Step 5: Verify (optional) ─────────────────────────────
        verification = None
        if ENABLE_VERIFIER:
            logger.log_step("Running verifier", "")
            # Build a string from key outputs to verify
            output_to_verify = ""
            if "summary" in result:
                output_to_verify += f"Summary: {result['summary']}\n"
            if "questions" in result:
                output_to_verify += f"Questions: {str(result['questions'])[:500]}\n"
            if "form_fields" in result:
                output_to_verify += f"Form fields: {str(result['form_fields'])[:500]}\n"

            if output_to_verify:
                verification = verify_output(text, output_to_verify)
                logger.log_result("Verification",
                    verification.get("verification_status", "unknown"))

        # ── Build response ────────────────────────────────────────
        response = {
            "file_name": os.path.basename(file_path),
            "file_type": ext,
            "doc_type": doc_type,
            "plan": plan,
            "available_skills": list(registry.list_skills().keys()),
        }

        # Include relevant outputs
        for key in ("summary", "structured_summary", "questions",
                     "form_fields", "tables", "total_tables",
                     "sheets", "total_sheets",
                     "method", "chunks_processed",
                     "extraction_method", "total_pages"):
            if key in result:
                response[key] = result[key]

        if verification:
            response["verification"] = verification

        response["logs"] = logger.get_logs()

        return response