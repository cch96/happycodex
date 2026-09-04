---
name: happycodex
description: Use for risky/destructive/public/long/compaction-prone work and architecture or design recommendations using current multi-artifact implementation facts.
---

## Ground and authority

Use the native Plan for bounded reversible work. For risky work, copy
`references/execplan.md` to a task-owned unversioned path returned by
`git rev-parse --git-path happycodex/execplans/<task-slug>.md`. Keep the plan
outside tracked source, index, refs, and candidate objects; replace its current
values in place, derive live state from tools, and never stage it.

Treat the boundary as the workspace, project, or task-owned domain, not an exact
path inventory. Paths and plans do not grant authority. Safe task-owned
additions or relocations may continue only while Outcome, consumer,
preservation, exclusions, and effects remain fixed. Never infer permission to
delete an old surface or mutate shared state.

Advisers, tools, plans, reviewers, and a native Goal cannot manufacture user
authority. A compatibility break needs explicit authority. Recommend a change
only for material safety or correctness, or when lower steady-state semantic
complexity justifies cutover risk.

Classify reconstructible non-consumer caches, temporary files, logs, and compiled
output as incidental only when unrelated to secrets, credentials, trust,
shared/system configuration, owners, or remote/paid resources; never silently
include those protected classes. Stop on excluded consumer input, destructive
shared mutation, or uncertainty.

Interpret amendments narrowly. `不用 review` waives matching review and requires
an unreviewed result. `自己解决` permits autonomous in-boundary reversible repair.
`直接发` permits the named standard effect for the established candidate and
target while pruning optional plan, review, or preflight work. None expands the
target, effect, retry, destructive cleanup, trust, Outcome, or preservation.
Stop if Goal identity, Outcome, boundary, candidate surface, effect
target/identity/cap, or a pending decision changes. A user reply authorizes only
the decision it answers.

## Route and ownership

Keep the request, Outcome, unresolved decisions, and primary judgment direct.
Handle small bounded work directly. Before an unread multi-artifact
recommendation, use one read-only scout for bounded observable questions; add
independent read-only scouts only when concurrency materially helps.

Allow one writer for every set of overlapping paths, mutable contracts, or
effect resources. The primary or Root stays read-only while that writer owns
them. Parallelize only independent, identity-pinned reads. ORDER dependencies,
effects, and shared mutations. Linked worktrees have separate indexes,
worktrees, and HEAD state, but worktrees with one common Git directory share
local refs, remote-tracking-ref writes, and branch checkout ownership.

Keep each Git boolean predicate's status separate: `0` is true, `1` is false,
and greater than `1` is error. A later command, combined wrapper, or pipeline
status cannot substitute. A remote-tracking ref is a cached observation, not
live remote state; observe the live remote only for a remote effect or a
freshness-sensitive conclusion.

Use a compact handoff: conclusion, scope, identity, decisive path/line evidence,
unknowns, and follow-up delta. Correlate Outcome-relevant seams across
identifiers, contracts, mutable resources, timelines, and candidate/effect
identity. Reread or rereview only on decision-changing evidence or state drift.
Never interrupt or replace a live writer.

Continuity is lost only on terminal failure or confirmed unreachability. Then
confirm the writer cannot resume and reconstruct authority, ownership, candidate
identity, and live state from tools and the task plan. Treat summaries as hints,
not authority.

## Admit and freeze

Supported paths use normal commands, configurations, inputs, and
consumer-reachable workflows. Before admitting a blocker, establish three links:
the normal supported path;
its final source in the direct request or Outcome, preservation of reachable
behavior/data/identity, a required workflow, or candidate-new material safety or
correctness; and material falsification. Missing links make a concern advisory.
Plan wording, reviewer preference, stricter local invariants, optional or
incidental checks, and unsupported manual injection cannot create a blocker.
Required robustness remains blocking. Reproduce a concrete failure where
feasible and preserve admitted blockers and required unknowns. Only required
missing or unknown coverage is adverse; optional coverage stays advisory.

If permission for the supported path is missing, ask once and do not substitute
an alternate effect. Keep a fixed Outcome, boundary, Done condition, owner, and
blockers; revise them only for decision-changing evidence or a concrete blocker.

Use one freeze for each independently closable Outcome; do not split steps that
share one effect. Freeze every direct, generated, and transitive consumer input,
including modes, deletions, and native identity. Exclude secrets, credentials,
and raw external events. Verify all mutable inputs remain authorized.

Reuse a green check only for the exact consumer-native identity it tested.
Validate an evidence-only non-consumer change with a focused check. A consumer
input change or uncertain classification invalidates relevant checks. Before
deleting a recovery surface, prove candidate, cutover, effect, and rollback
evidence remain durably reachable; otherwise stop.

## Review and effects

Reversible local work has no terminal review. For a material or release-bound
candidate, after required checks and freeze, run one fresh native read-only,
no-history, blocker-only Exact-final. Convergence review is advisory. Exact-final
may precede effect authority and grants none; admitted `NOT_YET` remains blocking
under the ladder below.

Keep one immutable task-local envelope containing one Candidate Review Body and
one Next-effect Binding. The Body identifies the reviewed consumer input and
premises; the Binding identifies the immediate authorized effect. Candidate,
premise, or relied-check drift invalidates review. Same-tree effect or ref-carrier
drift refreshes only the Binding. New consumer input requires relevant checks,
freeze, and review.

After `NOT_YET`, use at most one authorized in-boundary repair set covering all
findings and one fresh same-rule replacement review. A later adverse result
returns the blocker and decision; it creates no new grant. Plan `GO` validates
the plan, while candidate `GO` authorizes no effect.

A material one-shot effect is one whose repetition could create another durable,
paid, public, shared, destructive, or otherwise material result. Attempt each
admitted effect once, read back authoritative state, and classify it as
`landed`, `not_landed`, or `unknown`. Only authoritative proof of zero effect,
with the same Outcome, target, identity, boundary, cost cap, observation, and
observation predicate plus a causal fix, permits bounded recovery. Never retry
blindly. A partial, ambiguous, or unknown effect stops, and a missing cost cap is
not unlimited.

If a low-cost metered read landed, effect-side state rules out duplicate durable
results, and only local output was lost, repair the local cause before one causal
recovery; ask before cost grows. Explicit no-limit authority permits causal
recovery, never blind repetition.

## Closeout

Report the exact candidate, scope, checks, disposition, remaining authority,
and unknowns. A commit or handoff is not publication, and local work closes with
no external effect. Read back each separately authorized publication,
deployment, or integration, and keep functional acceptance distinct.

Account for staged, unstaged, untracked, external, skipped, and unverified state.
Never infer publication, installation, activation, or other external success
from silence. Report achieved, not achieved, or unknown only after recomputing
candidate/effect identity and checking Outcome and preservation on required real
paths.

Preserve manual, permanent, and recovery worktrees without exact cleanup
authority and durable recovery reachability. Never silently retarget a task
worktree, terminate a process, or clean a resource. Keep any unrun required
authenticated, write, or paid path partial and unverified after one permission
request.
