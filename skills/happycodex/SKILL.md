---
name: happycodex
description: High-risk cross-system/compaction reliability; resource-scoped writer ownership, durable evidence, fresh review; skip local low-risk edits.
---

# HappyCodex

One owner per shared mutable resource. Record worktree, branch/ref, ledger, output, activation;
disjoint resources may run concurrently, overlap rejects a second writer. Native Plan/approved Goal,
Git/tests, and agents/review execute; HappyCodex adds a durable contract—no controller or Task State
JSON. Authorization permits actions; ExecPlan defines completion; evidence binds a candidate; Goal
controls automatic continuation. Never infer one from another.

## Select the state

- A clearly local, low-risk task uses Native Plan/tests/diff. If it becomes public-contract or
  behavior-changing after edits, establish the ExecPlan before the next product write. Upgrade work
  when it becomes qualifying after edits; unrecoverable true pre-task baseline means stop and ask the user.
- Cross-system/public-contract/migration/persistence/concurrency/destructive/production-cutover/
  exhaustive/compaction-prone or research/multi-session/high-context work qualifies. Uncertainty qualifies.
- After baseline freeze and before extended research, use `references/execplan.md` at the repository
  policy path, else `docs/execplans/<task-slug>.md`. Commit this minimal skeleton immediately before
  investigation or challenger dispatch. If commits are forbidden, apply the no-commit rule; without
  that selection, stop. Freeze later in a separate revision.
- Native Plan is only the current cursor and has no fixed step cap. Guard: “restore the ExecPlan
  before any write, review, or completion.” Native Goal is only an objective pointer requiring
  explicit approval; ask once only if unattended continuation lacks a Goal choice; declining keeps
  Native Plan active. Goal-stop guard: before any wait/stop handoff, if the agent cannot pause an
  Goal, tell the user to run `/goal pause`; `/goal pause` is a mandatory open gate. Natively
  pause active Goal only when no safe in-scope progress remains and a persistent user-decision,
  destructive-action, external-dependency, or cost/complexity wait would repeat wakes/exceed
  authority. Turn end, interrupt, transient platform error, review finding, or remaining independent
  work is not pause; blocked is not pause. Goal wake or resume continues existing authority; it never
  authorizes an amendment, waiver, review, or cost increase. Stop waiting cancels only the current
  wait and does not waive a gate. Goal clear abandons. Read final visible Goal state; reconcile Goal
  and Outcome divergence; mark the matching Goal complete only after every completion gate closes.

## Freeze the contract

Capture verbatim requests/amendments with anchors/hashes; record change/reason, authorization
anchor/hash, affected claims, invalidated evidence, required reruns, normalized Outcome, immutable
repositories/revisions/worktrees/owners, baseline commands/failures, and phase/gates. Never persist a
secret in control/evidence/brief/receipt/log/evaluation artifacts; request redaction. Enumerate
material findings—including Goal/Outcome divergence—by stable identity: baseline-unchanged,
resolved, candidate-new, or unknown; classify current blockers. Unknown remains open; classify by
finding ID, not surrounding text; never omit a baseline finding.

Map each request clause/baseline-reachable class to claims: defaults, boundaries, type semantics,
malformed input, unrelated behavior, callers, residual config/prompts/docs/output, and downstream
consumers. Irrelevance is a positive claim requiring evidence.

Before freeze compare materially distinct, decision-changing designs; challenge omissions and record
boundary/rejections. At requirements-based saturation, when no clearly better option remains, stop;
skip cosmetic variants.

Root traces changed contracts through authoring/input, validation, execution,
persistence/serialization, and user-visible output; search entrypoints, persisted routing,
producers/consumers, configuration/deployment, observability/recovery, migration/rollback, and
reachable legacy bypasses. A scout gets one bounded question changing a named decision/gate: do not
target an Agent count; parallelize only independent questions and serialize dependencies. Launch
every scout/challenger with `fork_turns="none"`—no inherited Root conversation—and a neutral packet:
revision/tree and dirty state, stop condition, read-only scope, no preferred answer. Every scout,
challenger, and reviewer is read-only, never delegates, and gets no duplicate question. For
exhaustive or architecture-shaping claims (all/only/end-to-end/production-ready/replacement/retirement,
including unique), dispatch a fresh baseline-only challenger with the verbatim request and not Root's inventory.

A plan or writer summary that an agent completed is not a receipt. Resolve dispatch identity to a
reachable matching terminal record, evidence, and remaining uncertainty. Root reproduces the union,
not a vote; missing/mismatched stays open.

Root groups finding IDs sharing invariant/boundary into `family_id`; models never generate it. Each
Convergence Ledger family covers the six scan surfaces: source/identity, type/cardinality,
order/terminal, alias/mutability/TOCTOU, serialization/replay, consumers/failure propagation; each
has a counterexample, positive case, evidenced `N/A`, or stays open.

