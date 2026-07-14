---
name: happycodex
description: Reliability workflow for long-running or high-risk implementations, including cross-cutting refactors, public-contract changes, migrations, persistence or concurrency changes, and compaction-prone work. Use when Codex must keep one writer, preserve acceptance criteria and baseline failures, gather bounded evidence, and finish with fresh native review; skip routine localized edits that do not carry those risks.
---

# HappyCodex

The Root is the only writer. Codex's native plan, agents, Goal, Git, tests,
compaction, and review remain the execution engine.

## Freeze a durable completion contract

For high-risk, cross-system, migration, persistence, concurrency, production-cutover,
or compaction-prone work, read `references/execplans.md` completely before editing.

1. Inspect `git status`, relevant tests, accepted baseline failures, task-owned
   work, and preserved pre-existing changes. Isolate ambiguous ownership.
2. Record the full starting commit as the immutable task baseline. Follow repository
   policy for the ExecPlan location; otherwise use `docs/execplans/<task-slug>.md`.
   Commit its minimal skeleton before extended research.
3. Keep the Native Plan as the current cursor without imposing a fixed step count.
   Use Goal only after explicit user approval; Goal never replaces the ExecPlan.
   For unattended or automatic continuation without Goal, ask once whether to
   enable it. Otherwise do not raise Goal; without explicit approval, continue with
   the native plan.
4. When scope changes, update the working agreement, acceptance criteria, ExecPlan,
   and Native Plan together. Treat affected evidence and decisions as stale.

## Freeze the system boundary

Inspect discoverable facts first. Trace entry points, persisted routing, producers
and consumers, background workers, configuration and deployment, readiness,
observability and recovery, migration and rollback, and legacy paths. Trace the
primary contract through validation, execution, serialization, and visible output.
Check adversarial compatibility: defaults, boundaries, type semantics, malformed
input, unrelated behavior, and established callers. Find residual consumers in
profiles, prompts, documentation, generated artifacts, and downstream code.

For claims that are exclusive or unique, cover all or every surface, promise
end-to-end or production-ready behavior, or make a replacement or retirement claim, require
one independent read-only boundary challenger without Root's inventory. Reconcile
the union of both inventories; the Root reproduces every material claim.

The Root decides whether to investigate directly or delegate other bounded questions.
Use native read-only scouts only for a named decision or verification gate. Do not
target an Agent count. Parallelize only questions that are independent. Give each child
`fork_turns="none"` and `references/task-packets.md`; forbid edits, implementation,
external models, and child delegation. Persist its gate before dispatch. Never
duplicate prompts or vote. Recheck evidence when the candidate changes.

## Implement through evidence

Use independently verifiable vertical milestones, not code-layer batches. For each,
observe the smallest meaningful RED oracle. If RED is unsafe, impractical, or
lower-signal, record why exact before/after evidence is higher-signal. Make the
smallest change that reaches GREEN;
run focused and cumulative checks; inspect affected
call paths and the diff; update the ExecPlan; then make a semantic commit. Never
weaken acceptance criteria.

## Recover from durable facts

After resume or compaction, reconcile the ExecPlan, Native Plan, Git, tests,
worktrees, live scouts, and review results. Inspect `git status`, `git log`, and the
task diff. Source and reproducible evidence outrank summaries; avoid repeating
completed or still-live work. Stop and ask if material state or ownership, outcome,
or acceptance criteria cannot be recovered confidently.

## Optional second review

Native review remains the default. Use Fable only when an explicit user instruction
or applicable `AGENTS.md` rule requests it; never infer permission from risk. When
selected, read `references/external-review.md` before freezing the candidate.

## Finish with fresh native review

After implementation and checks, start a fresh Codex native review of the complete
task diff. Prefer `gpt-5.6-sol` at `max`:

```bash
codex review -c 'review_model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' - < "$review_brief"
```

Use the strongest supported read-only authorization allowed by the user and environment.
`ultra` requires explicit user authorization. Never silently downgrade the model or
effort; disclose any unavailable setting or reroute.

Normalize task state before review. Prefer a task-only commit and inspect
`git diff <task-baseline>..HEAD`. If a task-only commit is not used, require that
range plus every task-owned staged, unstaged, and untracked change as one scope; list
task-owned untracked paths explicitly. Isolate the task if separation is unclear.

Build a neutral factual brief in a temporary file outside the repository. Include
only the task, acceptance criteria, immutable baseline, complete task diff,
verification evidence, accepted baseline failures, and explicit review exclusions.
Omit the writer's implementation narrative, self-review, prior argument, desired
verdict, and defense. Do not combine the stdin brief with review selector flags.

The Root must independently reproduce each actionable finding:

- Confirmed: add a RED regression oracle when practical, fix it, reach GREEN, and
  rerun focused tests and required full checks.
- Rejected: retain counter-evidence and do not edit merely to agree.
- Unresolved and material: stop and ask the user.

At most one fresh re-review is permitted. If confirmed fixes change the candidate,
the Root must run that one fresh re-review after checks. Give it the same immutable
baseline, complete current diff, current verification evidence, accepted baseline
failures, and exclusions. Omit all prior findings, dispositions, and repair narrative
so it judges independently. Never review only the fix. If that re-review reports a
confirmed or unresolved material defect, stop and report without changing the
candidate; any fix requires a newly authorized review cycle. A literal zero-finding
result is unnecessary.

## Completion gate

Claim completion only when every acceptance criterion maps to behavior or
reproducible evidence, focused tests and required full checks are acceptable, the
complete final diff satisfied the review rule, scouts and worktrees are accounted
for, and `git status` contains only intentional task state plus recorded preserved
changes.
