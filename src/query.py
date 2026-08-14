"""
Core logic for one support request:

1. Retrieve relevant document chunks from Pinecone.
2. Check whether the retrieved context is sufficient to answer the question.
3. If RAG can answer -> answer using the internal documentation.
4. If RAG cannot answer -> use Context7 through MCP as a fallback.
5. Optionally analyze a screenshot.
6. Pull in prior turns from this Slack thread (if any) for continuity.
7. Log the result to a local CSV.

This file has no Slack/n8n code on purpose.
"""

import os
import re
import csv
import base64
import asyncio
from datetime import datetime, timezone
from typing import TypedDict

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from langgraph.graph import StateGraph, START, END

from mcp_fallback import resolve_via_mcp
from memory import get_history, add_turn


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

CHAT_MODEL = "gpt-4o"
EMBED_MODEL = "text-embedding-3-small"

# Number of Pinecone chunks to retrieve
TOP_K = 4

# We use this only as a minimum safety filter.
# It is NOT the final RAG decision.
MIN_RAG_SCORE = 0.40

LOG_FILE = "support_log.csv"


# ============================================================
# COST TRACKING
#
# Rough per-request $ cost estimate from actual OpenAI token usage.
# Rates below are per 1M tokens — check https://openai.com/api/pricing
# and update if they've changed; treat these as good-enough-to-compare
# requests against each other, not an exact invoice.
#
# Pinecone isn't included: serverless read-unit pricing depends on
# returned payload size, not a flat $/query rate, and at this app's
# scale it normally stays inside Pinecone's free tier anyway — a
# hardcoded per-query number would be more misleading than useful.
# ============================================================

PRICING_PER_1M_TOKENS = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "text-embedding-3-small": {"input": 0.02, "output": 0.00},
}


class CostTracker:
    """Accumulates estimated OpenAI $ cost across one diagnose() call."""

    def __init__(self):
        self.total_usd = 0.0
        self.calls = []  # [(model, input_tokens, output_tokens, cost_usd), ...]

    def add(self, model: str, usage) -> float:
        """Record one API response's token usage. Safe to call with
        usage=None (e.g. a failed/empty response) — adds nothing."""
        if usage is None:
            return 0.0

        rates = PRICING_PER_1M_TOKENS.get(model)
        if rates is None:
            return 0.0

        input_tokens = getattr(usage, "prompt_tokens", None)
        if input_tokens is None:
            input_tokens = getattr(usage, "total_tokens", 0)
        output_tokens = getattr(usage, "completion_tokens", 0)

        cost = (
            (input_tokens / 1_000_000) * rates["input"]
            + (output_tokens / 1_000_000) * rates["output"]
        )
        self.total_usd += cost
        self.calls.append((model, input_tokens, output_tokens, cost))
        return cost


# ============================================================
# CLIENTS
# ============================================================

openai_client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)

INDEX_NAME = os.environ.get(
    "PINECONE_INDEX_NAME",
    "bootcamp-debug-agent"
)

index = pc.Index(INDEX_NAME)


# ============================================================
# SECRET REDACTION
# ============================================================

SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",              # OpenAI-style keys
    r"AKIA[0-9A-Z]{16}",                # AWS access key IDs
    r"ghp_[a-zA-Z0-9]{30,}",             # GitHub tokens
    r"xox[baprs]-[a-zA-Z0-9-]{10,}",     # Slack tokens
]


def redact_secrets(text: str) -> str:
    """Replace obvious API keys/tokens with [REDACTED]."""
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text


# ============================================================
# EMBEDDINGS
# ============================================================

def embed(text: str, cost_tracker: CostTracker | None = None) -> list[float]:
    """Create an OpenAI embedding for the supplied text."""
    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    if cost_tracker:
        cost_tracker.add(EMBED_MODEL, response.usage)
    return response.data[0].embedding


# ============================================================
# PINECONE RETRIEVAL
# ============================================================

