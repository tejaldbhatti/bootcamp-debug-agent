# Manually curated support Q&A

Copy real questions and their working solutions from Slack here, in your
own words if you prefer, with no student names or identifying details.
Save this file, then run `python ingest.py` to add it to the knowledge base.

Keep each entry short and specific — one real problem, one real fix.
Skip anything that was never actually resolved (an unanswered question
teaches the agent nothing useful and can confuse retrieval).

---

### Question
ModuleNotFoundError: No module named 'langchain_openai' when running a
basic agent script.

**Answer:** This happens when only `langchain` was installed but not the
provider-specific package. Fix: `pip install langchain-openai` in the
same virtual environment the script is run from.

---

### Question
MCP server doesn't show up in VSCode even though it's listed in the
config file.

**Answer:** Usually a config file location mismatch — VSCode looks for
the MCP config in a specific settings path that differs from other
editors. Double-check the exact path expected by the VSCode MCP
extension version being used, and restart VSCode after saving the
config.

---

### Question
Why is there a staging area before commit in Git — why not just commit
directly?

**Answer:** This is intentional design, not a limitation. Git computes a
snapshot of what's staged, not what's sitting in the working directory.
Linus Torvalds deliberately built the staging area so developers
construct commits carefully rather than committing everything changed
since the last save automatically. It lets you group related changes
into meaningful, well-named commits instead of one giant "everything I
touched" commit. Analogy: it's like laying clothes out on the bed
before deciding what actually goes in the suitcase, rather than
throwing in everything from the closet. Beginners tend to add and
commit everything at once; experienced developers group changes into
meaningful, separately named commits.

---

### Question
"Failed to create conda environment: A system error occurred (ENOENT:
no such file or directory, scandir 'conda-meta')" when running a script
in VSCode.

**Answer:** Resolved via VSCode's command palette: run "Python: Select
Interpreter" and manually choose the correct interpreter/conda
environment, instead of relying on VSCode to auto-detect it.

---

### Question
What's the difference between "Publish Branch" and "Sync Changes" in
VSCode's Git panel?

**Answer:** "Publish Branch" shows up the first time you push a
branch — it only exists on your computer, GitHub doesn't know about it
yet. "Sync Changes" shows up after that; it uploads your new commits
and downloads any changes from GitHub, keeping both sides matched.
Simple rule: new branch → Publish Branch, branch already on GitHub →
Sync Changes. Example: first commit on `main` → button says "Publish
Branch" → click it → branch now exists on GitHub too. Next day, more
commits → button now says "Sync Changes" → click it → new commits go
up, anything new from GitHub comes down. Tip: a number next to "Sync
Changes" (like ↑2 ↓1) means 2 commits to push and 1 to pull.

---

### Question
After cloning a repo and starting a new lab, got errors where the
Python version / kernel / environment weren't happy with each other —
caused by a new folder/repo needing its own fresh setup.

**Answer:** Install the missing library in the environment the notebook
is actually running on — `!pip install package_name` (in a notebook
cell) or `conda install package_name` (in the terminal) — then restart
the notebook kernel.

---

### Question
Is there a better way to have prerequisites (pandas, numpy, ipykernel,
etc.) installed by default, instead of reinstalling them every time you
start a new project/lab folder?

**Answer:** Two common approaches: (1) Keep one shared environment
(conda or venv) that you reuse across labs, rather than creating a
brand-new one per repo/folder — in VSCode, just select that same
existing kernel/interpreter for the new notebook instead of letting it
create a fresh environment. (2) If each lab genuinely needs its own
isolated environment, add a `requirements.txt` (pip) or
`environment.yml` (conda) to the repo listing the needed packages, so
setup is one command (`pip install -r requirements.txt` or
`conda env create -f environment.yml`) instead of installing packages
one by one by hand.

---

### Question
Lab code template's class distribution shows "Malignant (1): 357,
Benign (0): 212" but the lab instructions say it should be "357 benign,
212 malignant" — is this a typo?

**Answer:** Not a typo — it's a labeling mix-up in the code template.
Scikit-learn's breast cancer dataset actually encodes `target == 0` as
malignant and `target == 1` as benign (the original Wisconsin
Diagnostic Breast Cancer dataset creators chose this encoding, and
scikit-learn preserves it as-is). If the code template's `label=` text
has "Benign" and "Malignant" swapped relative to that, the plot will
still show clear separation and any checkpoint will still pass — the
colors/legend text are just backwards relative to the actual encoding.
To verify which index is which: `print(cancer_data.target_names)`. To
fix the labels in a histogram plot, swap the `label=` strings, e.g.:

