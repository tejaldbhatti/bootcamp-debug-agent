# Bootcamp Debug Agent — Project Context

## What this is
A Slack support bot for an Ironhack AI bootcamp. Students post errors in
`#ask-for-support`, and this agent tries to answer using RAG over a
knowledge base of troubleshooting docs, falling back to a live MCP
(Context7) documentation lookup, and escalating to a human TA if neither
finds a confident answer.

## Stack
- **Pinecone** — vector store for RAG
- **OpenAI (GPT-4o)** — embeddings, answer generation, vision (for
  screenshots)
- **MCP / Context7** — live library documentation fallback when RAG
  isn't confident
- **n8n** (self-hosted) — orchestration: Slack Trigger → filter bot's
  own messages → call our Flask API → reply in Slack thread + log to
  Google Sheets
- **Flask (api.py)** — thin HTTP wrapper around `query.py`'s core logic
- Currently running locally + exposed via ngrok while testing; not yet
  deployed to Render

## Key files
- `query.py` — core pipeline: retrieve → answer/MCP fallback/escalate,
  now with thread memory and context-aware search for follow-ups
- `memory.py` — stores last few Q&A turns per Slack thread in
  `thread_memory.json` (local JSON file)
- `mcp_fallback.py` — async MCP client for Context7, loops through
  tool calls (resolve-library-id → get-library-docs)
- `api.py` — Flask endpoint `/diagnose`, accepts `question`,
  `image_base64`, `thread_id`
- `ingest.py` — chunks and embeds everything in `docs/` into Pinecone
- `docs/` — knowledge base: manual Q&A, plus troubleshooting guides for
  VSCode, LangChain, MCP, n8n, GitHub

## Current status / blocker
Core logic (`query.py`) is tested and working — RAG, MCP fallback, and
memory all work correctly when tested via CLI (`python query.py`).

The live n8n → Slack pipeline is NOT yet reliably threading replies.
Symptoms:
- Bot's replies sometimes post as new top-level messages instead of
  actual threaded replies (missing `thread_ts` on the Slack API call)
- Even after configuring the "Reply to a Message" option in n8n's
  Slack node with the expression
  `{{ $('Slack Trigger').item.json.thread_ts || $('Slack Trigger').item.json.ts }}`,
  it has intermittently gotten cleared/lost when other node options
  were toggled
- As a result, follow-up questions in Slack don't reliably link back to
  the correct `thread_id`, so `memory.py` can't find prior context for
  them — `thread_memory.json` shows mismatched/orphaned thread keys

## What's needed
Help verify and stabilize the n8n workflow's threading behavior so that:
1. Bot replies always post as genuine threaded replies (verify via the
   Slack API response's `thread_ts` field)
2. `thread_id` sent to `/diagnose` always matches across a real
   conversation thread
3. `thread_memory.json` accumulates turns under one consistent key per
   conversation, not fragmented across near-identical timestamps

n8n workflow itself isn't a local file (built in n8n's UI), so
screenshots/execution data may still be needed for that part — but
`query.py`, `memory.py`, and `thread_memory.json` are all available
locally to inspect directly.