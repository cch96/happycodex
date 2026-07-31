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
likely to cross compaction. Uncertainty qualifies. A clearly local low-risk edit
may use native Plan, tests, and diff; establish an ExecPlan before the next
product write if scope or risk grows.

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

Before freeze, compare materially distinct decision-changing designs and
challenge omissions until no clearly better in-contract design remains. For an
exhaustive or architecture-shaping claim, Root obtains a fresh baseline-only
read-only challenge from the frozen request and source without sharing preferred
answers or the evidence ledger.

## Roles and grants

Root reads, decides, grants, reproduces, and verifies. One fixed Executor is the
sole controlled-domain writer for the whole task: it owns the ExecPlan, tests,
product, commits, and receipts, never delegates, and cannot be replaced after
compaction. Explorers, Challengers, and reviewers are read-only. Root never
edits, stages, commits, installs, releases, or activates controlled bytes.

Record each participant's runtime-issued task/session identity, effective
model/effort, permissions, source, and terminal receipt. A label, summary, or
completion sentence is not evidence. Give a read-only agent one bounded,
decision-changing question; parallelize only independent questions. Root
reproduces the union of findings, not a vote.

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
  boundary-level alternative that removes the bypass and reruns affected checks.
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
the request, Root, fixed Executor, owner token, source/ref/worktree, exact grant,
obligations, selected checkpoint, tests, agents, phase, open gates, effects, and
receipt digests. After compaction or resume, read the full plan and reconcile it
with current Git, tests, claims, receipts, agents, and Goal before writing or
claiming completion. A conversation summary, copied handle, or prose cannot
reconstruct authority. Missing or mismatched durable facts fail closed.

## Safety invariants

- Authority: only the exact current grant authorizes writes. Missing, spoofed,
  wrong issuer/destination/lineage/target/scope, or merely delegated authority
  refuses or returns the decision to the user.
- Resource claims: before every write, stage, commit, receipt mutation, or
  authorized effect, acquire or verify every sorted worktree/ref/ledger/output
  key under one owner token; conflict or stale ownership stops.
- Recovery: restore the full current index and exactly one content-addressed
  checkpoint; reconnect only the recorded Executor and never substitute a
  writer.
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
- Cost and effects: every effect keeps its own exact impact, invocation,
  resource claim, separate exact gate plan, and outcome receipt. One current-task
  response may authenticate a content-addressed bundle of bounded model,
  corpus, holdout, and review plans for one candidate and snapshot; any failure,
  drift, or exhausted cap stops. Install, release, marketplace, and activation
  remain separate authorities. Dry-runs cause no effect.

## Review and complete

Project every owned staged, unstaged, and untracked product path into a clean
snapshot. Freeze neutral baseline and candidate identities; Root verifies
manifest equality, the complete risk-based diff inventory, checks, and allowed
control exclusions.

In `exact_final`, one fresh isolated read-only reviewer receives the verbatim
request, frozen source range, accepted failures, checks, and exclusions. Its
receipt binds session, source/config, model/effort, isolation, external reads,
diff and obligation coverage, truncation, findings, and Root reproduction.
Missing coverage, contamination, mismatch, unsupported evidence, or an unchanged
rerun leaves review open. Repair returns to `working`, refreezes, and obtains a
new neutral exact-final.

Enter `closed` only when every obligation is verified or evidenced `N/A`, real
paths pass, baseline failures are resolved or accepted unchanged, no secret or
material finding remains, owned status is accounted for, required effects and
receipts bind the frozen product, and the matching Goal—if any—is complete.
Disclose any explicitly waived or unrun gate.
