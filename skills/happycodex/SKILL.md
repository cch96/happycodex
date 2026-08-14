---
name: happycodex
description: Use for high-risk, cross-system, destructive, public-contract, migration, persistence, concurrency, exhaustive, long-running, or compaction-prone Codex work, and for architecture or design recommendations that depend on current multi-artifact implementation facts, when the work needs a static change boundary, isolated context, consumer-native candidate identity, and truthful closure.
---

# HappyCodex

HappyCodex guides native Codex plans, agents, Git, tests, and diffs without creating authority or a second control plane.

## Ground the work

Use the native Plan for bounded reversible work. Before substantial long or
compaction-prone work or the first risky write, copy `references/execplan.md` to
the repository policy path, or `docs/execplans/<task-slug>.md` when none exists.
Fill it, keep it static, and derive live state from tools.

The authorization boundary is the selected workspace/project or task-owned
domain, not an exact realized-path inventory. Planned paths coordinate ownership;
exact paths close consumer input at freeze. Reversible Outcome-required
task-owned additions or relocations may continue before freeze while consumer,
Outcome, preservation, exclusions, and effects stay unchanged; this does not authorize deleting old or shared surfaces.
Advisory or available capability never expands authority.

A compatibility break requires explicit authorization of its exact material consumer,
data, or cutover effect; ambiguous wording authorizes comparison only. Recommend it only
for material safety/correctness or lower steady-state semantic complexity relative to cutover risk.

Bounded additive, reconstructible, non-authoritative cache, temporary, log, or compiled
output is incidental only if non-consumer and unrelated to secrets, credentials, trust,
shared/system configuration, another owner, or remote/paid resources. Account for it.
Stop on shared-cache deletion, system/user/shared installation, excluded or omitted consumer input, or uncertainty.

Apply explicit amendments as prune-only authority within the current Outcome:
`不用 review` waives matching review and requires an unreviewed result;
`自己解决` permits autonomous in-boundary reversible repair; `直接发` permits the
named standard effect for the established candidate and target while pruning
optional plan, review, or preflight work. None expands target, effect, retry,
destructive/shared cleanup, or trust authority, or waives Outcome/preservation.

Use one freeze per independently closable Outcome. Do not split for elapsed
time, thinking, or CI waits. Do not split steps sharing one external effect.

## Route once by boundary

Keep the request, instructions, Outcome, unresolved decisions, and primary
judgment direct. Use the smallest of these routes:

- For a recommendation depending on unread multi-artifact current facts, ask one
  native read-only scout bounded observable questions before deciding. It returns
  facts, citations, scope, and unknowns, not the recommendation. Keep two
  bounded lookups direct.
- For a stable question over a supporting body, send it to one native
  read-only agent before primary ingestion. Add independent bodies only when
  concurrency materially helps.
- Once ownership and Done are stable, send substantial implementation to one
  native worker; keep small corrections direct. Allow one writer per overlapping path,
  semantic mutable contract, or effect resource, including cross-repository overlap.
- Invoke an external model or tool directly for its assigned question; do not
  delegate the invocation or treat it as terminal review.

When native spawn exposes `fork_turns`, pair any explicit `agent_type`, `model`, or
`reasoning_effort` with a self-contained packet and `fork_turns="none"` by default.
Use the smallest positive fork only for a recent raw artifact that cannot be referenced
or restated faithfully; reserve omitted/`"all"` for intentional same-agent inheritance.

Under a proactive-only restriction, the route above is this Skill's explicit
request: attempt the exposed native spawn; it never overrides an actual host
denial. With an explicit host denial, do not spawn. Direct fallback follows
after a spawn error, a concrete missing capability/tool, or an unbounded body
that would transfer primary judgment. Record that evidence before direct work.
Do not claim delegation was forbidden without an attempt when spawn is exposed.

After continuity loss, confirm the old writer cannot resume, reread the whole
ExecPlan, and reconstruct Git, index, candidate, effect, and trust state. Stop on
drift; summaries are hints, not authority.

## Converge on evidence

When Outcome, boundary, Done, ownership, and blockers stabilize, hand the fixed
Executor the write lock, increments, and exclusions. Root stays read-only and revises only
through that Executor after new decision-changing evidence or a concrete current blocker.

A blocker or required coverage item is admitted only when its failure is
reachable on a supported path and falsifies something directly required by the
user or Outcome, preservation of pre-change reachable behavior, data, or
identity, a required supported workflow, or candidate-new material safety or
correctness. Supported paths use normal commands, configurations, inputs, and
consumer-reachable workflows for the Outcome. Plan wording, reviewer preference,
and stricter local invariants cannot manufacture blockers; neither can optional
or incidental checks or unsupported-path manual artifact injection. Explicitly
required robustness or adversarial injection remains blocking. Reproduce the
concrete failure path where feasible. This never dismisses an existing admitted
blocker or required unknown. Before an advisory pass, state what could change the
verdict. A standing instruction does not renew passes. At completion, stop and
report findings, scope, and unknowns; this stop is not `GO`. Root may do one focused check
with a stated possible verdict change.

## Freeze one candidate

Derive direct, generated, and transitive consumer inputs, including modes,
deletions, and byte identities. Exclude secrets and raw external events. Verify
all mutable inputs remain authorized, then freeze closure with its consumer-native
immutable identity: Git tree/commit or content-addressed snapshot. A
worktree digest is invalid; if closure cannot freeze, report `modified-not-frozen`.

Reuse green checks only by exact consumer-native identity. Evidence-only,
non-consumer changes receive focused validation; consumer-input changes
invalidate relevant checks. Uncertain classification is consumer input. Do not
create an evidence-path registry.

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
identity. Unknown or incomplete coverage derived from the full admission rule is
adverse. Any candidate
byte change invalidates the verdict; a plan `GO` validates only the plan, and a
composite candidate needs one immutable envelope binding all components.

Both reviews use the same admission rule. `GO` validates only the reviewed
candidate and grants nothing. After `NOT_YET`, one already-authorized in-boundary
repair is allowed; one repair change-set addresses all admitted findings, then
refreeze and use one fresh replacement review. A later adverse result returns to the user
with the real unresolved blocker or decision; it does not automatically require
a new grant. Follow-up on an Exact-final handle is convergence-only, never
terminal.

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
