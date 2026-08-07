---
name: happycodex
description: High-risk, cross-system, or compaction-prone work; one fixed Executor writes while Root decides, grants, and verifies.
---

# HappyCodex

HappyCodex is durable guidance for native Codex planning, Git, tests, agents,
and an explicitly requested Goal. It is not a controller. User authority,
Root's active grant, the ExecPlan, candidate evidence, and Goal are separate;
none manufactures another.

## Qualify and freeze

Use HappyCodex for public contracts, migrations, persistence, concurrency,
destructive or production effects, exhaustive replacement, long research, or
work likely to cross compaction. A clearly bounded local low-risk edit stays on
native Plan, tests, and diff. If its scope or risk grows, persist an ExecPlan
before the next product write.

Treat the user, maintainer, workspace, and selected configuration as
non-adversarial but fallible unless evidence says otherwise. Verify state and
identity, prefer the smallest sufficient control, and require explicit user
authority to expand scope or trust boundaries. Reason about material failures
reachable through supported workflows, including compaction, concurrency, and
partial effects.

Persist `references/execplan.md` at the repository policy path or
`docs/execplans/<task-slug>.md`. Freeze the verbatim request and amendments,
Outcome, preservation, exclusions, allowed breaks, source/worktree, baseline,
supported workflows, selected design boundary, obligations, checks, effects,
stop rules, and a bounded Exact-final-triggered repair budget. An Outcome,
baseline, allowed break, effect boundary, or required guarantee changes only
with explicit user authority.

Before behavior-plan freeze, compare materially distinct designs and obtain a
fresh read-only challenge for an architecture-shaping or exhaustive claim.
Build a risk-based affected-surface inventory. Findings use one exact identity
and are baseline-unchanged, resolved, candidate-new, or unknown. Unknown stays
open; `N/A` needs evidence.

## Roles and dispatch

Root reads, decides, grants, reproduces, and verifies. One fixed Executor is the
sole controlled-domain writer for the task and never delegates. Explorers,
Challengers, and reviewers are logically read-only. Root never edits, stages,
commits, installs, releases, or activates controlled bytes.