```python
axes[idx].hist(df[df['target'] == 0][feature], alpha=0.5, label='Malignant', bins=30)
axes[idx].hist(df[df['target'] == 1][feature], alpha=0.5, label='Benign', bins=30)
```

Note for later: if computing precision/recall and you want the
"positive" class to be malignant (0), pass `pos_label=0` explicitly,
e.g. `precision_score(y_true, y_pred, pos_label=0)`.

---

### Question
Lab step "Making Predictions" (task 2 & 3: compare predictions with
actual values, look at a few examples) — the code template only shows
`knn.predict()` and prints the *count* of predictions. Is the code for
comparing/inspecting individual predictions missing?

**Answer:** Not missing — those two tasks are meant to be done by
inspection, not by writing more code. The template's print statements
only confirm predictions were made (the count). To actually look at
individual predictions, create a new cell and just type `y_train_pred`
(or `y_test_pred`) on its own to inspect the variable's contents
directly. Tasks 2 and 3 ("compare with actual values", "look at a few
examples") are about exploring the existing output, not writing new
logic — you're checking by eye whether the predicted values look
similar to the actual values. Adding more code is optional, not
required. The automated/coded way to do this comparison comes later,
in the next step.

---

### Question
Got `CondaToSNonInteractiveError` when trying to create a Conda
environment.

**Answer:** Not a broken install — Conda recently added a requirement
to accept its Terms of Service before creating any environment. Run
`conda tos accept` (with the appropriate channel arguments) before
retrying the environment creation command. This affects everyone using
a recent Conda version, not something specific to your setup.

---

### Question
VS Code only shows "venv" as an interpreter option, not "Conda" — even
though Conda is installed.

**Answer:** Usually one of: Conda wasn't installed correctly, VS Code
hasn't detected it yet, or VS Code simply needs to be restarted after
installation to pick up newly available tools. Installing software
doesn't always mean an already-open application knows it exists yet —
restart VS Code first before assuming the install failed.

---

### Question
Terminal/VS Code says `git: command not found` or "Git is not
recognized" even after installing Git.

**Answer:** In most cases Git isn't actually missing — VS Code just
needs to be restarted after the install so it can detect the new `git`
executable on the system PATH.

---

### Question
Created a Conda environment successfully, but it doesn't show up as a
kernel option in Jupyter/VS Code notebooks.

**Answer:** The environment exists, but it hasn't been registered as a
Jupyter kernel yet — those are two separate steps. Run:
`python -m pip install ipykernel` (installs the piece that lets Jupyter
talk to that Python environment), then
`python -m ipykernel install --user --name <env-name> --display-name "Python (<env-name>)"`
(registers it so it appears as a selectable kernel).

---

### Question
Why does the bootcamp recommend Python 3.11 (or 3.12) instead of the
newest Python release?

**Answer:** Many machine learning/data science libraries need time
after a new Python release before they officially support it. Using a
slightly older, stable version avoids compatibility issues with those
libraries — this is a deliberate choice, not an oversight.

---

### Question
Notebook cell with a `try/except` around `pd.read_csv(CSV_FILE)` prints
`CRITICAL ERROR: The file at ../data/titanic.csv does not exist. Check
your path!` — the `FileNotFoundError` branch is triggering.

**Answer:** This is a relative-path issue, not a missing-file issue in
most cases. A relative path like `../data/titanic.csv` is resolved
against the notebook kernel's **current working directory**, not
against where the `.ipynb` file visually sits in the VS Code file
explorer. Fix steps:
1. Check the actual working directory the kernel is running from:
   `import os; print(os.getcwd())`
2. Compare that to where `data/titanic.csv` actually lives on disk, and
   adjust the relative path (`../`, `./`, etc.) to match, or move up/down
   folders accordingly.
3. If unsure, use an absolute path temporarily to confirm the file
   loads, then fix the relative path once you know the correct working
   directory.
4. Also double-check the file actually exists at that location and the
   filename/extension matches exactly (case-sensitive on some systems).

---

### Question
Saved changes to a `.ipynb` notebook in VS Code, but nothing shows up in
the Source Control panel to stage or commit.

**Answer:** A few common causes, worth checking in this order:
1. **Wrong folder opened as the workspace.** If the folder opened in
   VS Code doesn't contain the `.git` folder (e.g. you opened a
   subfolder instead of the actual repo root), Source Control will show
   nothing for any file. Check `File > Open Folder` points at the repo
   root.