After reproducing the union, freeze before product edits in a distinct contract-freeze revision
carrying `HappyCodex-ExecPlan: <path>`, or selected no-commit location. That revision freezes the user
contract: operative sources, normalized Outcome, exclusions, allowed breaks, and baseline. Root may
monotonically add a derived claim entailed by a frozen clause/baseline-reachable behavior; record
provenance and reopen dependent evidence. Other suggestions enter the external backlog. Removing or
narrowing a claim, widening a break, using `N/A`, or changing Outcome/baseline needs explicit user
authorization. Advance a baseline only with verbatim authorization; version, rerun, reopen.

## Implement and recover

Use `implementation → focused_hardening → candidate_frozen → exact_final → closed`.
All reviewers reach terminal before Root reproduces/unions findings and freezes `repair_batch`.
Ledger grammar: `Status: open | boundary_required | closed` and
`Repair batch: <id>/instance | <id>/boundary`. Never run exact-final mid-batch.

A terminal GREEN repair wave requires a frozen batch, six disposed surfaces, focused/cumulative
GREEN, and durable revision/evidence. Before terminal GREEN, a same-family sibling joins with RED
coverage and expanded authority, without recurrence. After it, a Root-confirmed same-family material
finding or credible safety/data-integrity `unknown` increments recurrence whether or not the family
was closed; rejected, impossible, or non-material findings do not.

First recurrence sets `boundary_required`: only boundary repair writes; establish a unique
authoritative choke point, delete bypasses, rescan six surfaces. After boundary GREEN run exactly one
history-aware focused choke-point-bypass falsification. Infrastructure failure/reviewer contamination
is replaced without consuming it; product change invalidates it. GO closes. A second recurrence
after boundary repair stops for user choice: expand refactor, change contract, or abandon. A new
independent family gets an instance batch without incrementing another.

During RED/repair/reconciliation, review mode is none and authorized writes may proceed. When focused
review is the stable wave's sole gate, writes stop and review mode is focused_hardening.
`stop_for_user` permits neither; exact-final forbids writes and uses `exact_final`. Candidate freeze
requires closed families, no write/reconciliation, focused review without a new material family, and
cumulative GREEN.

Per vertical slice, observe RED or justify characterization; make a coherent change with
real-path/state-transition oracles—a mock cannot prove its seam; map tests and compatibility
counterexamples to affected obligations/gates; run focused/cumulative checks, inspect preservation,
persist evidence, and retain a semantic revision/snapshot. At each risk-bearing milestone run a
bounded correctness gate; do not run a full reviewer after every revision. Focused reviewers may see
history, ledgers, counterexamples, and repair story but never replace final review. Focused
hardening defaults to `high`; use `max` only for a recurring family or unresolved material
uncertainty. Exact-final remains `max`. Run full
final-candidate review only after cumulative checks and source freeze.

Before product writes, `scripts/resource_claim.py` acquires sorted keys: Git uses common-dir CAS;
file/output/ledger/activation uses adjacent atomic directories. All must succeed; verify owner token
before every write. Conflict, unwritable, or stale/unknown stops without auto-release. Disjoint
resources may run.

If commits are forbidden, require a user-selected durable location; without that selection, stop.
Leave the index untouched; retain skeleton, freeze, every green slice, and closure in a reachable
private Git ref or approved content-addressed archive. Record revisions/owned dirty paths; a
garbage-collectable object ID or writer completion sentence cannot substitute. Unclassified input
stays open.

The ExecPlan is a current index: target 8,000 words, hard limit 12,000 words. Keep contract, open
claims/families, grant, candidate, evidence/invalidation, and gates; compress closure to checkpoint,
revision/archive, receipt digest, and invalidation. Missing/tampered summaries fail closed.

After compaction, find the plan by guard, semantic commit trailer, or unique task-owned 0.4.1
ExecPlan; read fully before writing. Reconstruct baseline, writer ownership, current milestone,
pending gates, test status, and worktree; reconcile Goal, Git, checks, receipts, agents. Existing
`marker_ids` bind a content-addressed Recovery Manifest: namespaced revision/tree tuples, claims, one
selected ref/archive, writer, tests, agents, gates, phase, family status, batch, recurrence. Recover
the current index and exactly one authoritative checkpoint, never unbounded history. Unknown
writer/worktree, missing agent, unreproduced receipt, unaccepted failure, or summary mismatch fails
closed. Facts win; ask the user for the missing material fact only when durable sources cannot
recover it. Resume of the same task requires post-resume reads from ExecPlan, Git, tests, and
live-agent facts; conversation summary, live handle, or prose claim supplies none. Maintainer
evaluation, not each user task, proves native compaction and summary-independent reconstruction.