def retrieve(question: str, cost_tracker: CostTracker | None = None):
    """Search Pinecone for the most relevant document chunks."""
    query_vector = embed(question, cost_tracker)
    result = index.query(
        vector=query_vector,
        top_k=TOP_K,
        include_metadata=True
    )
    return result["matches"]


# ============================================================
# DEBUG DISPLAY
# ============================================================

def print_matches(matches):
    """Print retrieved Pinecone chunks to the terminal (dev aid)."""
    print("\n" + "=" * 70)
    print("PINECONE RETRIEVAL RESULTS")
    print("=" * 70)

    if not matches:
        print("No matches found.")
        return

    for i, match in enumerate(matches, start=1):
        score = match.get("score", 0)
        metadata = match.get("metadata", {})
        source = metadata.get("source", "unknown")
        text = metadata.get("text", "")

        print(f"\nResult #{i}")
        print(f"Score  : {score:.4f}")
        print(f"Source : {source}")
        print(f"Text   : {text[:1000]}")

    print("\n" + "=" * 70)


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_context(matches) -> str:
    """Convert Pinecone matches into readable context for GPT."""
    if not matches:
        return ""

    context_parts = []
    for match in matches:
        metadata = match.get("metadata", {})
        source = metadata.get("source", "unknown")
        text = metadata.get("text", "")
        score = match.get("score", 0)

        context_parts.append(
            f"""
SOURCE: {source}
SIMILARITY SCORE: {score:.4f}

{text}
"""
        )

    return "\n\n---\n\n".join(context_parts)


# ============================================================
# RAG RELEVANCE CHECK
# ============================================================

def check_rag_relevance(question: str, matches, cost_tracker: CostTracker | None = None) -> bool:
    """
    Ask GPT whether the retrieved documentation contains enough
    information to answer the student's question. Better than relying
    only on the Pinecone similarity score.
    """
    context = build_context(matches)
    if not context:
        return False

    prompt = f"""
You are evaluating whether an internal knowledge base can answer
a student's technical support question.

Student question:
{question}

Retrieved internal documentation:
{context}

Your task:

Determine whether the retrieved documentation contains enough
specific and useful information to answer the student's question.

Return ONLY one word:

YES

or

NO

Return YES if the documentation contains a direct answer,
relevant troubleshooting steps, configuration information,
examples, or enough information to construct a reliable answer.

Return NO if the documentation is unrelated, too vague, or does
not contain enough information to answer the question.
"""

    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    if cost_tracker:
        cost_tracker.add(CHAT_MODEL, response.usage)

    decision = response.choices[0].message.content.strip().upper()
    print(f"\nRAG relevance decision: {decision}")

    return decision.startswith("YES")


# ============================================================
# BUILD RAG ANSWER PROMPT
# ============================================================

def build_answer_prompt(question: str, matches, image_path: str | None):
    """Build the prompt used when RAG has enough information."""
    context = build_context(matches)

    text_prompt = f"""
You are a helpful teaching assistant for an AI bootcamp.

A student has asked a technical support question.

Use ONLY the internal documentation provided below to answer
the student's question.

Do NOT invent information that is not supported by the
documentation.

Give the student a clear, systematic troubleshooting answer.

When appropriate:

1. Start with the most likely cause.
2. Give numbered troubleshooting steps.
3. Tell the student exactly where to check something.
4. Explain what the student should expect to see.
5. Explain what to do if the check fails.
6. Mention the exact error message when it is available.
7. Ask for a screenshot/error message only when necessary.

Internal documentation:

{context}

Student question:

{question}
"""

    content = [{"type": "text", "text": text_prompt}]

    if image_path:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })

    return content


# ============================================================
# SCREENSHOT DESCRIPTION (runs before retrieval)
# ============================================================

