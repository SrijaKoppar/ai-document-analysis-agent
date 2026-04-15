"""
Quick smoke-test for the LLM agent.
Run from project root:  python3 test_llm.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("  LLM Agent - Smoke Test")
print("=" * 60)

# ── 1. Import ────────────────────────────────────────────────
print("\n[1/4] Importing LLMService...")
try:
    from app.services.llm import LLMService, llm_service, llm
    print("      ✅ Import OK")
except Exception as e:
    print(f"      ❌ Import FAILED: {e}")
    sys.exit(1)

# ── 2. Instantiation ─────────────────────────────────────────
print("\n[2/4] Checking singleton instance...")
print(f"      Model : {llm_service.model}")
print(f"      ✅ llm_service ready")

# ── 3. Basic generate() ──────────────────────────────────────
print("\n[3/4] Calling generate() — basic prompt...")
response = llm_service.generate("Say 'hello' in one word.")
if response.startswith("LLM Error"):
    print(f"      ❌ LLM Error: {response}")
else:
    print(f"      ✅ Response: {response[:200]}")

# ── 4. generate_strict_json() ────────────────────────────────
print("\n[4/4] Calling generate_strict_json() — JSON prompt...")
json_response = llm_service.generate_strict_json(
    'Return this exact JSON: {"status": "ok", "model": "gemma"}'
)
if '"error"' in json_response and "LLM Error" in json_response:
    print(f"      ❌ JSON Error: {json_response}")
else:
    print(f"      ✅ JSON Response: {json_response[:300]}")

print("\n" + "=" * 60)
print("  Done.")
print("=" * 60)