0.4.1 accepts fresh genesis plus refreshed coverage or an exact waiver: no prior reader/disposition,
migration, alias, dual write, incremental certification, controller, Task State JSON, or Evidence
DAG. After closure, a new independent Outcome or baseline uses a new task and ExecPlan (Goal only if
requested); an in-contract repair stays in the current task.

## Review the exact product

Commit task changes or project every owned staged, unstaged, and untracked path into a clean review
snapshot. Freeze source baseline/candidate IDs; build two neutral commits from complete product
snapshots; exclude only the sole ExecPlan; prove manifest equality and a complete diff-unit inventory.
The source range is authoritative. Freeze the Git product tree, review configuration, and review
toolchain; namespace repositories identically and keep changed submodules open until included.

Any product-source change returns to focused_hardening and invalidates candidate evidence and
all exact-final reviews. Before launch persist command, candidate identity, review mode, and durable
output. A foreground buffer is not a receipt; after interruption, resolve its durable terminal
record before rerun.

Exact-final reviewers must not see the Convergence Ledger, historical findings, counterexamples,
repair story, or preferred verdict. Run dedicated native `codex review` in the same fresh reviewer
session. It inherits the configured model; if unset, prefer `gpt-5.6-sol`. Request `max` and the
strongest user/environment-authorized read-only profile; `ultra` requires explicit authorization.
Keep selector flags separate from the stdin brief; disclose downgrades/reroutes. Phase 1 gets
verbatim user text, scope, accepted baseline failures, objective verification facts, and explicit
exclusions. Before candidate evidence it emits stable numbered obligation IDs and text; Root hashes
them. Contract-hidden, it runs correctness/adversarial checks for every independent obligation and
diff unit. If inventory is absent, do not reveal the contract; allow one same-session receipt-only
correction. Incomplete correctness stops. Only then reveal the contract-only projection and map its
independent inventory both ways. Exclude evidence, decisions, receipts, Retrospective, findings,
writer narrative, prior findings, verdict, original Git metadata/worktree, and Root conversation.
Declared dependency reads require purpose/digest.

Require receipt identity/status, configured-model source, effective model/effort/permissions,
network/write access, authorization/degradation, every diff unit/obligation, queries/counts,
paths, external reads, evidence, limits, and mapping. Detailed findings stay in the native review
output; ExecPlan keeps digests/counts/limits/dispositions. Missing units, truncation, mismatch,
contamination, or unsupported evidence leaves review open; split correctness but keep a repository
completeness pass. A fresh detached Desktop review substitutes only with identical source range,
isolation, neutral brief, model/effort disclosure, and complete receipt.

The review product-tree identity excludes the ExecPlan. Append closure in one administrative closure
revision or no-commit snapshot; prove the product tree is unchanged. Any product change invalidates
review; a material evidence-only change invalidates affected review evidence; contract changes reopen
dependent evidence. Only explicit user text waives a named gate. Record the exact waiver scope;
outside that scope reopens the gate, and completion must disclose every unrun gate.

A finding blocks only if it may violate the original request or frozen acceptance, behavior proven by
the last accepted receipt, safety or data integrity, a production condition, or exhaustive
replacement or retirement. Root marks confirmed/rejected/unresolved, records rejected
counter-evidence, sends noncontract issues to an external backlog, and stops on unresolved material findings. Disputed
classification or repeated repaired-case failure stops for the user. Before repair/rerun identify
the minimally invalidated behavior/review/holdout receipts, expected rerun cost, and any required
user decision. Repair, refresh required evidence, and start a fresh neutral full-scope review. There
is no fixed review-count quota; never rerun an unchanged candidate or shop for a verdict.

An explicitly requested external reviewer independently gets the same synthetic scope and neutral
brief. Selection is task-scoped and asked once. “Look” is advisory-once unless policy requires an
exact-final gate; candidate change retires advisory GO; required review reruns on convergence.
Evidence requires the runtime-issued command/session/effective-model receipt; an agent or task name
never proves reviewer identity. Exact selections win; otherwise Fable 5 defaults to `max`.
Unavailable: a required review stops; `when available` continues with one disclosed skip. Union
findings without voting; Root reproduces them. Never downgrade, substitute, install, enable, or
search for it.

## Complete honestly

Complete only when every claim is verified or evidence-backed `N/A` and real-path checks pass.
Baseline failures are resolved or explicitly accepted and unchanged; an unaccepted baseline failure
blocks. No new product-tree secret finding exists; disclose a pre-existing finding. Account for
agents, worktrees, dirty paths, diff units, receipts, production/retirement gates, and clean tree. A
candidate failure cannot be relabeled as baseline.
