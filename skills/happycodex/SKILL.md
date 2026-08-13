---
name: happycodex
description: Use for high-risk, cross-system, destructive, public-contract, migration, persistence, concurrency, exhaustive, long-running, or compaction-prone Codex work, and for architecture or design recommendations that depend on current multi-artifact implementation facts, when the work needs a static change boundary, isolated context, consumer-native candidate identity, and truthful closure.
---

# HappyCodex

HappyCodex is portable guidance around native Codex plans, agents, Git, tests,
and diffs. It does not create authority or operate a second control plane.

## Ground the work

Use the native Plan for bounded reversible work. Before substantial exploration
or dispatch on long or compaction-prone work, and before the first risky write
otherwise, copy `references/execplan.md` to the repository policy path or
`docs/execplans/<task-slug>.md` and fill its task facts. Keep it static; derive
live paths, identities, agent history, and results from the workspace and tools.

The authorization boundary is the selected workspace/project or task-owned
domain, not an exact realized-path inventory. Planned paths coordinate
ownership and exact paths close the consumer input at freeze. Reversible,
Outcome-required task-owned additions or relocations may continue before freeze
while consumer, Outcome, preservation, exclusions, and primary effects stay
unchanged; this does not authorize deleting old or shared surfaces. Advisory or
available capability never expands authority.

A compatibility break requires explicit authorization of the exact
incompatibility and material consumer, data, or cutover effect; ambiguous
no-compatibility wording authorizes comparison only. Recommend a break only for
a material safety/correctness need or lower steady-state semantic complexity
relative to cutover risk.

Treat bounded additive, reconstructible, non-authoritative cache, temporary,
log, or compiled output as incidental only when it is not a consumer input and
touches no secrets, credentials, trust, shared/system configuration, another
owner, or remote/paid resource. Account for it at closure. Stop for deletion or
overwrite of shared cache, system/user/shared installation, excluded or omitted
consumer input, or uncertain classification.

## Route once by boundary

Keep the request, instructions, Outcome, unresolved decisions, and primary
judgment direct. Use the smallest of these routes:

- For a recommendation whose unverified current facts span artifacts or require
  enumeration, send bounded observable questions to one native read-only scout
  before deciding. It returns facts, citations, searched scope, and unknowns,
  never the recommendation. Keep one or two bounded lookups direct.
- For a stable question requiring a supporting body to be searched, summarized,
  compared, or filtered, send that body to one native read-only agent before
  primary ingestion. Add agents only for independent bodies when concurrency
  materially helps.
- Once ownership and Done are stable, send substantial implementation to one
  native worker before editing; keep a small coherent correction direct. Allow
  one writer per overlapping path, semantic mutable contract, or effect
  resource, including cross-repository overlap.
- Invoke an external model or tool directly for its assigned question; do not
  delegate the invocation or treat it as terminal review.

When native spawn exposes `fork_turns`, pair any explicit `agent_type`, `model`, or
`reasoning_effort` with a self-contained packet and `fork_turns="none"` by default.
Use the smallest positive fork only for a recent raw artifact that cannot be referenced
or restated faithfully; reserve omitted/`"all"` for intentional same-agent inheritance.

When host guidance prohibits only *proactive* delegation but permits delegation
requested by the user or an applicable Skill, the scout or worker required
above is this Skill's explicit request: attempt the exposed native spawn. This
bridge never overrides an actual host denial. With an explicit host denial, do
not spawn; state the denial and proceed directly only if safe. Direct fallback
is also allowed after a spawn error, a concrete missing capability/tool, or when
the supporting body cannot be bounded without transferring primary judgment.
Record that evidence before direct work. Do not claim delegation was forbidden
without an attempt when capability is exposed and only proactive delegation is
restricted.

After continuity loss, confirm the old writer cannot resume, reread the whole
ExecPlan, and reconstruct Git, index, candidate, effect, and trust-boundary
state. Stop on drift; summaries are hints, not authority.

## Converge on evidence

When Outcome, boundary, Done, ownership, and blockers are stable, hand the fixed
Executor the write lock with those facts, authorized increments, and exclusions.
Root stays read-only and revises the candidate only through that Executor after
new decision-changing evidence or a concrete current blocker.

A concern becomes an obligation only through a concrete failure path against
Outcome, preservation, a required workflow, or candidate-new material safety or
correctness; reproduce it during implementation where feasible. This never
dismisses an existing blocker or required unknown. Before an
advisory pass, state the bounded reason that could change the verdict. A standing
instruction does not renew passes. When the declared pass completes without
renewal, stop reviewing and report its findings, searched scope, and unknowns;
this stop is not `GO`. After delegated evidence, Root may do one focused check
whose possible verdict change is stated in advance, then report the verdict and
required unknowns.

## Freeze one candidate

Derive every direct, generated, and transitive consumer input, including modes,
deletions, and byte identities. Exclude secrets and raw external events. Verify
all mutable inputs remain authorized, then freeze the closure with its
consumer-native immutable identity: for example a Git tree/commit, deterministic
package, image/revision digest, or content-addressed snapshot. A mutable
worktree digest is invalid. If immutable closure cannot be created within
authority, report `modified-not-frozen`.

Before deleting a branch, worktree, or other recovery surface, prove required
candidate, cutover, effect, and rollback evidence remains durably reachable;
otherwise stop.

A native Goal, when explicitly requested by the user, adds no authority.
Continue autonomously only while Goal identity, Outcome, boundary, candidate
surface (paths and generated inputs, not current bytes or commit), effect
target/identity/cap, and pending-decision state remain unchanged. Otherwise
stop; a user reply authorizes only the decision it answers. Candidate byte
changes within those conditions require checks and a new freeze, not a new
scope grant.

## Review one identity

Ordinary reversible local work needs no terminal review. Convergence review is
advisory; reviewers may be reused or followed up without a round cap. For a
public, external, irreversible, or other high-risk frozen candidate, use one
fresh native read-only no-history
blocker-only Exact-final over the readable immutable baseline, candidate, and
plan. Require strict `GO` or `NOT_YET` and an echo of the exact candidate
identity. Unknown or incomplete required coverage is adverse. Any candidate
byte change invalidates the verdict; a plan `GO` validates only the plan, and a
composite candidate needs one immutable envelope binding all components.

Admit only a reproduced frozen-obligation or preservation failure, or a
reachable candidate-new material safety/correctness regression. `GO` validates
only the reviewed candidate and grants nothing. After `NOT_YET`, make at most
one already-authorized in-boundary repair while its budget remains, refreeze,
and use one fresh replacement review. Any later adverse result returns to the
user. Follow-up on an Exact-final handle is convergence-only, never terminal.

## Act once and close truthfully

Before an external effect, recheck its target, identity, cap, and observation
predicate. Attempt it once, observe read-only, and classify `landed`,
`not_landed`, or `unknown`. Retry only after authentic proof of zero effect and
an existing recovery grant. Partial, ambiguous, or unknown effects stop.

Close as achieved, not achieved, or unknown only after recomputing candidate
and effect identity, verifying Outcome and preservation, running required real
paths, and accounting for staged, unstaged, untracked, external, skipped, and
unverified state. Never infer publication, installation, activation, or other
external success from silence.
