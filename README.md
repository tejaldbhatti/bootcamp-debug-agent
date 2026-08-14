# Bootcamp Debug Agent

A Slack support bot for an AI bootcamp. Students post errors in
`#ask-for-support`; the agent answers using RAG over a troubleshooting
knowledge base, falls back to a live MCP (Context7) documentation
lookup when RAG isn't confident, and escalates to a human TA when
neither finds a solid answer. Follow-up questions in the same Slack
thread keep context via lightweight thread memory.

## How it works

```
Slack message
      |
Slack Trigger (n8n) --- filter out the bot's own messages
      |
Flask API (api.py) -> query.diagnose()
      |
Prior thread history (memory.py), if any
      |
Pinecone retrieval
      |
Minimum-score check -> GPT relevance check
      |
   +--+--+
   |     |
  RAG   MCP (Context7)      -- neither confident -> escalate to a TA
   |     |
   +--+--+
      |
   Answer
      |
Reply in the Slack thread + log to Google Sheets (n8n)
```

## Stack

| Piece | Role |
|---|---|
| Pinecone | Vector store for RAG |
| OpenAI (GPT-4o) | Embeddings, answer generation, vision (screenshot errors) |
| MCP / Context7 | Live library documentation fallback |
| n8n | Orchestration — Slack Trigger → Flask API → reply + log |
| Flask (`api.py`) | Thin HTTP wrapper around `query.py` |

## Project layout

| File | Purpose |
|---|---|
| `query.py` | Core pipeline: retrieve → answer / MCP fallback / escalate. Has a `__main__` block for testing from the terminal, no Slack/n8n needed. |
| `memory.py` | Stores the last few Q&A turns per Slack thread in `thread_memory.json`, so follow-ups have context. |
| `mcp_fallback.py` | Async MCP client for Context7 (`resolve-library-id` → `get-library-docs`). Kept separate since it's the only async piece. |
| `api.py` | Flask endpoint `POST /diagnose` — accepts `question`, `image_base64`, `thread_id`. |
| `ingest.py` | Chunks and embeds everything in `docs/` into Pinecone. Run once, and again whenever docs change. |
| `slack_export.py` | Optional: pulls real Q&A pairs out of Slack history into `docs/` (see note below on student data). |
| `n8n_workflow.json` | Exported n8n workflow — Slack Trigger → bot-message filter → Call Diagnose API → reply in thread + log to Google Sheets. |
| `docs/` | Knowledge base source files. **Not committed** — see below. |

### About `docs/`

The knowledge base is intentionally **not** pushed to GitHub (it's in
`.gitignore`) since it's the bootcamp's own curriculum/troubleshooting
content. It's also not needed at deploy time — the live app only
queries the already-ingested Pinecone index, never these files
directly. Only `ingest.py` reads `docs/`, and only when you're
building or refreshing the index.

If you're setting this up fresh, create a `docs/` folder locally and
add your own `.md`/`.txt` notes before running `ingest.py` — see
`docs/manual_qa.md`-style Q&A notes, or use `slack_export.py` to pull
real threads (redact anything student-identifying first — see the
warning in that section further down).

## Setup

```bash
cd bootcamp-debug-agent
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in your real API keys — never commit .env
```

## 1. Build the knowledge base

Pick whichever fits your access/comfort level:

**Manual (recommended to start):** write real questions + working
solutions into a `docs/*.md` file, in your own words, with no student
names. Usually higher quality than a raw export, since you naturally
keep only confirmed-working fixes.

**Automated export** (needs a Slack bot token with channel history
access):
```bash
python slack_export.py
```
Writes a Q&A markdown file with basic secret redaction applied
automatically. This pulls raw message text, including student
names/Slack IDs — check your Slack workspace's data policy before
using this with real student data, and scrub identifying details
before committing anything derived from it anywhere.

## 2. Ingest into Pinecone

```bash
python ingest.py
```

Creates the Pinecone index if needed and uploads chunks from
everything in `docs/`.

## 3. Test the core logic standalone

```bash
python test_mcp_fallback.py   # optional: confirms Context7 works in isolation first
python query.py               # full retrieve -> answer -> escalate loop, no Slack/n8n needed
```

A `support_log.csv` file will appear locally — a stand-in for the
Google Sheets log during local testing.

## 4. Wire up the full pipeline

1. Start the API: `python api.py` (runs on `http://localhost:5000`)
2. In n8n, import `n8n_workflow.json`
3. Set your Slack channel ID, Slack credentials, and Google Sheets
   credentials/spreadsheet ID in the relevant nodes
4. If n8n runs somewhere other than your machine, replace
   `http://localhost:5000` with a reachable URL (ngrok while testing;
   see **Deployment** below for a stable alternative)
5. Activate the workflow and test by posting in the Slack channel,
   then replying in-thread to confirm follow-ups keep context

## Deployment

Not yet deployed — currently running locally and exposed via ngrok
while testing. Planned: deploy `api.py` to Render so n8n has a stable
URL instead of one that changes every time ngrok restarts.

## Status

- Core logic (RAG, MCP fallback, escalation, thread memory) — working,
  verified via CLI and through the full n8n → Slack pipeline
- Slack thread replies — fixed: the n8n Reply node's "Reply to a
  Message" timestamp expression was missing its `||` fallback
  operator, causing every reply to post unthreaded; a bot-message
  filter was also added right after the Slack Trigger node
- Render deployment — not yet done (see Deployment above)
