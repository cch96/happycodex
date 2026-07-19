# HappyCodex 0.4 clean-break certification engine

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: in-contract repair after fresh Native NOT-YET
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
| O-02 | outcome | Canonical receipts separate semantic input, harness implementation, and derived artifact identities. | Deterministic hash tests and mutation counterexamples. | verified offline after NR-03 repair |
| O-03 | outcome | A read-only impact command reports exact invalidated gates, reasons, and live-run count/cost before execution. | Table-driven dependency tests; an unclassified material input change falsifies. | verified offline after NR-01/03/04 repair; live execution remains unapproved |
| O-04 | outcome | Historical behavior v1-v20 files and version-specific compatibility tests leave the active tree while remaining reachable in Git history. | Final path inventory and ancestry proof. | verified |
| O-05 | preservation | Installed Skill behavior, plugin identity, public install commands, and `$happycodex:happycodex` invocation remain stable except the intentional 0.4 version/change note. | Exact runtime diff and contract tests. | verified; no version edit in phase one |
| O-06 | outcome | Maintainer policy describes current public 0.3 baseline, the 0.4 gate model, and this task's explicit Fable exclusion correctly. | Policy review and tests. | verified |
| O-07 | outcome | Offline suite, official Skill/plugin validators, dry-runs, diff hygiene, and final fresh native review close with no unresolved blocker. | Exact command receipts and review coverage. | offline gates verified; fresh repair review pending |
| O-08 | preservation | No Fable invocation, controller, hook, daemon, scheduler, MCP/app runtime, or authoritative Task State JSON is added or run. | Tree/command inventory. | verified |
| O-09 | outcome | Every transitive evaluator module/schema is classified into and bound by a canonical semantic, harness, or artifact manifest. | Module inventory and mutation tests; any executable unclassified file falsifies. | verified offline after NR-03/04 repair |
| O-10 | outcome | The evidence ledger has one new-schema `current.json`, explicitly records `refresh_required`, and cannot claim certification without a live successor receipt. | State-machine tests and final ledger inspection. | verified offline after NR-02 repair; live successor still pending |
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
  live.py
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
  behavior, plus exact Python/Codex/Git/rg toolchain identities;
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
- then-called bound approval token (later rejected by `NR-01`)
  `80c73a726fa384e75ce8e4da7d13f02307c336d63d8551be18720fa9656ca337`.

The CLI rejects live corpus/holdout execution without that exact current token, but a
token is not a substitute for the still-required persisted user cost approval.
Candidate unit validation is 99/99 green in 1.558 seconds; Ruff check/format and both
new dry-runs are green. Exact official validators and fresh review follow the
implementation commit.

## Native review receipt and repair impact

