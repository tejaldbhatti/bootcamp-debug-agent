# VSCode for Beginners: Notebooks, Python Files, Environments, Codex

Written for students new to VSCode. Covers what each piece actually
does and the errors beginners hit most often.

---

## 1. Jupyter Notebooks in VSCode

**What it is:** A `.ipynb` file mixes text, code, and output in one
document, run cell by cell through a **kernel** (the Python process
actually executing your code — not VSCode itself).

**How students use it:** Open a `.ipynb` file → click a cell → press
`Shift+Enter` to run it → output appears directly below.

**Common beginner errors:**

- **"Select Kernel" keeps appearing / no kernel selected.** The
  notebook doesn't know which Python environment to run in yet. Click
  the kernel picker (top-right of the notebook) and choose the correct
  environment (e.g. `Python 3.11 (bootcamp-env)`). If it's not listed,
  the environment likely hasn't been registered as a Jupyter kernel yet
  (see the `ipykernel` fix in the environments section below).
- **Cell runs forever / stuck on `[*]`.** Either a genuinely long
  computation, an infinite loop, or a stuck kernel. Try
  "Restart Kernel" (circular arrow icon at the top of the notebook)
  before assuming your code is broken.
- **Variable from an earlier cell is "not defined."** Notebooks execute
  cells in the order you *run* them, not the order they appear on the
  page. If cells are run out of order (e.g. cell 5 before cell 3), a
  variable might not exist yet. Fix: use "Restart Kernel and Run All"
  to execute everything top-to-bottom cleanly.
- **Output/plots don't show up.** Usually means the cell producing the
  plot wasn't actually re-run after a code change — re-run that
  specific cell.

---

## 2. Running `.py` Files

**What it is:** A `.py` file is plain Python code, executed top to
bottom all at once — no cell-by-cell execution like a notebook.

**How students run it:** Either click the ▶ "Run" button in the top
right of the editor, or in a terminal: `python filename.py`.

**Common beginner errors:**

- **"No such file or directory" / file not found for a data file the
  script reads.** The terminal's current working directory doesn't
  match where the file actually is. `cd` into the correct folder first,
  or check with `pwd` (Mac/Linux) / `cd` alone (Windows) what directory
  you're actually in.
- **`ModuleNotFoundError` when a notebook using the same import worked
  fine.** The `.py` file might be running under a different Python
  interpreter/environment than the notebook. Check the interpreter
  selected in VSCode's bottom status bar matches the environment the
  package was installed into.
- **Script runs with no errors but produces no visible output.**
  Unlike a notebook, a `.py` file won't automatically display the value
  of an expression — you need an explicit `print()` statement to see
  anything in the terminal.

---

## 3. Python Environments (Conda / venv) & Interpreters

**What it is:** An isolated space containing its own Python version and
installed packages, so different projects don't conflict with each
other. The bootcamp standardizes on **Conda** environments.

**How students set one up:**
```bash
conda create -n bootcamp-env python=3.11
conda activate bootcamp-env
python -m pip install ipykernel
python -m ipykernel install --user --name bootcamp-env --display-name "Python 3.11 (bootcamp-env)"
```

**Common beginner errors:**

- **`CondaToSNonInteractiveError`** — Conda requires accepting its
  Terms of Service before creating an environment. Run `conda tos
  accept` first, then retry.
- **Only "venv" shows as an option, not "Conda."** Usually means VSCode
  hasn't detected Conda yet — restart VSCode after installing/creating
  environments.
- **Environment created, but doesn't appear as a notebook kernel.**
  The environment exists, but hasn't been registered with Jupyter yet —
  run the `ipykernel install` command shown above.
- **Installed a package, but the script/notebook still says it's
  missing.** The package was installed into a *different* environment
  than the one actually running the code. Check which environment is
  active (`conda env list` shows the active one with a `*`) and which
  interpreter/kernel VSCode has selected — they need to match.
