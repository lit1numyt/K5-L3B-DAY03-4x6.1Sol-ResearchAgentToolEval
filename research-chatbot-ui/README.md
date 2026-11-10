# Research Chatbot Web UI

Lightweight FastAPI + vanilla JS front end for the existing multi-round tool-calling agent.
The backend is stateless; conversations live in the browser's localStorage.

## Setup
1. Copy `app/` into the repo root (merge with existing folders; nothing existing is replaced).
2. Append `requirements-additions.txt` to your `requirements.txt`.
3. Copy `.env.example` to `.env`; add your provider key using the variable names your provider already expects.
4. Open `app/services/agent_service.py` and fix the block marked **ADAPT** (imports, tool loading, loop signature, result keys).
5. Merge `.gitignore` entries; make sure `.env` is ignored.

## Run
```bash
./run.sh          # dev with reload  -> http://127.0.0.1:8000
./run.sh prod     # no reload, for demos
```
`ENABLE_DOCS=1` in `.env` exposes `/docs` locally.

## API
- `GET /health` -> `{"status":"ok"}`
- `POST /api/chat`
  ```json
  {"conversation_id":"abc","messages":[{"role":"user","content":"Hi"}]}
  ```
  Response: `{conversation_id, status, assistant_text, rounds, tool_events}`.
  `status` is `answered`, `waiting_for_user`, or `max_tool_rounds`.
  Errors: 422 (validation: empty list, bad role, last message not `user`, oversize), 500 (generic message; details in server logs).

The browser never sends or overrides the system prompt or tools.

## Cloudflare Tunnel
1. Run `./run.sh prod` (binds to 127.0.0.1 only).
2. Point your tunnel hostname at `http://127.0.0.1:8000`, e.g. in `config.yml`:
   ```yaml
   ingress:
     - hostname: chat.example.com
       service: http://127.0.0.1:8000
     - service: http_status:404
   ```
3. **Put Cloudflare Access (or equivalent) in front of the hostname before sharing it.** The agent can execute tools, and this app has no auth of its own.
4. Cloudflare proxies time out at roughly 100 s without a response. Long multi-round runs can hit this; lower `MAX_TOOL_ROUNDS` if so.

## Notes
- Markdown is rendered with `marked` + `DOMPurify` from jsDelivr (pinned versions). To avoid the CDN, save both files to `app/static/js/vendor/` and update the `<script>` tags in `index.html`. If they fail to load, replies show as escaped plain text.
- Clearing browser data deletes conversations (by design: no server storage).
