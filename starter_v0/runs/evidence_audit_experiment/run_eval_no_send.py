"""Run the unchanged evaluator with Telegram execution replaced by an offline stub."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import run_eval


def block_send(text: str = "", confirmed: bool = False) -> dict:
    return {"tool": "send", "status": "blocked_for_eval", "message": "No Telegram message is sent by this evaluation."}


run_eval.TOOL_FUNCTIONS["send"] = block_send
run_eval.main()
