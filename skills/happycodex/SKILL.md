---
name: happycodex
description: Use for high-risk, cross-system, destructive, public-contract, migration, persistence, concurrency, exhaustive, long-running, or compaction-prone Codex work, and for architecture or design recommendations that depend on current multi-artifact implementation facts, when the work needs a static change boundary, isolated context, consumer-native candidate identity, and truthful closure.
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

Record the request and Outcome, workspace/project or task-owned authorization
boundary, planned primary surfaces, preservation and exclusions, supported
workflows, baseline and allowed breaks, consumer and complete input-closure
rule, incidental-footprint rule, checks, Done, stops, and recovery.
For each external effect record its exact target, identity source, cap,
observation predicate, and allowed recovery cap or none. Keep the plan static:
do not store live phases, realized file inventories, digests, agent history, or
review history. Reconstruct those facts from the workspace and tools.

Do not use an exact mutable-path or realized-resource inventory as the authorization boundary. It coordinates primary ownership and later closure; it does not require per-path reauthorization
for reversible Outcome-required work inside the unchanged selected workspace/project or task-owned
boundary. Before freeze, task-owned additions or relocations may continue when the consumer,
Outcome, preservation, exclusions, and primary effects remain unchanged. This does not imply
deletion of old or shared surfaces. Advisory evidence adds no authority; it may refine planned
primary surfaces inside the unchanged authorization boundary. A compatibility break remains a
proposal until the request explicitly authorizes the exact incompatibility and any material
consumer, data, or cutover effect. Recommend it only for a material safety or correctness need or
a net reduction in steady-state semantic complexity relative to cutover risk; ambiguous no-compatibility wording authorizes comparison only.

Treat bounded additive, reconstructible, non-authoritative cache, temporary,
log, or compiled output as incidental only when it is not a consumer input and
touches no secrets, credentials, trust, shared/system configuration, another
owner, or remote or paid resource; continue and account for it at closure.
Stop for shared-cache deletion or overwrite, system/user/shared installation,
any excluded class, omitted consumer input, or uncertain classification.

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

For a recommendation, assessment, or design verdict that depends on current
facts not yet verified in-session, use an evidence-first scout when those facts
span more than one artifact or require search to enumerate. Before forming the
recommendation, the Primary writes a small bounded set of open factual questions
that are answerable by observation and sends them to one native read-only agent.
The scout returns facts only, with citations, searched scope, and unknowns; it
does not recommend. Judgment and the final recommendation stay with the Primary.
Skip the scout when one or two bounded direct lookups suffice or the relevant
facts are already verified in the current session.

Only once a stable question requires a supporting body to be searched,
summarized, compared, or filtered, send that body to one native read-only agent
before the Primary ingests it. Require a concise answer with citations, searched
scope, and unknowns. Wait before deciding; the convergence rule below governs
the focused verification. Context offload requires neither parallel lanes nor
low remaining context. Add agents only for independent bodies when concurrency
materially helps. Keep every challenge or review within its assigned question.
When a challenge or review uses an external model or tool, the Primary invokes
that tool directly and observes its result directly. Do not create a native
agent to call, relay, or wrap the external invocation.

As soon as mutable ownership and Done evidence are stable, send substantial
implementation to one native worker before editing. Give exact ownership and
require changed paths, verification, and risks in return. Keep a small coherent
correction direct. Allow only one writer per overlapping mutable path or
resource. Apply one writer across overlapping semantic mutable contracts and
effect resources, including cross-repository surfaces even when files differ.
Prefer a typed reader when available; do not automatically rewrite roles.

If native agents are unavailable or fail, or a body cannot be bounded without
transferring unresolved judgment, state the fallback before the Primary
consumes or edits it. Never replay the work silently.

After compaction, interruption, or lost writer continuity, first confirm the
old writer cannot resume. Reread the entire ExecPlan, inspect Git, index,
candidate, and effect state, and rerun the checks needed to rederive current
facts. Summaries are hints, not authority. Stop on identity, scope, index,
effect, or trust-boundary drift.

## Converge on evidence

When Outcome, change boundary, Done, mutable ownership, and current blockers are stable, Root gives the fixed Executor an explicit stability handoff.
State the Outcome, change boundary, Done, writer, current blockers, authorized increments, and exclusions.
The handoff gives the Executor the write lock over the candidate. After it, Root must not send another candidate revision brief unless
that brief cites new decision-changing evidence or a concrete current blocker. Root write count alone is not a closure proxy;
a restatement, optional check, or concern without an admitted failure path does not reopen the candidate.

A new concern enters current obligations only through a concrete failure path against the Outcome, preservation, a required workflow, or candidate-new material safety or correctness.
A reasoned path is sufficient at plan stage; during implementation, reproduce it where feasible. This gate never dismisses a current blocker or required unknown.
Before another advisory pass, Root states a bounded reason that could change the current verdict: new
decision-changing evidence, a decision-relevant question, a concrete failure hypothesis, or a new user-requested review bounded to the current
artifact and Outcome. Ask the user to select a scope only when materially different scopes remain.
A standing instruction alone does not renew passes. After the declared scope is complete, or no
further bounded pass can resolve a required unknown, stop initiating advisory review and report
findings, searched scope, and unknowns. This stop is not `GO`.

After delegated evidence, Root may perform at most one focused verification. Before it, state which current verdict the check could flip;
then deliver the verdict and required unknowns. For a user status or conclusion request, give the current verdict and required unknowns first, before proposing optional checks.

## Freeze what the consumer receives

Freeze makes Root read-only over the candidate. Any candidate change returns
ownership to the fixed Executor; rerun required checks and refreeze before using
the existing review semantics.

After writes and checks, derive the exact complete consumer input closure, including
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

Convergence review is advisory and may be reused, interrupted, messaged, or
followed up without a round cap. It never supplies terminal authority. Admit
terminal evidence only from one fresh no-history Exact-final reviewer over one
immutable consumer-native candidate identity. Require strict `GO` or `NOT_YET`
and echo that identity. Any candidate-byte change invalidates the verdict. A
tracked immutable plan may be reviewed. A plan `GO` validates only that plan;
implementation needs its own frozen candidate review. A composite candidate
requires one immutable envelope binding every component identity.

Follow-up or message to an Exact-final handle is allowed but makes any later
output convergence-only; terminal admission still requires a fresh reviewer.
Interrupting a reviewer is allowed. Optional native hooks may warn about these
boundaries or deny only unsupported explicit custom-agent/full-history spawns.
They are optional, trust-dependent, and bypassable guardrails, not complete
enforcement; keep Skill guidance authoritative when hooks are absent or skipped.

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
