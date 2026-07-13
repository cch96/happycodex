# Native Codex Loop Post-Review Escalation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the five confirmed review defects and add a non-recursive, human-authorized post-fix native review series without changing the normal two-attempt cap.

**Architecture:** `review_runner.py` keeps the default identity unchanged and adds an explicit parent-series escalation path bound to the augmented Task Contract. Security checks run before model launch; verdict locations are validated against exact changed hunks. The root remains the only writer.

**Tech Stack:** Python standard library, `unittest`, Git plumbing, Codex CLI 0.144.1, Markdown Skill/plugin contracts.

---

### Task 1: Freeze escalation and security regressions

**Files:**
- Modify: `tests/test_review_runner.py`
- Modify: `tests/test_contracts.py`

- [ ] Add failing tests proving committed auth values are rejected before fake Codex launch, `ECONNREFUSED` and candidate `socket.py` cannot pass the probe, invalid/out-of-hunk locations fail, and `[P0]`/priority mismatches fail.
- [ ] Add failing tests for `--escalate-from-series`: valid exhausted default parent creates a distinct series; missing/modified addendum fields, parent hash, receipt hash, finding IDs, repo/base/head, non-exhausted parent, or recursive parent fail before state creation.
- [ ] Run the focused tests and require failures caused by missing production behavior, not fixture/setup errors.
- [ ] Commit only the RED tests with message `test: bind authorized review escalation`.

### Task 2: Exclude credentials before reviewer access

**Files:**
- Modify: `scripts/review_runner.py`
- Test: `tests/test_review_runner.py`

- [ ] Add a streaming byte matcher that carries `max_secret_length - 1` bytes across chunks.
- [ ] Scan every regular checked-out file outside `.git` and every blob returned by `git rev-list --objects HEAD` through a persistent `git cat-file --batch` process.
- [ ] Invoke the scan immediately after `_prepare_clone` and before writing reviewer config or launching any Codex command; raise `ReviewRunnerError` on the first match without persisting the secret.
- [ ] Run the committed-secret tests and the existing credential/redaction/head-only-bundle tests; require PASS.
- [ ] Commit with message `fix: reject credentials in review object set`.

### Task 3: Make network proof import-safe and errno-exact

**Files:**
- Modify: `scripts/review_runner.py`
- Test: `tests/test_review_runner.py`

- [ ] Generate `python3 -I -S -c` and exit 0 only for raised or returned `errno.EPERM`/`errno.EACCES`; accessible network exits 1 and all other failures exit 2/nonzero.
- [ ] Run focused network tests, then a standalone real `codex sandbox -P native-review` probe against a live localhost listener; require exit 0 only inside the restricted profile.
- [ ] Commit with message `fix: isolate network preflight imports`.

### Task 4: Bind findings to priority and changed hunks

**Files:**
- Modify: `scripts/review_runner.py`
- Test: `tests/test_review_runner.py`

- [ ] Parse each changed path from `git diff --name-only -z base..head`, then parse its `git diff --unified=0` new-side hunk ranges.
- [ ] Require location path containment under clone, regular-file existence, membership in changed paths, positive in-file lines, hunk overlap, and exact title/numeric priority equality.
- [ ] Run incomplete/valid/outside/unchanged/out-of-hunk/priority-mismatch finding tests; require PASS.
- [ ] Commit with message `fix: bind review findings to changed code`.

### Task 5: Implement one-generation authorized escalation

**Files:**
- Modify: `scripts/review_runner.py`
- Test: `tests/test_review_runner.py`

- [ ] Add optional `escalate_from_series: Path | None` through CLI, `run_series_review`, and receipt construction.
- [ ] Parse the exact canonical addendum fields and validate original Contract hash, parent canonical path/hash, final receipt hash/head, five finding IDs, and authorization text.
- [ ] Derive `review-series/escalations/<sha256>` from repo/base/current-contract/parent-series/parent-receipt hashes; store parent provenance in state and receipts; reject any parent already containing escalation provenance.
- [ ] Keep `MAX_REVIEW_ATTEMPTS = 2` for both default and escalation series.
- [ ] Run all escalation tests plus existing lock/symlink/hardlink/cap tests; require PASS.
- [ ] Commit with message `feat: add authorized post-review escalation`.

### Task 6: Update the reusable Skill contract

**Files:**
- Modify: `skills/native-codex-loop/SKILL.md`
- Modify: `skills/native-codex-loop/references/packets.md`
- Modify: `README.md`
- Modify: `tests/test_contracts.py`

- [ ] Add pressure/contract tests requiring stop-after-two by default, explicit user approval, append-only addendum, exact parent-series binding, one escalation generation, and no recursive/global bypass.
- [ ] Update Skill/reference/README minimally to teach those mechanics and credential/hunk gates without current-thread-specific paths or hashes.
- [ ] Run contract tests, Skill quick validator, and plugin validator; require PASS.
- [ ] Commit with message `docs: define authorized review escalation`.

### Task 7: Freeze and verify the post-fix candidate

**Files:** all task-owned changed files above.

- [ ] Run `python3 -m unittest discover -s tests -v`; expect exit 0 and the new total test count.
- [ ] Run `ruff check scripts tests`, `python3 -m compileall -q scripts tests`, `git diff --check`, plugin `validate_plugin.py .`, and Skill `quick_validate.py`; expect all PASS.
- [ ] Confirm `git status --porcelain=v1` is empty and record the exact head and augmented Contract hash.
- [ ] Build a private review packet with the exact augmented Contract and invoke the runner with `--escalate-from-series` pointing to the frozen default `series.json`.
- [ ] Require the new series final attempt/receipt to succeed on the exact head with parent-series and parent-receipt hashes matching the addendum. Do not create another escalation generation.

### Task 8: Run the new Fable task

**Files:** external private packets/receipts only.

- [ ] Create a new stateless task directory; never reuse the failed packet/session.
- [ ] Fable round 1 reviews `f9059b8..9d935f1` (1904 lines). If it returns findings already covered by later commits, record their IDs and dispositions.
- [ ] Fable round 2 reviews `9d935f1..<final-head>` with the round-1 finding IDs; keep under 2000 lines and require a valid receipt.
- [ ] Independently reproduce every finding. If round 2 requires another material edit, stop rather than invoke a third Fable process.

### Task 9: Install and replay Storyboard

**Files:** validated source mirror, personal marketplace state, isolated preflight outputs, Storyboard experiment outputs.

- [ ] Validate source, use the plugin-creator cachebuster helper, sync the immutable reviewed source to `~/plugins/native-codex-loop`, and reinstall from the confirmed personal marketplace; never hand-edit marketplace JSON.
- [ ] In isolated HOME/CODEX_HOME, prove Skill discovery, absence of custom enhancements, real review receipt, cleanup, and final-SHA behavior.
- [ ] Run three fresh pressure cases and require three of three current-head review receipts.
- [ ] Run the matched historical Storyboard replay with oracle data offline/inaccessible until freeze; then run full pytest, Ruff, mypy, seven original hidden tests, and two supplemental seam tests.
- [ ] Report review yield, confirmed fixes, no-regression result, token/time, repeated work, and limitations; complete Goal only if every contract gate passes.
