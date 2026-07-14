---
name: happycodex
description: Use for long, cross-cutting, or compaction-prone implementations that need one writer, durable evidence, conditional read-only scouts, and fresh native review.
---

# HappyCodex

The Root is the only writer. Plans, scouts, tests, Git, and review provide distinct
evidence; none substitutes for another.

## Establish durable state

1. Before editing, inspect repository status, relevant tests, and accepted baseline
   failures.
2. Resolve `git rev-parse --verify HEAD^{commit}` and record the full starting commit
   OID as the immutable task baseline before any task edit; never advance it. Record
   outcome, acceptance criteria, exclusions, verification, and stop conditions in
   the native plan, and keep that living evidence record current.
3. Use Goal only when the user explicitly requests Goal for this task.
4. Record task-owned changes and preserved pre-existing non-task changes' ownership
   and review exclusion. Isolate the task when ownership remains ambiguous.
5. When the user changes scope, update the working agreement and plan together.
   Mark affected criteria, evidence, and decisions stale until revalidated.

## Explore only for decision value

Delegate only independent unknowns tied to named decisions or verification gates.
Use orthogonal read-only scouts when distinct investigations could change distinct
decisions. Give each direct child `fork_turns="none"` and a complete task packet from
`references/task-packets.md` with a unique lens, evidence target, and exact inspected
snapshot. Parallelize only independent investigations. Scouts are direct and
read-only; the Root alone edits, commits, and integrates.

The Root reproduces every material scout claim in source or another primary artifact.
If the candidate changed, revalidate the evidence before uptake. Record uptake using
the reference checklist. Dispatch further scouts only for a newly exposed independent
boundary; otherwise update the plan and continue.

## Implement through evidence

1. For a behavior change, create the smallest meaningful RED oracle and observe the
   intended failure; when RED is lower-signal, record exact before/after evidence.
2. Make the smallest change that reaches GREEN.
3. Run focused tests, inspect affected call paths and the diff, then run required full
   checks.
4. Update the plan when evidence changes the next step; never weaken acceptance
   criteria. Checkpoint task-owned changes after coherent green slices when useful.

## Recover from native state

After resume or compaction, inspect any user-requested Goal, the native plan,
`git status`, `git log`, task diff, worktrees, live scouts, focused tests, full checks,
and review result. Reconcile conflicts in favor of source and reproducible evidence,
update the plan, and avoid repeating completed or still-live work. Ask the user if
the objective or acceptance criteria cannot be recovered confidently.

## Finish with native review

After implementation and checks, start a fresh Codex native review of the complete
task diff, not an in-thread self-review or scout. Resolve model and effort outside the
reviewer brief. Prefer `gpt-5.6-sol` at `max`:

```bash
codex review -c 'review_model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' - < "$review_brief"
```

Every review and re-review passes the resolved model and effort through both `-c`
overrides. If the preferred pair is unavailable, disclose that before using the
strongest authorized supported configuration at or below `max`, honoring any lower
user cap. Never silently downgrade. Record the requested configuration and any
invocation-reported model, effort, fallback, or reroute; do not claim values the
invocation did not expose. `ultra` requires explicit user authorization.

For every review invocation, write a factual brief to a temporary review brief file
outside the repository, pass it through stdin, remove it afterward, and never
shell-interpolate its contents. When supplying that prompt, do not combine it with
the `--base`, `--commit`, or `--uncommitted` selector flags.

The factual brief contains only the task, acceptance criteria, immutable baseline,
complete diff scope, verification evidence, accepted baseline failures, and recorded
review exclusions. Keep it neutral: omit the writer's implementation narrative,
self-review, rebuttal, preferred verdict, or defense.

Normalize task state before review. Prefer a task-only commit and scope the brief to
`git diff <task-baseline>..HEAD`. Otherwise include that range plus every task-owned
staged, unstaged, and untracked path. Carry recorded non-task exclusions into the
brief; commit or isolate when separation is ambiguous.

The Root must independently reproduce every actionable finding:

- Confirmed: add a RED regression oracle when practical, fix it, reach GREEN, and
  rerun focused tests and full checks.
- Rejected: record counter-evidence and do not edit merely to agree.
- Unresolved and material: stop and ask the user.

If confirmed fixes change the candidate, rerun checks and perform at most one fresh
review under the same complete-scope, immutable-baseline, factual-brief, and resolved
model/effort contract. Never review only the fix, and do not run a third review in
this loop. A literal zero-finding result is unnecessary; stop and report if any
confirmed or unresolved material finding remains.

## Completion gate

Claim completion only when every acceptance criterion maps to behavior or evidence,
focused tests and full checks are acceptable, the complete final diff passed the
review rule above, scouts and worktrees are accounted for, and `git status` contains
only intentional task state plus recorded preserved changes.
