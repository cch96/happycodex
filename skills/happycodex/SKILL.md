---
name: happycodex
description: Use for high-risk, cross-system, destructive, public-contract, migration, persistence, concurrency, exhaustive, long-running, or compaction-prone Codex work that needs a static change boundary, isolated context, consumer-native candidate identity, and truthful closure.
---

# HappyCodex

Use HappyCodex as portable guidance around native Codex plans, agents, Git,
tests, and diffs. It is not a controller, ledger, scheduler, authorization
system, or retry engine.

## Ground the work

Keep bounded, reversible local work on the native Plan. Create one repository
ExecPlan before substantial exploration or dispatch when work is long-running
or compaction-prone, and before the first risky write otherwise. Copy
`references/execplan.md` to the repository policy path or
`docs/execplans/<task-slug>.md`.

Record the request and Outcome, workspace, exact mutable paths or resources,
preservation and exclusions, supported workflows, baseline and allowed breaks,
consumer and complete input-closure rule, checks, Done, stops, and recovery.
For each external effect record its exact target, identity source, cap,
observation predicate, and allowed recovery cap or none. Keep the plan static:
do not store live phases, realized file inventories, digests, agent history, or
review history. Reconstruct those facts from the workspace and tools.

Treat the user, workspace, maintainer, and selected configuration as
non-adversarial but fallible unless evidence says otherwise. Verify relevant
identity and state. An available capability never expands the requested work.

## Work with native agents

Use context offload independently of parallelism. Delegate one bounded native
read-only agent for one noisy search, log, or test lane when that protects the
primary context. Use a small host-selected set only for genuinely independent
lanes whose parallel execution materially helps. Keep delegation bounded and
native agent ownership explicit. Request concise evidence and directly recheck
load-bearing facts.

For substantial implementation, prefer one native worker so the Primary can
retain the durable reasoning context. The Primary may write bounded changes
directly. At any moment allow only one writer for overlapping mutable paths or
resources; non-overlapping writers may proceed when coordination is explicit.
Do not mutate an owned overlapping resource while its worker is active.

After compaction, interruption, or lost writer continuity, first confirm the
old writer cannot resume. Reread the entire ExecPlan, inspect Git, index,
candidate, and effect state, and rerun the checks needed to rederive current
facts. Summaries are hints, not authority. Stop on identity, scope, index,
effect, or trust-boundary drift.

## Freeze what the consumer receives

After writes and checks, derive the complete consumer input closure, including
generated and transitive inputs, modes, deletions, and byte identities. Verify
that every mutable input is inside the change boundary. Freeze a readable,
immutable representation using the consumer's native identity: for example a
Git tree or commit, deterministic package/archive, image or revision digest, or
content-addressed snapshot. A digest of a mutable worktree is not a frozen
candidate.

Never put secrets or raw external events in product bytes. If the required
immutable representation cannot be created within authority, report the
candidate as modified but not frozen.

## Review once when risk requires it

Do not require review for ordinary reversible local work or merely because a
continuity break occurred. Use at most one read-only pre-challenge before
freeze when an architectural decision is hard to reverse. For a public,
external, irreversible, or otherwise high-risk frozen candidate, run one fresh,
no-history, blocker-only terminal review against readable immutable baseline
and candidate inputs.

Admit only a reproduced frozen-obligation failure, preservation failure, or
reachable candidate-new material safety or correctness regression. Suppress
style, naming, optimization, alternative designs, speculative hardening,
unfrozen tests, and unrelated pre-existing issues. The terminal decision is
`GO` or `NOT_YET`; incomplete coverage or a required unknown is adverse.
Reviewers cannot change the Outcome or propose a repair. A later user-approved
repair creates a new candidate and review identity, never an automatic loop.

## Act once and close truthfully

Before an external effect, recheck its exact target, identity, cap, and
observation predicate. Make one mutation attempt, then perform bounded read-only
observation and classify it as `landed`, `not_landed`, or `unknown`. Retry only
when authentic evidence proves a pre-effect no-effect terminal and the static
plan already grants recovery. Partial, ambiguous, or unknown effects stop all
mutation and return to the user.

Close as achieved, not achieved, or unknown only after recomputing candidate
and effect identity, verifying Outcome and preservation, running required real
paths, and accounting for staged, unstaged, untracked, external, skipped, and
unverified state. Never infer installation, publication, activation, or other
external success from the absence of an error.
