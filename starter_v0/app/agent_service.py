from __future__ import annotations

import os
import queue
import threading
from pathlib import Path
from typing import Any

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from tools import TOOL_FUNCTIONS
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parents[1]
load_lab_env(ROOT)


class AgentService:
    """Thin web-facing adapter around the existing CLI agent loop."""

    def __init__(self) -> None:
        available = next((name for name, key in [("openai", "OPENAI_API_KEY"), ("openrouter", "OPENROUTER_API_KEY"), ("anthropic", "ANTHROPIC_API_KEY"), ("gemini", "GEMINI_API_KEY")] if os.getenv(key)), "openai")
        self.provider_name = os.getenv("BOT_PROVIDER") or os.getenv("PROVIDER") or available
        self.model = os.getenv("BOT_MODEL") or os.getenv("MODEL") or None
        self.history_window = self._positive_int("HISTORY_WINDOW", 5, maximum=50)
        self.max_tool_rounds = self._positive_int("MAX_TOOL_ROUNDS", 4, maximum=20)
        self.system_prompt_path = self._path_env("SYSTEM_PROMPT_PATH", ROOT / "artifacts" / "system_prompt.md")
        self.tools_path = self._path_env("TOOLS_PATH", ROOT / "artifacts" / "tools.yaml")
        self._provider: Any | None = None
        self._tools: list[dict[str, Any]] | None = None
        self.disable_delivery = os.getenv("WEB_DEMO_ENABLE_SEND", "0").lower() not in {"1", "true", "yes"}

    @staticmethod
    def _positive_int(name: str, default: int, *, maximum: int) -> int:
        try:
            value = int(os.getenv(name, str(default)))
        except ValueError:
            return default
        return min(max(value, 1), maximum)

    @staticmethod
    def _path_env(name: str, default: Path) -> Path:
        value = os.getenv(name)
        return (ROOT / value).resolve() if value and not Path(value).is_absolute() else Path(value) if value else default

    def _get_provider(self) -> Any:
        if self._provider is None:
            self._provider = make_provider(self.provider_name)
        return self._provider

    def _get_tools(self) -> list[dict[str, Any]]:
        if self._tools is None:
            declarations = load_tool_declarations(self.tools_path)
            self._tools = to_openai_tools(declarations)
        return self._tools

    def _get_tool_functions(self) -> dict[str, Any]:
        functions = dict(TOOL_FUNCTIONS)
        if self.disable_delivery:
            functions["send"] = lambda **kwargs: {
                "tool": "send_telegram",
                "status": "needs_confirmation",
                "awaiting_user": True,
                "message": "Telegram delivery is disabled in the web demo. No message was sent.",
            }
        return functions

    def metadata(self) -> dict[str, Any]:
        label = "web-demo"
        for snapshot in sorted((ROOT / "artifacts").glob("system_prompt_v*.md"), reverse=True):
            candidate = snapshot.stem.removeprefix("system_prompt_")
            tool_snapshot = ROOT / "artifacts" / f"tools_{candidate}.yaml"
            if tool_snapshot.is_file() and snapshot.read_bytes() == self.system_prompt_path.read_bytes() and tool_snapshot.read_bytes() == self.tools_path.read_bytes():
                label = candidate
                break
        version = build_artifact_version(label, self.system_prompt_path, self.tools_path)
        key_name = {"openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}.get(self.provider_name)
        return {
            "provider": self.provider_name,
            "model": self.model or getattr(self._get_provider(), "default_model", None),
            **artifact_version_dict(version),
            "system_prompt": self.system_prompt_path.name,
            "tools": self.tools_path.name,
            "history_window": self.history_window,
            "max_tool_rounds": self.max_tool_rounds,
            "delivery_mode": "disabled_for_web_demo" if self.disable_delivery else "enabled_by_configuration",
            "provider_configured": bool(os.getenv(key_name)) if key_name else self.provider_name == "ollama",
        }

    def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
        history = trim_history(messages, self.history_window)
        return run_model_tool_loop(
            provider=self._get_provider(),
            messages=[{"role": "system", "content": system_prompt}, *history],
            tools=self._get_tools(),
            model=self.model,
            max_tool_rounds=self.max_tool_rounds,
            tool_functions=self._get_tool_functions(),
        )

    def stream_chat(self, messages: list[dict[str, str]]):
        """Yield progress events while preserving the existing blocking agent loop."""
        events: queue.Queue[dict[str, Any]] = queue.Queue()

        def worker() -> None:
            try:
                system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
                history = trim_history(messages, self.history_window)
                result = run_model_tool_loop(
                    provider=self._get_provider(),
                    messages=[{"role": "system", "content": system_prompt}, *history],
                    tools=self._get_tools(),
                    model=self.model,
                    max_tool_rounds=self.max_tool_rounds,
                    on_event=events.put,
                    tool_functions=self._get_tool_functions(),
                )
                events.put({"type": "finished", "result": result})
            except Exception as exc:
                events.put({"type": "error", "message": str(exc)})
            finally:
                events.put({"type": "closed"})

        threading.Thread(target=worker, daemon=True).start()
        while True:
            event = events.get()
            if event["type"] == "closed":
                break
            yield event
