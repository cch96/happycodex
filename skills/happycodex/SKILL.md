---
name: happycodex
description: High-risk cross-system/compaction reliability; one writer, durable evidence, fresh review; skip local low-risk edits.
---

# HappyCodex

Root is the only writer. Native Plan/approved Goal, Git/tests, and agents/review execute;
HappyCodex adds only a durable contract—no controller or Task State JSON.
Authorization permits actions; ExecPlan defines completion; evidence binds a candidate;
Goal controls automatic continuation. Never infer one from another.

## Select the state

- A clearly local, low-risk task uses Native Plan/tests/diff. If it becomes public-contract or
  behavior-changing after edits, it is qualifying: establish the ExecPlan before the next product
  write. Upgrade other work when it becomes qualifying after edits; unrecoverable true pre-task
  baseline means stop and ask the user.
- Cross-system/public-contract/migration/persistence/concurrency/destructive/production-cutover/
  exhaustive/compaction-prone work qualifies; research/edit-heavy/multi-session/high-context does
  too. Uncertainty qualifies.
- After baseline freeze and before extended research, use `references/execplan.md` at the repository
  policy path, else `docs/execplans/<task-slug>.md`. Commit this minimal skeleton immediately before
  investigation or challenger dispatch. If commits are forbidden, apply the no-commit rule;
  without that selection, stop. Freeze later in a separate revision.
- Native Plan is only the current cursor and has no fixed step cap. Guard: “restore the
  ExecPlan before any write, review, or completion.” Native Goal is only an objective pointer
  requiring explicit approval; ask once only if unattended continuation lacks a Goal choice.
  Declining keeps Native Plan active.
  Goal-stop guard: before any wait/stop handoff, if the agent cannot pause an active Goal,
  tell the user to run `/goal pause`; `/goal pause` is a mandatory open gate. Natively
  pause active Goal only when no safe in-scope progress remains and a persistent
  user-decision, destructive-action, external-dependency, or cost/complexity wait
  would repeat wakes/exceed authority. Turn end, interrupt,
  transient platform error, review finding, or remaining independent work is not pause;
  blocked is not pause. Goal wake or resume continues existing authority; it never authorizes an
  amendment, waiver, review, or cost increase. Stop waiting cancels only the current wait
  and does not waive a gate. Goal clear abandons. Read final visible Goal state; if Goal and
  Outcome diverge, reconcile; mark the matching Goal complete only after every completion gate closes.

## Freeze the contract

Capture verbatim operative requests/amendments with anchors/hashes. Record change/reason,
authorization anchor/hash, affected claims, invalidated evidence, required reruns, normalized
Outcome, immutable repositories/revisions/worktrees/owners, exact baseline commands, accepted
failures, and phase/gates. Never persist a secret in control/evidence/brief/receipt/log/evaluation
artifacts; request redaction. Enumerate material findings—including Goal/Outcome divergence—by stable identity:
baseline-unchanged, resolved, candidate-new, or unknown; classify current blockers. Unknown remains open; classify by finding
ID, not surrounding text; never omit a baseline finding.

Map each material request clause/baseline-reachable behavior class to typed claims: defaults,
boundaries, type semantics, malformed input, unrelated behavior, established callers, residual
config/prompts/docs/generated output, and downstream consumers. Irrelevance is a positive claim
requiring evidence.

Before freeze compare materially distinct, decision-changing designs; challenge omissions and
record boundary/rejections. At requirements-based saturation, when no clearly better option remains,
stop; skip cosmetic variants.

Root traces every changed contract through authoring/input, validation, execution,
persistence/serialization, and user-visible output; then searches entrypoints, persisted routing,
producers/consumers, workers, configuration/deployment, observability/recovery, migration/rollback,
and reachable legacy bypasses. A scout gets one bounded question that can change a named decision/gate:
do not target an Agent count; parallelize only independent questions and serialize dependencies.
Launch every scout/challenger with `fork_turns="none"`—no inherited Root conversation—and a neutral
packet: revision/tree and dirty state, stop condition, read-only scope, no preferred answer. Every
scout, challenger, and reviewer is read-only, never delegates, and gets no duplicate question. For
exhaustive or architecture-shaping claims (all/only/end-to-end/production-ready/replacement/retirement,
including unique), dispatch a fresh baseline-only challenger with the verbatim request and not Root's
inventory.

A plan or writer summary that an agent completed is not a receipt. Resolve pre-edit dispatch identity
to a reachable matching terminal record, new evidence, and remaining uncertainty. Root reproduces
the union, not a vote; missing/mismatched stays open.

After reproducing the union, freeze before production edits in a distinct contract-freeze revision
carrying `HappyCodex-ExecPlan: <path>`, or selected no-commit location. That revision freezes the user
contract: operative sources, normalized Outcome, exclusions, allowed breaks, and baseline. Root may
monotonically add a derived claim entailed by a frozen clause/baseline-reachable behavior; record
provenance and reopen dependent evidence. Send other suggestions to the external backlog. Removing
or narrowing a claim, widening a break, using `N/A`, or changing Outcome/baseline needs explicit user
authorization. Advance a baseline only with verbatim authorization; version, rerun, reopen.

## Implement and recover

For each vertical behavior slice:

1. Observe the smallest meaningful RED; if unsafe/impractical/weaker than characterization, record
   why and use the strongest baseline/candidate contrast.
2. Make the smallest coherent change; use real-path/state-transition oracles—a mock cannot prove its seam.
3. Map tests and compatibility counterexamples to affected obligations/gates; run focused/cumulative checks,
   inspect path/diff/preservation, update evidence/checkpoint, then make a semantic revision with the trailer
   above or retain a snapshot below.

