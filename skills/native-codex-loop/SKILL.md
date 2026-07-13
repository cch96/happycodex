---
name: native-codex-loop
description: Use when Codex must implement a long, multi-phase, cross-cutting, or compaction-prone change without losing requirements, while keeping one writer and using native planning, conditional scouts, tests, Git checkpoints, and final native review.
---

# Native Codex Loop

Use Codex's built-in controls as one convergent workflow. The Root is the only
writer. Plans, scouts, tests, Git, and review provide different kinds of evidence;
none substitutes for the others.

## Start with a working agreement

1. Read applicable `AGENTS.md`, the user request or task file, repository status,
   existing tests, and accepted baseline failures.
2. Put a concise working agreement in the native plan: outcome, acceptance criteria,
   exclusions, verification commands, and stop conditions. Record the starting revision
   once as the immutable task baseline before any task edit; never advance it for that
   task. Keep the plan as a living evidence record. Do not require an ExecPlan file.
3. Use Goal only when the user explicitly requests Goal. For a task likely to span
   compaction or several sessions, recommend Goal and obtain explicit confirmation
   before creating one. Never replace, complete, or update an unrelated active Goal.
4. Preserve existing user changes. Establish which diff belongs to this task before
   editing, record the ownership and review exclusion of preserved pre-existing non-task
   changes, and use an isolated branch or worktree when ambiguity would remain.
5. When the user changes scope, update the working agreement and plan together. Revise
   acceptance criteria, exclusions, and verification explicitly; mark affected prior
   evidence and decisions stale, then revalidate them before reuse.

## Route exploration only when it pays

Before the first edit, list the important unknowns and the named decisions or
verification gates each could change.

- For a localized, already-understood change, record `no delegation` and inspect it in
  the Root.
- When there are at least two independent unknowns affecting different decisions, or
  several independent seams that must be traced, use two or three orthogonal read-only
  scouts. Give each direct child `fork_turns="none"` and a complete task packet from
  `references/task-packets.md`.
- Give each scout a distinct lens and unique evidence requirement. Parallelize only
  investigations that do not depend on one another. Record the inspected revision in
  each packet and freeze it so scouts do not reason about a moving target.
- Do not delegate implementation, edits, commits, integration, or recursive delegation.
  Do not run same-prompt Best-of-N or persona-only brainstorming.

The Root reproduces every material scout claim in source, tests, logs, or a specified
primary source. Agent text alone is not evidence. If the revision has changed since the
scout ran, re-confirm its citations and claims against the current candidate before
uptake. Record a short uptake note in the plan: decision, reproduced evidence,
disposition, unique evidence, and resulting plan or gate change. Launch at most one
bounded challenge wave, and only when reproduced evidence reveals a new boundary or
contradiction. Otherwise continue in the Root.

## Implement through evidence

Work in the smallest coherent slices:

1. For a bug or behavior change, create the smallest meaningful RED oracle and observe
   it fail for the intended reason. If RED is impractical or lower-signal, record the
   exact before/after check instead.
2. Make the smallest Root-owned implementation that reaches GREEN.
3. Run focused tests, inspect the diff and affected call paths, then run broader or full
   checks at the repository's required cadence.
4. Update the plan when evidence changes the best next step. Never silently weaken an
   acceptance criterion or preserve a planned design contradicted by stronger evidence.
5. Create a Git checkpoint after a coherent green slice when it improves recovery or
   review. Never fold unrelated user changes into it.

## Recover from native state

After resume or compaction, reconstruct state from durable facts before acting:

- inspect the active Goal if one was requested;
- read the current native plan and working agreement;
- run `git status`, inspect `git log`, the task diff, and relevant worktrees;
- check live agents and the latest focused tests, full checks, and review result.

Reconcile disagreements in favor of source and reproducible evidence, then update the
plan. Do not repeat completed work or redispatch an investigation that is still live.
If the objective or acceptance criteria cannot be recovered confidently, ask the user.

## Finish with native review

After implementation and required checks, self-inspect the complete task diff and run a
fresh Codex native review. Use the strongest native review setting authorized by the
task; record any unavailable model or effort setting instead of claiming it was used.
Give the reviewer only a factual brief: task, acceptance criteria, the complete diff,
verification evidence, and accepted baseline failures. Do not include the writer's
implementation narrative, self-review, rebuttal, preferred verdict, or defense.

The supported CLI treats a custom prompt as mutually exclusive with review selector
flags. Do not combine them. Put the factual text in a temporary review brief file; do
not interpolate its contents into a shell command. Set `review_brief` to that file's
path and run `codex review - < "$review_brief"` so the bytes arrive through stdin.

Normalize task state before review and describe the selected scope in that brief:

- Preferred committed form: commit all task changes, verify the worktree is clean, and
  ask the reviewer to inspect `git diff <task-baseline>..HEAD`.
- Pure uncommitted form: use only when no task checkpoint commit exists and the complete
  task is represented by the staged, unstaged, and untracked changes.
- If task commits and current task changes coexist, either commit the remainder or make
  the brief require both `git diff <task-baseline>..HEAD` and the complete staged,
  unstaged, and untracked task changes as one review scope. List task-owned untracked
  paths explicitly and verify the result addresses both components.

- Selector-only `codex review --base <task-baseline>` or `codex review --uncommitted`
  is acceptable only when the same task, acceptance criteria, verification evidence,
  and baseline failures are already visible to the reviewer in repository inputs.

Do not replace this with an in-thread self-review or a scout. The Root must
independently reproduce every actionable finding:

- confirmed defect: add a RED regression oracle when practical, fix it, reach GREEN,
  and rerun focused tests plus full checks;
- rejected finding: record concise counter-evidence and do not edit for agreement;
- unresolved material finding: stop and ask the user rather than guessing.

If confirmed findings changed the candidate, run one fresh re-review of the complete
updated diff. Normalize task state again and use a new factual brief with
`codex review - < "$review_brief"`. Prefer to commit all task changes and inspect
`git diff <task-baseline>..HEAD` against the same task baseline. If commits remain
unavailable, include the full staged, unstaged, and untracked union described above; the
complete task must remain represented by current changes and any task checkpoints.
Never advance the baseline or select only the post-review fix. If that re-review still
has a confirmed or unresolved material finding, report the evidence and ask the user;
do not create an unbounded review loop.

## Completion gate

Claim completion only when:

- every acceptance criterion maps to implemented behavior or explicit evidence;
- required focused tests and full checks have acceptable results;
- the complete final diff received native review, with no unresolved material finding;
- all scout work and Git worktrees are accounted for;
- `git status` contains only intentional task state plus preserved pre-existing non-task
  changes whose ownership and review exclusion were recorded before editing;
- any requested Goal still matches this objective and is complete in fact.

Tests passing, a plan marked complete, or an agent saying “done” is never sufficient on
its own.
