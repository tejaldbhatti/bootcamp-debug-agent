# n8n for Beginners: Setup & Common Errors

Written for students new to n8n. Covers what each piece does and the
errors beginners hit most often, organized by area.

---

## 1. What n8n Actually Is

**What it is:** n8n is a workflow automation tool — you connect
"nodes" (each representing a trigger, an action, or a piece of logic)
on a visual canvas, and n8n runs them in sequence when triggered.
Think of it as: instead of writing custom glue code to connect Slack,
a spreadsheet, and an API, you wire nodes together visually.

**Key concept for beginners:** every node passes data to the next node
as JSON. Understanding what JSON structure a node outputs (visible in
its **Output** panel after running it) is the single most useful skill
for debugging any workflow, since almost every "why isn't this
working" question comes down to a mismatch between what one node
outputs and what the next node expects as input.

---

## 2. Triggers & Activation

**What it is:** Every workflow starts with a **trigger** node (Manual
Trigger, Webhook, Schedule, Slack Trigger, etc.) that determines when
the workflow runs.

**Common beginner errors:**

- **Workflow doesn't run automatically even though it looks correctly
  built.** Check whether the workflow is actually **Active** (toggle in
  the top-right of the workflow editor) — a workflow with a real
  trigger (Webhook, Slack Trigger, Schedule) still won't fire unless
  it's toggled active, not just saved.
- **Testing with Manual Trigger works, but the real trigger (e.g. a
  webhook) doesn't.** Manual Trigger only runs when you click "Test
  workflow" — it doesn't validate that a webhook URL or external
  service integration is actually wired up correctly. These need to be
  tested separately, with the real event, not just the manual button.
- **A workflow was working, then stopped after being edited.** Some
  triggers (especially webhooks) register a URL with an external
  service at the time the workflow is activated — editing and
  re-saving a workflow can sometimes require reactivating the trigger
  for that registration to refresh, since the previously registered
  webhook URL may have gone stale.

---

## 3. Credentials & Authentication

**What it is:** Nodes that connect to external services (Slack,
Google Sheets, OpenAI, etc.) need credentials configured — API keys or
OAuth connections — stored separately in n8n's credentials manager, not
hardcoded into the node.

**Common beginner errors:**

- **Imported workflow shows a red warning triangle on every external
  node.** This is expected, not a bug — credentials never travel with
  an exported/imported workflow JSON file, for security reasons. Each
  node needs its credential reconnected locally after import.
- **OAuth-based credential (Google Sheets, Slack, etc.) stops working
  after a while.** OAuth tokens expire and need reconnecting —
  reopening that credential in n8n and going through the
  authorization flow again usually fixes it.
- **Credential looks connected, but the node still fails with an auth
  error.** Double-check the credential actually has the right
  **scopes/permissions** for what the node is trying to do (e.g. a
  Google Sheets credential authorized for read-only won't work for an
  Append/write operation).

---

## 4. Reading Node Input/Output (the core debugging skill)

**What it is:** Every node execution shows an **Input** panel and an
**Output** panel with the actual JSON that flowed through it — this is
the primary way to debug why a workflow isn't behaving as expected.

**Common beginner errors:**

- **Not checking Input/Output panels before assuming a node is
  "broken."** Run the workflow (or click a past execution), open the
  node, and look at exactly what came in and what went out — this
  answers most "why doesn't this work" questions faster than guessing
  at the configuration.
- **Expression (`{{ }}`) references a field that doesn't exist in the
  actual input data.** n8n expressions pull values from the previous
  node's JSON output using paths like `{{ $json.fieldName }}` — if the
  actual field is nested differently, named differently, or simply
  isn't present (check the Input panel to confirm), the expression
  will fail or return empty/undefined rather than what was expected.
- **Referencing a field from a node that isn't directly connected.**
  `{{ $('Node Name').item.json.field }}` requires the exact node name
  in quotes — if that node was ever renamed, expressions referencing
  its old name will break silently.

---

## 5. Common Nodes: HTTP Request, Slack, Google Sheets

**What it is:** These are among the most commonly used nodes in
practice — connecting to an external API directly, posting to Slack,
and logging to a spreadsheet.

**Common beginner errors:**

- **HTTP Request node returns an error status (4xx/5xx).** Check the
  Output panel — n8n usually surfaces the actual error response body
  from the external API, which almost always explains the real cause
  (wrong auth, malformed body, wrong endpoint) more precisely than the
  generic HTTP status code alone.
- **Slack node posts to the wrong channel, or a reply doesn't thread
  correctly.** For threaded replies, the node needs the specific
  `thread_ts` value from the original triggering message, referenced
  via an expression pointing back to the trigger node's output — not
  just the channel ID alone.
