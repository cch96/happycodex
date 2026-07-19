# HappyCodex 0.4 clean-break certification engine

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: skeleton
Resume: read this entire ExecPlan and reconcile Goal, Native Plan, Git, tests,
receipts, worktrees, and agents before any write, review, or completion claim.

## Operative sources

Source: current task, direct user messages. Exact combined-block SHA-256 is pending
the contract-freeze revision.

<!-- operative-source-begin -->
好的，下一步优化什么0.4版本什么优化

fable 暂时不管，其他你看看怎么优化，如果考虑重构不考虑兼容收益高买

好的你看看有没有遗漏，没有的话定义goal 然后执行
<!-- operative-source-end -->

## Normalized Outcome

Deliver a local HappyCodex 0.4 candidate that clean-breaks the internal
evaluation/receipt/result compatibility surface into a modular, deterministic
certification engine. Separate semantic, harness, and artifact identities; provide a
read-only impact planner that identifies exact rerun gates and costs; remove legacy
v1-v20 result/test compatibility; and keep the installed Runtime behavior and public
`$happycodex:happycodex` invocation stable.

Fable is excluded from this Outcome. No controller, hook, daemon, scheduler, MCP/app
runtime, authoritative Task State JSON, or automatic external publication is in
scope. Any live model corpus or holdout requires a persisted cost estimate and an
explicit user cost decision before launch.

## Immutable starting snapshot

| Item | Value |
| --- | --- |
| Repository | `/home/caichenghang/projects/happycodex` |
| Baseline branch | `main` |
| Baseline revision | `2836d7363db364807a2ec384dc1b6c2cc13df95e` |
| Baseline remote | `origin/main` at the same revision |
| Work branch | `feat/happycodex-0.4-certification-engine` |
| Starting worktree | clean |
| Writer | Root only |
| Goal | pending omission challenge, then explicitly requested creation |
| Accepted baseline failures | none yet; reproduce before freeze |

## Initial boundary and findings

- Internal compatibility may break for evaluator modules, CLI commands, receipt
  schemas, historical result layout, and version-specific tests.
- Public install commands, plugin identity, Skill invocation, and core Runtime
  semantics remain preservation claims unless the user explicitly widens the break.
- `AGENTS.md` still describes public/active 0.2 and a required Fable release gate.
  This is baseline policy drift after the completed 0.3 release and must be resolved
  for 0.4 without reclassifying it as a product failure.
- Current evaluation input identity binds the entire monolithic runner bytes, so a
  metadata-only implementation edit invalidates every model receipt. This is the
  primary defect class.
- Raw model outputs remain external; only sanitized, secret-free summaries and
  content identities may enter the repository.

## Initial claims

| ID | Type | Claim | Closure / falsifier | State |
| --- | --- | --- | --- | --- |
| O-01 | outcome | A modular pure-standard-library certification engine replaces the monolithic internal evaluator without legacy internal compatibility. | Module/CLI inventory plus tests; legacy reader or dual-write path falsifies. | open |
| O-02 | outcome | Canonical receipts separate semantic input, harness implementation, and derived artifact identities. | Deterministic hash tests and mutation counterexamples. | open |
| O-03 | outcome | A read-only impact command reports exact invalidated gates, reasons, and live-run count/cost before execution. | Table-driven dependency tests; an unclassified material input change falsifies. | open |
| O-04 | outcome | Historical behavior v1-v20 files and version-specific compatibility tests leave the active tree while remaining reachable in Git history. | Final path inventory and ancestry proof. | open |
| O-05 | preservation | Installed Skill behavior, plugin identity, public install commands, and `$happycodex:happycodex` invocation remain stable except the intentional 0.4 version/change note. | Exact runtime diff and contract tests. | open |
| O-06 | outcome | Maintainer policy describes current public 0.3 baseline, the 0.4 gate model, and this task's explicit Fable exclusion correctly. | Policy review and tests. | open |
| O-07 | outcome | Offline suite, official Skill/plugin validators, dry-runs, diff hygiene, and final fresh native review close with no unresolved blocker. | Exact command receipts and review coverage. | open |
| O-08 | preservation | No Fable invocation, controller, hook, daemon, scheduler, MCP/app runtime, or authoritative Task State JSON is added or run. | Tree/command inventory. | open |
| B-01 | allowed-break | Internal evaluator imports, CLI syntax, receipt/result schema, and historical result paths have no backward-compatibility obligation. | Any compatibility shim must be removed or separately authorized. | open |
| P-01 | premise | Baseline and branch identities above are exact and the starting worktree is clean. | Git receipts. | open |

## Design saturation

Pending a fresh baseline-only architecture challenger and Root reproduction. Compare
at least: in-place modularization with compatibility, clean-break modular engine,
and Runtime/controller expansion. Freeze only after no decision-changing omission
remains.

## Validation envelope

Baseline and candidate offline commands, exact live-run costs, required reruns, and
review launch records will be frozen before their respective actions. Fable is not a
gate for this task. External push, PR, active-plugin mutation, or release publication
requires a later explicit user request.

## Checkpoint

- Milestone: skeleton before omission challenger.
- Next: commit skeleton, dispatch fresh baseline-only architecture challenge, reproduce
  the union, define/create Goal, run baselines, and freeze the contract.
- Product writes: closed until contract-freeze revision.
- Owned paths: this ExecPlan only.
- Missing facts: baseline command results, exact module/API design, live evaluation
  cost estimate, final version cachebuster, and review identities.

## Retrospective

Fill only after every completion gate closes.
