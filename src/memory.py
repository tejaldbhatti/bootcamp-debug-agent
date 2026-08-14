"""
Lightweight thread memory: stores the last few question/answer turns
per Slack thread, so a follow-up question in the same thread has
context from earlier in the conversation.

Backed by a simple local JSON file — no database needed at this
scale. Only the plain question/answer text is stored per turn (not
the full RAG context that was injected that turn), so history stays
small and cheap to include in future prompts.
"""

import json
import os

MEMORY_FILE = "thread_memory.json"
MAX_TURNS = 6  # keep the last N question/answer exchanges per thread


def _load_all() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all(data: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_history(thread_id: str | None) -> list[dict]:
    """Return this thread's prior turns as OpenAI-style chat messages."""
    if not thread_id:
        return []
    data = _load_all()
    return data.get(thread_id, [])


def add_turn(thread_id: str | None, question: str, answer: str):
    """Append a question/answer pair to this thread's stored history."""
    if not thread_id:
        return  # no thread_id (e.g. CLI testing) — memory is a no-op
    data = _load_all()
    history = data.get(thread_id, [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    # keep only the most recent MAX_TURNS exchanges (2 messages each)
    data[thread_id] = history[-(MAX_TURNS * 2):]
    _save_all(data)
