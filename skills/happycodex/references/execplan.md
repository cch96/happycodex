# HappyCodex ExecPlan

Persist this current index before qualifying research or product work. Use the
repository policy path when one exists, otherwise
`docs/execplans/<task-slug>.md`. Keep exactly one authoritative current
snapshot; old evidence is referenced by content digest, not copied as history.
This is guidance and durable intent, not a controller.

## Frozen envelope

Record:

- verbatim request and amendments with anchors or digests;
- normalized Outcome, preservation, exclusions, allowed breaks, and waivers;
- named supported workflows and their preconditions and visible outcomes;
- selected design and complexity boundary, rejected decision-changing designs,
  and remaining uncertainty;
- repository, source commit/tree/status, ref, worktree, package/config identity;
- baseline command, exit, exact failures, and accepted failure identities;
- obligations, affected surfaces, checks, effects, and stop rules; and
- the Exact-final-triggered repair budget and consumed count.

Outcome, baseline, allowed breaks, trust/effect boundaries, and required gates
change only under explicit user authority. A source-derived obligation may be
added only when an already frozen workflow requires it; bind its provenance and
invalidation rule.

## Current snapshot

Use this shape and replace stale values rather than appending grant history:

| Field | Current value |
| --- | --- |
| Phase | `working/candidate_frozen/exact_final/closed` |
| External authority evidence | exact user evidence/digest and permitted boundary |
| Active Executor grant | fixed output identity, exact paths/resources/actions/effects/checks/stops |
| Prestate | source/ref/worktree/status plus effect destination identity |
| Repair budget | used / limit |
| Latest falsifier | unexpected identity + action identity + relevant prestate, or `none` |
| Reconciliation latch | active/inactive with effect-state reconciliation requirement |
| Receipts | content digests for checks, effects, candidate, and review |
| Obligations and gates | exact open/verified/N/A identities |
| Goal | absent or matching explicit user request and state |

External user authority evidence is not the active Executor grant. Repository
code cannot manufacture authority. Install, release, marketplace, activation,
network, and other external effects keep separate exact authority.

A bare continuation grants nothing unless an exact content-addressed proposal
is pending. Clear assent to the immediately preceding exact proposal authorizes
only that proposal. Treat an old or mismatched snapshot shape as unknown and
return to the user; do not add a compatibility reader or migration.

New durable state or schema, cross-context coordination, and compatibility or
control-plane machinery outside the frozen boundary are envelope expansion. If
repair machinery caused a finding, compare removal, rollback, and
simplification before adding another control. Candidate failures cannot be
relabeled. Goal grants no amendment, waiver, review, cost, authority, or effect.

Never persist secrets or raw events in controlled product bytes; use only
sanitized summaries or digests outside those bytes. If commits are forbidden,
keep the index untouched and require a user-selected durable location. Preserve
the milestone in an approved reachable ref or content-addressed archive. If no
selected archive or approved durable location exists, durability is not ready:
`STOP_FOR_USER`.

## Roles and receipts

| Role | Required dispatch and admission evidence |
| --- | --- |
| Root | task identity; frozen source; decision, grant, reproduction, and phase receipts |
| Explorer | one bounded question; requested route/config/fork; source identity; host output handle; exposed or unverified telemetry; advisory/admitted state |
| Challenger | neutral pre-freeze question; same identity and telemetry fields; Root reproduction |
| Executor | fixed host output handle; exact grant/source/prestate/path/effect boundary; terminal Git/test/effect receipt |
| Exact-final | fresh `fork_turns=none`; neutral brief digest; frozen candidate; host output handle; coverage; findings; Root reproduction/disposition |

Before dispatch and before substantive output, bind logical role and intended
consequence, selected agent request, requested route/config/fork, input
identities, prompt digest, and required guarantees. Platform acceptance and a
host-authenticated output handle are always required. Record absent effective
name/model/effort/permissions as `unverified`; do not claim what is unverified.
Missing output identity, exposed mismatch, violated required guarantee,
identity/scope drift, or ambiguous/partial effects stops.

For multiple independent decision-changing axes, dispatch one native Explorer
per axis concurrently, each with one question. Unverified Explorer/Challenger
route or isolation is advisory until Root reproduces source facts. Challenger
precedes behavior-plan freeze; Executor follows it. Exact-final is fresh,
empty-history, logically read-only, and neutral. Hard technical isolation is
required only when predeclared; prompt/profile text does not establish it.