- **Google Sheets node fails to append/find the right sheet.** Confirm
  both the correct spreadsheet ID **and** the correct sheet
  name/tab — a workflow can have valid credentials and still fail if
  it's pointed at the wrong sheet name within the file.

---

## 6. Workflow Structure & Data Flow

**What it is:** How nodes connect and how data branches/merges across
a workflow.

**Common beginner errors:**

- **One node's output needs to reach two different downstream nodes,
  and only one seems to get the data.** n8n does support one output
  connecting to multiple downstream nodes (a "fan-out") — if only one
  branch appears to receive data, check that both connections are
  actually drawn on the canvas, not just one.
- **Workflow works with one test item but breaks with multiple
  items.** n8n nodes typically process arrays of items — logic written
  assuming exactly one item at a time can behave unexpectedly when a
  trigger produces multiple items in a single execution. Check whether
  a node is set to run once per item or once for the whole batch.

---

## 7. Airtable Integration

**What it is:** Connecting n8n to Airtable to read/write records,
usually via a personal access token credential.

**Common beginner errors:**

- **"Could not load list — 403 Forbidden" when selecting a Base, even
  though the credential connected successfully.** A credential that
  "connects" doesn't guarantee it can see every base. Check three
  things in order:
  1. The token's permissions need the **specific base/table** added
     explicitly — general scopes alone (e.g. `schema.bases:read`)
     aren't enough without also granting access to that particular
     base.
  2. Confirm the base actually lives in the **same workspace** the
     token has access to — a token created under one workspace won't
     see bases in a different workspace on the same account.
  3. n8n can cache the list of available bases — if permissions were
     just changed, try refreshing the credential connection or
     retrying the base selection a couple of times before assuming
     something's still misconfigured; a caching/propagation delay is a
     real, confirmed cause here.

- **Telegram data being mapped into Airtable is missing a field the
  table expects (e.g. "username").** Telegram's `username` field often
  isn't present at all if the user hasn't set one publicly — this is a
  data gap, not a workflow bug. Workaround: reuse an available field
  (like `first_name`) as a stand-in so there's still something to map.
  Also worth relabeling n8n's "Edit Fields" parameter names to match
  Airtable's actual column names before the mapping step — makes the
  connection between the two much less error-prone.

---

## 8. Google Drive / Docs on Self-Hosted n8n

**What it is:** Connecting n8n to Google Drive/Docs. The setup is
meaningfully different depending on whether n8n is Cloud or
self-hosted.

**Common beginner errors:**

- **The simple "Sign in with Google" button doesn't work / shows an
  org permission warning.** This one-click flow only works on **n8n
  Cloud**. On a **self-hosted** instance, a Google OAuth2 app has to be
  set up manually. Full setup path:
  1. Create/select a project in Google Cloud Console
     (console.cloud.google.com)
  2. Enable the **Google Drive API** for that project (APIs & Services
     → Library) — without this, sign-in can succeed but every actual
     Drive action still fails
  3. Configure the OAuth consent screen (External user type unless
     using Workspace), and while in "Testing" mode, explicitly add each
     Google account that needs access under "Test users" — otherwise
     Google blocks sign-in with an "app not verified" error
  4. Create an OAuth Client ID (type: Web application), and paste
     n8n's exact "OAuth Redirect URL" (shown on the credential screen)
     into "Authorized redirect URIs" in Google Cloud Console — must
     match exactly, no typos or trailing spaces
  5. Copy the resulting Client ID and Client Secret into n8n's Google
     Drive credential (Connection tab) and save
  6. Click "Sign in with Google" in n8n, using the same account added
     as a test user
  7. Test with a Google Drive node ("List Files" first, to confirm
     access before trying Download/other operations)

---

## 9. Telegram Trigger Specifics

**What it is:** Using a Telegram Trigger node to fire a workflow when a
message is sent to a bot.

**Common beginner errors:**

- **Sending a Telegram message doesn't trigger the workflow
  automatically — only clicking "Execute" in the editor works.** The
  workflow needs to be **Activated** (toggle in the top right of the
  editor), not just saved. An inactive workflow only responds to
  manual execution; once activated, real incoming Telegram messages
  trigger it automatically with no manual step needed.
- **Needed fields (name, username) aren't all present in the Telegram
  payload.** Check the actual JSON in the trigger node's Output panel
  rather than assuming a field exists — Telegram usernames in
  particular are often unset/private and simply won't be in the data.

---

## Quick diagnostic checklist

1. Is the workflow actually toggled **Active**, not just saved?
2. Are all credentials reconnected (especially after importing a
   workflow)?
3. What does the Input/Output panel of the failing node actually show?
4. Does an expression's field path match what's really in the previous
   node's JSON output?
5. For Slack/Sheets specifically: right channel/thread, right
   spreadsheet/sheet name?
