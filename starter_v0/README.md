# Source code

Toàn bộ source code của lab nằm trong folder này. Chạy mọi lệnh từ `starter_v0/`.

- File bắt đầu chạy: `run_eval.py` (chạy eval), `chat.py` (chat live), `scripts/preflight_provider.py` (kiểm tra provider).
- Web UI: `./run.sh`, sau đó mở `http://127.0.0.1:8000/`.
- Cách chạy: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`; `python chat.py --provider openrouter --version v3`; `pytest`.
- Input: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, bộ case `data/*.json`, API key trong `.env` (mẫu ở `.env.example`).
- Output: `runs/*.json` (kết quả eval), `transcripts/*.transcript.json` (chat live), `analysis/*.csv` (nếu chạy `scripts/parse_runs.py`).
- File học viên được sửa: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tools/` (thêm tool mới và đăng ký trong `tools/__init__.py`), `tests/test_tools_todo.py`, code UI và `requirements.txt`. Không sửa nội dung case trong `data/eval_base.json`.

Chi tiết từng bước xem [README.md](../README.md) ở root; cấu hình API key xem [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md).

## Research Chatbot web UI

The FastAPI application in `app/` wraps the existing `chat.py` multi-round tool loop. It does not store conversations on the server: the browser keeps them in localStorage and sends the current history with every request.

```bash
cp .env.example .env
# fill in the provider and tool keys required by your demo
./run.sh
```

Useful endpoints are `/`, `/health`, `/api/chat`, `/api/chat/stream`, and `/docs`. The browser uses `/api/chat/stream`, an SSE endpoint that emits progress events and answer chunks before a final `done` event. For development, use `RELOAD=1 ./run.sh`. The default bind address is `127.0.0.1:8000`, which is suitable as the origin for a Cloudflare Tunnel. Configure the tunnel separately and protect a public demo with Cloudflare Access or equivalent authentication.

Because the existing provider interface is synchronous, the current stream wraps the reliable multi-round agent loop and progressively delivers the completed answer after execution. Provider-native token streaming can be added later without changing the frontend event contract.

The web configuration uses `BOT_PROVIDER`, `BOT_MODEL`, `HISTORY_WINDOW`, and `MAX_TOOL_ROUNDS`; provider credentials retain the names documented in `.env.example` and the existing provider modules.

## ArXiv function-calling benchmark

Run the terminal-only benchmark from `starter_v0/` with a configured provider:

```bash
./.venv/bin/python arxiv_funtion_test/run_arxiv_eval.py --provider openrouter
```

Useful options include `--model MODEL`, `--max-cases N`, and `--output-dir PATH`. The evaluator runs the 20 cases in `arxiv_funtion_test/`, prints per-case scores and rubric dimensions, reports critical failures, and saves a detailed JSON report under `runs/arxiv/`. The evaluator treats the repository's existing `papers` tool as the rubric's `arxiv_search` function name and does not penalize parameters that the current arXiv tool does not expose; those are reported as API limitations.
