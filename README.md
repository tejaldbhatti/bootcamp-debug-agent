# Bootcamp Debug Agent — Minimal Prototype

Deliberately simple: 4 small Python files, no LangGraph, no agent
framework abstractions yet. Once this core logic works, it can be
wrapped in LangGraph nodes later without changing the underlying pieces.

## Files

- `ingest.py` — loads docs from `docs/`, chunks them, embeds them, and
  upserts them into Pinecone. Run once, and again whenever docs change.
- `query.py` — the core logic: retrieve → answer, or fall back to a
  live MCP docs lookup, or escalate → redact secrets → log to CSV. Has
  a `__main__` block so you can test it alone from the terminal, no
  Slack/n8n needed.
- `mcp_fallback.py` — when RAG isn't confident, tries the Context7 MCP
  server (live, version-specific library documentation) before giving
  up and escalating. Kept in its own file since MCP is async and the
  rest of the code isn't.
- `memory.py` — lightweight thread memory: stores the last few
  question/answer pairs per Slack thread in a local JSON file, so
  follow-up questions in the same thread have context. Pass a
  `thread_id` into `diagnose()` to use it; omit it (e.g. from the CLI
  test) to skip memory entirely.
- `api.py` — a tiny Flask server that exposes `query.diagnose()` over
  HTTP, so n8n can call it.
- `n8n_workflow.json` — a starter workflow: Slack message → call the API
  → reply in the Slack thread → log a row to Google Sheets.
- `docs/sample_notes.md` — placeholder knowledge base. Replace with real
  content (exported doc pages, your own FAQ notes, etc.) before real use.

## 1. Set up locally

```bash
cd bootcamp-debug-agent
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then fill in your real API keys
```

## 2. Add real Q&A data to the knowledge base

Two options — pick whichever fits your access/comfort level:

**Option A — Manual (recommended to start, no Slack API access needed):**
Open `docs/manual_qa.md` and copy in real questions + working solutions
from the Slack channel, in your own words, with no student names. This
is often higher quality than a raw export since you naturally keep only
the confirmed-working fixes.

**Option B — Automated export (needs a Slack bot token with channel
history access — see below):**
```bash
python slack_export.py
```
Writes `docs/slack_history.md` with question/answer pairs pulled
directly from the channel, unanswered threads clearly labeled as such,
basic secret redaction applied automatically. Note: this pulls raw
message text, including student names/Slack IDs — check with whoever
manages your Slack workspace's data policy before using this option
with real student data.

## 3. Ingest all docs (sample notes + your Q&A data) into Pinecone

```bash
python ingest.py
```

This creates the Pinecone index (if it doesn't exist yet) and uploads
the chunks from everything in `docs/` — no changes needed to this
script since it just reads whatever `.md`/`.txt` files are there.

## 4. Test the MCP fallback on its own (optional, before the full flow)

```bash
python test_mcp_fallback.py
```

Confirms the Context7 connection and tool-calling work in isolation,
before testing it as part of the full `diagnose()` flow. Worth running
this first since it's the most complex piece of code in the project —
easier to debug on its own than buried inside a larger flow.

## 5. Test the core logic on its own

```bash
python query.py
```

Type a question like `ModuleNotFoundError langchain` and check the
answer. This step alone proves RAG + escalation logic works, with zero
Slack or n8n involved — the same "smallest possible slice" the lab
asks for.

A `support_log.csv` file will appear — this is your local stand-in for
the Google Sheets log for now.

## 6. Wire up the full pipeline (once step 5 works)

1. Start the API: `python api.py` (runs on `http://localhost:5000`)
2. In n8n, import `n8n_workflow.json`
3. Replace the placeholders:
   - `REPLACE_WITH_SUPPORT_CHANNEL_ID` — your Slack channel ID
   - `REPLACE_WITH_SPREADSHEET_ID` — your Google Sheet ID
4. Connect your Slack and Google Sheets credentials in n8n
5. If n8n runs somewhere other than your machine, replace
   `http://localhost:5000` with a reachable URL (e.g. via ngrok, or
   deploy `api.py` somewhere small like Render/Fly.io)
6. Activate the workflow and test by posting in the Slack channel

## What's intentionally NOT here yet (this is a prototype, not the MVP)

- LangGraph-based multi-step diagnosis (currently: retrieve → answer,
  with the MCP fallback and escalation as the only two branches — good
  enough to validate the concept)
- Thread memory / follow-up questions
- Real Google Sheets logging (currently: local CSV)
- Deployment, monitoring, error handling, retries

These come once the core loop is proven to work — see Phase 2–4 in the
Project Plan document.
