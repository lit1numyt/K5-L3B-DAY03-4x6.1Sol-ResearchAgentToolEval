#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install -r requirements.txt

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
if [[ "${RELOAD:-0}" == "1" ]]; then
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
fi
exec uvicorn app.main:app --host "$HOST" --port "$PORT"
