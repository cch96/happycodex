---
name: happycodex
description: High-risk cross-system/compaction reliability; one fixed Executor writes, Root decides and verifies, durable evidence, fresh review; skip local low-risk edits.
---

# HappyCodex

One fixed Executor is the sole writer. Root reads, decides, grants, reproduces,
and verifies; Explorer, Challenger, and reviewer are read-only. Record the fixed Executor thread,
worktree, branch/ref, ledger, output, and activation. Native Plan/approved Goal, Git/tests, and
agents/review execute; HappyCodex adds a durable contract—no controller or Task State JSON.
Authorization permits actions; ExecPlan defines completion; evidence binds a candidate; Goal controls
automatic continuation. Never infer one from another.

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

Root defines and the fixed Executor persists verbatim requests/amendments with anchors/hashes under
an exact write grant; record change/reason, authorization anchor/hash, affected claims, invalidated
evidence, required reruns, normalized Outcome, immutable
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

Root decision and reproduction require effective `gpt-5.6-sol` at `max`. Pin each dispatch by
explicit spawn settings or a verified custom-agent profile and retain its effective receipt:
Explorer is `gpt-5.6-terra` at `high`; Challenger is `gpt-5.6-sol` at `high`; the fixed Executor is
`gpt-5.6-sol` at `high`. A role label is not proof. If the host cannot bind and report the exact
model/effort, use an exact fresh `codex exec` session or stop before a product write; never silently
inherit, reroute, or substitute.

Root traces changed contracts through authoring/input, validation, execution,
persistence/serialization, and user-visible output; search entrypoints, persisted routing,
producers/consumers, configuration/deployment, observability/recovery, migration/rollback, and
reachable legacy bypasses. An Explorer gets one bounded question changing a named decision/gate:
do not target an Agent count; parallelize only independent read questions and serialize dependencies.
Launch every Explorer/Challenger with `fork_turns="none"`—no inherited Root conversation—and a
neutral packet: revision/tree and dirty state, stop condition, read-only scope, no preferred answer.
Every Explorer, Challenger, and reviewer is read-only, never delegates, and gets no duplicate
question. For exhaustive or architecture-shaping claims
(all/only/end-to-end/production-ready/replacement/retirement, including unique), dispatch a fresh
baseline-only Challenger with the verbatim request and not Root's inventory.

A plan or writer summary that an agent completed is not a receipt. Resolve dispatch identity to a
reachable matching terminal record, evidence, and remaining uncertainty. Root reproduces the union,
not a vote; missing/mismatched stays open.

Root groups finding IDs sharing invariant/boundary into `family_id`; models never generate it. Each
Convergence Ledger family covers the six scan surfaces: source/identity, type/cardinality,
order/terminal, alias/mutability/TOCTOU, serialization/replay, consumers/failure propagation; each
has a counterexample, positive case, evidenced `N/A`, or stays open.

After reproducing the union, Root grants the fixed Executor creation of a distinct contract-freeze
revision before product edits, carrying `HappyCodex-ExecPlan: <path>`, or selected no-commit location.
That revision freezes the user contract: operative sources, normalized Outcome, exclusions, allowed
breaks, and baseline. Root may
monotonically add a derived claim entailed by a frozen clause/baseline-reachable behavior; record
provenance and reopen dependent evidence. Other suggestions enter the external backlog. Removing or
narrowing a claim, widening a break, using `N/A`, or changing Outcome/baseline needs explicit user
authorization. Advance a baseline only with verbatim authorization; version, rerun, reopen.

## Implement and recover

Use `implementation → focused_hardening → candidate_frozen → exact_final → closed`.
Root selects one Executor thread before the first write and records its thread/session identity,
effective model/effort, worktree, and owner token. That same Executor persists the ExecPlan, tests,
product, commits, and closure; it never delegates. Root never edits, stages, commits, installs, or
activates product/control bytes. Each write grant binds exact paths/resources, prestate, permitted
operations, acceptance, and stop conditions; changed prestate or scope returns to Root.
All reviewers reach terminal before Root reproduces/unions findings and freezes `repair_batch`.
Ledger grammar: `Status: open | boundary_required | closed` and
`Repair batch: <id>/instance | <id>/boundary`. Never run exact-final mid-batch.

A terminal GREEN repair wave requires a frozen batch, six disposed surfaces, focused/cumulative
GREEN, and durable revision/evidence. Before terminal GREEN, a same-family sibling joins with RED
coverage and expanded authority, without recurrence. After it, a Root-confirmed same-family material
finding or credible safety/data-integrity `unknown` increments recurrence whether or not the family
was closed; rejected, impossible, or non-material findings do not.

First recurrence sets `boundary_required`: Root grants only the Executor boundary repair writes;
establish a unique authoritative choke point, delete bypasses, rescan six surfaces. After boundary
GREEN run exactly one
history-aware focused choke-point-bypass falsification. Infrastructure failure/reviewer contamination
is replaced without consuming it; product change invalidates it. GO closes. A second recurrence
after boundary repair stops for user choice: expand refactor, change contract, or abandon. A new
independent family gets an instance batch without incrementing another.

During RED/repair/reconciliation, review mode is none and Executor writes may proceed only under the
current grant. When focused review is the stable wave's sole gate, writes stop and review mode is
focused_hardening.
`stop_for_user` permits neither; exact-final forbids writes and uses `exact_final`. Candidate freeze
requires closed families, no write/reconciliation, focused review without a new material family, and
cumulative GREEN.

