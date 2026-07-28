# HappyCodex 0.4.1 ExecPlan

## When to create it

Before research/challenger dispatch, persist a qualifying skeleton at the repository policy path or `docs/execplans/<task-slug>.md`. Native Plan is cursor; Goal explicit.

## Template

Protocol: `HappyCodex/0.4.1`
Invocation: `$happycodex:happycodex`
Writer resources: worktree `<path>`; branch/ref `<ref>`; ledger `<path>`; output `<namespace>`; activation `<target>`; owner `Root`
State: implementation / focused_hardening / candidate_frozen / exact_final / closed
Resume: read this file and reconcile native facts before any write, review, or completion.

### Outcome and baseline

**Operative sources.** Append verbatim user text with anchor/hash; only later verbatim authorization supersedes it. Goal/Outcome divergence stops. A waiver names its gate, exact scope, reopen condition, and unrun gates.

**Amendment.** Change/reason: `<delta>`; Authorization anchor/hash: `<source/digest>`; Affected claims: `<IDs>`; Invalidated evidence: `<IDs/digests>`; Required reruns: `<commands/gates>`.

**Normalized outcome.** Map every source clause to success, preservation, allowed breaks, exclusions, and stops.

**Design saturation.** Record decision-changing options, omission challenge, boundary/rejections, and saturation; omit cosmetic variants.

**Immutable snapshot.** Repository: `<name>`; revision/tree: `<full IDs>`; worktree/status: `<path/status>`; owner: `Root/preserved`; operative baseline: `yes/no`.

For multiple repositories, use a namespaced revision/tree tuple. Disjoint resources may run concurrently; overlap rejects a second writer.

Advance only with quoted authorization; version, rerun, and reopen evidence.

**Baseline check.** Command: `<exact>`; exit: `<code>`; structured failure identities/count: `<IDs/signatures>`; normalized digest: `<digest>`; accepted: `yes/no`.

Freeze checks; candidate failures are not baseline and unaccepted failures stay open. Sanitize sensitive logs.

### Claims Ledger

Use one table. Types are `outcome`, `preservation`, `allowed-break`, and `premise`; states are only `open`, `verified`, or `N/A`; `N/A` requires path, search, or command evidence.

The contract-freeze revision freezes the user contract: sources, Outcome, exclusions,
breaks, and baseline. Add a derived
claim only when entailed by a frozen clause or reachable baseline behavior; record provenance
and reopen evidence. Narrowing, widening a break, `N/A`, or changing Outcome/baseline needs
explicit user authorization.

| ID | Type | Claim | Closure | Falsifier / oracle | Evidence | State |
| --- | --- | --- | --- | --- | --- | --- |
| `<ID>` | `<type>` | `<observable claim>` | `<required proof>` | `<real counterexample>` | `<fresh fact>` | `open` |

Enumerate changed entrypoint, routing, dispatch, selector, configuration, and public-input classes; unclassified stays open.

### Convergence Ledger

Root alone assigns `family_id`; finding schema stays unchanged. Freeze each `repair_batch` after all candidate reviewers are terminal. The six scan surfaces are source/identity,
type/cardinality, order/terminal, alias/mutability/TOCTOU, serialization/replay, and consumers/failure propagation.

| Family | Invariant / boundary | Members | Scan surfaces | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<family_id>` | `<invariant / implementation boundary>` | `<finding IDs>` | `<counterexample / positive / N/A / open per surface>` | `open/closed` | `<batch>` | `<IDs>` | `<count>` |

### Checkpoint

- Milestone / affected obligations / gates / next RED:
- Last green revision/snapshot / checks/digests / freeze:
- Owned dirty paths / preserved user changes:
- Recovery: baseline / writer / milestone / gates / tests / worktree / durable sources / missing facts / handoff:
- Agent: dispatch and terminal IDs/status / revision/tree/dirty state / question/scope/gate/stop / evidence/uncertainty / Root disposition/freshness:
- Review: product-tree / synthetic commits/manifest / task/command/durable output / model/effort/state/digest/scope/limits/counts/dispositions:
- Secret and baseline/candidate finding differential:

This file is a current index: target 8,000 words, hard limit 12,000. Retain frozen
contract, open claims/families, current grant, candidate, valid evidence/invalidation,
and gates; compress closed history to checkpoint, reachable revision/archive, receipt
digest, and invalidation relation. Missing or inconsistent summaries recover along the
chain and fail closed. In no-commit mode use the Skill's reachable snapshot rule; a
writer completion sentence cannot substitute for reachable artifacts.

### Retrospective

Fill only after final completion; record lessons/risks, do not expose it to a reviewer, and never use it as evidence.

## Neutral review brief

`focused_hardening` may see history, families, counterexamples, and repair story but
cannot satisfy final review. `exact_final` is fresh and neutral: Phase 1 receives verbatim
requests/amendments, source and synthetic commits, scope, accepted baseline failures,
objective facts, and exclusions. Exclude the ExecPlan; prove manifest equality. Before
candidate evidence, freeze numbered independent obligations, then inspect every obligation
and diff unit. Missing inventory permits one same-session correction; incomplete correctness stops.

Only then send contract-only sources, Outcome, claims, and oracles; exclude evidence,
decisions, findings, receipts, Retrospective, repair story, and verdict.

## Coverage receipt

Record reviewer/session/command/output, model/effort/permissions, source/synthetic commits,
manifest, units/obligations, queries/evidence/limits/mapping, external reads, contamination,
and Root dispositions. Keep findings in native output; backlog noncontract issues.

Append receipt/closure administratively; prove product-tree identity excluding only the ExecPlan. Product/claim changes reopen evidence.