- **"Environments are on GitHub too, right?"** No — environments are
  always local only. Cloning a repo does not bring its environment
  along; it must be recreated on each machine separately.

- **Conda was installed, but `conda` command isn't recognized anywhere
  (terminal, VSCode) — and it's not a PATH-restart issue.** During
  Anaconda/Miniconda installation, there's a checkbox like "Add Conda to
  my PATH environment variable" — it's often **unchecked by default**
  (the installer itself recommends against it to avoid conflicts with
  other Python installs), so Conda gets installed but never becomes
  available as a plain `conda` command. Fixes, in order of ease:
  1. Use the dedicated **"Anaconda Prompt"** (Windows) or a fresh
     terminal after installation — this often has the right setup
     already, separate from the regular default terminal.
  2. Properly hook Conda into your shell: open Anaconda Prompt (or the
     terminal Conda was installed from) and run `conda init` (or
     `conda init powershell` / `conda init bash` depending on shell),
     then restart the terminal/VSCode. This is the recommended fix over
     manually editing PATH.
  3. As a last resort, manually add Conda's install folder (and its
     `Scripts`/`bin` subfolder) to the system PATH environment variable,
     then restart the terminal — more error-prone than `conda init`, so
     try that first.

- **A specific environment exists (confirmed via `conda env list`) but
  doesn't appear in VSCode's kernel/interpreter picker — how to add it
  manually.** Two different pickers can be involved, and the fix
  differs slightly:
  - **For `.py` files (interpreter picker):** click the interpreter
    name in the bottom status bar → **"Enter Interpreter Path"** →
    browse to that environment's actual Python executable (e.g.
    `~/anaconda3/envs/<env-name>/bin/python` on Mac/Linux, or
    `C:\Users\<name>\anaconda3\envs\<env-name>\python.exe` on Windows).
  - **For notebooks (Jupyter kernel picker):** the environment needs
    `ipykernel` installed and registered as a kernel first (see the
    `ipykernel install` command earlier in this section) — an
    environment without a registered kernel often won't show up here
    even if it's a valid Python environment.
  - If it still doesn't appear after that: VSCode caches the list of
    detected environments. Run **"Developer: Reload Window"** from the
    Command Palette (or fully restart VSCode) to force it to re-scan.

---

## 4. Codex (OpenAI's coding agent) in VSCode

**What it is:** An AI pair-programming extension that can read, edit,
and run code in your project directly from VSCode, given plain-English
instructions.

**How students set it up:**
1. Install the official extension ("Codex – OpenAI's coding agent" by
   OpenAI) from the VSCode Extensions panel
2. Sign in (ChatGPT Plus/Pro/Team account, or an API key depending on
   setup)
3. Open the Codex panel (icon in the activity bar, or Command Palette →
   "Codex: Open Codex Sidebar")

**Common beginner errors:**

- **Codex icon/panel missing after install.** Restart VSCode — same
  "newly installed software isn't detected until restart" pattern as
  Git and Conda.
- **Not sure whether to sign in with ChatGPT or an API key.** Signing
  in with a ChatGPT Plus/Pro account gives access to cloud features
  (e.g. delegating longer tasks); an API key works for local use but
  loses those cloud features. For most bootcamp lab work, either works
  — API key is simpler if you don't have a paid ChatGPT plan.
- **Repeatedly re-asks for approval on similar commands.** This is a
  known extension quirk — approving "every time" doesn't always stick
  across command variations. Not a setup mistake on your end.
- **Confusing Codex with GitHub Copilot.** They're related but
  different: Copilot is GitHub's own AI assistant (inline suggestions,
  chat); Codex is OpenAI's separate coding agent extension. Some setups
  route Codex through a Copilot subscription — if unsure which one a
  lab is asking about, check whether the instructions mention "Copilot"
  or "Codex" specifically, since setup steps differ.

---

## 5. Creating Environments via VSCode's GUI