def describe_screenshot(image_path: str, cost_tracker: CostTracker | None = None) -> str:
    """
    Use vision to extract the actual error/content shown in a
    screenshot as plain text. Pinecone retrieval only works on text,
    so without this step, a vague accompanying message (e.g. "see
    screenshot") gives retrieval nothing useful to search on and the
    image content is effectively ignored.
    """
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    content = [
        {
            "type": "text",
            "text": (
                "This is a screenshot a student shared along with a "
                "technical support question. Describe, in plain text, "
                "exactly what error message(s), tool names, and relevant "
                "details are visible in this image. Quote the exact error "
                "text if it's visible. Don't diagnose or suggest a fix — "
                "just describe what's shown, factually."
            ),
        },
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]

    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": content}],
    )
    if cost_tracker:
        cost_tracker.add(CHAT_MODEL, response.usage)
    return response.choices[0].message.content


# ============================================================
# ASK GPT (now thread-aware)
# ============================================================

def ask_model(content, history: list[dict] | None = None, cost_tracker: CostTracker | None = None) -> str:
    """
    Send a prompt to GPT and return the answer. If `history` is given
    (prior turns from this Slack thread), it's included before the
    current message so follow-up questions have context.
    """
    messages = (history or []) + [{"role": "user", "content": content}]

    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )
    if cost_tracker:
        cost_tracker.add(CHAT_MODEL, response.usage)
    return response.choices[0].message.content


# ============================================================
# CSV LOGGING
# ============================================================

def log_to_csv(question: str, answer: str, escalated: bool, source: str, cost_usd: float = 0.0):
    """Append the support request to support_log.csv.

    Note: if support_log.csv already exists from before the cost_usd
    column was added, its older rows will have one fewer column than
    new ones — fine for appending, but re-open in Excel/Sheets with
    that in mind (or start a fresh file) if you're analyzing it there.
    """
    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer", "escalated", "source", "cost_usd"])
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            question,
            answer,
            escalated,
            source,
            f"{cost_usd:.6f}"
        ])


# ============================================================
# LANGGRAPH STATE MACHINE
#
# Same pipeline as before, expressed as an explicit graph instead of
# nested if/else. Flow:
#
#     redact_and_prepare
#           |
#        retrieve
#        /      \
#  (too weak)  check_relevance
#       |        /        \
#       |   (relevant)  (not relevant)
#       |       |             |
#       |  answer_from_rag    |
#       |       |             |
#        \      |            /
#         mcp_fallback <-----
#         /          \
#    (found)      (not found)
#       |               |
# answer_from_mcp    escalate
#       \               /
#        \             /
#          finalize
# ============================================================

class DiagnoseState(TypedDict, total=False):
    # inputs
    question: str
    image_path: str | None
    thread_id: str | None
    # working state, filled in as nodes run
    safe_question: str
    history: list[dict]
    search_query: str
    matches: list
    best_score: float
    rag_is_relevant: bool
    mcp_result: str | None
    cost_tracker: CostTracker
    # outputs
    answer: str
    escalated: bool
    source: str
    cost_usd: float


def node_redact_and_prepare(state: DiagnoseState) -> dict:
    """STEP 1-4: redact secrets, describe screenshot, load thread
    history, and build a context-aware search query for follow-ups."""

    print("\n" + "=" * 70)
    print("BOOTCAMP DEBUG AGENT")
    print("=" * 70)

    print("\nStudent question:")
    print(state["question"])

    cost_tracker = CostTracker()

    safe_question = redact_secrets(state["question"])

    image_path = state.get("image_path")
    if image_path:
        print("\nScreenshot provided — extracting error text via vision...")
        screenshot_description = describe_screenshot(image_path, cost_tracker)
        print("\n--- SCREENSHOT DESCRIPTION (for debugging) ---")
        print(screenshot_description)
        print("--- END SCREENSHOT DESCRIPTION ---\n")
        safe_question = (
            f"{safe_question}\n\n[What the screenshot shows]:\n{screenshot_description}"
        )

    history = get_history(state.get("thread_id"))
    if history:
        print(f"\nLoaded {len(history) // 2} prior turn(s) from this thread.")

    # Retrieval and MCP only ever see the raw question text, so a vague
    # follow-up like "does that work on Mac too?" has nothing to search
    # on by itself. Combine it with the most recent exchange so search
    # actually has something to work with. (safe_question stays the
    # clean text used for logging/display — this is only for search.)
    if history:
        last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        last_assistant = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), "")
        search_query = (
            f"Earlier in this conversation:\n"
            f"Q: {last_user}\nA: {last_assistant}\n\n"
            f"Follow-up question: {safe_question}"
        )
        print("\nFollow-up detected — using conversation context for search.")
    else:
        search_query = safe_question

    return {
        "safe_question": safe_question,
        "history": history,
        "search_query": search_query,
        "cost_tracker": cost_tracker,
    }


