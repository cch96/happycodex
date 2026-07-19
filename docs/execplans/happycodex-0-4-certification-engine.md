# HappyCodex 0.4 clean-break certification engine

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: offline candidate; fresh review and live-cost decision pending
Resume: read this entire ExecPlan and reconcile Goal, Native Plan, Git, tests,
receipts, worktrees, and agents before any write, review, or completion claim.

## Operative sources

Source: current task, direct user messages. Exact combined-block SHA-256:
`4ba241dce163c16a6b46b9c02cedb37f6a2be3567454d80dec1589da519302a6`.

<!-- operative-source-begin -->
好的，下一步优化什么0.4版本什么优化

fable 暂时不管，其他你看看怎么优化，如果考虑重构不考虑兼容收益高买

好的你看看有没有遗漏，没有的话定义goal 然后执行
<!-- operative-source-end -->

## Normalized Outcome

Deliver a local HappyCodex 0.4 certification-engine candidate that clean-breaks the internal
evaluation/receipt/result compatibility surface into a modular, deterministic
certification engine. Separate semantic, harness, and artifact identities; provide a
read-only impact planner that identifies exact rerun gates and costs; remove legacy
v1-v20 result/test compatibility; and keep every shipped-package byte, installed
Runtime behavior, and public `$happycodex:happycodex` invocation stable during this
offline phase.

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
| Goal | active `019f780e-925e-7193-8bd2-0a04d6efe31e` |
| Accepted baseline failures | none |

## Initial boundary and findings

- Internal compatibility may break for evaluator modules, CLI commands, receipt
  schemas, historical result layout, raw-result filenames, write ordering, stdout,
  exit codes, and version-specific tests. There will be no legacy reader, alias,
  dual-write, migration, or compatibility field.
- Public install commands, plugin identity, Skill invocation, core Runtime semantics,
  and all paths selected by `PACKAGE_PATHS` remain byte-for-byte preservation claims
  in this phase. No 0.4 manifest/cachebuster or release claim is allowed before a
  later explicitly authorized certification/release phase.
- `AGENTS.md` still describes public/active 0.2 and a required Fable release gate.
  This is baseline policy drift after the completed 0.3 release and must be resolved
  for 0.4 without reclassifying it as a product failure.
- Current evaluation input identity binds the entire monolithic runner bytes, so a
  metadata-only implementation edit invalidates every model receipt. This is the
  primary defect class.
- Conversely, extracting modules without a transitive engine manifest would leave
  new executable inputs unattested. The new engine therefore binds canonical
  manifests for semantic, harness, and artifact module classes, not wrapper bytes.
- `behavior-v21.json` is the current certified 0.3 evidence. The clean break must
  replace the historical index atomically with a new `current.json` whose state is
  `refresh_required`; it may become `certified` only after an explicitly approved
  live successor. Offline proof cannot silently promote it.
- Raw model outputs remain external; only sanitized, secret-free summaries and
  content identities may enter the repository.

## Initial claims

