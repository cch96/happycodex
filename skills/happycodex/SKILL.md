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

Create a native Goal only on explicit user request; never create, recreate, or
widen it to recover missing state. Preserve its one Outcome; the Goal waives no
scope/change boundary, effect grant, review, approval, or Done. Define the
candidate surface by paths and generated inputs, not current bytes or commit
identity. Continue autonomously only while the same Goal, Outcome, change
boundary, candidate surface, and effect target, identity, and cap govern with no
pending user decision. If unchanged native Goal identity is unconfirmed, pause
mutation for the user; a reply authorizes only the decision it answers. Done
governs completion.

## Route work by boundary

Keep the request, applicable instructions, Outcome, change boundary, unresolved
decisions, and judgment core with the Primary. Read the exact judgment artifact
whose semantics are evaluated and keep one focused verification direct. Do not
ingest every supporting artifact. Do only the smallest discovery needed to form
another bounded question.

Only once a stable question requires a supporting body to be searched,
summarized, compared, or filtered, send that body to one native read-only agent
before the Primary ingests it. Require a concise answer with citations, searched
scope, and unknowns. Wait before deciding, then spot-check decision-changing
citations without replaying the body. Context offload requires neither parallel
lanes nor low remaining context. Add agents only for independent bodies when
concurrency materially helps. Keep every challenge or review within its assigned
question. When a challenge or review uses an external model or tool, the Primary
invokes that tool directly and observes its result directly. Do not create a
native agent to call, relay, or wrap the external invocation.

As soon as mutable ownership and Done evidence are stable, send substantial
implementation to one native worker before editing. Give exact ownership and
require changed paths, verification, and risks in return. Keep a small coherent
correction direct. Allow only one writer per overlapping mutable path or
resource.

If native agents are unavailable or fail, or a body cannot be bounded without
transferring unresolved judgment, state the fallback before the Primary
consumes or edits it. Never replay the work silently.

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

Before deleting a branch, worktree, or other recovery surface, prove required
candidate, cutover, effect, and rollback evidence remains durably reachable;
otherwise stop.

## Review once when risk requires it

Do not require review for ordinary reversible local work or merely because a
continuity break occurred. Use at most one read-only pre-challenge before
freeze when an architectural decision is hard to reverse. For a public,
external, irreversible, or otherwise high-risk frozen candidate, run one fresh
native read-only, no-history, blocker-only terminal review against readable
immutable baseline and candidate inputs. Keep that native exact-final review
separate from any optional external challenge or review.

Admit only a reproduced frozen-obligation failure, preservation failure, or
reachable candidate-new material safety or correctness regression. Suppress
style, naming, optimization, alternative designs, speculative hardening,
unfrozen tests, and unrelated pre-existing issues. The terminal decision is
`GO` or `NOT_YET`; incomplete coverage or a required unknown is adverse.
`GO` validates only the reviewed candidate and adds no authority; reviewers
cannot change the Outcome or propose repairs. After `NOT_YET`, make one already
pre-authorized in-boundary repair only while repair and replacement-review
budget remains; otherwise pause. That repair creates a new candidate and review
identity. After that replacement review, any adverse result returns to the user;
never continue automatically.

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
