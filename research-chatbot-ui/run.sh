#!/usr/bin/env bash
# Usage: ./run.sh          (dev, auto-reload)
#        ./run.sh prod     (no reload; use for demos / Cloudflare Tunnel)
set -euo pipefail
cd "$(dirname "$0")"

[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if [ -f .env ]; then set -a; source .env; set +a; fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if [ "${1:-dev}" = "prod" ]; then
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --proxy-headers --forwarded-allow-ips="127.0.0.1"
else
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
fi
