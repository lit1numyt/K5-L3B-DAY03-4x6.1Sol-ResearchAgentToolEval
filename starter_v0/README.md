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

Useful endpoints are `/`, `/health`, `/api/chat`, and `/docs`. For development, use `RELOAD=1 ./run.sh`. The default bind address is `127.0.0.1:8000`, which is suitable as the origin for a Cloudflare Tunnel. Configure the tunnel separately and protect a public demo with Cloudflare Access or equivalent authentication.

The web configuration uses `BOT_PROVIDER`, `BOT_MODEL`, `HISTORY_WINDOW`, and `MAX_TOOL_ROUNDS`; provider credentials retain the names documented in `.env.example` and the existing provider modules.
