"""
Structured logger for agent pipeline visibility.
Prints step-by-step actions so the demo audience can follow along.
"""
import time
from datetime import datetime

# ANSI colors for terminal output
_COLORS = {
    "STEP":    "\033[96m",   # cyan
    "OK":      "\033[92m",   # green
    "WARN":    "\033[93m",   # yellow
    "ERROR":   "\033[91m",   # red
    "RESET":   "\033[0m",
    "BOLD":    "\033[1m",
}


def _ts():
    return datetime.now().strftime("%H:%M:%S")


def step(msg: str):
    print(f"{_COLORS['STEP']}[{_ts()}] ▶ {msg}{_COLORS['RESET']}")


def ok(msg: str):
    print(f"{_COLORS['OK']}[{_ts()}] ✅ {msg}{_COLORS['RESET']}")


def warn(msg: str):
    print(f"{_COLORS['WARN']}[{_ts()}] ⚠️  {msg}{_COLORS['RESET']}")


def error(msg: str):
    print(f"{_COLORS['ERROR']}[{_ts()}] ❌ {msg}{_COLORS['RESET']}")


class AgentLogger:
    """Context-manager style logger that tracks timing per step."""

    def __init__(self):
        self.logs = []

    def log_step(self, step_name: str, detail: str = ""):
        entry = {
            "timestamp": _ts(),
            "step": step_name,
            "detail": detail,
        }
        self.logs.append(entry)
        step(f"{step_name}  {detail}")

    def log_result(self, step_name: str, detail: str = ""):
        entry = {
            "timestamp": _ts(),
            "step": step_name,
            "detail": detail,
            "status": "ok",
        }
        self.logs.append(entry)
        ok(f"{step_name}  {detail}")

    def log_error(self, step_name: str, detail: str = ""):
        entry = {
            "timestamp": _ts(),
            "step": step_name,
            "detail": detail,
            "status": "error",
        }
        self.logs.append(entry)
        error(f"{step_name}  {detail}")

    def get_logs(self):
        return self.logs