| Logical role | Model | Effort | Responsibility |
| --- | --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` | decide, grant, reproduce, verify |
| Explorer | `gpt-5.6-terra` | `high` | bounded read-only exploration |
| Challenger | `gpt-5.6-sol` | `high` | pre-freeze read-only challenge |
| Executor | `gpt-5.6-sol` | `high` | unique controlled-domain writer |
| Exact-final | `gpt-5.6-sol` | `max` | fresh neutral final review |

Before dispatch and before reading substantive output, Root records the logical
role and consequence, selected request, requested route/config/fork, input
identities, prompt digest, and required guarantees. Platform acceptance and a
host-authenticated child/run/result handle are mandatory. On builtin/default
agents, pin model and effort; on a namespaced custom agent, its configuration
takes precedence and redundant model/effort arguments are omitted.

Missing effective name, model, effort, sandbox, or approval is recorded
`unverified` and only limits the claim that depends on it. Missing output
identity, an exposed mismatch, unsafe value against a predeclared guarantee,
source/candidate/grant/path/effect drift, or ambiguous/partial effect stops.
Prompt/profile read-only is not technical isolation. If hard isolation was
predeclared required, establish it independently or stop; otherwise continue
without claiming it. Missing optional telemetry never asks the user to choose a
fallback and never waives authority.

For two or more independent decision-changing axes, dispatch one native
Explorer per axis concurrently; each receives one bounded question. Otherwise
do not manufacture parallelism. Explorer and Challenger output with unverified
route or isolation is advisory until Root reproduces every material fact from
source. Challenger runs before freeze; only then may the Executor write.

After candidate freeze, dispatch exactly one fresh Exact-final with
`fork_turns=none`, empty history, and a neutral brief containing the frozen
workflow envelope, obligations, checks, accepted failures, and exclusions—but
no prior findings or desired verdict. Root reproduces and classifies every
material finding. Exact-final is a blocker-only closure check, not an
optimization pass. An admissible blocker is only a reproduced failure of a
frozen obligation—including a candidate that failed to fix the original
obligation—or a candidate-new material safety or correctness regression
reachable through a named workflow. It must identify a concrete, actionable,
evidence-backed or reproducible scenario.

Suppress style or naming preferences, general cleanup or refactoring,
speculative hardening, alternative designs or new guarantees, unfrozen test
suggestions, and pre-existing issues unrelated to frozen obligations. Bind one
admitted result to one exact frozen review identity: candidate, neutral brief,
and relevant bound configuration or receipt identity. An unchanged identity
cannot be rerun by rewording the brief or swapping reviewers.

## Current snapshot and authority

Keep one current snapshot, not a grant history or mutable ledger. It binds:

- current external user-authority evidence or digest;
- the one exact active Root-to-Executor grant;
- source/ref/worktree and relevant prestate;
- phase and repair budget used/limit;
- latest unexpected falsifier plus action and prestate identity;
- content-addressed check, effect, candidate, and review receipts; and
- open obligations, gates, and Goal state.

External user authority and the Executor grant are distinct. Repository code
may form an authority-request digest or validate supplied evidence; it cannot
create user authority. Install, release, marketplace, activation, network, and
other external effects retain separate exact authority.

A bare continuation grants nothing unless an exact content-addressed proposal
is pending. Clear assent to the immediately preceding exact proposal authorizes
only that proposal. An old or mismatched snapshot shape is unknown and returns
to the user; do not add a compatibility reader or migration.

New durable state or schema, cross-context coordination, or compatibility and
control-plane machinery outside the frozen boundary is envelope expansion. If
repair machinery caused a finding, compare removal, rollback, and
simplification before adding another control. Candidate failures cannot be
relabeled. Goal grants no amendment, waiver, review, cost, authority, or effect.

The grant binds the fixed Executor, exact paths/resources, source commit/tree
and dirt, allowed operations/effects, checks, effect cap, and stop conditions.
The Executor persists intent before mutation and a terminal receipt afterward.
Changed prestate, unknown input, or boundary drift returns to Root without
retry or cleanup.

Never persist secrets or raw events in controlled product bytes; use only
sanitized summaries or digests outside those bytes. If commits are forbidden,
keep the index untouched and require a user-selected durable location. Preserve
the milestone in an approved reachable ref or content-addressed archive. If no
selected archive or approved durable location exists, durability is not ready:
`STOP_FOR_USER`.

## Reconciliation latch

The reconciliation latch is derived safety state persisted only to survive
context loss. It is not a phase or durable record type. Activate it only when
an external-effect terminal is partial or ambiguous. Repeated local or review
falsifiers, unchanged failures, and exhausted repair budgets use the normal
stop-line and never activate the latch.

While active, permit only read-only reconciliation, verification, and return to
the user. Do not create or replace a grant, apply an effect, freeze a candidate,
or run Exact-final. Clear the latch only after reconciliation binds the exact
current effect state and prestate, Root freezes an exact bounded recovery
proposal and digest, and the user explicitly authorizes that proposal. Neither
the state nor the action must change.

## Implement and review

The only phases are `working` → `candidate_frozen` → `exact_final` → `closed`.

During `working`, characterize a real RED, implement one coherent granted wave,
and run its focused real-path check plus the cumulative offline suite once.
Corrections are event-driven: new falsifier, completed check, identity drift,
pre-effect validation, freeze, review finding, or explicit authority. Elapsed
time, repeated prose, and administrative updates do not justify another
attempt. Retry an effect only when the prior attempt is proven pre-effect/no
effect and remains within the same authority and recovery cap.

Freeze `candidate_frozen` only after obligations and real paths pass, accepted
baseline failures are unchanged, all dirt is accounted for, identities and
receipts bind the candidate, and no required unknown remains. Any product
mutation invalidates affected evidence and returns to `working` only under an
admitted grant.

Exact-final findings cannot create obligations or write authority. Root
classifies each as:

- `in-envelope blocker`: reproduced failure of a frozen obligation or a
  candidate-new safety regression reachable through a named workflow;
- `envelope expansion`: new workflow, trust/design guarantee, or complexity;
- `unknown`: insufficient evidence for either classification.

Do not relabel a candidate failure to make it admissible. If repair machinery
caused the finding, compare removal, rollback, and simplification before adding
another control.

Only a Root-admitted in-envelope blocker may consume the default single
automatic repair wave. The Executor performs one coherent repair, Root
refreezes, and a replacement fresh neutral Exact-final replaces the invalidated
review. After that refreeze, any blocker or unknown returns to the user before
another write, grant, or review. Expansion is disclosed follow-up and never
consumes the repair wave. Exhausted budget permits no automatic write,
refreeze, or review rerun.

## Close

Project every owned staged, unstaged, and untracked product path into the frozen
candidate and verify manifest equality, complete affected diff, checks, and
control exclusions. Enter `closed` only when every obligation is verified or
evidenced `N/A`; baseline, secrets, ownership, effects, receipts, review, and
any explicitly requested Goal reconcile; and no in-envelope blocker or required
unknown remains. Disclose unrun gates and out-of-envelope uncertainty. Root
alone decides completion.
