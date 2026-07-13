# Task Packet Contracts

Machine-read files use the canonical code blocks below. Replace angle-bracket values,
but preserve labels, punctuation, field order, and one field per line. Other lists in
this reference describe required semantic slots. Never replace a missing fact with a
guess.

## Task Contract

Create this UTF-8 file outside the candidate repository with mode `0600`:

```text
# Task Contract

Objective: <measurable outcome>
Acceptance: <complete enumerated observable criteria>
Exclusions: <explicit non-goals>
Baseline: <full task-baseline SHA>
Repository/worktree: <canonical absolute path>
Goal thread ID: <exact thread ID or none>
Goal objective SHA256: <64 lowercase hex or none>
Verification: <criterion-to-command/evidence map and accepted baseline failures>
Stop conditions: <conditions that prohibit completion or require user authority>
```

Hash the exact UTF-8 Goal objective bytes. When Goal was not requested, both Goal fields
must be literal `none`; otherwise both must carry the real binding.

Never rewrite frozen content. For an authorized scope change, append a dated addendum
that states the user instruction and preserves the prior text, then record the new whole-file
SHA256 in native plan state.

### Authorized review escalation addendum

Use this append-only addendum only after the default series has consumed both attempts,
the final review supports material fixes, those findings are independently confirmed,
and the user later gives explicit approval. Preserve the original file bytes and append
exactly one blank line followed by this shape:

```text
## Addendum <YYYY-MM-DD> — Human-authorized post-review escalation

User authorization: <exact user instruction>
User authorization SHA256: <SHA256 of exact UTF-8 instruction bytes>
Prior Task Contract SHA256: <SHA256 before this addendum>
Prior series file: <canonical absolute default series.json>
Prior series SHA256: <SHA256 of exact series.json bytes>
Prior final receipt SHA256: <SHA256 of exact attempt-2/receipt.json bytes>
Prior reviewed head: <full attempt-2 head SHA>
Confirmed finding IDs: <comma-separated stable IDs in review order>
Authorization: <must explicitly permit one non-recursive post-fix review series, bind this addendum, the prior series, and its final receipt, and keep every series capped at two attempts>
Completion restriction: <actions forbidden until the escalated review passes>
```

The finding ID count must equal the parent review's finding count. Run
`review_runner.py` with `--escalate-from-series` naming that exact parent. One escalation
generation is the limit; an escalation `series.json` can never become another parent.

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

Start with this exact machine-read header and inline the exact canonical Task Contract:

```text
# Review packet

- Objective: <find material defects; do not implement>
- Repository root: <canonical source path for provenance>
- Base commit: `<full baseline SHA>`
- Head commit: `<full candidate SHA>`
- Task contract SHA256: `<whole-file SHA256>`
- Acceptance: <frozen acceptance criteria>
- Applicable instructions: <governing AGENTS.md constraints>
- Changed paths: <task-owned files>
- Verification receipt: <commands, exits, and baseline failures>
- Scope exclusions: <generated, unrelated, or deferred areas>
- Output contract: <native findings format and residual-risk requirement>

--- TASK CONTRACT START ---
<exact Task Contract bytes without its final newline>
--- TASK CONTRACT END ---
```

The runner substitutes its isolated clone for repository inspection. The base is always
the frozen task baseline, never a later checkpoint; the head is the clean candidate.
- **Task and acceptance criteria:** Inline the frozen text. A path plus hash is allowed only when that file exists in the reviewed commit/clone; clone-external sources must be inlined with their provenance hash.
- **Verification receipt:** Include commands, exit codes, failure counts, and known
  baseline failures. Never say merely “tests pass.”
- **Output contract:** Each finding carries priority and identifies the violated
  criterion, evidence, Reproduction, and smallest safe next check. End with residual
  risk or an explicit no-actionable-finding result.

Before launch, the runner rejects credential strings in checked-out files or any Git
blob reachable from `HEAD`. Returned finding titles must agree with numeric priority,
and every absolute location must name a changed regular file and overlap a new-side
zero-context diff hunk.

Do not include author identity, model identity, implementation reasoning, the parent's
self-review, or a requested approval verdict. Atomically create the packet outside the
candidate repository as a private regular file with mode `0600`; never reuse a symlink.

## Finding disposition

For every finding, the root records:

- **Finding ID and claim:** Assign stable IDs in returned order, such as `R1-F1`.
- **Reproduction:** Exact command, test, or code-path trace and observed result
- **Disposition:** `confirmed`, `rejected`, or `unresolved`
- **Evidence:** Output or file/symbol references supporting the disposition
- **Action:** Regression test and fix commit for confirmed findings; reason for no edit otherwise
- **Reverification:** Focused command and final required checks after the action

Never batch-discard findings as “reviewer noise.” Never edit merely to satisfy an unreproduced opinion.
