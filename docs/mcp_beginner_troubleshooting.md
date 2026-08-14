# MCP (Model Context Protocol) for Beginners: Setup & Common Errors

Not part of the official bootcamp syllabus, but comes up in practice
since it's closely tied to VSCode/Codex-style AI tooling. Written for
students encountering it for the first time.

---

## 1. What MCP Actually Is

**What it is:** MCP is an open protocol that lets AI tools (like an
editor's AI assistant) connect to external "servers" that expose
tools, data, or capabilities — for example, a server that can read
files, query a database, or call an API. The AI assistant discovers
and uses whatever tools an MCP server exposes, without needing custom
integration code for each one.

**Key concept for beginners:** an MCP *server* isn't a website — it's
usually a small local program (often started automatically by the
editor) that the AI assistant talks to over a defined protocol. Most
setup problems come from that program either not starting correctly or
not being configured with the exact settings the editor expects.

---

## 2. Configuration File Issues

**What it is:** MCP servers are registered in a config file (the exact
location and format differs by editor/tool — this is the single
biggest source of confusion for beginners).

**Common beginner errors:**

- **Server doesn't show up in the editor at all.** Almost always a
  config file location mismatch — different editors/tools look for MCP
  config in different specific paths, and a config that's correct for
  one tool won't be picked up by another. Double-check the exact
  expected path for the specific editor/extension version being used
  rather than assuming all MCP-compatible tools share one config
  location.
- **JSON syntax error in the config file (trailing comma, missing
  bracket, etc.) silently breaks everything.** MCP config is typically
  plain JSON, and a single syntax error can cause the whole config to
  fail to load with no clear error message pointing at the specific
  line. Validate the JSON structure carefully (a JSON linter/formatter
  catches this fast) before assuming the server itself is broken.
- **Config changes don't take effect.** Most editors need a restart (or
  at minimum a config reload command) after editing MCP config — the
  running instance doesn't always hot-reload it automatically.

---

## 3. Transport Type Mismatches

**What it is:** MCP servers can communicate over different transport
methods — most commonly **stdio** (the editor launches the server as a
subprocess and talks to it directly) or **HTTP/SSE** (the server runs
independently and the editor connects to it over a network address).

**Common beginner errors:**

- **Server is configured for the wrong transport type.** If a server
  expects stdio but the config tries to connect to it as if it were an
  HTTP server (or vice versa), the connection will fail even though
  both the server and the config look individually correct. Check
  which transport the specific MCP server actually implements/expects
  before writing the config entry for it.
- **Command/path in the config is wrong for launching a stdio
  server.** For stdio servers, the config typically needs an exact
  command (e.g. `npx some-mcp-server` or a direct path to an
  executable) — a typo or wrong working directory here means the
  editor can't actually start the server process.

---

## 4. Permission & File Access Errors

**What it is:** MCP servers that read/write files or run commands
operate with whatever permissions the process they're running under
has.

**Common beginner errors:**

- **Permission denied when the server tries to access a file or
  directory.** Usually means the server process doesn't have access to
  the working directory it's trying to operate on — check where the
  server was actually launched from versus where it's trying to read
  or write.
- **Server can see some files but not others in the same project.**
  Some MCP servers are explicitly scoped to a specific root directory
  in their config — if a file falls outside that configured scope, it
  won't be accessible even if the server process technically has OS
  permission to read it.

---

## 5. Environment Variables & API Keys for MCP Servers

**What it is:** Many MCP servers need their own API keys or config
values (separate from the ones used elsewhere in a project), passed
via environment variables in the server's config entry.

**Common beginner errors:**

- **Server starts but immediately fails/errors on first use.** Often
  means a required environment variable (API key, token, etc.) wasn't
  set in the server's specific config block — MCP server env vars are
  usually configured per-server in the same JSON config, separate from
  a project's own `.env` file, so setting the key in `.env` alone
  doesn't automatically make it available to the MCP server process.
- **Works when run manually in a terminal, but not when launched by the
  editor.** The editor launches the server in its own process
  environment, which may not inherit the same environment variables as
  a manually opened terminal. Check whether the MCP config itself
  explicitly passes the needed variables, rather than assuming they'll
  be inherited.

---

## 6. Tool Not Being Used / Not Appearing

**What it is:** Even with a correctly connected server, the AI
assistant might not use a tool the way expected.

**Common beginner errors:**

- **Server connects successfully, but its tools never get called.**
  Similar to the LangChain agent-tools issue — this can come down to
  how clearly each tool describes what it does; vague tool descriptions
  make it harder for the model to decide when a tool is relevant.
- **Confusing "server connected" with "server configured correctly."**
  A green checkmark or "connected" status usually just means the
  process started and the protocol handshake succeeded — it doesn't
  guarantee every tool the server exposes is actually usable end to
  end (e.g. a tool might still fail once actually invoked, due to a
  missing permission or env var as above).

---

## Quick diagnostic checklist

1. Is the config file in the exact path this specific editor/tool
   expects?
2. Is the JSON in that config file actually valid (no trailing
   commas/missing brackets)?
3. Has the editor been restarted/reloaded since the config was last
   changed?
4. Does the config use the transport type (stdio vs HTTP) that this
   specific server actually implements?
5. Are any required API keys/env vars set directly in the MCP server's
   config block, not just in a project's `.env` file?
6. Is the server's working directory/scope actually covering the files
   it needs to access?
