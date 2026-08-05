---
name: happycodex
description: High-risk, cross-system, or compaction-prone work; one fixed Executor writes while Root decides, grants, and verifies.
---

# HappyCodex

HappyCodex is durable guidance for native planning, Git, tests, agents, review,
and an explicitly requested Goal. It is not a controller. Authority permits an
exact action; the ExecPlan defines completion; evidence binds a candidate; Goal
controls automatic continuation. Never infer one from another.

## Select and freeze

Use HappyCodex for public contracts, migrations, persistence, concurrency,
destructive or production work, exhaustive replacement, long research, or work
likely to cross compaction. Material uncertainty about a supported workflow
qualifies. A clearly local low-risk edit may use native Plan, tests, and diff;
establish an ExecPlan before the next product write if scope or risk grows.

Reason only about material failures reachable through supported workflows,
including compaction, concurrency, and partial effects. Unless the request or
source establishes otherwise, treat the user, maintainer, workspace, and
selected configuration as non-adversarial but fallible: verify state and
identity, not motive. Prefer the smallest sufficient control; expanding scope
or trust boundaries requires explicit user authority.

Persist `references/execplan.md` at the repository policy path or
`docs/execplans/<task-slug>.md`. Freeze the verbatim request and amendments,
normalized Outcome, preservation, exclusions, allowed breaks, source/worktree,
baseline command and failures, roles, grants, obligations, checks, effects, and
stop conditions. Changing Outcome, baseline, an allowed break, or a required
gate needs explicit user authority. A source-derived obligation may be added
only with its provenance and invalidation rule.

Build a risk-based affected-surface inventory. Follow each material obligation
through the surfaces its behavior can actually reach: input and validation,
callers, state and replay, outputs, recovery, and downstream failure. Do not
force irrelevant surfaces into a mechanical checklist. Material findings keep
one exact case-sensitive identity and are baseline-unchanged, resolved,
candidate-new, or unknown; unknown stays open and `N/A` needs evidence.

Before freeze, compare materially distinct designs that could change the Outcome
within the stated trust boundary. Challenge material omissions, then stop when
remaining alternatives would not change that Outcome. For an exhaustive or
architecture-shaping claim, Root obtains a fresh baseline-only read-only
challenge from the frozen request and source.

## Roles and grants

Root reads, decides, grants, reproduces, and verifies. One fixed Executor is the
sole controlled-domain writer for the whole task: it owns the ExecPlan, tests,
product, commits, and receipts, never delegates, and cannot be replaced after
compaction. Explorers, Challengers, and reviewers are read-only. Root never
edits, stages, commits, installs, releases, or activates controlled bytes.

Use this exact logical-role matrix:

