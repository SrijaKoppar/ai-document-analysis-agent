"""
Centralized configuration for the Document Analysis Agent.
"""
import os

# ── LLM ──────────────────────────────────────────────────────
LLM_MODEL = os.getenv("LLM_MODEL", "llama3:latest")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── File Handling ─────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv"}

# ── Text Processing ──────────────────────────────────────────
MAX_CHUNK_SIZE = 3000          # chars per chunk for map-reduce
CHUNK_OVERLAP = 200            # overlap between chunks
MAX_TEXT_FOR_CLASSIFIER = 2000 # chars sent to classifier
MAX_TEXT_FOR_SINGLE_CALL = 4000  # max chars for a single LLM call

# ── Agent ─────────────────────────────────────────────────────
ENABLE_VERIFIER = True         # run verifier sub-agent after main output
MAX_PLAN_RETRIES = 2           # retry parsing planner output
