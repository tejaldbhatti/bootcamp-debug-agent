# LangChain for Beginners: Setup & Common Errors

Written for students new to LangChain. Covers what each piece does and
the errors beginners hit most often, organized by area.

---

## 1. Installation & Imports

**What it is:** LangChain is split across multiple packages —
`langchain` (core orchestration), `langchain-core` (base abstractions),
and provider-specific packages like `langchain-openai`,
`langchain-anthropic`, `langchain-community` (community-maintained
integrations). This split happened as the library grew, and it's the
single biggest source of beginner import errors.

**Common beginner errors:**

- **`ModuleNotFoundError: No module named 'langchain_openai'`** (or
  `langchain_anthropic`, `langchain_community`, etc.) — installing
  `langchain` alone does **not** install these. Install the specific
  provider package needed:
  `pip install langchain-openai` (note: package name uses a hyphen,
  import uses an underscore — `from langchain_openai import ...`).
- **`ImportError: cannot import name 'X' from 'langchain'`** — usually
  means the class moved to a different sub-package in a newer LangChain
  version. Check the current import path in the docs rather than
  assuming old tutorial code is still accurate; LangChain's internal
  organization has changed significantly across versions.
- **Works in one script but not another on the "same" setup.** Almost
  always a different Python environment between the two — see the
  VSCode environment troubleshooting doc for diagnosing this
  (`where`/`which python`, checking the active environment).
- **Old tutorial code uses `from langchain.chat_models import
  ChatOpenAI` and it doesn't work.** This import path has moved in
  recent versions — current code should use
  `from langchain_openai import ChatOpenAI`. When a tutorial's imports
  don't match installed docs, assume the tutorial is outdated rather
  than assuming your install is broken.

---

## 2. API Keys & Authentication

**What it is:** Most LangChain integrations (OpenAI, Anthropic,
Pinecone, etc.) need an API key, usually read from an environment
variable.

**Common beginner errors:**

- **`AuthenticationError` / `Incorrect API key provided`.** Almost
  always one of: the `.env` variable name doesn't match exactly what
  the code expects (e.g. `OPEN_API_KEY` vs `OPENAI_API_KEY` — a real,
  confirmed cause of this exact error in this bootcamp), the `.env`
  file was never loaded (missing `load_dotenv()`), or the key itself is
  a placeholder/expired value.
- **Key loads fine, but the wrong provider's key is being used.** If a
  script mixes multiple providers (OpenAI + Anthropic, say), double
  check each client is explicitly given the right variable —
  LangChain won't guess which key belongs to which provider.
- **Works locally, fails when deployed/shared.** The `.env` file
  (correctly) isn't committed to git, so a teammate's clone or a
  deployed environment won't have it — each environment needs its own
  `.env` set up separately, same as with any other environment
  variable/secret.

---

## 3. Chains & LCEL (LangChain Expression Language)

**What it is:** Chains combine a prompt, a model, and (optionally)
output parsing into a single callable pipeline. Modern LangChain code
typically builds these with the `|` (pipe) operator — LCEL — rather
than older chain classes.

**Common beginner errors:**

- **Mixing old-style chain classes with new LCEL syntax and getting
  confusing errors.** These are two different ways of building the
  same kind of pipeline; mixing patterns from different-era tutorials
  in one script is a common source of confusion. Prefer sticking to one
  consistent style within a single script.
- **`TypeError` when piping components together with `|`.** Usually
  means one component in the chain doesn't return the type the next
  component expects (e.g. piping a raw string where a
  `ChatPromptTemplate` output was expected). Check each piece's
  expected input/output type individually before assuming the whole
  chain is wrong.
- **Prompt template variables not filling in correctly / showing up as
  literal `{variable}` text in the output.** Usually a mismatch between
  the variable name used in the template string and the key used when
  invoking the chain (e.g. template expects `{question}` but the chain
  was called with `{"query": ...}`).

---

## 4. Agents & Tools

**What it is:** An agent is a model that can decide to call external
"tools" (functions) as part of answering, rather than just generating
text.

**Common beginner errors:**

- **Tool isn't being called even though it should clearly apply.**
  LangChain builds the tool's schema from its function signature and
  **docstring** — a missing or vague docstring (or missing type hints
  on parameters) can mean the model doesn't understand what the tool
  does or when to use it. A clear docstring describing exactly what the
  tool does and what its parameters mean fixes this more often than
  people expect.
