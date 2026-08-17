# Bootcamp Debug Agent

An AI support agent for a bootcamp's Slack channel. Students post
errors; it answers from an internal RAG knowledge base, falls back to
live library docs via MCP when RAG isn't confident, keeps context
across threaded follow-ups, and escalates to a human when neither
source has a solid answer. Deployed and running in production.

**Highlights**
- Diagnosis logic modeled as an explicit **LangGraph** state machine (8 nodes, conditional routing) rather than nested if/else
- **RAG** (Pinecone + OpenAI embeddings) with a GPT relevance check before trusting a retrieval, not just a similarity score
- **Live doc fallback** via MCP (Context7), with a multi-round tool-calling loop for chained lookups
- **Thread-aware**: Slack follow-ups keep conversation context; vague follow-ups get context-aware search
- **Per-request cost tracking**: OpenAI $ cost estimated from actual token usage, logged per turn
- **Vision**: screenshots described via GPT-4o before retrieval, so image-only reports still search well
- Deployed on **Render**, orchestrated by **n8n** (Slack trigger → API → threaded reply + Google Sheets log), with shared-secret auth on the API

## Contents
1. [Architecture](#architecture)
2. [Stack](#stack)
3. [Project layout](#project-layout)
4. [Deployment](#deployment)
5. [Status](#status)

## Architecture

```
Slack message
      |
n8n: Slack Trigger -> filter bot's own messages
      |
Flask API (src/api.py) -> query.diagnose()  [LangGraph state machine]
      |
retrieve -> too weak? --------------------+
      |                                   |
  relevance check --(not relevant)--------+
      |(relevant)                         |
  answer from RAG                    MCP (Context7)
      |                              found? -> answer from MCP
      |                              not found? -> escalate to a TA
      +-------------------+-------------------+
                           |
        save thread memory + log (incl. cost)
                           |
        n8n: reply in Slack thread + log to Sheets
```

## Stack

| Piece | Role |
|---|---|
| Pinecone | Vector store for RAG |
| OpenAI (GPT-4o) | Embeddings, answers, vision, relevance checks |
| LangGraph | Explicit state machine for the diagnosis pipeline |
| MCP / Context7 | Live library documentation fallback |
| n8n | Orchestration: Slack Trigger → Flask API → reply + log |
| Flask + Gunicorn | API, deployed on Render |

## Project layout

```
bootcamp-debug-agent/
├── requirements.txt / .env.example
├── n8n_workflow.json      # exported n8n workflow
├── docs/                  # knowledge base source — local only, not committed
└── src/
    ├── api.py             # POST /diagnose
    ├── query.py           # LangGraph pipeline (the core of the project)
    ├── mcp_fallback.py     # async MCP client
    ├── memory.py          # per-thread Q&A history
    ├── ingest.py           # docs/ -> Pinecone
    └── slack_export.py     # optional: pull real Q&A from Slack history
```

`docs/` (the knowledge base source) isn't committed — it's the
bootcamp's own curriculum content, kept private.

## Deployment

Live on Render. Key settings:
- Root Directory: `src` · Start command: `gunicorn -b 0.0.0.0:$PORT api:app`
- Env vars set in Render's dashboard: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_SUPPORT_CHANNEL_ID`, `API_SHARED_SECRET`
- `API_SHARED_SECRET` is checked against an `X-API-Key` header n8n sends — without it, `/diagnose` would be open to anyone with the URL
- `thread_memory.json` is not persistent (Render's filesystem is ephemeral) — a redeploy resets in-thread context, a reasonable tradeoff for a support bot

## Status

Working end-to-end: RAG, MCP fallback, escalation, thread memory, cost
tracking, and Slack threading are all verified in production through
the full n8n → Render pipeline.