**What it is:** Instead of typing `conda create`/`python -m venv` in a
terminal, VSCode has a built-in flow: Command Palette → **"Python:
Create Environment"** → pick an environment manager (venv, Conda,
Global, or browse to an interpreter) → VSCode creates it for you.

**Common beginner errors:**

- **Not sure which option to pick (venv vs Conda vs Global).** For this
  bootcamp, pick **Conda** — it's what the rest of the class workflow
  is built around. Picking venv isn't "wrong" on its own, but mixing
  venv-created environments with conda-created ones across different
  labs is exactly what causes "which environment am I even in"
  confusion later. Consistency matters more than which one is
  technically better.
- **Conda doesn't appear as an option in the list, only venv/Global.**
  The GUI can only offer Conda if it actually detects a Conda
  installation on the system. If Conda is installed but still not
  showing: restart VSCode first; if it still doesn't appear, Conda
  likely isn't correctly on the system PATH — closing and reopening a
  fresh terminal (or restarting the machine) after installing Conda
  usually resolves this.
- **Environment creation fails partway through / hangs.** If the "Use
  requirements.txt" checkbox was selected during creation and that file
  has a broken or unavailable package listed, the environment creation
  can fail or leave a half-installed environment behind. Fix: create
  the environment without the requirements file first (uncheck that
  option), confirm it works, then install packages separately.
- **Environment gets created, but VSCode doesn't automatically use it.**
  Creating an environment doesn't always auto-select it for the current
  notebook/file. After creation, explicitly select it: click the
  interpreter/kernel picker and choose the newly created environment by
  name.
- **Ends up with multiple environments and doesn't know which is
  "the real one."** This usually happens from running "Create
  Environment" more than once (e.g. once per lab folder, without
  realizing an environment already exists from before). Run
  `conda env list` in a terminal to see everything that actually
  exists, and delete unused/duplicate ones with
  `conda env remove -n <name>` to reduce confusion.