2. **The file is gitignored.** Some repo templates ignore `*.ipynb` or
   notebook checkpoint files on purpose to avoid committing bulky
   output/execution metadata. Check `.gitignore` in the repo root for a
   matching pattern.
3. **File wasn't actually saved / no real content change.** Confirm
   with `Cmd/Ctrl+S`, not just running cells — running cells changes
   execution counts/output but doesn't always trigger a save on its
   own.
4. **Source Control panel is stale.** Click the refresh icon at the top
   of the Source Control panel.
5. **The notebook lives outside the open workspace folder entirely,**
   so git doesn't track it at all.

Fastest way to diagnose all of the above at once: open a terminal in
that same folder and run `git status` — it will say plainly whether the
file is tracked, ignored, or outside the repo.

---

### Question
`ModuleNotFoundError: No module named 'openai'` when running a script
(likely to also happen with other packages like `datasets`).

**Answer:** Install the missing package: `pip install openai` (or
`pip install datasets`), run either in the terminal or a notebook cell.
If the error keeps coming back after installing it once, the likely
cause is installing into a different environment/kernel than the one
actually running the script — double check the active conda
environment (or VS Code's selected interpreter/kernel) matches the one
you installed the package into before re-running.

---

### Question
Are Conda/Python environments stored locally on your computer, or on
GitHub?

**Answer:** Always local only. Environments (and the packages installed
in them) are never pushed to GitHub — cloning a repo on a new machine
does not bring the environment with it; it has to be recreated there
separately.

---

### Question
Step using Hugging Face product images errors out around
`encode_image_to_base64` / `sample_path = products_df.iloc[0]["image_path"]`.

**Answer:** The original `encode_image_to_base64` function assumes it's
given a file path on disk (`open(path, "rb")`), but the Hugging Face
dataset actually returns a **PIL image already in memory**, not a file
path — so `image_path` doesn't exist as a column/approach here. Fix:
rewrite the function to accept a PIL image and encode it via
`io.BytesIO()` instead of opening a file:

```python
import io, base64

def encode_image_to_base64(pil_image):
    """Encode an in-memory PIL image to a base64 string."""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

# Example usage — note: pass the image itself, not a path
sample_image = products_df.iloc[0]["image"]
encoded_image = encode_image_to_base64(sample_image)
```

Tip: save at least some images to disk locally rather than re-loading
from the Hugging Face dataset every single time — it's noticeably
faster for repeated runs.

---

### Question
`.env` file has the API key, `load_dotenv()` runs with no errors, but
`os.getenv("OPENAI_API_KEY")` still comes back empty/None. Tried
absolute path, relative path, `find_dotenv()`, removed quotes around
the key — nothing works.

**Answer:** Before anything else, check for a **variable name
mismatch** between the `.env` file and the code — this was the actual
cause in a real case that looked identical to this (everything about
loading the file was correct, but the key was saved in `.env` as
`OPEN_API_KEY` while the notebook was reading `OPENAI_API_KEY` —
different variable names, so it silently returns None with no error).
Full troubleshooting checklist:
1. Confirm the exact variable name in `.env` matches exactly what the
   code calls in `os.getenv(...)` — typos or a missing "AI" are easy to
   miss
2. Try `from dotenv import load_dotenv, find_dotenv` then
   `load_dotenv(find_dotenv())` — lets Python locate the `.env` file
   automatically instead of relying on a path
3. Try a relative path: `load_dotenv(".env")`
4. Confirm the `.env` file actually contains the key (open it and look)
5. Print `os.getenv("OPENAI_API_KEY")` directly to check what's actually
   being loaded
6. Confirm the key value itself is the one you were actually given (not
   an old/placeholder value)

Also: if `.env` isn't in `.gitignore`, add it there — accidentally
committing an API key is a real risk, not just a formatting concern.

---

### Question
`zsh: command not found: brew` — Homebrew commands don't work in the
terminal (Mac).

**Answer (general known fix, not confirmed against this specific
thread — verify before relying on it):** Usually one of two causes:
1. **Homebrew isn't actually installed yet** — install it from
   https://brew.sh (run the official install command in Terminal).
2. **Homebrew is installed but not on the shell's PATH** — common on
   Apple Silicon Macs (M1/M2/M3), where Homebrew installs to
   `/opt/homebrew/bin` instead of the older Intel-Mac default of
   `/usr/local/bin`. Fix by adding it to your shell config:
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   source ~/.zshrc
   ```
   Then close and reopen the terminal (or re-run `source ~/.zshrc`) and
   try `brew --version` again.

---

### Question
How do you install `ffmpeg` (needed for some labs), and it's not being
recognized by the system?

**Answer:**
**On Windows:**
1. Download from https://ffmpeg.org/download.html
2. It needs to be manually added to the system PATH — follow the
   Installation section instructions on this guide:
   https://video.stackexchange.com/questions/20495/how-do-i-set-up-and-use-ffmpeg-in-windows
   (the PATH-setup step is the critical one; skipping it is the most
   common reason `ffmpeg` still isn't recognized afterward)
3. Restart the computer after installing

**On Mac:**
1. If Homebrew is already installed: `brew install ffmpeg`
2. If Homebrew isn't installed yet, install it first via terminal:
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   then run `brew install ffmpeg`
3. Restart the computer after installing

More on Homebrew itself: https://brew.sh/

---

### Question
`pip install ffmpeg` succeeds with no errors, but `ffmpeg --version` in
the terminal still says "not recognized" (Windows PowerShell).

**Answer:** This is a common trap — the PyPI package literally named
`ffmpeg` is **not** the actual FFmpeg program; it's an unrelated/thin
package, so `pip install ffmpeg` will never make the real `ffmpeg`
command available in your terminal. FFmpeg itself has to be installed
as a standalone program, not via pip. Fix: download the actual FFmpeg
build directly from
https://ffmpeg.org/download.html#build-windows and add it to your
system PATH (see the other ffmpeg Windows install entry in this doc for
the PATH-setup step, which is the part most commonly missed). A
step-by-step video walkthrough: https://www.youtube.com/watch?v=KBnyOH1o5Ms

---

### Question
Why does `git clone` always create a subfolder with the same name as
the repo, instead of putting the files directly where I ran the
command?

**Answer:** This is expected default behavior, not a bug. By default,
`git clone <url>` creates a new folder named after the repository and
puts everything inside it. If you want the contents cloned directly
into the current folder instead (without an extra nested subfolder),
run `git clone <url> .` (with a space and a dot at the end).

---

### Question
How do you add a collaborator to a personal GitHub repository?

**Answer:** Steps:
1. Get the collaborator's GitHub username (they need a GitHub account
   first)
2. Go to the repository's main page on GitHub
3. Click **Settings** (if not visible, check the dropdown menu near the
   repo name first)
4. In the "Access" section of the sidebar, click **Collaborators**
5. Click **Add people**
6. Type their name/username in the search field and select them from
   the matching results
7. Click **Add [name] to [repository]**
8. They'll get an email invite — once accepted, they have collaborator
   access to the repo

Note: on GitHub Free, you can add unlimited collaborators to both
public and private repositories.

---

### Question
Even with a conda environment already activated, VS Code shows a
warning: "You may have installed Python packages into your global
environment, which can cause conflicts between package versions. Would
you like to create a virtual environment with these packages to isolate
your dependencies?"

**Answer:** Safe to ignore (click "Don't show again" if it's annoying).
This is VS Code's built-in Python extension detecting that packages
also exist in the global/base Python install, and offering to create a
separate `venv` for them — it doesn't know you're already using conda
for isolation. Since the bootcamp workflow uses conda environments
(not VS Code's own venv suggestion) for isolation, this prompt doesn't
apply and can be dismissed.

---

### Question
Cloned a teammate's repo and ran their `.py` file locally — got
`ModuleNotFoundError` for one package, installed it, then got the same
error for a different package, and this kept repeating.

**Answer:** This whack-a-mole pattern usually means their code needs
several packages, and they were never installed in one consistent
environment on your machine. Instead of installing packages one at a
time as each error appears:
1. Check if the repo has a `requirements.txt`. If so, activate your
   environment and run `pip install -r requirements.txt` once — this
   installs everything needed in a single step.
2. If there's no `requirements.txt`, ask the teammate to generate one
   from their own environment: `pip freeze > requirements.txt`, then
   share it — far more reliable than reproducing their setup by trial
   and error.
3. Double-check you're actually running the script in the same
   environment you're installing packages into — confirm the active
   Python interpreter/kernel (shown in VS Code's bottom-right corner or
   top-right of a notebook) matches where you ran `pip install`. A
   mismatch here is the most common reason a "fixed" error keeps coming
   back for a new package each time.

---

### Question
Struggling to switch from `.ipynb` to `.py` files — used to running
notebooks cell by cell, and running `python filename.py` in the
terminal keeps giving "file not found." What's actually different
between the two, and how do you work with `.py` files?

**Answer:** Conceptually: a `.ipynb` notebook mixes text, code, and
output together and runs through a **kernel** (which is just Python
running behind the scenes) — you execute cell by cell. A `.py` file is
plain code only, run top-to-bottom all at once from the terminal with
`python filename.py`. `.py` is the standard format for actual software
deployment (notebooks are great for exploration, not for shipping
code).

The "file not found" error almost always means the terminal's **current
directory** doesn't match where the file actually is — `python
filename.py` looks for that file relative to wherever the terminal is
currently pointed, not relative to where the file happens to be open in
your editor. Fix: `cd` into the folder containing the file first (or
provide the full/relative path to it), then run the command again.
Quick check: run `pwd` (Mac/Linux) or `cd` alone (Windows) to see the
current directory, and `ls` (or `dir` on Windows) to confirm the file
is actually there.

Also worth checking: are you running the `.py` file in the same
Python environment you use for your notebooks? A mismatched
environment can cause a *different* set of errors (missing packages)
once the file-not-found issue is solved.

---

### Question
Gradio generates a new public URL every time the app is run. Is there a
way to always test on the same, stable URL?

**Answer:** Gradio's default `share=True` link is temporary and changes
each run by design. For a stable/static URL, two options:
1. **Deploy to Hugging Face Spaces** — gives a permanent, unchanging
   URL for the app.
2. **Use ngrok** — the free tier includes one static domain, which can
   be pointed at your local Gradio app for a consistent URL across
   runs.

---

### Question
`git pull`/sync fails with "fatal: Need to specify how to reconcile
divergent branches" — want to just push local changes to main without
pulling/merging anything else, since all the real work was done
locally.

**Answer:** Divergent branches means your local branch and the remote
(GitHub) branch each have commits the other doesn't have — usually
because something was pushed to GitHub that was never pulled locally
(or was forgotten). There's no way to just push past this; git needs
to reconcile the two histories somehow first. Options, roughly from
safest to most aggressive:
1. **Reconcile normally:** set a merge/rebase strategy (e.g.
   `git config pull.rebase false` for a merge, or
   `git config pull.rebase true` for a rebase), then `git pull` and
   resolve any conflicts, then push.
2. **Keep local changes as the source of truth:** if you're confident
   nothing important exists on the remote that isn't already local,
   you can force your local state to win — but this is destructive to
   whatever differs on the remote, so only do this if you're sure
   (e.g. `git push --force` after confirming with your team, or
   pulling with a merge strategy favoring local changes).
3. **Manually reconcile:** pull, inspect the conflicts, and resolve
   them yourself file by file.

There's no way to avoid dealing with the divergence once it's
happened — once branches have diverged, that has to be resolved one way
or another before pushing succeeds again.

---

### Question
n8n's Airtable node ("Create a record" or similar) shows "Could not
load list — 403 Forbidden: Invalid permissions, or the requested model
was not found" when trying to select a Base, even though the
credential/token connected successfully.

**Answer:** Three separate things to check, in order (a credential
that "connects" successfully doesn't guarantee it can see everything
needed):
1. **Token scope doesn't include the specific base/table.** A
   personal access token needs explicit access granted to the specific
   database/table it needs to read, not just general API scopes (e.g.
   `schema.bases:read` alone isn't enough — the token also needs the
   specific base added to its access list). Add the exact base/table
   to the token's permissions. To find exact base/table IDs for
   troubleshooting: https://support.airtable.com/docs/finding-airtable-ids
2. **Two different Airtable workspaces on the same account.** If the
   token was created under a different workspace than the one the
   target base actually lives in, it won't see that base in the list
   even with otherwise-correct permissions — confirm the base is in the
   same workspace the token has access to.
3. **Stale cache.** n8n can cache the list of available bases/tables
   from a credential — if permissions were just changed, the dropdown
   may still show the old (empty/forbidden) result until the
   credential connection is refreshed or the node is reloaded.

Confirmed in a separate real case: even after checking token
authorization/workspace and regenerating the token (with a successful
connection test), the 403 persisted until simply **retrying the base
selection a couple more times** — consistent with a caching/propagation
delay rather than an actual permissions problem. If everything above
checks out and it still fails, trying again after a short wait is a
reasonable next step before assuming something is misconfigured.

---

### Question
Building a Telegram → Airtable workflow in n8n. The lab/Airtable table
expects both "Name" and "username" fields, but the Telegram trigger's
JSON only provides `first_name` — no separate username field to map.
Also unsure whether to relabel the n8n parameter fields to match
Airtable's column names.

**Answer:** Telegram usernames are often not public/set for a given
user, so `message.from.username` may simply not exist in the payload —
this isn't a missing-step error, it's a real data gap. Workaround:
duplicate/reuse the available data (e.g. use `first_name` again as a
stand-in for the missing username field) so there's still something to
map into that Airtable column, rather than leaving it unmapped. On
relabeling: yes, it's worth relabeling the n8n "Edit Fields" parameter
names to match Airtable's actual column names — makes the later
mapping step into the Airtable node clearer and less error-prone than
leaving generic field names. For the general sender/chat fields: the
"sender" column can hold the name (`message.from.first_name`), and a
separate "chat" column can hold the chat ID (`message.chat.id`).

---

### Question
Sending a message on Telegram doesn't trigger the n8n workflow
automatically — have to manually click "Execute" for the trigger to
fire and data to reach Airtable.

**Answer:** Publish/activate the workflow (toggle it to **Active**, top
right of the workflow editor) — a saved-but-inactive workflow only
responds to the manual "Execute" button in the editor, not to real
incoming events. Once activated, subsequent Telegram messages trigger
the workflow automatically with no manual intervention needed.

---

### Question
Connecting Google Docs/Drive to n8n shows an error/permission prompt
referencing the organization (e.g. "Ironhack needs to give permission
to this app") — the simple "Sign in with Google" flow doesn't work.

**Answer:** This happens because self-hosted n8n instances don't get
the one-click "Sign in with Google" option — that only works on n8n
Cloud. On self-hosted, a Google OAuth2 app has to be set up manually
(Client ID + Secret from Google Cloud Console, with an exact matching
redirect URL). Full setup:

1. **Create/select a Google Cloud project.** Go to
   console.cloud.google.com, use the project dropdown at the top,
   either pick an existing project or create a new one (e.g.
   "n8n-integration"). Make sure it's the selected/active project
   before continuing.
2. **Enable the Google Drive API.** Left menu → APIs & Services →
   Library → search "Google Drive API" → Enable. Required — without
   this, the OAuth sign-in itself can succeed but any actual Drive node
   action will still fail.
3. **Configure the OAuth consent screen.** APIs & Services → OAuth
   consent screen → choose "External" (unless using Google Workspace),
   fill in app name/support email/developer contact email. While the
   app is in "Testing" mode, add the specific Google account(s) that
   will use it under "Test users" — otherwise Google blocks sign-in
   with an "app not verified" error.
4. **Create OAuth Client ID credentials.** APIs & Services →
   Credentials → Create Credentials → OAuth client ID → type "Web
   application." In n8n's Google Drive credential screen, copy the
   exact "OAuth Redirect URL" shown there (e.g.
   `https://your-n8n-instance/rest/oauth2-credential/callback`) and
   paste that **exact** URL into "Authorized redirect URIs" in Google
   Cloud Console — no trailing spaces, no typos, must match exactly.
5. **Copy Client ID and Client Secret into n8n.** Google shows a popup
   with both values after creating the credential — paste them into
   the corresponding fields on n8n's Google Drive credential
   (Connection tab), then save.
6. **Sign in with Google inside n8n.** Click "Sign in with Google" on
   the credential screen, sign in with the same account added as a test
   user in step 3, and approve the requested Drive permissions.
7. **Test the connection.** Add a Google Drive node to a workflow,
   select the new credential, set operation to "Download" or
   "List Files" (to confirm access first), point it at a real
   file/folder, and execute the node — success confirms the whole setup
   is working.

---

### Question
[Copy the next real question here]

**Answer:** [Copy the real working fix here]

---
