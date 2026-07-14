---
name: happycodex
description: Use for long, cross-cutting, public-contract, or compaction-prone implementations that need one writer, durable acceptance evidence, optional bounded read-only investigation, and fresh native review.
---

# HappyCodex

The Root is the only writer. Codex's native plan, agents, Goal, Git, tests,
compaction, and review remain the execution engine.

## Establish durable state

1. Before editing, inspect `git status`, relevant tests, and accepted baseline
   failures. Record task-owned work and preserved pre-existing changes; isolate
   the task if ownership is ambiguous.
2. Record the full starting commit as the immutable task baseline. In the native
   plan, capture the outcome, acceptance criteria, exclusions, verification, and
   stop conditions, then update decisions and evidence as work changes them.
3. Use Goal only when the user explicitly requests Goal for this task.
4. When scope changes, update the working agreement, acceptance criteria, and
   plan together. Treat affected evidence and decisions as stale until checked.

## Cover risk before editing

Inspect discoverable facts first. Compare only materially different options, and
ask only decision-changing questions the environment cannot answer.

For a cross-seam or public-contract change, cover every relevant surface:

- Trace the primary contract from input or authoring through validation,
  execution, serialization, and user-visible output.
- Check adversarial compatibility: defaults, boundaries, type semantics, malformed
  input, unrelated behavior, and established callers.
- Find residual consumers: configuration, profiles, prompts, documentation,
  generated artifacts, and downstream code that may preserve old assumptions.

The Root decides whether to investigate directly or delegate. Use native read-only
scouts only when a bounded investigation could change a named decision or
verification gate and delegation repays its coordination and reproduction cost.
Do not target an Agent count. Parallelize only questions that are independent;
serialize when one answer defines, narrows, or determines the need for the next.

Give each child `fork_turns="none"` and the compact packet in
`references/task-packets.md`. Ask one distinct question, forbid edits and child
delegation, and identify the exact inspected snapshot. Do not duplicate a prompt,
vote on answers, or delegate implementation. The Root reproduces every material
claim in source, tests, or another primary artifact and rechecks it if the candidate
has changed. If an unresolved factual premise can still change the plan, investigate
it directly or with one bounded child before editing.

## Implement through evidence

1. For a behavior change, create the smallest meaningful RED oracle and observe
   the intended failure. If RED is unsafe, impractical, or lower-signal, record why
   and use exact reproducible before-and-after evidence.
2. Make the smallest change that reaches GREEN.
3. Run focused tests, inspect affected call paths and the diff, then run required
   full checks.
4. Update the plan when evidence changes the next step; never weaken acceptance
   criteria. Checkpoint coherent green slices when useful.

## Recover from native state

After resume or compaction, inspect any user-requested Goal, the native plan,
`git status`, `git log`, the task diff, worktrees, live scouts, focused tests, full
checks, and review results. Reconcile discrepancies in favor of source and
reproducible evidence, update the plan, and avoid repeating completed or still-live
work. Ask the user if material state or ownership, the outcome, or acceptance
criteria cannot be recovered confidently.

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
