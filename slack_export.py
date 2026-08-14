"""
Exports the support channel's message history into docs/slack_history.md,
formatted as question/answer pairs so ingest.py can chunk and embed it
just like any other doc.

Run this once to backfill history, and periodically to refresh it:
    python slack_export.py
"""

import os
import re
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
CHANNEL_ID = os.environ["SLACK_SUPPORT_CHANNEL_ID"]
OUTPUT_FILE = "docs/slack_history.md"

# Same simple secret patterns used in query.py — kept duplicated here on
# purpose so this script has no dependency on the rest of the app.
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"ghp_[a-zA-Z0-9]{30,}",
    r"xox[baprs]-[a-zA-Z0-9-]{10,}",
]


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text or "")
    return text


def get_root_messages():
    """Fetch all top-level messages in the channel (paginated)."""
    messages = []
    cursor = None
    while True:
        resp = client.conversations_history(channel=CHANNEL_ID, cursor=cursor, limit=200)
        messages.extend(resp["messages"])
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return messages


def get_first_reply(thread_ts: str) -> str | None:
    """Return the text of the first reply in a thread, if any."""
    resp = client.conversations_replies(channel=CHANNEL_ID, ts=thread_ts, limit=2)
    replies = resp["messages"]
    if len(replies) > 1:
        return replies[1]["text"]
    return None


def main():
    messages = get_root_messages()
    print(f"Found {len(messages)} messages, building export...")

    lines = ["# Slack support channel history (exported)\n"]
    for msg in messages:
        text = redact(msg.get("text", "").strip())
        if not text:
            continue

        answer = None
        if msg.get("reply_count", 0) > 0:
            answer = redact(get_first_reply(msg["ts"]) or "")

        lines.append(f"### Question\n{text}\n")
        if answer:
            lines.append(f"**Answer:** {answer}\n")
        else:
            lines.append("**Status:** Unanswered — do not treat as a resolved fix.\n")
        lines.append("---\n")

    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {OUTPUT_FILE}. Now run: python ingest.py")


if __name__ == "__main__":
    main()
