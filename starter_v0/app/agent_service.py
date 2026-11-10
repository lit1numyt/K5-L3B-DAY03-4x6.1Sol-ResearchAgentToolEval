from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).resolve().parents[1]
load_lab_env(ROOT)


class AgentService:
    """Thin web-facing adapter around the existing CLI agent loop."""

    def __init__(self) -> None:
        self.provider_name = os.getenv("BOT_PROVIDER", os.getenv("PROVIDER", "openrouter"))
        self.model = os.getenv("BOT_MODEL") or os.getenv("MODEL") or None
        self.history_window = self._positive_int("HISTORY_WINDOW", 5, maximum=50)
        self.max_tool_rounds = self._positive_int("MAX_TOOL_ROUNDS", 4, maximum=20)
        self.system_prompt_path = self._path_env("SYSTEM_PROMPT_PATH", ROOT / "artifacts" / "system_prompt.md")
        self.tools_path = self._path_env("TOOLS_PATH", ROOT / "artifacts" / "tools.yaml")
        self._provider: Any | None = None
        self._tools: list[dict[str, Any]] | None = None

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

    def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
        history = trim_history(messages, self.history_window)
        return run_model_tool_loop(
            provider=self._get_provider(),
            messages=[{"role": "system", "content": system_prompt}, *history],
            tools=self._get_tools(),
            model=self.model,
            max_tool_rounds=self.max_tool_rounds,
        )
