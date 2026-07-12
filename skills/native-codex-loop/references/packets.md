# Task Packet Contracts

Use these fields verbatim as slots. Omit a slot only when it is explicitly `None`; never replace a missing fact with a guess.

## Delegation packet

- **Objective:** One bounded question whose answer changes a named parent decision.
- **Source of truth:** Exact disposable head-only clone, commit, files, symbols, logs, or official documentation to inspect. Never give the candidate/source worktree path.
- **Known context:** Facts already verified; exclude the parent's preferred answer.
- **Write boundary:** `Non-writing policy. Do not edit, commit, create worktrees, or invoke external models.`
- **Scope exclusions:** Adjacent topics and paths the child must not expand into.
- **Output contract:** Required fields, ordering, evidence citations, and maximum useful length.
- **Validation:** How the parent can check the returned claim.
- **Stop condition:** What uncertainty or access failure must be reported instead of guessed through.

Use one packet per independent question. If two packets can change the same file or depend on each other's answer, run them sequentially in the root.

## Review packet

- **Objective:** Find material correctness, security, regression, contract, or missing-test defects; do not implement.
- **Repository root:** Canonical source path for provenance. The runner substitutes its isolated clone; the reviewer uses only its current working directory.
- **Base commit:** The frozen task-baseline SHA from the start contract; never a later checkpoint.
- **Head commit:** Clean candidate SHA; require the reviewer to verify it before reviewing.
- **Task contract SHA256:** Hash of the immutable start contract. Inline that contract's
  exact objective, criteria, exclusions, baseline, Goal binding, and verification map.
  Delimit the exact text with `--- TASK CONTRACT START ---` and
  `--- TASK CONTRACT END ---`; pass the same file through `--task-contract`.
- **Task and acceptance criteria:** Inline the frozen text. A path plus hash is allowed only when that file exists in the reviewed commit/clone; clone-external sources must be inlined with their provenance hash.
- **Applicable instructions:** Exact `AGENTS.md` constraints that govern changed paths.
- **Changed paths:** Task-owned files only; identify any pre-existing dirty paths separately.
- **Verification receipt:** Commands, exit codes, failure counts, and known baseline failures. Never say merely “tests pass.”
- **Scope exclusions:** Generated, unrelated, or intentionally deferred areas.
- **Output contract:** Use the native review format. Each finding carries priority and identifies the violated criterion, evidence, Reproduction, and smallest safe next check. End with residual risk or an explicit no-actionable-finding result.

Do not include author identity, model identity, implementation reasoning, the parent's self-review, or a requested approval verdict. Keep the packet outside the candidate repository.

## Finding disposition

For every finding, the root records:

- **Finding ID and claim:** Assign stable IDs in returned order, such as `R1-F1`.
- **Reproduction:** Exact command, test, or code-path trace and observed result
- **Disposition:** `confirmed`, `rejected`, or `unresolved`
- **Evidence:** Output or file/symbol references supporting the disposition
- **Action:** Regression test and fix commit for confirmed findings; reason for no edit otherwise
- **Reverification:** Focused command and final required checks after the action

Never batch-discard findings as “reviewer noise.” Never edit merely to satisfy an unreproduced opinion.