| Logical role | Model | Effort | Responsibility |
| --- | --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` | decompose, decide, grant, reproduce, verify |
| Explorer | `gpt-5.6-terra` | `high` | read-only bounded exploration |
| Challenger | `gpt-5.6-sol` | `high` | read-only pre-behavior-plan-freeze challenge |
| Executor | `gpt-5.6-sol` | `high` | unique fixed controlled-domain writer |
| Exact-final | `gpt-5.6-sol` | `max` | one fresh read-only final review |

Before dispatch and before reading substantive child output, record the logical
role, intended use and consequence, selected agent request, requested
route/config/fork, input identities and prompt digest, and guarantees required
by the task, source, or user. Root owns this authenticated dispatch/tool receipt.
Automatic capability handling cannot manufacture authority or silently waive a
required guarantee. Require Platform acceptance of the exact spawn request. On
the portable builtin/default path, explicitly pin model and effort. For a
namespaced custom agent, its file's model and effort take precedence; omit
redundant or conflicting explicit model/effort arguments.

Require a mechanically authenticated child/run/result handle that binds
terminal output to the accepted dispatch. Missing output identity cannot
downgrade. Cross-bind any exposed runtime metadata to the dispatch record. Stop
for an explicit mismatch in a requested or required identity or route,
malformed or ambiguous claimed evidence, an unsafe exposed value relative to a
predeclared required guarantee, grant/source/path/effect boundary drift,
candidate or source drift, or ambiguous or partial effects. Keep logical role
distinct from platform agent type and custom-agent name. Names, config requests,
labels, and agent self-reports are not effective-routing evidence.

Apply missing observability only to the guarantee or use that depends on it:

- Effective agent name is record-only when exposed; if absent, record
  `unverified`.
- Missing effective model or effort: record `unverified` and continue unless
  exact routing was predeclared required. An exposed effective model or effort
  mismatch requires discard and stop. Do not claim exact routing while it is
  unverified.
- Missing effective sandbox or approval: record `unverified`. When technical
  isolation was predeclared required, independently establish the isolation or
  effect boundary or stop. When it was not required, continue without claiming
  technical isolation. A full-access result mismatches only a predeclared
  read-only technical-isolation guarantee. Prompt/profile read-only remains
  non-proof.
- Missing optional telemetry never asks the user to choose a fallback. No
  user-facing modes or levels exist. Never require `普通模式继续`. Ask the user
  only when continuation would change the Outcome, authority, trust boundary,
  or an explicitly required guarantee.

Root first decomposes the problem into independent, decision-changing axes.
Run multiple Explorers concurrently only when multiple such axes exist, and
give each Explorer exactly one bounded question. For two or more qualifying
axes, dispatch one native Explorer per axis concurrently through the host's
builtin `explorer` selector or an admitted namespaced custom Explorer selector.
Parallel ordinary tool calls are not Explorer dispatches. Unverified Explorer
or Challenger route or isolation output is advisory leads only. Root reproduces
every material fact from source before it affects a plan, grant, or phase; it
never votes. Challenger runs before the behavior-plan freeze. Only after that
freeze does the unique Executor write. Executor may write despite missing route
or permission telemetry only when host-issued output identity, fixed-writer
ownership, exact grant, source/prestate, paths/resources, and allowed effects
are bound. Root relies on actual Git, tests, and receipts, not Executor prose.

After candidate freeze, spawn exactly one fresh Exact-final with
`fork_turns = none`, empty history, and a neutral brief that excludes prior
findings and desired verdicts. Exact-final may count without verified model or
permission telemetry only when exact routing and hard isolation were not
predeclared required, the reviewer is fresh with empty history and a neutral
brief, output identity is bound, candidate identity remains unchanged, and Root
reproduces material findings; disclose unverified guarantees. If required hard
isolation is unproven, review remains open. A repair returns to `working`,
invalidates affected frozen evidence, and requires a new candidate freeze and a
new Exact-final.

Record each participant's authenticated dispatch/tool receipt, any
runtime-issued session/turn metadata, and Root admission decision separately.
The dispatch receipt owns logical role, selected request, intended consequence,
requested route/config/fork, input identities, prompt digest, and required
guarantees. Runtime metadata owns exposed route, permissions, runtime identity,
and actual platform/custom name. The admission record binds the available
evidence and any restrictions to phase, source, terminal state, and terminal
receipt. A label, summary, or completion sentence is not evidence.

A custom profile's `sandbox_mode = "read-only"` may be overridden by a live
full-access parent task. Prompt instructions and profile defaults are not hard
isolation. When technical read-only isolation is required, establish a
read-only top-level or parent environment before dispatch, then verify effective
permissions or independently bind an equivalent no-effect boundary. If neither
is established, stop; otherwise record missing optional permission telemetry as
`unverified` without claiming technical isolation.

Every write grant binds the fixed Executor, exact paths/resources, source
commit/tree and dirt, allowed operations, acceptance, effect budget, and stop
conditions. The Executor persists durable intent before mutation and a complete
receipt afterward. Changed prestate, identity/config drift, ambiguous or partial
effect, unknown input, or wider scope returns to Root without retry or cleanup.

## Event correction

Corrections are event-driven. Elapsed time, repeated prose, and administrative
updates do not justify another attempt.

- On a new falsifier, expand the affected-surface inventory and join it to the
  current coherent diagnosis and repair wave before terminal GREEN.
- On an unchanged failure, reconcile durable facts; never retry the same effect
  by rewording, restarting, or seeking a friendlier result.
- At the end of a repair wave, run its real-path focused check and the cumulative
  offline suite once. A failed check reopens the same wave.
- After terminal GREEN, one material recurrence permits at most one
  boundary-level alternative that addresses the failure and reruns affected checks.
  If that alternative fails unchanged or the issue recurs again, ask the user.
- Immediately before any effect, re-read the exact grant, claim, prestate,
  invocation, cost boundary, and destination. Drift or ambiguity stops.

## Implement and recover

The only phases are `working` → `candidate_frozen` → `exact_final` → `closed`.
During `working`, the Executor records a real RED or explicit characterization,
implements one coherent granted wave, and runs focused plus cumulative checks. A
mock cannot prove its own seam. Do not run exact-final while repairing.

Freeze `candidate_frozen` once obligations are evidenced, required real paths
pass, accepted baseline failures remain unchanged, owned dirt is accounted for,
source/package/config identities are bound, and no material unknown remains.
Any product change after freeze returns to `working` and invalidates affected
candidate and review evidence.

Keep the ExecPlan a current index, not a history dump. Its recovery record binds
the request, Root, fixed Executor, source/ref/worktree, exact grant, obligations,
selected checkpoint, tests, phase, open gates, effects, and receipts. After
compaction or resume, read the full plan and reconcile it with current Git,
tests, claims, receipts, agents, and Goal before writing or claiming completion.
A conversation summary, copied handle, or prose cannot reconstruct authority.
Missing or mismatched durable facts fail closed.

## Safety invariants

- Authority: only the exact current grant permits writes. Missing, mismatched,
  or out-of-scope authority returns the decision to the user.
- Resource claims: before a controlled mutation or effect, verify its required
  resources remain assigned to the recorded Executor; conflict or stale
  ownership stops.
- Recovery: restore the full current index and exactly one content-addressed
  checkpoint; reconnect only the recorded Executor.
- Baseline: record each baseline failure by exact identity. It blocks unless
  explicitly accepted and unchanged; candidate failures cannot be relabeled.
- Secrets: never persist secrets or raw model events in product, control, brief,
  receipt, log, or review artifacts; retain sanitized summaries and digests
  outside controlled bytes.
- No-commit: if commits are forbidden, require a user-selected durable location,
  leave the index untouched, and preserve each milestone in an approved
  reachable ref or content-addressed archive; otherwise stop.
- Goal: create Goal only when explicitly requested. It continues existing
  authority but grants no amendment, waiver, review, cost, or effect; complete it
  only after the matching gates close.
- Cost and effects: bind each external effect to its impact, destination,
  budget or cap, and outcome receipt. Retry only when the prior attempt is
  proven no-effect and remains within the same authorization; ambiguous or
  partial effects stop. Keep install, release, marketplace, and activation
  under separate authority; dry-runs cause no effect.

## Review and complete

Project every owned staged, unstaged, and untracked product path into a clean
snapshot. Freeze neutral baseline and candidate identities; Root verifies
manifest equality, the complete risk-based diff inventory, checks, and allowed
control exclusions.

In `exact_final`, one fresh logically read-only reviewer receives the verbatim
request, frozen source range, accepted failures, checks, and exclusions.
Technical read-only isolation is a hard requirement only when predeclared. Its
receipt always binds authenticated output identity, frozen source and candidate
identities, neutral brief, checks, diff and obligation coverage, terminal
result, findings, and Root reproduction. Record the requested and any exposed
or `unverified` model, effort, and permissions. Missing optional route or
permission telemetry alone does not leave review open. A required but unproven
guarantee, missing output identity or coverage, explicit mismatch, candidate
drift, unsupported evidence, or an unchanged rerun leaves review open. Repair
returns to `working`, refreezes, and obtains a new neutral exact-final.

Enter `closed` only when every obligation is verified or evidenced `N/A`, real
paths pass, baseline failures are resolved or accepted unchanged, no secret or
material finding remains, owned status is accounted for, required effects and
receipts bind the frozen product, and the matching Goal—if any—is complete.
Disclose any explicitly waived or unrun gate.