At each risk-bearing milestone run a bounded correctness gate; do not run a full reviewer after every
revision. Run the full final-candidate review only after cumulative checks.

If commits are forbidden, require a user-selected durable location; without that selection, stop.
Leave the index untouched; retain skeleton, freeze, every green slice, and closure in a reachable
private Git ref or approved content-addressed archive. Record revisions/owned dirty paths; a
garbage-collectable object ID is insufficient. Unclassified final-diff input stays open.

After compaction/resume, find the plan by guard, semantic commit trailer, or unique task-owned 0.3
ExecPlan; read it fully before writing. Reconstruct baseline, writer ownership, current milestone,
pending gates, test status, and worktree; reconcile Goal, Git, checks, review receipts, and live-agent
state. Facts win; uncertain Outcome, modified paths, missing agent, or gates stay open. Ask the user
for the missing material fact when durable sources cannot recover it. After native compaction,
resume of the same task requires post-resume reads from ExecPlan, Git, tests, and live-agent facts;
a conversation summary, live handle, or prose claim cannot supply a fact. Maintainer evaluation,
not each user task, separately proves native compaction and summary-independent reconstruction.

After closure, a new independent Outcome or baseline uses a new task and ExecPlan, with Goal only
if explicitly requested; an in-contract repair stays in the current task.

## Review the exact product

Commit task changes or project every owned staged, unstaged, and untracked path into a clean review
snapshot. Freeze source baseline/candidate IDs; build two neutral commits from complete product
snapshots; exclude only the sole ExecPlan; prove manifest equality and a complete diff-unit inventory.
The source range is authoritative. Namespace repositories identically; include changed submodules or
keep the gate open.

Before reviewer launch persist its command, candidate identity, and durable output destination. A
foreground buffer is not a receipt; after interruption, resolve its durable terminal record before rerun.

Run dedicated native `codex review` in the same fresh reviewer session. It inherits the configured
model; if unset, prefer `gpt-5.6-sol`. Request `max` and the strongest user/environment-authorized
read-only profile; `ultra` requires explicit authorization. Keep selector flags separate from the
stdin brief; disclose downgrades/reroutes. Phase 1 gets verbatim user text, scope, accepted baseline
failures, objective verification facts, and explicit exclusions. Before candidate evidence it emits
stable numbered obligation IDs and text; Root hashes them. Contract-hidden, it runs
correctness/adversarial checks for every independent obligation and diff unit. If inventory is
absent, do not reveal the contract; allow one same-session receipt-only correction. Incomplete
correctness stops. Only then reveal the contract-only projection and map its independent inventory
both ways. Exclude evidence, decisions, receipts, Retrospective, findings, writer narrative, prior
findings, verdict, original Git metadata/worktree, and Root conversation. Declared dependency reads
require purpose/digest.

Require receipt identity/status, configured-model source, effective model/effort, effective permission
profile/network/write access, authorization/degradation, every diff unit/obligation, queries/counts,
paths, external reads, evidence, limitations, and mapping. Detailed findings stay in the native review output;
ExecPlan stores identity/scope/digests/counts/limitations/dispositions. Root reproduces them. A missing
diff unit, truncation, mismatch, contamination, or unsupported evidence leaves review open; split
correctness but keep a repository completeness pass. A fresh detached Desktop review substitutes
only with the same source range, isolation, neutral brief, model/effort disclosure, and complete receipt.

The review product-tree identity excludes the ExecPlan. Append receipts/closure in one administrative
closure revision or no-commit snapshot; prove the product tree is unchanged. Any product change
invalidates review; a material evidence-only change invalidates affected review evidence; contract
changes reopen dependent evidence. Only explicit user text waives a named
gate. Record the exact waiver scope; a candidate or contract outside that scope reopens the gate, and
completion must disclose every unrun gate.

A finding blocks only if it may violate the original request or frozen acceptance, behavior proven by
the last accepted receipt, safety or data integrity, a production condition, or exhaustive replacement
or retirement; labels do not decide and zero findings are unnecessary. Root marks it
confirmed/rejected/unresolved, records rejected counter-evidence, sends noncontract issues to an
external backlog, and stops on unresolved material findings. Disputed classification or repeated
repaired-case failure stops for the user. Before repair or rerun, identify the minimally invalidated
behavior/review/holdout receipts, expected rerun cost, and any required user decision; stop when needed.
Repair defects, refresh only required evidence, and start a fresh neutral full-scope review. There is
no fixed review-count quota; never rerun an unchanged candidate or shop for a verdict.

An explicitly requested external reviewer independently gets the same synthetic scope and neutral
brief. Selection is task-scoped and asked once. “Look” is advisory-once unless user/scoped policy
requires an exact-final gate; candidate change retires advisory GO; required exact-final review
reruns on convergence without new permission. Evidence
requires the runtime-issued command/session/effective-model receipt; an agent or task name never
proves reviewer identity. Exact selections win; otherwise Fable 5 defaults to `max`. Unavailable: a
required review stops; `when available` continues with one disclosed skip. Union findings without
voting; Root reproduces them. Never downgrade, substitute, install, enable, or search for it.

## Complete honestly

Complete only when every claim is verified or evidence-backed `N/A` and real-path checks pass.
Baseline failures are resolved or explicitly accepted and unchanged; an unaccepted baseline failure
blocks. No new product-tree secret finding exists; disclose a pre-existing finding. Account for
agents, worktrees, dirty paths, diff units, receipts, production/retirement gates, and clean final
tree. A candidate failure cannot be relabeled as baseline.
