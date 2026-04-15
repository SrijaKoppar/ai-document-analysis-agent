"""
Simple evaluation framework for the Document Analysis Agent.
Run from project root: python3 -m evaluation.evaluator
"""
import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.agent import Agent
from app.services.llm import llm
import app.skills  # noqa: F401  trigger registration


def evaluate():
    """Run evaluation on test documents in data/uploads/"""
    agent = Agent(llm)

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")

    if not os.path.exists(upload_dir):
        print(f"❌ Upload directory not found: {upload_dir}")
        return

    files = [f for f in os.listdir(upload_dir)
             if f.endswith((".pdf", ".xlsx", ".xls", ".csv"))]

    if not files:
        print(f"⚠️  No test files found in {upload_dir}")
        print("   Add PDF/Excel/CSV files to data/uploads/ and re-run.")
        return

    print("=" * 70)
    print("  Document Analysis Agent — Evaluation")
    print("=" * 70)

    results = []

    for filename in files:
        file_path = os.path.join(upload_dir, filename)
        print(f"\n{'─' * 70}")
        print(f"📄 Testing: {filename}")
        print(f"{'─' * 70}")

        queries = [
            "Summarize this document",
            "Extract all questions from this document",
        ]

        for query in queries:
            print(f"\n  Query: {query}")
            start = time.time()

            try:
                result = agent.run(file_path, query)
                elapsed = time.time() - start

                entry = {
                    "file": filename,
                    "query": query,
                    "time_seconds": round(elapsed, 1),
                    "doc_type": result.get("doc_type", "?"),
                    "plan": result.get("plan", []),
                    "has_summary": "summary" in result,
                    "has_questions": "questions" in result,
                    "has_error": "error" in result,
                    "verification_status": result.get("verification", {}).get("verification_status", "N/A"),
                }
                results.append(entry)

                print(f"  ✅ Completed in {elapsed:.1f}s")
                print(f"     Doc type: {entry['doc_type']}")
                print(f"     Plan: {entry['plan']}")
                print(f"     Has summary: {entry['has_summary']}")
                print(f"     Has questions: {entry['has_questions']}")
                print(f"     Verification: {entry['verification_status']}")

                if entry["has_error"]:
                    print(f"     ❌ Error: {result['error']}")

            except Exception as e:
                elapsed = time.time() - start
                print(f"  ❌ Failed in {elapsed:.1f}s: {str(e)}")
                results.append({
                    "file": filename,
                    "query": query,
                    "time_seconds": round(elapsed, 1),
                    "error": str(e),
                })

    # ── Summary ──────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("  EVALUATION SUMMARY")
    print(f"{'=' * 70}")

    total = len(results)
    passed = sum(1 for r in results if not r.get("has_error") and not r.get("error"))
    failed = total - passed
    avg_time = sum(r.get("time_seconds", 0) for r in results) / max(total, 1)

    print(f"  Total tests:  {total}")
    print(f"  Passed:       {passed}")
    print(f"  Failed:       {failed}")
    print(f"  Avg time:     {avg_time:.1f}s per query")
    print(f"  Pass rate:    {passed/max(total,1)*100:.0f}%")

    # Save results
    report_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {report_path}")


if __name__ == "__main__":
    evaluate()