def node_retrieve(state: DiagnoseState) -> dict:
    """STEP 5: search Pinecone and record the best score."""

    print("\nSearching Pinecone...")
    matches = retrieve(state["search_query"], state.get("cost_tracker"))
    print_matches(matches)

    best_score = matches[0]["score"] if matches else 0

    print(f"\nBest Pinecone score: {best_score:.4f}")
    print(f"Minimum RAG score: {MIN_RAG_SCORE}")

    return {"matches": matches, "best_score": best_score}


def route_after_retrieve(state: DiagnoseState) -> str:
    """STEP 6: if Pinecone's best result is extremely weak, skip
    straight to the MCP fallback instead of bothering with a relevance
    check."""

    if not state["matches"] or state["best_score"] < MIN_RAG_SCORE:
        print("\nRAG retrieval is too weak.")
        print("-> Switching to MCP / Context7...")
        return "too_weak"

    print("\nRAG retrieved potentially relevant documentation.")
    print("-> Checking whether the documentation can answer the question...")
    return "check_relevance"


def node_check_relevance(state: DiagnoseState) -> dict:
    """STEP 7: ask GPT whether the retrieved docs are actually useful."""

    rag_is_relevant = check_rag_relevance(state["search_query"], state["matches"], state.get("cost_tracker"))

    if rag_is_relevant:
        print("\nRAG has enough information.")
        print("-> Generating answer from internal documentation.")
    else:
        print("\nRAG does not have enough information.")
        print("-> Switching to MCP / Context7...")

    return {"rag_is_relevant": rag_is_relevant}


def route_after_relevance(state: DiagnoseState) -> str:
    return "relevant" if state["rag_is_relevant"] else "not_relevant"


def node_answer_from_rag(state: DiagnoseState) -> dict:
    content = build_answer_prompt(state["safe_question"], state["matches"], state.get("image_path"))
    answer = ask_model(content, history=state.get("history"), cost_tracker=state.get("cost_tracker"))
    answer = redact_secrets(answer)
    return {"answer": answer, "escalated": False, "source": "rag"}


def node_mcp_fallback(state: DiagnoseState) -> dict:
    """STEP 8: call Context7 through MCP. Reached either directly from
    a too-weak Pinecone result, or after RAG was found not relevant."""

    cost_tracker = state.get("cost_tracker")

    def _track_usage(usage):
        if cost_tracker:
            cost_tracker.add(CHAT_MODEL, usage)

    mcp_result = asyncio.run(resolve_via_mcp(state["search_query"], on_usage=_track_usage))

    if mcp_result:
        print("\nMCP returned documentation.")
        print("-> Asking GPT to formulate the answer.")
        print("\n--- RAW MCP RESULT (for debugging) ---")
        print(mcp_result[:3000])
        print("--- END RAW MCP RESULT ---\n")

    return {"mcp_result": mcp_result}


def route_after_mcp(state: DiagnoseState) -> str:
    return "found" if state.get("mcp_result") else "not_found"