Fresh read-only reviewer `/root/cert_engine_final_review` inspected immutable baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e` through candidate
`444e53e297b7131556e73f6a59ce5d75b7702467`. It read the full plan, source/diff,
deletion inventory, and changed tests; independently reproduced 99/99 and all offline
gates; reported no contamination or truncation; and invoked no network, Fable, Goal,
live evaluator, or write. Verdict: NOT-YET with four findings:

- `NR-01` critical: the impact token is not bound to actual CLI model/effort/timeout,
  case/arm, or package identities and no persisted user-cost authority exists.
- `NR-02` high: `state=certified`, empty pending, and `certification={}` passes ledger
  validation without a live successor receipt.
- `NR-03` high: artifact sanitizers remain inside corpus harness; holdout policy and
  CLI/interpreter boundaries are also too coarse for exact invalidation.
- `NR-04` high: a removed corpus case is excluded from current rerun scope and reports
  zero calls/cost.

Root reproduced all four offline. The minimum repair adds counterexamples first, then:

1. persist a nullable, exact invocation-bound user authority receipt in the evidence
   ledger; live CLI remains mechanically blocked while it is null;
2. require a closed certification receipt with successor commit/tree and exact
   corpus/holdout/review/authority/snapshot digests before `certified` validates;
3. move derived sanitization into the artifact module, split CLI/interpreter and
   holdout-policy identities to the narrowest safe gates, and keep unknown changes
   fail-closed;
4. classify case removal as a review/blocking schema change rather than zero-cost
   success, with no live token minted until the corpus is valid again.

This repair changes only evaluator/tests/ledger/plan support. It does not touch the
shipped package and does not enlarge the already-pending maximum 14 corpus plus three
paired holdouts. It invalidates the current engine/snapshot/token receipts, which must
be regenerated offline. The repaired revision requires a fresh exact Native review;
no live call is authorized before that review and the later user cost decision.

## Repair closure candidate

The four review findings now have executable counterexamples and bounded repairs:

- `NR-01`: `live_authority` is a required nullable ledger field. The printed
  `impact_token` excludes that field from its binding basis to avoid a persistence
  cycle, but it cannot authorize execution. Live dispatch moved to classified harness
  module `evaluation/live.py` and requires both the fresh binding and a persisted
  `current-task/user/...` receipt whose exact package identities, model, effort,
  timeout, candidate arm, cases, and holdout pairs match the actual invocation.
- `NR-02`: `certified` now requires a closed successor commit/tree receipt plus exact
  snapshot, engine-manifest, corpus, holdout, review, and authority digests. Empty or
  malformed receipts, mismatched engine/authority/package/settings, retained pending
  gates, and certified-state input drift fail closed.
- `NR-03`: sanitizers moved from corpus harness to artifact-only receipt code; CLI is
  artifact/control projection, live dispatch is shared harness, holdout comparison is
  holdout-only semantic policy, and Python/Codex/Git/rg path/version/binary identities
  are in every current snapshot and raw run identity receipt.
- `NR-04`: corpus-case removal raises an identity error before scope intersection or
  token minting. The holdout manifest and snapshot also require exactly three pairs;
  unknown new corpus cost continues to fail closed.

The focused RED ran before repair and failed on all four classes: missing
`evaluation/live.py`, sanitizer functions still inside corpus harness, absent
toolchain and `live_authority`, permissive empty certification, missing authority APIs,
and zero-cost case deletion. The repaired focused suite is 22/22 green; cumulative
offline validation is 106/106 green in 2.582 seconds. Both official validators pass,
Ruff check and format-check pass, both dry-runs pass, JSON and `git diff --check` pass,
and the shipped package remains byte-exact at
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.

Final formatted offline identities are:

- engine manifest `34963db0de975f18ad2c0fdeb40f419eb0942feaf90a8d6de2eb5e974be3de75`;
- snapshot `084ee4172dc283ac916033a7170510316bc6a93ebadfa61748f4d0404d494442`;
- ledger `f7e9e5f47c569f300bb35c5e4616481cbcbb5d464fdaf401115605170bd49c83`;
- impact token `205d1c0d13aa34411c6c9309dc6eb920edd340acde535580046a61fcca908fa2`.

The sole persisted invalidation reason remains `engine_generation_changed`; exact live
scope remains 14 candidate cases plus two to three adaptive pairs, 18 to 20 model
calls, 585,209 to 637,027 combined tokens, and 2,911.874 to 3,187.085 seconds. The
ledger still has `live_authority: null`, so no live call can start.

The frozen public benchmark is commit
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`, not later 0.2 repository head
`5c5d4c0a4d7590871acd14e4f1ef282f2f564177`. A temporary archive of the frozen commit
reproduces package artifact `77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`
and semantic identity `fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`;
`impact --public` then reports `live_authority_ready: true` with exactly one corpus and
one adaptive-holdout invocation descriptor. The temporary archive was removed. This
read-only proof made no model call and does not alter the benchmark.

## Validation envelope

Candidate offline commands, exact live-run costs, required reruns, and review launch
records will be frozen before their respective actions. Fable is not a gate for this
task. External push, PR, active-plugin mutation, manifest/cachebuster edit, or release
publication requires a later explicit user request.

## Checkpoint

- Milestone: all four findings against first candidate
  `444e53e297b7131556e73f6a59ce5d75b7702467` are repaired and the exact offline
  envelope is green; the repair commit and fresh exact review remain pending.
- Goal: active `019f780e-925e-7193-8bd2-0a04d6efe31e`; its objective is the
  Normalized Outcome plus all frozen preservation, exclusion, offline validation, and
  live-cost gates in this document.
- RED: the original architecture RED and the later four-finding repair RED are both
  persisted above; the repaired focused contract is 22/22 and cumulative suite is
  106/106.
- Next: commit the bounded repair, launch a fresh exact read-only review, and resolve
  any in-contract finding. If review is green, stop for the explicit maximum-cost user
  decision before persisting authority or making any live call.
- Product/support writes: support-only paths remain open; shipped-package paths remain
  closed.
- Owned paths: `evaluation/`, `tests/`, `AGENTS.md`, and this ExecPlan; shipped-package
  paths remain closed.
- Missing facts: repair commit/review identity, explicit user cost decision, and live
  successor receipts.

## Retrospective

Fill only after every completion gate closes.
