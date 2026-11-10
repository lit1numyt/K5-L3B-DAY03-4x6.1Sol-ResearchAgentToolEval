# Running and verifying the research UI

The canonical UI is `starter_v0/app/` (FastAPI + JavaScript). Dependencies are declared in `starter_v0/requirements.txt`.

## Windows

```powershell
cd starter_v0
.\run.ps1 -InstallDependencies
```

For subsequent starts, `.\run.ps1` is enough. Optional arguments: `-ListenPort 8001`, `-BindAddress 127.0.0.1`, `-Reload`. The script uses `.venv/Scripts/python.exe`; it does not depend on Bash activation. Configure provider/tool credentials in starter_v0/.env as described in TOOL-SETUP.md. Explicit BOT_PROVIDER/PROVIDER wins; otherwise the service selects a provider with an available key.

Open http://127.0.0.1:8000/. `/health` checks process health and `/api/meta` reports provider, model, actual artifact hashes/version and whether a key is configured, without exposing the key.

## Verified behavior

- Live chat calls the existing model/tool loop and displays tool arguments, failed tools and clarification/waiting states.
- Saved benchmark inspection adapts a selected case from the stored run; PASS/FAIL and failures are taken from that case. It does not run an API request or fabricate a new result.
- Fixture/manifest JSON files do not appear as saved lab runs. Reporting labels are derived from filenames while original metadata remains visible.
- Provider/HTTP errors remain errors, not a fabricated answer or benchmark PASS.
- The browser stores local conversations; no public deployment has been created by this work.

Actual UI screenshots are in report/team/review_evidence/. A server started during verification listens on loopback port 8000. Keep that process running while using the local link.

## Live transcript for C6

```powershell
.\.venv\Scripts\python.exe chat.py --provider openai --model gpt-4o-mini --version v8 --disable-send --max-tool-rounds 6
```

`--disable-send` preserves real research/provider calls but blocks Telegram delivery. Transcript metadata records this mode. The scripted live demonstration in the report uses four real API turns: internal research, missing account, supplied account, and a Telegram request. Prompts are recorded, not presented as an unrecorded human session.

C6 also asks for a usable public/demo link. Localhost proves local operation, not external access. The team must provide an approved public deployment/tunnel if needed. Do not claim that screenshots alone fulfill C6. Telegram bonus requires a different, explicitly confirmed real-delivery transcript; this demo does not claim it.
