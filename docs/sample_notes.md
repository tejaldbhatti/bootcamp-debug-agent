# Sample knowledge base (placeholder)

This is a small placeholder knowledge base so the prototype has something to
retrieve from. Replace or add files in this `docs/` folder with real notes,
FAQs, or exported doc pages from LangChain, MCP, n8n, and VSCode/Codex before
using this for real students.

## LangChain: common setup issues

- If you see `ModuleNotFoundError` for a LangChain submodule, it is often a
  version mismatch: recent LangChain releases split functionality across
  several packages (e.g. `langchain`, `langchain-core`, `langchain-openai`).
  Reinstalling with `pip install -U langchain langchain-openai` usually fixes it.
- Missing API key errors usually mean the environment variable (e.g.
  `OPENAI_API_KEY`) was not exported in the same terminal session running the
  script, or a `.env` file wasn't loaded (needs `python-dotenv` + `load_dotenv()`).
- Agent tool errors often come from a tool function missing a docstring or
  type hints — LangChain uses these to build the tool schema for the model.

## MCP (Model Context Protocol): common setup issues

- An MCP server that doesn't show up in an editor/agent is almost always a
  config path or transport mismatch — double check the config file location
  and whether the server expects stdio vs. HTTP transport.
- Permission errors often mean the MCP server process doesn't have access to
  the working directory it's trying to operate on.

## n8n: common setup issues

- A workflow that doesn't trigger usually means the trigger node (e.g. Slack
  Trigger) isn't "Active" or the webhook URL registered with the external
  service is stale after a workflow edit.
- Credential errors usually mean the OAuth token expired and needs
  reconnecting in the n8n credentials panel.

## VSCode / Codex integration: common setup issues

- If suggestions stop appearing, it's often an expired auth session for the
  extension — signing out and back in resolves most of these.
- Extension conflicts (two AI-assistant extensions enabled at once) can cause
  silent failures; disabling one at a time helps isolate the issue.