- **Agent seems to loop or call tools repeatedly without finishing.**
  Often means the tool's return value isn't clearly signaling
  completion, or the prompt/instructions don't tell the model when to
  stop. Check what the tool actually returns and whether that return
  value gives the model enough information to decide it's done.
- **`ValidationError` when defining a tool's input schema.** Usually a
  mismatch between the function's actual parameters and the
  schema/type hints declared for it — these need to match exactly.

---

## 5. RAG, Embeddings & Vector Stores

**What it is:** Retrieval-Augmented Generation — embedding documents
into a vector database, then retrieving relevant chunks at query time
to ground the model's answer in real content instead of relying only
on what it learned during training.

**Common beginner errors:**

- **Retrieval returns irrelevant chunks.** Common causes: chunk size
  too large (dilutes relevance) or too small (loses context), or the
  embedding model used for the query doesn't match the one used to
  embed the documents — these must be the same model.
- **`Dimension mismatch` error from the vector store.** The embedding
  model's output size doesn't match the vector store index's configured
  dimension (e.g. index created for a 1536-dimension model, but
  queries are now using a different embedding model with a different
  size). If you switch embedding models, the index usually needs to be
  recreated, not just re-populated.
- **Nothing gets retrieved at all / empty results.** Check that
  documents were actually ingested (upserted) into the vector store
  successfully before querying — a failed or partial ingestion step
  earlier is a common root cause, not the retrieval query itself.
- **Answers still sound generic / not grounded in the actual docs.**
  Verify the retrieved context is actually being included in the final
  prompt sent to the model — a common bug is retrieving chunks
  correctly but forgetting to pass them into the prompt template.

---

## 6. Memory / Conversation History

**What it is:** Letting a chain or agent remember earlier messages in
a conversation, instead of treating every call as a fresh, isolated
question.

**Common beginner errors:**

- **Follow-up questions ignore earlier context entirely.** Memory
  isn't automatic — it has to be explicitly wired into the
  chain/agent and the conversation history has to actually be passed
  back in on each call.
- **Conversation grows and eventually hits a token limit /
  context-length error.** Long-running conversations without any
  summarization or trimming strategy will eventually exceed the
  model's context window — this is expected behavior, not a bug, and
  needs an explicit strategy (trimming, summarizing older messages) as
  conversations grow.

---

## 7. LangGraph (multi-step / stateful workflows)

**What it is:** A framework for building agents as an explicit graph of
steps/nodes, useful when logic needs real branching (e.g. "classify →
retrieve → decide answer vs escalate") rather than a single
straight-through chain.

**Common beginner errors:**

- **Unsure when to use LangGraph vs a plain chain/agent.** Rule of
  thumb: if the logic is genuinely branching (different paths depending
  on a decision), LangGraph gives more control and visibility. If it's
  a straightforward single pipeline, a plain chain is simpler and
  sufficient — don't reach for LangGraph by default.
- **Graph state isn't updating the way expected between nodes.** Each
  node needs to explicitly return the state updates it's responsible
  for — state doesn't automatically carry forward changes that weren't
  explicitly returned from a node function.

---

## 8. LangSmith (tracing & debugging)

**What it is:** A tool for viewing traces of what a chain/agent
actually did step by step — which prompts were sent, what came back,
which tools were called — useful for debugging why an agent behaved a
certain way.

**Common beginner errors:**

- **No traces showing up in LangSmith.** Usually means tracing wasn't
  enabled — check that the relevant environment variables
  (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, and similar) are set
  before running the script, not after.
- **Confusing LangSmith (the debugging/observability tool) with
  LangChain (the framework) or LangGraph (the workflow structure) —
  these are three separate but related projects, not interchangeable
  names for the same thing.**

---

## Quick diagnostic checklist

1. Which specific provider package is actually installed vs imported?
2. Is the API key variable name in `.env` an exact match to what the
   code reads?
3. Is the correct Python environment active (see VSCode troubleshooting
   doc)?
4. For RAG: was ingestion actually confirmed successful before
   debugging retrieval?
5. For agents: does the tool have a clear docstring and matching type
   hints?
