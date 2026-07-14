---
name: happycodex
description: Use for long, cross-cutting, or compaction-prone implementations that need one writer, durable evidence, dependency-aware read-only scouts, conditional plan challenge, and fresh native review.
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

Before resolving an open design choice, inspect available evidence, compare only
materially different options, and ask only decision-changing questions the
environment cannot answer.

Classify each bounded investigation before dispatch:

- Keep it in the Root when it is localized, a direct command can answer it, or
  delegation and reproduction cost is not repaid by latency, context isolation, or
  reduced omission risk.
- Delegate one to three direct read-only scouts, limited by available slots, when each
  answers a different bounded question and contributes unique evidence tied to a named
  decision or verification gate. Use the fewest scouts that repay their overhead.
  Evidence may cross the same paths or symbols; orthogonality concerns the question and
  expected evidence, not disjoint files or symbols. Run scouts in parallel only when
  each packet can be fixed before any returns and each answer remains valid and useful
  without another return.
- Serialize when a result defines or narrows the next question, freezes a contract the
  next investigation consumes, determines whether that investigation is needed, or work
  requires shared mutable state. Reproduce and absorb the prerequisite first, then
  decide anew whether the next bounded scout still repays its overhead. A dependency
  does not itself justify another child.

Give every direct child `fork_turns="none"` and a complete task packet from
`references/task-packets.md` with a unique lens, evidence target, coordination boundary,
and exact inspected snapshot. Do not duplicate one question or vote on answers. Scouts
use only observational commands with no persistent repository or external side effects;
the Root alone owns writes, stateful commands, commits, and integration.

Account for all pre-edit scouts before the first task edit; while they run, the Root may
perform only read-only work. After editing begins, the Root may progress only work that
neither consumes a live scout's evidence nor changes its question or source of truth.
Wait at the first affected decision, edit, or gate. Wait only for live scouts that block
that gate; stop and account for stale, failed, or irrelevant work, then take it over in
the Root or remove the dependency instead of redispatching it to preserve a count.

The Root reproduces every material scout claim in source or another primary artifact and
records uptake using the reference checklist. If the candidate changed, revalidate the
evidence. Scout-run commands are exploratory evidence; required verification remains
Root-owned. After uptake, update the plan. Dispatch another scout only when a
prerequisite now unlocks a distinct bounded question or evidence exposes a new boundary;
never repeat an answered question or seek a different opinion.

After all pre-edit uptake, refine the plan and resolve known gaps first. Before the first
task edit, optionally use at most one fresh read-only plan challenger only when
independent criticism could change the plan and at least one trigger remains: a
high-impact or hard-to-reverse decision lacks sufficient evidence or mitigation, a
material evidence conflict remains unresolved, or an acceptance criterion lacks a
concrete verification path. Do not challenge a blocker whose next action is already
clear; gather evidence, ask the user, or stop. Give the challenger `fork_turns="none"`
and the plan challenge adaptation from the reference. Reproduce every factual premise
of a material challenge in primary evidence, then correct the plan or record why it
stands. A challenge verdict cannot clear a known blocker. When no useful trigger remains,
continue without a plan challenger. The challenger does not implement and does not
replace final diff review.

## Implement through evidence

1. For a behavior change, create the smallest meaningful RED oracle and observe the
   intended failure. If RED is unsafe, impractical, or lower-signal, record why and
   use exact before/after evidence.
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