- **(Windows) venv creation succeeds, but activating it in the terminal
  fails with a message about running scripts being disabled.** This is
  a PowerShell execution policy restriction, unrelated to VSCode or the
  environment itself. Fix: open PowerShell as the current user and run
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try
  activating again. (This is specifically a venv/PowerShell issue —
  Conda environments aren't affected by this.)
- **GUI-created environment doesn't show up as a Jupyter kernel.** Same
  underlying cause as the terminal flow — the environment needs
  `ipykernel` installed and registered. VSCode's newer versions often
  prompt "Install ipykernel?" automatically the first time you try to
  use a fresh environment in a notebook — if that prompt was dismissed
  or missed, install it manually:
  `python -m pip install ipykernel` in that environment.

---

## 6. Diagnostic Habits Worth Building (applies to Conda or venv)

A few extra habits that catch a lot of "it should be working" confusion
early, before it turns into a long back-and-forth.

**Check which Python is actually being used, not just which one you
activated:**
```bash
where python      # Windows
which python       # Mac/Linux
```
This shows the actual path in use — if it doesn't point inside your
expected environment folder, that's the mismatch causing the error.

**Prefer `python -m pip install X` over plain `pip install X`.**
`python -m pip` guarantees the package installs into the Python
currently running, whereas a bare `pip` command can silently belong to
a different Python installation than expected — a common source of
"I installed it, but it still says missing."

**Before changing anything else, check these five things first:**
1. Am I in the correct project folder? (`pwd` / `dir`)
2. Is Python actually working? (`python --version`)
3. Is the right environment active? (look for `(env-name)` in the
   terminal prompt, or check `conda env list` for the active `*`)
4. Does VSCode's selected interpreter/kernel match that same
   environment?
5. Is the package actually installed in that specific environment?
   (`python -m pip list`)

Most environment-related errors are one of these five, not something
deeper or broken.

**How to ask for help effectively.** A vague "it doesn't work" message
takes much longer to resolve than a specific one. A good support
message includes: the exact error text, operating system, Python
version (`python --version`), current folder (`pwd`/`dir`), which
Python is active (`where`/`which python`), and the exact command that
was run. Example of a message that's fast to answer: *"On Windows,
created the env with `conda create -n bootcamp-env python=3.11`,
activated it, but running `python app.py` gives
`ModuleNotFoundError: No module named 'pandas'`."* — this alone often
tells a TA the likely cause before even replying.

---

## 7. More Environment & Terminal Troubleshooting

**`'pip' is not recognized as an internal or external command`.**
Confirm with `python -m pip --version` — if that works, `pip` on its
own just isn't on the PATH as a standalone command. Use
`python -m pip install package_name` going forward instead of bare
`pip install`.

**`python` command isn't recognized at all, in any form.** Try the
alternates in order: `python3 --version`, then (on Windows)
`py --version`. Whichever one actually returns a version number is the
command to use consistently from then on — including when creating
environments (e.g. `py -m venv .venv` instead of `python -m venv .venv`
if that's the one that worked).

**Terminal shows the environment activated (e.g. `(bootcamp-env)` in
the prompt), but clicking the ▶ Run button still uses a different
Python.** These are two separate things in VSCode: what's activated in
the terminal, and what interpreter VSCode has selected for the Run
button/editor. Activating in the terminal doesn't automatically change
the selected interpreter. Fix: `Python: Select Interpreter` and
explicitly choose the same environment that's activated in the
terminal, then run again.

**Environment folder was created but doesn't show up in the Explorer
panel.** Usually just needs a refresh — right-click in the Explorer
panel and refresh, or reload the window
(`Developer: Reload Window` from the Command Palette). If it's a
dotfolder like `.venv`, double-check VSCode's file explorer isn't
configured to hide dotfiles.

**Recovering a broken/corrupted environment — start fresh, safely.**
Sometimes the fastest fix really is deleting the environment and
recreating it, rather than debugging it further:
1. Close VSCode
2. Delete only the environment itself (the `.venv` folder, or remove
   the conda env with `conda env remove -n <env-name>`)
3. Reopen the project
4. Recreate the environment and reinstall dependencies
   ⚠️ **Important:** only delete the environment folder/env itself —
   never delete actual project files (`.py` files, `data/`,
   `requirements.txt`, notebooks) while doing this, since those aren't
   part of the environment and can't be regenerated by recreating it.

**VSCode is showing the wrong/incomplete set of files.** This usually
means only a single file was opened instead of the actual project
folder. Use **File → Open Folder** and select the real project root —
not just one `.py` file — so the rest of the project (data files,
`requirements.txt`, other scripts) is visible and VSCode's
environment/interpreter detection works correctly for the whole
project.

**`requirements.txt` install fails.** First upgrade pip itself:
`python -m pip install --upgrade pip`, then retry the install. If one
specific package is the actual failure point, read that package's
error message specifically rather than assuming the whole file is
broken — common causes are an unsupported Python version for that
package, a missing system-level dependency, a version conflict between
two listed packages, or a network/connectivity issue reaching the
package index.

**The golden rule:** when something breaks, don't immediately
reinstall Python, VSCode, or every package from scratch. Work through
the diagnostic checklist first (correct folder → Python working →
correct environment active → correct interpreter selected in VSCode →
package actually installed in that environment) — the overwhelming
majority of these errors trace back to one of those five things, not
something fundamentally broken.

---

## Quick diagnostic checklist (for any of the above)

When something in VSCode "isn't working" and the cause isn't obvious:
1. Which interpreter/kernel is actually selected? (bottom status bar,
   or top-right of a notebook)
2. Does `conda env list` show the environment you expect as active?
3. Has VSCode been restarted since the last install?
4. Run `git status` / `pwd` / `conda --version` to sanity-check the
   basics before assuming something is broken.