def node_answer_from_mcp(state: DiagnoseState) -> dict:
    content = [{
        "type": "text",
        "text": (
            "You are a helpful teaching assistant for an AI bootcamp.\n\n"
            "Use ONLY the documentation below to answer the student's "
            "question. Do NOT use your own training knowledge about "
            "this library, even if you think you remember how it "
            "works — libraries change, and your training data may "
            "be outdated. If the documentation below doesn't clearly "
            "answer the question, say so honestly instead of "
            "guessing from memory.\n\n"
            f"Documentation:\n{state['mcp_result']}\n\n"
            f"Student question:\n{state['safe_question']}"
        ),
    }]

    answer = ask_model(content, history=state.get("history"), cost_tracker=state.get("cost_tracker"))
    answer = redact_secrets(answer)
    return {"answer": answer, "escalated": False, "source": "mcp_fallback"}


def node_escalate(state: DiagnoseState) -> dict:
    answer = (
        "I couldn't find a confident answer in the available "
        "documentation. A TA needs to take a look at this."
    )
    return {"answer": answer, "escalated": True, "source": "escalated"}


def node_finalize(state: DiagnoseState) -> dict:
    """STEP 9-10: save this turn to thread memory and log the result,
    including the estimated OpenAI cost accumulated across every node
    this request passed through."""

    cost_tracker = state.get("cost_tracker")
    cost_usd = cost_tracker.total_usd if cost_tracker else 0.0
    print(f"\nEstimated OpenAI cost for this request: ${cost_usd:.6f}")

    add_turn(state.get("thread_id"), state["safe_question"], state["answer"])
    log_to_csv(state["safe_question"], state["answer"], state["escalated"], state["source"], cost_usd)
    return {"cost_usd": cost_usd}


def _build_graph():
    graph = StateGraph(DiagnoseState)

    graph.add_node("redact_and_prepare", node_redact_and_prepare)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("check_relevance", node_check_relevance)
    graph.add_node("answer_from_rag", node_answer_from_rag)
    graph.add_node("mcp_fallback", node_mcp_fallback)
    graph.add_node("answer_from_mcp", node_answer_from_mcp)
    graph.add_node("escalate", node_escalate)
    graph.add_node("finalize", node_finalize)

    graph.add_edge(START, "redact_and_prepare")
    graph.add_edge("redact_and_prepare", "retrieve")

    graph.add_conditional_edges("retrieve", route_after_retrieve, {
        "too_weak": "mcp_fallback",
        "check_relevance": "check_relevance",
    })
    graph.add_conditional_edges("check_relevance", route_after_relevance, {
        "relevant": "answer_from_rag",
        "not_relevant": "mcp_fallback",
    })
    graph.add_conditional_edges("mcp_fallback", route_after_mcp, {
        "found": "answer_from_mcp",
        "not_found": "escalate",
    })

    graph.add_edge("answer_from_rag", "finalize")
    graph.add_edge("answer_from_mcp", "finalize")
    graph.add_edge("escalate", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = _build_graph()


# ============================================================
# MAIN DIAGNOSIS PIPELINE
# ============================================================

def diagnose(
    question: str,
    image_path: str | None = None,
    thread_id: str | None = None,
) -> dict:
    """
    Main support pipeline, run as a compiled LangGraph state machine
    (see the node functions and _build_graph() above).

    `thread_id` should be the Slack thread's root timestamp (thread_ts,
    or the message's own ts if it's the first message in the thread).
    Pass None (e.g. from the CLI test) to skip memory entirely.
    """

    final_state = _compiled_graph.invoke({
        "question": question,
        "image_path": image_path,
        "thread_id": thread_id,
    })

    return {
        "answer": final_state["answer"],
        "escalated": final_state["escalated"],
        "best_score": final_state["best_score"],
        "source": final_state["source"],
    }


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":
    thread_id = input("Thread ID (leave blank to skip memory): ").strip() or None
    question = input("Student question: ")

    result = diagnose(question, thread_id=thread_id)

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(f"\nSource: {result['source']}")
    print(f"Best RAG score: {result['best_score']:.4f}")
    print(f"Escalated: {result['escalated']}")
    print("\nAnswer:")
    print(result["answer"])