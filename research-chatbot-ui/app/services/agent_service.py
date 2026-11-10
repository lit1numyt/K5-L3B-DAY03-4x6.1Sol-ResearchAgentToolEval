"""Compatibility adapter; all agent execution lives in starter_v0."""
from functools import lru_cache
from pathlib import Path
import importlib.util
import sys

LAB_ROOT = Path(__file__).resolve().parents[3] / "starter_v0"
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Canonical research UI implementation is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def _service():
    return _module("_research_ui_service", LAB_ROOT / "app/agent_service.py").AgentService()


def chat(messages):
    public = _module("_research_ui_public", LAB_ROOT / "app/public_data.py")
    return public.public_result(_service().chat(messages))