| ID | Type | Claim | Closure / falsifier | State |
| --- | --- | --- | --- | --- |
| O-01 | outcome | A modular pure-standard-library certification engine replaces the monolithic internal evaluator without legacy internal compatibility. | Module/CLI inventory plus tests; legacy reader or dual-write path falsifies. | verified offline |
| O-02 | outcome | Canonical receipts separate semantic input, harness implementation, and derived artifact identities. | Deterministic hash tests and mutation counterexamples. | verified offline |
| O-03 | outcome | A read-only impact command reports exact invalidated gates, reasons, and live-run count/cost before execution. | Table-driven dependency tests; an unclassified material input change falsifies. | verified offline |
| O-04 | outcome | Historical behavior v1-v20 files and version-specific compatibility tests leave the active tree while remaining reachable in Git history. | Final path inventory and ancestry proof. | verified |
| O-05 | preservation | Installed Skill behavior, plugin identity, public install commands, and `$happycodex:happycodex` invocation remain stable except the intentional 0.4 version/change note. | Exact runtime diff and contract tests. | verified; no version edit in phase one |
| O-06 | outcome | Maintainer policy describes current public 0.3 baseline, the 0.4 gate model, and this task's explicit Fable exclusion correctly. | Policy review and tests. | verified |
| O-07 | outcome | Offline suite, official Skill/plugin validators, dry-runs, diff hygiene, and final fresh native review close with no unresolved blocker. | Exact command receipts and review coverage. | open |
| O-08 | preservation | No Fable invocation, controller, hook, daemon, scheduler, MCP/app runtime, or authoritative Task State JSON is added or run. | Tree/command inventory. | verified |
| O-09 | outcome | Every transitive evaluator module/schema is classified into and bound by a canonical semantic, harness, or artifact manifest. | Module inventory and mutation tests; any executable unclassified file falsifies. | verified offline |
| O-10 | outcome | The evidence ledger has one new-schema `current.json`, explicitly records `refresh_required`, and cannot claim certification without a live successor receipt. | State-machine tests and final ledger inspection. | verified offline; live successor pending |
| O-11 | preservation | Phase-one changes do not alter `.agents`, `.codex-plugin`, `README.md`, or `skills`; therefore the full shipped-package manifest remains `0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`. | Exact package-manifest check and Git diff. | verified |
| B-01 | allowed-break | Internal evaluator imports, CLI syntax, receipt/result schema, and historical result paths have no backward-compatibility obligation. | Any compatibility shim must be removed or separately authorized. | exercised |
| B-02 | allowed-break | Internal raw filenames, output-directory layout, write-once ordering, stdout payloads, and exit codes may change to the new CLI contract. | New CLI integration tests are authoritative; preserving an old path is not a requirement. | exercised |
| P-01 | premise | Baseline and branch identities above are exact and the starting worktree is clean. | Git receipts. | verified |

## Design saturation

Fresh baseline-only challenger `/root/cert_engine_boundary_challenger_fast` inspected
baseline `2836d7363db364807a2ec384dc1b6c2cc13df95e` without this plan or a preferred
implementation. Its verdict was NOT-YET until four omissions were frozen. Root
reproduced and disposed the union as follows:

1. Accepted: wrapper-only hashes miss extracted executable modules. The new manifest
   binds every classified Python/schema input and fails on an unclassified module.
   The challenger's suggestion to retain legacy fields is rejected because B-01 is
   the operative clean-break authorization; new manifests replace old runner fields.
2. Accepted: v21 cannot remain current across the engine rewrite. The ledger switches
   atomically to `refresh_required`, retains only immutable Git/digest provenance, and
   cannot return to `certified` from offline checks.
3. Accepted: filenames, directory layout, write ordering, stdout, and exit status are
   part of the internal break, now explicit in B-02 and covered by new integration
   tests rather than accidental preservation.
4. Accepted: phase one is support-only. All shipped package bytes remain exact, and
   the stdlib/dependency inventory expands recursively over the new engine.

Alternatives and saturation:

- In-place modularization with adapters was rejected: it preserves the historic
  surface and recreates the invalidation/dual-ledger debt.
- A clean-break package with a single `python3 -m evaluation.cli` entry point was
  selected. It separates core identity/impact/receipt logic, corpus execution, and
  holdout comparison while keeping raw output external.
- Runtime/controller expansion was rejected as unnecessary and outside the operative
  Outcome. A third-party framework or non-stdlib rewrite was rejected by repository
  policy and adds no required capability.
- The union now covers shipped/runtime bytes, transitive engine inputs, evidence
  state, operational CLI behavior, tests/callers, cost, and release authority. No
  decision-changing omission remains for offline implementation.

## Frozen architecture and impact model

The target package is:

```text
evaluation/
  __init__.py
  cli.py
  core/{__init__,identity,impact,receipt}.py
  corpus/{__init__,contract,engine}.py
  holdout/{__init__,blind,compare,engine}.py
  cases/*.json
  holdouts/{manifest.json,cases/*.json}
  results/current.json
```

`python3 -m evaluation.cli` exposes only `verify`, `impact`, `corpus`, and `holdout`.
`verify` validates the dependency inventory and ledger without a model call. `impact`
is read-only and returns gates, exact affected cases/pairs, reasons, live-call count,
and historical token/wall estimates. `corpus` and `holdout` require an external raw
output directory; dry-run is side-effect-free. No old script/module entry point or
result path survives.

Identity layers are non-overlapping:

- semantic: case/holdout data, runtime-semantic package projection, model/effort/
  timeout, prompt/context/schema, isolation/permission policy, oracle and comparison
  policy;
- harness: every executable module that realizes fixture/install/invoke/parse/blind
  behavior, plus interpreter/CLI contract identity;
