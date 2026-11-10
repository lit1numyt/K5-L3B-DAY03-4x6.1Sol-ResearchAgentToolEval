# Research Chatbot UI

The runnable, tested UI is integrated in `../starter_v0/app/`. Both launchers here forward to that canonical application; no ADAPT edits are required. The compatibility service also delegates to the canonical agent instead of importing nonexistent functions from agent.py.

On Windows, from this directory:

```powershell
.\run.ps1 -InstallDependencies
```

For later starts use `.\run.ps1`. Or run `starter_v0/run.ps1` directly. The UI is at http://127.0.0.1:8000/ and supports live chat plus saved/live benchmarks. Provider keys are read from starter_v0/.env; never paste them into the browser.

Read ../docs/UI.md for the verified setup, transcript command and limits. The UI shows real tool arguments, execution errors and waiting states. Telegram delivery is disabled in the web demo by default. A local URL is not a public deployment link.
