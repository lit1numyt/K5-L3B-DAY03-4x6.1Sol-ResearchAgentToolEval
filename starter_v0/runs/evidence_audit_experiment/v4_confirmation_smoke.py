"""Real-model three-turn smoke test; the Telegram tool is replaced by an offline stub."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools

load_lab_env(ROOT)
functions = dict(TOOL_FUNCTIONS)
functions["send"] = lambda text="", confirmed=False: {"tool": "send", "status": "blocked_for_eval"}
provider = make_provider("openai")
declared = to_openai_tools(load_tool_declarations(ROOT / "artifacts/tools_v4.yaml"))
messages = [{"role": "system", "content": (ROOT / "artifacts/system_prompt_v4.md").read_text(encoding="utf-8")}]
user_turns = ["Đăng bản tin này lên Telegram giúp mình.", "Có.", "Nội dung bản tin: Hôm nay nhóm hoàn thành benchmark."]
outputs = []
for user in user_turns:
    messages.append({"role": "user", "content": user})
    result = run_model_tool_loop(provider=provider, messages=messages, tools=declared, model=None,
                                 max_tool_rounds=3, tool_functions=functions)
    outputs.append({"user": user, "result": result})
    messages.append({"role": "assistant", "content": result.get("assistant_text", "")})
    print("user:", user)
    print("calls:", [(e.get("tool"), e.get("args", {}).get("response_type")) for e in result.get("tool_events", [])])
    print("assistant:", result.get("assistant_text", ""))

target = Path(__file__).with_name("v4_confirmation_smoke_result.json")
target.write_text(json.dumps({"note": "Real model; Telegram execution blocked", "turns": outputs}, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved:", target)