- artifact: sanitizers, receipt serialization, tracked ledger projection, and the
  exact full-package artifact digest.

Impact fails closed. Semantic mutation invalidates the exact dependent corpus cases
and downstream holdouts. Unknown or execution-affecting harness mutation requires the
same live refresh unless a frozen offline equivalence proof covers it. Artifact-only
mutation requires regeneration/validation but zero model calls. Version/change-note
metadata is artifact/install-only; it is not changed in this phase. An unclassified
input is an error, never an implicit no-op.

## Baseline receipts

All commands ran on the work branch with only the committed ExecPlan skeleton added;
baseline product and evaluator bytes were unchanged:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: exit 0,
  97/97 passed in 1.472 seconds.
- official Skill validator: exit 0, `Skill is valid!`.
- official plugin validator: exit 0.
- `python3 evaluation/run_corpus.py --dry-run`: exit 0, 14 cases.
- `python3 evaluation/run_holdouts.py --dry-run`: exit 0, three pairs and adaptive
  policy validated.
- `ruff check .`: exit 0; `ruff format --check .`: exit 0, five files unchanged.
- `git diff --check main..HEAD`: exit 0.

Historical v21 candidate cost is 498,708 combined uncached-input/output tokens and
2,429.409 seconds for 14 terminals. This is an estimate, not approval. The rewrite is
expected to require 14 candidate corpus calls and, because the holdout engine changes,
two to three adaptive pairs before certification. Exact post-implementation impact and
cost must be persisted, then execution stops for an explicit user decision.

## Offline implementation receipt

The clean break is implemented with one package command surface and no adapters. The
old `run_corpus.py`, `run_holdouts.py`, result index, and behavior-v1 through v21 files
are absent from the active tree; Git history remains the recovery mechanism. The
active result directory fell from about 1.68 MB to one 4.8 KB ledger. Version-specific
test methods were removed while all current fixture, oracle, isolation, package,
blinding, adaptive, and cost-policy tests remain.

`python3 -m evaluation.cli impact` on the formatted candidate records:

- engine manifest `8d32a481b9bfa739a3d2d6158608498b43e4d60d276e41b5af453c37acfa13ad`;
- snapshot `43e77a0a06e75eeb84d1e809dc196b1a4290ddb72a5881f76dd7784cb11e21fa`;
- ledger `7675e923b6cd583cb98f95f27045ea549f0d5753473afcce786a868898e3ac4e`;
- sole invalidation reason `engine_generation_changed`;
- exact scope: all 14 candidate cases plus the three-pair adaptive holdout, 18 to
  20 live calls;
- historical estimate: 585,209 to 637,027 combined tokens and 2,911.874 to
  3,187.085 wall seconds;
- bound approval token
  `80c73a726fa384e75ce8e4da7d13f02307c336d63d8551be18720fa9656ca337`.

The CLI rejects live corpus/holdout execution without that exact current token, but a
token is not a substitute for the still-required persisted user cost approval.
Candidate unit validation is 99/99 green in 1.558 seconds; Ruff check/format and both
new dry-runs are green. Exact official validators and fresh review follow the
implementation commit.

## Validation envelope

Candidate offline commands, exact live-run costs, required reruns, and review launch
records will be frozen before their respective actions. Fable is not a gate for this
task. External push, PR, active-plugin mutation, manifest/cachebuster edit, or release
publication requires a later explicit user request.

## Checkpoint

- Milestone: offline engine, ledger transition, compatibility deletion, tests, and
  exact impact/cost receipt implemented after contract freeze
  `c03c6e1a1c644a4ca32f18f9cfd261746be1eb3a`.
- Goal: active `019f780e-925e-7193-8bd2-0a04d6efe31e`; its objective is the
  Normalized Outcome plus all frozen preservation, exclusion, offline validation, and
  live-cost gates in this document.
- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_certification_engine -v` exited 1 before implementation because
  `evaluation.core` did not exist; the same contract is now green.
- Next: commit the implementation, run exact offline/official validation on that
  revision, launch a fresh full-scope native review, reproduce any findings, and stop
  at the explicit live-cost decision.
- Product/support writes: open after the distinct freeze revision.
- Owned paths: `evaluation/`, `tests/`, `AGENTS.md`, and this ExecPlan; shipped-package
  paths remain closed.
- Missing facts: post-implementation exact impact/cost, live successor receipts, and
  final review identity.

## Retrospective

Fill only after every completion gate closes.