Exact-final is a blocker-only closure check, not an optimization pass. An
admissible blocker is only a reproduced failure of a frozen obligation,
including a candidate that failed to fix the original obligation, or a
candidate-new material safety or correctness regression reachable through a
named workflow. Require a concrete, actionable, evidence-backed or reproducible
scenario. Suppress style or naming preferences, general cleanup or refactoring,
speculative hardening, alternative designs or new guarantees, unfrozen test
suggestions, and pre-existing issues unrelated to frozen obligations.

Bind one admitted result to one exact frozen review identity: candidate,
neutral brief, and relevant bound configuration or receipt identity. An
unchanged identity cannot be rerun by rewording the brief or swapping
reviewers. The neutral brief still excludes prior findings and a desired
verdict.

## Obligations

Use one current table. Follow only risk-justified affected surfaces and record
`N/A` with evidence.

| ID | Type | Observable contract | Affected surfaces | Falsifier / RED | Evidence identity | State |
| --- | --- | --- | --- | --- | --- | --- |
| `<exact ID>` | outcome/preservation/break/premise/exclusion | behavior | input, callers, state, output, recovery as applicable | counterexample | digest/receipt | open/verified/N/A |

Material findings keep one exact case-sensitive identity and are
baseline-unchanged, resolved, candidate-new, or unknown. Unknown stays open.

| Finding | Reproduced evidence | Class | Disposition | Budget | Consequence |
| --- | --- | --- | --- | --- | --- |
| `<exact ID>` | source/check identity | in-envelope blocker/envelope expansion/unknown | block/follow-up/return-user | used/limit | write/review/closure stop |

Findings after behavior-plan freeze cannot create authority. Only a reproduced
in-envelope blocker may consume an authorized repair wave. Expansion is
follow-up unless separately authorized; unknown returns to the user before
write. After the single replacement Exact-final, any blocker or unknown returns
to the user before another write, grant, or review rerun.

## Reconciliation latch

The reconciliation latch is derived safety state persisted only to survive
context loss. It is not a phase or durable record type. Activate it only for a
partial or ambiguous external-effect terminal, never for repeated local or
review falsifiers. Unchanged failures and exhausted repair budgets use the
normal stop-line.

While active, allow only read-only reconciliation, verification, and return to
the user. Forbid grants, effects, candidate freeze, and Exact-final. Clear it
only after reconciliation binds the exact current effect state and prestate,
Root freezes an exact bounded recovery proposal and digest, and the user
explicitly authorizes that proposal. Neither state nor action must change.

## Working and checks

The only phases are `working`, `candidate_frozen`, `exact_final`, and `closed`.
During `working`, record a real-path RED or explicit characterization, one
coherent repair wave, changed paths, focused command/result, and one cumulative
offline suite result. A mock cannot establish its own seam.

Corrections require new evidence: a falsifier, completed check, identity drift,
pre-effect validation, candidate freeze, review finding, or explicit authority.
Elapsed time or repeated prose is not progress. Retry only a provider/effect
attempt proven pre-effect/no-effect within the same authority and recovery cap.
An ambiguous or partial external-effect terminal activates the reconciliation
latch.

At `candidate_frozen`, bind clean candidate commit/tree, complete changed-path
inventory, source/package/config identities, obligations, checks, accepted
failures, effect receipts, repair budget, and exclusions. Product mutation
invalidates affected evidence.

At `exact_final`, bind the fresh neutral brief, requested route/permissions,
exposed or unverified telemetry, authenticated output identity, frozen
candidate, coverage, result, findings, and Root reproduction/classification.
Only a Root-admitted in-envelope blocker with remaining budget may return to
`working`; refreeze requires a replacement fresh Exact-final.

## Recovery and closure

After compaction, read the full plan and reconcile its single snapshot against
Git, tests, claim/effect receipts, active agents, and Goal before any write or
completion claim. Reconnect only the recorded Executor. Unknown or mismatched
facts stay open. A summary or copied handle does not reconstruct authority.

Enter `closed` only when every obligation is verified or evidenced `N/A`, real
paths pass, accepted failures are unchanged, all dirt and effects are accounted
for, Exact-final is admitted, no in-envelope blocker or required unknown
remains, separate effects have receipts, and an explicitly requested Goal is
complete. Record final commit/tree and disclose unrun gates, waivers, and
out-of-envelope uncertainty.
