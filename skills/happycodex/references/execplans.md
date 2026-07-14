# Durable ExecPlan contract

Read this reference completely before editing any qualifying high-risk task.
An ExecPlan is human-readable Markdown and the durable completion contract. It is
not a Task State JSON document, scheduler database, or replacement for Codex.

## State layers

- The ExecPlan preserves the original outcome, system boundary, frozen obligations,
  acceptance, decisions, evidence, and recovery state across compaction.
- The Native Plan is the current execution cursor. It has no fixed step count and
  may be rewritten as the active phase changes.
- Git and tests are facts: commits, diffs, worktree state, and reproducible command
  results override stale prose.
- Goal never replaces the ExecPlan. Use Goal only after explicit user approval for
  a persistent task target; it does not widen authority or permissions.

## Bootstrap before research

1. Inspect repository instructions, `git status`, the full starting commit,
   worktrees, relevant tests, accepted baseline failures, task-owned changes, and
   preserved pre-existing state. Isolate the task when ownership is ambiguous.
2. Follow repository policy for plan placement. Otherwise create
   `docs/execplans/<task-slug>.md`. If policy forbids a tracked plan and provides no
   durable alternative, ask the user to authorize one instead of hiding state.
3. Create the skeleton before extended research. Include the original outcome
   verbatim, immutable baseline and worktree state, Root as the only writer, current
   phase, accepted baseline failures, pending gates, and the exact verification
   commands already run.
4. Commit the skeleton before dispatching long investigations. A test adjustment
   needed only to exclude repository plans from a published bundle may share that
   bootstrap commit; do not begin product implementation.

Keep the document self-contained. Maintain `Progress`, `Surprises & Discoveries`,
`Decision Log`, and `Outcomes & Retrospective` sections. Leave the retrospective
empty until the task actually completes.

## Discover and freeze the boundary

Root first inspects entry points, persisted routing, producers and consumers,
background workers, configuration and deployment, readiness, observability, and
recovery, migration and rollback, and legacy paths. Record a concrete obligation
for every surface that can make the requested outcome false.

Claims that are exclusive or unique, cover all or every surface, promise end-to-end
or production-ready behavior, or replace or retire an old path require one boundary
challenger working without Root's inventory. Before dispatch, persist its gate ID,
question, snapshot, status, and evidence required. Reconcile the union of the two
inventories. Root reproduces every material return in source, tests, logs, or a
primary artifact; no vote can close an obligation.

This is a real native child boundary, not role-play or an additional Root search.
Persist the native agent or task ID after dispatch and its terminal status plus
evidence after return. A Root re-read or second search does not count as a challenger.
If Root cannot verify both dispatch and return, including when agent tooling is
unavailable or the child is lost, the gate remains open and the exhaustive claim
cannot complete. Never infer tool activity from an assistant narrative alone.

Each obligation has exactly one state: `open`, `verified`, or `N/A`. `verified`
requires current reproducible evidence. `N/A` requires a concrete path, search,
command, or behavioral evidence proving the surface cannot affect the outcome.
Unresolved factual premises remain `open`.

Commit the reconciled matrix as the contract-freeze commit before implementation.
Record the freeze commit in the next evidence update so later review can compare
the frozen contract with the candidate.

## Control amendments

After freeze, Root may add obligations autonomously. Root must not delete, downgrade,
or newly mark an obligation `N/A` when that narrows the outcome without explicit user
authorization. In unattended execution, Root may only add or stop. Append every
amendment with rationale, evidence, and authorization. Affected evidence becomes
stale until rerun.

The original outcome is immutable. Clarifications may be appended, never silently
rewritten. A user-approved outcome change is recorded as an amendment and propagated
to acceptance, milestones, and the Native Plan.

## Implement vertical milestones

Define each independently verifiable vertical milestone by observable behavior,
affected obligations, commands, and expected evidence. Do not split solely by code
layer. For behavior changes:

1. Observe the smallest meaningful RED oracle. If RED is unsafe, impractical, or
   lower-signal, record exact before/after evidence and why it is stronger.
2. Reach GREEN with the smallest coherent change.
3. Run focused and cumulative checks, inspect call paths and the diff, and challenge
   defaults, boundaries, type semantics, malformed input, unrelated behavior, and
   established callers.
4. Update evidence and current phase, then create a semantic commit.

Do not run a costly full reviewer after every commit. The milestone gate proves the
slice; fresh review evaluates the frozen complete candidate.

## Recover after compaction

After resume or compaction, read the ExecPlan and inspect the Native Plan, Git, tests,
worktrees, live-agent state, and review receipt. At minimum inspect `git status`,
`git log`, the baseline-to-HEAD diff, current milestone tests, and pending gates.
Reconcile discrepancies in favor of source and reproducible evidence.

The conversation summary is not authoritative. A missing or inaccessible scout
remains pending; never infer its gate passed. Reissue only after confirming no live
child still owns the question. Stop for the user when ownership, original outcome,
or acceptance cannot be recovered confidently.

## Contract-bearing review projection

The full ExecPlan may contain writer context needed for recovery, but fresh review
receives only these contract-bearing sections after its independent inventory:
original outcome, baseline, frozen obligation matrix, acceptance oracles, authorized
amendments, current evidence, and Pending Gates. Pending Gates must expose pending
scouts and worktrees plus current review-receipt and evidence freshness, without
revealing historical verdicts. Exclude Decision Log, Surprises & Discoveries, writer
self-review, historical findings, Review State, and Outcomes & Retrospective.

The Review Receipt stores only objective scope, model/effort, command or task
identifier, result, and evidence freshness. Never store findings or repair narrative
there; a rereviewer must not inherit the previous review's answer.