Per vertical slice, Executor observes RED or justifies characterization, then makes a coherent
granted change with real-path/state-transition oracles—a mock cannot prove its seam; map tests and compatibility
counterexamples to affected obligations/gates; run focused/cumulative checks and return exact
diff/check receipts. Root independently inspects preservation and prestate, then grants persistence
of evidence and a semantic revision/snapshot. At each risk-bearing milestone run a
bounded correctness gate; do not run a full reviewer after every revision. Focused reviewers may see
history, ledgers, counterexamples, and repair story but never replace final review. Focused
Challengers remain `gpt-5.6-sol` at `high`; Root uses `max` for recurring or unresolved material
uncertainty. Exact-final remains `gpt-5.6-sol` at `max`. Run full
final-candidate review only after cumulative checks and source freeze.

Before every write grant, the Executor uses `scripts/resource_claim.py` to acquire all sorted keys:
Git uses common-dir CAS; file/output/ledger/activation uses adjacent atomic directories. All must
succeed; verify the fixed owner token before every write. Conflict, unwritable, stale/unknown, or a
second writer stops without auto-release. Read-only work on disjoint resources may run concurrently.

If commits are forbidden, require a user-selected durable location; without that selection, stop.
Executor leaves the index untouched and retains skeleton, freeze, every green slice, and closure in
a reachable private Git ref or approved content-addressed archive. Root verifies revisions/owned
dirty paths; a garbage-collectable object ID or writer completion sentence cannot substitute. Unclassified input
stays open.

The ExecPlan is a current index: target 8,000 words, hard limit 12,000 words. Keep contract, open
claims/families, grant, candidate, evidence/invalidation, and gates; compress closure to checkpoint,
revision/archive, receipt digest, and invalidation. Missing/tampered summaries fail closed.

After compaction, find the plan by guard, semantic commit trailer, or unique task-owned 0.5 ExecPlan;
read fully before granting or writing. Reconstruct baseline, fixed Executor identity and ownership,
current milestone, pending gates, test status, and worktree; reconcile Goal, Git, checks, receipts, agents. Existing
`marker_ids` bind a content-addressed Recovery Manifest: namespaced revision/tree tuples, claims, one
selected ref/archive, writer, tests, agents, gates, phase, family status, batch, recurrence. Recover
the current index and exactly one authoritative checkpoint, never unbounded history. Unknown
writer/worktree, missing fixed Executor, unreproduced receipt, unaccepted failure, or summary
mismatch fails closed. Reconnect only the recorded Executor; never replace it with a second writer.
Facts win; ask the user for the missing material fact only when durable sources cannot recover it.
Resume of the same task requires post-resume reads from ExecPlan, Git, tests, and live-agent facts;
conversation summary, live handle, or prose claim supplies none. Maintainer
evaluation, not each user task, proves native compaction and summary-independent reconstruction.

0.5 starts from the exact 0.4.2 contract with no compatibility reader, migration, alias, dual write,
controller, Task State JSON, or Evidence DAG. After closure, a new independent Outcome or baseline
uses a new task and ExecPlan (Goal only if requested); an in-contract repair stays in the current
task.

## Review the exact product

Executor projects every owned staged, unstaged, and untracked path into a clean review snapshot
under Root's grant. Executor freezes baseline/candidate as two neutral product commits; Root proves
manifest equality and a complete diff-unit inventory and excludes only the sole ExecPlan. The source
range is authoritative; include changed submodules.

Any product-source change returns to focused_hardening and invalidates candidate evidence and
exact-final review. Before launch persist command, candidate, mode, and durable output. A foreground buffer
is not a receipt; after interruption resolve its durable terminal record.

Exact-final reviewers must not see the Convergence Ledger, historical findings, counterexamples,
repair story, or preferred verdict. Run dedicated native `codex review` in one fresh isolated
read-only session pinned to `gpt-5.6-sol` at `max`; the same model is allowed, the Root or Executor
session is not. Keep selector flags separate from the stdin brief; any downgrade/reroute leaves the
gate open. Give it verbatim user text, exact source range, accepted baseline failures, objective
checks, and exclusions; exclude the ledger, evidence, conclusions, writer narrative, original Git
metadata/worktree, and Root conversation. Dependency reads require purpose and digest.

Require a runtime-issued receipt binding session, source/config, exact model/effort/permissions,
write/network access, diff-unit/obligation coverage, external reads, limits, and findings. Missing
units, truncation, mismatch, contamination, or unsupported evidence leaves review open. A detached
Desktop review substitutes only with the same source, isolation, neutral brief, and receipt; a role
name never proves identity.

The review product-tree identity excludes the ExecPlan. Root grants Executor one administrative
closure revision or no-commit snapshot and proves the product tree is unchanged. Any product change
invalidates review; a material evidence-only change invalidates affected review evidence; contract
changes reopen dependent evidence. Only explicit user text waives a named gate. Record the exact
waiver scope; outside that scope reopens the gate, and completion must disclose every unrun gate.

A finding blocks only if it may violate the original request or frozen acceptance, behavior proven by
the last accepted receipt, safety or data integrity, a production condition, or exhaustive
replacement or retirement. Root marks confirmed/rejected/unresolved, records rejected
counter-evidence, sends noncontract issues to an external backlog, and stops on unresolved material findings. Disputed
classification or repeated repaired-case failure stops for the user. Before repair/rerun identify
the minimally invalidated behavior/review/holdout receipts, expected rerun cost, and any required
user decision. Repair, refresh required evidence, and start a fresh neutral full-scope review. There
is no fixed review-count quota; never rerun an unchanged candidate or shop for a verdict.

## Complete honestly

Complete only when every claim is verified or evidence-backed `N/A` and real-path checks pass.
Baseline failures are resolved or explicitly accepted and unchanged; an unaccepted baseline failure
blocks. No new product-tree secret finding exists; disclose a pre-existing finding. Account for
agents, worktrees, dirty paths, diff units, receipts, production/retirement gates, and clean tree. A
candidate failure cannot be relabeled as baseline.
