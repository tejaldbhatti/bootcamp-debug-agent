# Git & GitHub for Beginners: Setup & Common Errors

Written for students new to Git/GitHub. Covers the core mental model
and the errors beginners hit most often.

---

## 1. Git vs GitHub — the distinction that confuses almost everyone

**Git** is version control software that runs entirely on your own
computer — no internet connection needed. It tracks snapshots of your
project over time.

**GitHub** is a website/service built on top of Git — used for backing
up repos online, collaborating with others, and showcasing projects.

Mental model: **Git = your hard drive's history. GitHub = Dropbox for
code.** They're related but not the same thing, and "Git isn't
working" and "GitHub isn't working" are usually two different kinds of
problems.

---

## 2. The Core Workflow

```
git add      → stage changes (prepare what you want to save)
git commit   → take a snapshot of the project right now
git push     → upload your snapshots to GitHub
git pull     → download the latest snapshots from GitHub
```

**Why staging exists at all (a common beginner question):** this is
intentional design, not an extra annoying step. Git computes a
snapshot of what's staged, not what's sitting in your working
directory — this lets you deliberately group related changes into a
meaningful, well-named commit instead of committing "everything I
touched since the last save" automatically. Analogy: laying clothes on
the bed before deciding what actually goes in the suitcase.

**What a commit actually is:** Git doesn't save individual files — it
saves a snapshot of the entire project's state at that moment. That's
why `git log` shows a history of snapshots, and why you can return to
any earlier snapshot without losing anything from in between.

---

## 3. Common Setup & Recognition Errors

- **`git: command not found` / "Git is not recognized" even after
  installing Git.** In most cases Git isn't actually missing — the
  terminal/VSCode just needs to be **restarted** after installation to
  detect the newly available `git` command on the system PATH.
- **VSCode's Source Control panel shows nothing to stage/commit, even
  after saving changes.** A few possible causes, in order of
  likelihood: the folder opened in VSCode isn't actually the repo root
  (no `.git` folder inside it); the file is gitignored (check
  `.gitignore`); the file wasn't actually saved; the Source Control
  panel is just stale (click refresh). Fastest single diagnostic: open
  a terminal in that folder and run `git status` — it states plainly
  whether a file is tracked, ignored, or outside the repo entirely.

---

## 4. Cloning

- **`git clone` always creates a subfolder with the same name as the
  repo, instead of putting files directly where the command was run.**
  This is expected default behavior, not a bug. To clone directly into
  the current folder without the extra nested subfolder:
  `git clone <url> .` (note the space and dot at the end).

---

## 5. Pushing & the "buffer size" error

- **`fatal: the remote end hung up unexpectedly`, especially on a
  large push, even though the objects appear to be written
  successfully.** This is a real, confirmed cause: the connection is
  dropping mid-transfer because Git's default network buffer is too
  small for the transfer size, so GitHub never gets to confirm the push
  even though Git finished writing the objects locally. Before assuming
  something is broken (large files, wrong remote, bad branch), rule
  those out quickly:
  - Check for oversized files (GitHub has file-size limits)
  - Confirm the remote URL is correct: `git remote -v`
  - Confirm the commits actually exist locally: `git log --oneline`
  - Confirm the branch situation is as expected: `git branch -a`

  If all of those look normal and the error persists, increase Git's
  HTTP buffer size:
  ```bash
  git config --global http.postBuffer 524288000
  ```
  This raises the buffer from Git's default (~1MB) to 500MB, giving
  enough room to complete larger transfers without the connection
  dropping. Then push again. If a previous failed attempt left the
  remote in a partial/inconsistent state, a force push may be needed
  to resolve it: `git push origin main --force` (use `--force`
  carefully — it overwrites the remote branch's history with the local
  one).

---

## 6. Divergent Branches

- **`git pull`/sync fails with "Need to specify how to reconcile
  divergent branches."** This means the local branch and the remote
  branch each have commits the other doesn't have — usually because
  something was pushed to GitHub that was never pulled locally (or was
  forgotten). There's no way to just push past this; it has to be
  reconciled first. Options, roughly safest to most aggressive:
  1. Set a strategy and pull normally: `git config pull.rebase false`
     (merge) or `git config pull.rebase true` (rebase), then
     `git pull` and resolve any conflicts
  2. If confident the local version should win entirely: force local
     changes to overwrite the remote (e.g. `git push --force`) — only
     do this after confirming with any collaborators, since it
     discards whatever differs on the remote
  3. Manually reconcile: pull, inspect conflicts, resolve file by file

  Once branches have diverged, there's no way around dealing with
  it — one of the above has to happen before pushing works again.

---

## 7. VSCode's Git Panel Buttons

- **"Publish Branch" vs "Sync Changes" — what's the difference?**
  "Publish Branch" appears the first time a branch is pushed — it only
  exists locally until then. "Sync Changes" appears afterward; it
  uploads new local commits and downloads any new remote commits in one
  action. Simple rule: new branch → Publish Branch; branch already on
  GitHub → Sync Changes. A number next to "Sync Changes" (e.g. ↑2 ↓1)
  means 2 commits to push and 1 to pull.

---

## 8. Collaborators & Access

- **Adding a collaborator to a personal repository.** Repository page
  → Settings → Collaborators (under "Access" in the sidebar) → Add
  people → search by username → send invite. They need a GitHub
  account already, and access starts once they accept the emailed
  invite. GitHub Free allows unlimited collaborators on both public and
  private repos.

---

## Quick diagnostic checklist

1. Is this actually a Git problem (local) or a GitHub problem (remote/
   web)?
2. Has VSCode/terminal been restarted since Git was last
   installed/changed?
3. Does `git status` show what's expected (tracked vs ignored vs
   outside repo)?
4. Does `git remote -v` point to the correct repository?
5. For push failures: is it a size/buffer issue, or a divergent-branch
   issue? (`fatal: remote end hung up` vs `need to specify how to
   reconcile` are different problems with different fixes.)
