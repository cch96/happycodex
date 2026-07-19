# HappyCodex 0.4 clean-break certification engine

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: immutable simplification candidate and preflight GREEN; fresh review pending
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
| O-03 | outcome | A read-only impact command reports exact invalidated gates, reasons, and live-run count/cost before execution. | Table-driven dependency tests; an unclassified material input change falsifies. | NOT-YET: a partial pending holdout scope can be planned but not executed |
| O-04 | outcome | Historical behavior v1-v20 files and version-specific compatibility tests leave the active tree while remaining reachable in Git history. | Final path inventory and ancestry proof. | verified |
| O-05 | preservation | Installed Skill behavior, plugin identity, public install commands, and `$happycodex:happycodex` invocation remain stable except the intentional 0.4 version/change note. | Exact runtime diff and contract tests. | verified; no version edit in phase one |
| O-06 | outcome | Maintainer policy describes current public 0.3 baseline, the 0.4 gate model, and this task's explicit Fable exclusion correctly. | Policy review and tests. | verified |
| O-07 | outcome | Offline suite, official Skill/plugin validators, dry-runs, diff hygiene, and final fresh native review close with no unresolved blocker. | Exact command receipts and review coverage. | NOT-YET: offline matrix is green but the tenth fresh review found five blockers |
| O-08 | preservation | No Fable invocation, controller, hook, daemon, scheduler, MCP/app runtime, or authoritative Task State JSON is added or run. | Tree/command inventory. | verified |
| O-09 | outcome | Every transitive evaluator module/schema is classified into and bound by a canonical semantic, harness, or artifact manifest. | Module inventory and mutation tests; any executable unclassified file falsifies. | verified offline |
| O-10 | outcome | The evidence ledger has one new-schema `current.json`, explicitly records `refresh_required`, and cannot claim certification without a live successor receipt. | State-machine tests and final ledger inspection. | NOT-YET: direct runner seams bypass persisted authority and zero-call refresh cannot certify |
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
  core/{__init__,identity,impact,ledger,receipt}.py
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
  or authority/control behavior, plus exact Python/Codex/Git/rg toolchain identities;
  Python also binds its standard-library tree, shared-library closure, and resolver;
- artifact: sanitizers and receipt serialization, plus the exact full-package
  artifact digest.

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
- `NR-03`: sanitizers moved from corpus harness to artifact-only receipt code; CLI and
  live dispatch are shared harness, holdout comparison is holdout-only semantic policy,
  and Python/Codex/Git/rg path/version/binary identities are in every current snapshot
  and raw run identity receipt.
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

## Second Native review receipt

Fresh read-only reviewer `/root/cert_engine_repair_review` inspected immutable
baseline `2836d7363db364807a2ec384dc1b6c2cc13df95e` through repair candidate
`c5a325c4a87cb0687f7d3633d9bd6666ba2a7306`. It read the full policy/plan and
45-file range, traced source and tests, reproduced baseline 97/97 and candidate
106/106 in clean archives, and independently passed verify/impact, both dry-runs,
Ruff, both official validators, JSON/diff hygiene, package preservation, frozen
public-benchmark identity, removal/new-cost failure cases, and legacy-path absence.
It made no model, corpus, holdout, network, Fable, Goal, install, activation, or
tracked repository write. One initial worktree validation may have refreshed ignored
cache data; the clean-archive rerun removed contamination doubt, tracked state stayed
clean, and bounded rereads left no unresolved truncation.

Verdict was NOT-YET with two new findings:

- `NR-05` critical: the closed receipt still treats arbitrary hexadecimal source
  commit/tree and corpus/holdout/review digests as evidence. The positive unit test
  itself creates nonexistent identities plus corpus-only authority and expects
  validation success. Neither Git reachability/blob content nor exact authority
  coverage of the persisted impact is proven, and the approval source digest is
  unchecked against approval content.
- `NR-06` high: `cli.py`, `core/impact.py`, and the authority half of
  `core/receipt.py` are classified artifact-only even though they control dispatch,
  settings, invalidation scope, cost, token construction, and certification. Mutating
  them yields only a receipt gate and zero model calls. Python identity also omits its
  transitive stdlib and loaded shared-library bytes.

Root accepts both. The minimum repair will (a) persist and validate the complete
approved impact and exact invocation coverage; bind approval request/response content;
require reachable Git source/tree and reachable content-addressed JSON evidence for a
certified transition; and validate existing corpus/holdout receipt coverage without
adding a reviewer protocol, and (b) split ledger/control from artifact sanitization,
classify CLI/impact/ledger/live as shared harness, add real-file mutation tests, and
extend Python runtime identity. The current full pending live scope already covers
these harness changes, so the historical maximum remains unchanged. A third fresh
review is required after the bounded repair.

Focused `NR-05/06` RED is now durable: 23 tests ran with three failures and five
errors. It reproduced artifact-only zero-call plans for real `cli.py` and
`core/impact.py` mutations, missing `core/ledger.py`, absent Python stdlib/shared-lib
identities, acceptance of the old incomplete authority envelope, and no repository
argument for reachable certification evidence. No model or external mutation ran.

## NR-05/06 repair closure candidate

The second repair keeps artifact sanitization in `core/receipt.py` and moves all
authority, ledger, source, and evidence validation into classified shared-harness
`core/ledger.py`. `cli.py`, `live.py`, `core/identity.py`, `core/impact.py`, and
`core/ledger.py` now share the corpus-harness invalidation scope, so a real-file
mutation of any control module produces the full 18-to-20-call plan; the same
mutation of receipt sanitization remains a zero-model receipt gate.

Live authority now persists the complete validated impact, snapshot identity, exact
corpus/holdout invocation list, literal approval response and its SHA-256, and the
canonical approval-request digest. A token alone still grants nothing. The authority
must cover every nonempty live scope exactly and use the frozen public-0.2 artifact.

A `certified` transition now resolves the successor commit and tree from Git, extracts
that exact source, and proves its engine manifest plus shipped-package content against
the snapshot and current package identity. Corpus, holdout-run, holdout-summary, and
opaque review locators must name descendant commits reachable from `HEAD`; each
locator binds path, Git blob, and file SHA-256. Mechanical validators then bind the
full engine inventory, toolchain, package, semantic case inputs, source holdout
manifest/cases, adaptive ordering, arm identities, telemetry aggregates, and release
cost gate. This adds no reviewer protocol: review JSON remains opaque but must be a
nonempty reachable content-addressed object.

Python identity now hashes 735 non-cache standard-library files and the deterministic
47-library dependency closure of the interpreter and stdlib extension modules, plus
the `ldd` resolver bytes. The focused suite is 24/24 green, including a temporary Git
repository that exercises the complete positive certification path and rejects a
reachable but source-mismatched successor. Current offline identities are engine
`fbda676ee49a8f12d4d98b16ba4381954e77cb37a948eb5b63ec222b73dfc609`,
snapshot `62472587707a5501e4d3d03bec40b366d0c6b4dcc1117bf0b1b5deb10cd0e51f`,
ledger `d611687e20baec2a8536b61356a4a7f10e3af08ed98a64a17680357e8645aa2e`,
and impact token
`e6bfad33d89ec56d5e58658fd790c6ec83335143df4648493118c6a79a0eb83c`.
The ledger remains `refresh_required` with null live authority and unchanged exact
cost/scope.

The full offline matrix is green: 108/108 unit tests in 5.189 seconds; both official
Skill/plugin validators; Ruff check and format-check; both CLI dry-runs; verify and
impact JSON; JSON parsing and diff hygiene; legacy-path/generated-artifact absence;
and the exact shipped-package artifact
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.
An isolated archive of frozen public commit
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2` again reproduced semantic
`fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
`impact --public` emitted exactly the corpus and holdout descriptors with
`live_authority_ready: true`. The archive was removed. No model call ran. A third
immutable fresh review remains open.

## Third review blocker and post-cert RED

Fresh read-only reviewer `/root/cert_engine_final_repair_review` audited exact commit
`7f7e6afa97298fbf1bd34d10216fa4738257ce71` and independently identified a critical
remaining `NR-05` chronology false-green. The positive certification test commits a
successor source while `current.json` still has `live_authority: null`, constructs
authority only later in memory, then commits evidence and validates the final object.
`core/ledger.py` proves source code/package identity but never reads the source
commit's ledger, so it cannot prove exact authority was persisted before evidence or
that the approved impact equals the source ledger's pending scope.

Root then reproduced two downstream completion failures in the same state-machine
path: tracked `results/evidence/*.json` is rejected as unclassified engine input after
certification, and `verify` rehashes an already loaded certified ledger without the
repository context required to resolve its evidence. The minimum closure also binds
the impact token and authority digest into corpus/holdout run evidence, so reachable
JSON cannot silently reuse an invocation lacking the persisted approval binding.

The next focused RED is durable at 27 tests: two failures and two errors. It proves
(1) authority created only after the source commit is accepted, (2) live dispatch does
not pass the authority digest into the runner, (3) final evidence outputs poison the
engine inventory, and (4) certified `verify` drops repository context. This remains a
bounded offline control/receipt repair; package bytes and the already-pending live
scope/cost do not change. A new immutable fresh review is required after closure.

The bounded closure is now green. The successor source validator reads that exact
commit's `current.json`, requires `refresh_required`, the same snapshot, null
certification, and the exact final authority, validates the source ledger, and
recomputes the authority impact from its pending scope. Live dispatch injects the
canonical authority digest into the runner; corpus summary and the pre-model holdout
run receipt both bind that digest and the approved impact token, and certification
requires those exact bindings. Content-addressed evidence JSON is explicitly treated
as non-executable output, while unknown JSON elsewhere still fails closed. Certified
`verify` now preserves repository context when revalidating the ledger hash.

All 27 focused tests and the full 111/111 suite pass. Both official validators, Ruff,
format-check, verify/impact, both dry-runs, JSON/diff hygiene, and package preservation
are green. Final offline identities for this closure are engine
`0f01a09f4fe7c4b582b06e40c2276b78f298302a29c9b45325a04660d4309344`,
snapshot `1b41997e8a7ba7545b0a102a74f9d1a2720ab37d727abd647674ac6a6db07390`,
ledger `3d273593e30e0eb9c342bdb270dc49def3962eab4d13c4130f76a3327cc1ce2c`,
and impact token
`f655f4dccb37bd837a0d929e85e99da3e44af3e4c0f9eac2940af26ea508de2b`.
The live authority remains null and the 18-to-20-call maximum cost is unchanged. A
new exact fresh review remains mandatory before requesting cost approval.

## Fourth fresh review and bounded NOT-YET

Fresh read-only reviewer `/root/cert_engine_post_chronology_fresh_review` audited
exact commit `ffb59831e6fc647dd980675d1b9a5959209863be` against baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`. It kept the repository tracked-clean,
ran only isolated offline checks, and returned `NOT-YET` with four new correctness
findings:

1. `NR-07` critical: evidence ancestry is inclusive, so an evidence locator may name
   the same commit as the authority-bearing successor source. Authority persistence
   must strictly predate every certification evidence commit.
2. `NR-08` high: impact and live dispatch authorize an exact case subset, and the
   runner emits that subset, but certification currently requires all corpus cases.
   A one-case plan therefore cannot reach `certified` through the shipped contract.
3. `NR-09` high: successor validation compares its package content but not its exact
   artifact identity. A Git executable-bit change can preserve content while changing
   the package artifact identity.
4. `NR-10` medium: snapshot/impact construction accepts a corpus object after only an
   ID check, while the runner applies the complete case-schema oracle later. Impact
   can therefore issue a token and cost for a case execution will reject.

The reviewer independently confirmed the repaired authority-at-source equality and
pending-impact recomputation, corpus/holdout token and authority-digest bindings,
evidence-output classification, certified `verify` repository context, reachable Git
blob/SHA binding, package preservation, and legacy-path removal. Its isolated clean
clone passed 111/111 candidate tests and 97/97 baseline tests; both official
validators, Ruff, verify/impact, dry-runs, JSON hygiene, and package digest also
passed. No model, Fable, network, Goal, install, release, or repository write ran.

Root accepts all four findings. The next repair is limited to strict source-before-
evidence ordering, an end-to-end exact-scope corpus certification contract, Git-
faithful source artifact reconstruction, and a single shared case-schema validation
path. New RED counterexamples and another exact fresh review are mandatory; the live
cost gate remains closed.

The fourth-review RED is now durable. Three focused tests produce one failure and two
errors: malformed corpus input reaches snapshot/impact, an authorized one-case
summary is rejected as incomplete, and the positive Git certification fixture is
rejected because the intended merged-coverage manifest is not yet part of the
schema. That Git fixture also carries the next-layer same-commit evidence and
executable-bit source variants, which must be rejected once the coverage envelope is
implemented. The safe incremental contract will not trust pending scope alone: it
must validate a reachable prior 0.4 certified ledger, recompute impact from its
snapshot, and make refreshed-versus-prior coverage explicit for every current case
and pair; otherwise only full fresh coverage is valid.

The bounded repair is green. Evidence commits must be strict descendants of the
authority-bearing source. A source archive is normalized from Git file-mode classes
to the repository's private package modes before its complete semantic/artifact
identity is compared with the snapshot, so an executable-bit drift is rejected.
Corpus and holdout snapshot construction now call the same full schema validators as
execution. Certification carries an exact merged coverage manifest: newly authorized
summaries cover precisely the impact scope, while every `prior` case or pair requires
a strictly older, SHA-bound, recursively valid 0.4 certified ledger. The validator
recomputes prior-snapshot-to-successor impact, binds the source and final prior/cost
records, and still requires a fresh review. If that chain is absent or changed, only
full refreshed coverage can certify.

The expanded positive Git fixture first certifies a complete snapshot, then mutates
one valid case and certifies the one-call successor using explicit prior coverage. It
also rejects same-commit evidence, source executable-bit drift, and a changed prior
ledger digest. Both corpus and holdout malformed-input controls fail during impact,
before token or cost construction. The focused certification suite is 30/30 and the
complete offline suite is 114/114 green. Final offline identities are engine
`d683a5029137c59b8c894b699477f9767363d6dbed06a536f7e74f2391fff970`,
snapshot `16c8c6b612469a81d2a5bd29a93d0a9c1643b9cb30a5e48564c8d6b47a848448`,
ledger `8ccdd7607e10bf958e8b9298d2815458183e1240f126c70fcedf1d86a3e47fc1`,
and impact token
`b3316e278a43d125a1e41f7ea369e166bbd2a86570bacc5274dbd0b9eb4a8a5a`.
Live authority remains null and the 18-to-20-call cost is unchanged. A new exact
fresh review is mandatory before cost approval.

## Fifth fresh review and holdout outcome NOT-YET

Fresh read-only reviewer `/root/cert_engine_coverage_final_review` audited exact
commit `ebd65d80117edc3868ba373830f69b81a859e0d9` in clean detached clones and
returned `NOT-YET` with one high-severity evidence-consistency finding. The runner
defines `better` as candidate pass plus public-0.2 fail, `equal` as both pass, and
`regression` as candidate fail. Certification instead applies the corpus all-pass
rule to both holdout arms and trusts the declared pair outcome. It therefore rejects
the legitimate public-fail receipt for `better`, while accepting two passing arms
mislabelled as `better`.

The reviewer independently verified every `NR-07` through `NR-10` repair, the exact
current 18-to-20-call impact and identities, 114/114 candidate tests, 97/97 baseline
tests, both official validators, Ruff, dry-runs, JSON/diff hygiene, package
preservation, and all exclusion claims. It classified zero-call artifact/install
certification as a disclosed later-phase limitation rather than a blocker for this
unchanged-package full-refresh phase. No model, Fable, network, Goal, install,
publication, or repository write ran.

Root accepts the single finding. The bounded repair must derive every holdout outcome
from exact candidate/public `passed` states using the same comparison rule as the
runner; candidate must pass for a releasable summary, public failure is valid only as
`better`, and failed-arm telemetry must remain structurally valid. A focused RED,
complete offline rerun, and a sixth fresh exact review are required.

## Fifth focused RED

At commit parent `a1e06e0`, root added one exact regression that exercises both sides
of the holdout outcome contract. An authentic two-pair `better` summary uses passing
candidate receipts and failing public-0.2 receipts with non-empty oracle-failure
digests; a forged `better` summary leaves both arms passing. The command

    python -m unittest tests.test_certification_engine.CertificationReceiptAndCliTests.test_certified_state_accepts_only_reachable_bound_evidence

fails before the forged branch is reached because certification raises
`corpus evidence case did not pass` on the authentic public control failure. This is
the intended RED for the accepted fifth-review blocker. An earlier class-name typo
only produced unittest discovery error and is not product evidence.

## Fifth repair green

Certification now treats `passed` as arm evidence instead of an all-pass corpus
assumption. Candidate/public booleans mechanically derive `regression`, `better`, or
`equal`; the declared receipt must match. A failed arm must carry a positive
oracle-failure count and a non-empty valid digest, while a successful arm retains the
exact no-timeout/empty-failure contract. The authentic `better` and forged-label
regressions both pass after this bounded change.

The complete offline envelope is green: the focused certification module passes
30/30 in 4.718 seconds and the cumulative suite passes 114/114 in 6.070 seconds. Both
official validators, Ruff check and format-check, verify/impact, both dry-runs, all 21
JSON documents, working-tree diff hygiene, and package preservation pass. Current
identities are engine
`53b83e96fd0a3849eb53479123693403fc88e3af077ae72e2287765f2f635905`,
snapshot `f4c6f3ec375f5255afb6e4bab2a0311d06338b95ef75fa2443f45c0ff71379e9`,
ledger `dd395cd99221fda3415a5d82b819cf05dba1ccf533f1fd1c8dac0fdc9ea34296`,
and impact token
`56d3a366ae5ce57e2b58e02abfe1aab0ed03e8a24578bb6ae6f3a7e881d1b0ac`.
The shipped package remains
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.
An isolated archive of frozen public commit
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2` reproduces semantic
`fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
public-bound impact is ready and the archive was removed. Live authority remains
null, the exact cost is unchanged, and no model, Fable, network, install, or release
action ran.

## Sixth fresh review and receipt-consistency NOT-YET

Fresh read-only reviewer `/root/cert_engine_holdout_final_review` audited exact clean
commit `e29facbfeeb010c078e32f3995ee88fb110e8be4` from a detached local clone and
returned `NOT-YET`. Root accepts three P1 evidence-consistency findings:

1. Passing-arm evidence does not require zero exit status, and runner-impossible
   nested receipt values remain accepted. A `passed=true, exit_code=7` arm can be
   certified as `equal` even though the blinded runner grades it as failure; scalar
   result/native-compaction values and a non-object usage phase also pass parsing.
2. Pair-level cost metrics are free-standing. Certification never proves that each
   pair metric equals its candidate/public arm's uncached tokens, output tokens, and
   elapsed time, so forged cheap metrics can turn `simplify_and_retest` into `pass`.
3. A one-pair `equal` summary whose next action is still `run_second` is accepted.
   The runner cannot emit that as terminal because the second distinct pair is
   mandatory.

The reviewer reproduced all three acceptances in memory while 1/1 focused and
114/114 cumulative tests remained green, proving missing oracles rather than existing
test failures. It independently passed both official validators, Ruff check and
format-check, all 21 JSON documents, diff hygiene, package and public-benchmark
identities, and exact impact/cost reconstruction. Engine, snapshot, ledger, and token
matched the identities above; `live_authority` remained null. No model, live runner,
network, Fable, Goal mutation, install, publication, or repository write ran.

The reviewer also observed that semantic revisions beginning at `7f7e6af` omitted
the `HappyCodex-ExecPlan` commit trailer. Root records this as process drift and will
restore the trailer on every subsequent semantic/admin revision. Rewriting reviewed
history would invalidate exact durable review identities while adding no product or
recovery information: the single task-owned ExecPlan is unique, committed, and the
documented alternative recovery locator. Therefore history rewrite is rejected as an
administrative regression, not treated as a product blocker.

The bounded repair must add exact REDs for all three false greens, validate nested
cost/status receipt structure, bind pair metrics to arm telemetry, require an actual
terminal adaptive state, refresh offline identities, and receive a seventh fresh
exact review. This invalidates no behavior, holdout, install, or product receipt and
does not change the exact live cost.

## Sixth focused RED

At commit parent `61fff4c`, the exact reachable-evidence test now presents four
runner-impossible summaries as subtests: successful candidate exit 7; a failed public
arm with a non-object usage phase plus scalar result/native-compaction receipts;
candidate arm telemetry whose actual combined-token/wall ratios require
`simplify_and_retest` while its free-standing pair metrics claim `pass`; and a
one-pair `equal` history whose next action remains `run_second`. The command

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_certification_engine.CertificationReceiptAndCliTests.test_certified_state_accepts_only_reachable_bound_evidence -v

reports four `ValueError not raised` failures in 1.012 seconds. This exactly
reproduces every accepted sixth-review false green without invoking a runner or model.
The valid positive fixture's pair metrics were also aligned with its arm telemetry so
the eventual GREEN cannot depend on the pre-existing inconsistency.

## Sixth repair green

Successful evidence now requires `passed=true`, no timeout, zero exit, and the exact
empty oracle-failure receipt. Every usage phase must be a non-empty object containing
non-negative input/cached/output counters; certification recomputes aggregate usage
and uncached input from those phases. Result, fresh-recovery, and native-compaction
receipts are object-or-null, never scalar. Pair metrics must exactly equal the two
validated arm receipts before aggregation, and an adaptive summary is complete only
at `stop` or `reject`. The four false-green subtests and the authentic `better` path
all pass.

The focused certification suite passes 30/30 in 4.677 seconds and the cumulative
suite passes 114/114 in 6.101 seconds. Both official validators, Ruff check and
format-check, verify/impact, both dry-runs, all 21 JSON documents, working-tree diff
hygiene, package preservation, and isolated public-benchmark reconstruction pass.
Current identities are engine
`cbf619655a6ca73818a51ab09442d85e687dcaa7889370225c177712beca635d`,
snapshot `308854c01f7fc7f288d701cdb6c52abfeffb719288c27df2901eded091470aba`,
ledger `f3f4e01b847f0115ca7ddc415ac002e2ef612bf0e1b0bbc498d6fe2f9154a4ab`,
and impact token
`02f313e76676e771f5655ad5f8cd077e627c9fd7c941542e8a85e84183063a58`.
The shipped package and public benchmark identities remain byte-exact. Public-bound
impact is ready; live authority is null and the cost remains 18-to-20 calls,
585,209-to-637,027 combined tokens, and 2,911.874-to-3,187.085 seconds. No model,
Fable, network, install, publication, or external mutation ran.

## Seventh fresh review launch

The frozen product repair is
`3be9d2574cb4bc04c0cd0f79a1a80eb864b77df9` over baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`; this administrative launch record does
not change the product tree. A new `fork_turns=none` read-only reviewer will receive
the exact candidate, frozen Outcome/exclusions, and a neutral request to reproduce the
four sixth-review probes, audit every diff unit and obligation, and hunt new blockers.
Its durable terminal output destination is agent task
`/root/cert_engine_terminal_final_review`. The reviewer may use only local detached
clones and offline validators; model/live corpus/live holdout, network, Fable, Goal,
installation, plugin, marketplace, Git ref, and repository writes are forbidden.

## Seventh fresh review and case-specific receipt NOT-YET

Fresh read-only reviewer `/root/cert_engine_terminal_final_review` audited exact
administrative candidate `2746a206af4ce7e82c0519856b8f387c345d3d32` and product
repair `3be9d2574cb4bc04c0cd0f79a1a80eb864b77df9` from clean detached local
clones. It confirmed the intervening diff is ExecPlan-only and returned `NOT-YET`
with one P1 nested-receipt finding.

The source case `pre-freeze-compaction` requires the runner's native compaction path,
which produces exactly three usage phases plus primary/fresh recovery and native
compaction receipts. Certification accepts the positive Git fixture's one phase,
empty result/isolation, and null fresh/native receipts for every case. It also accepts
mismatched source/installed Skill digests, although installation rejects that state.
Consequently a terminal ledger can claim the required native reconstruction without
the runner-shaped evidence.

Root accepts the finding. The reviewer independently confirmed every sixth-review
repair and the authentic `better` path, 30/30 focused, 114/114 candidate, 97/97
baseline, both official validators, Ruff, verify/impact, dry-runs, JSON/diff hygiene,
package/public identities, exact cost, null authority, and all exclusions. No model,
live runner, network, Fable, Goal, install, external mutation, or repository write
ran.

The bounded repair must validate the exact sanitizer envelopes, source/installed
Skill equality, static isolation policy, source-case phase count, and native versus
ordinary recovery receipt presence. The positive Git fixture must use the real
sanitizer instead of hand-written minimal nested objects. This remains harness/test
only, retains the existing full-refresh cost, and requires an eighth fresh exact
review.

## Seventh focused RED

The positive reachable-certification fixture now builds every case receipt through
the production `sanitized_case_receipt` path. It emits three phases and complete
native/fresh recovery for `pre-freeze-compaction`, one phase for ordinary and holdout
cases, the full isolation policy receipt, and matching installed/source Skill
digests. Four independent mutations then remove native recovery, mismatch installed
Skill identity, empty isolation, or replace the sanitized result envelope with `{}`.

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_certification_engine.CertificationReceiptAndCliTests.test_certified_state_accepts_only_reachable_bound_evidence -v

reports four `ValueError not raised` subtest failures in 1.013 seconds. The production-
sanitizer positive path itself remains reachable; only the four runner-impossible
mutations are RED. No model or runner invocation occurred.

## Seventh supplemental nested-binding RED

Root's pre-commit source audit found three more projections of the same accepted
nested-receipt blocker. The sanitizer preserves the case oracle's six permission
fields, the complete static isolation-policy digest, and all primary/resume/fresh
thread digests, but certification checked only their types rather than binding them
to the frozen case and to one another. A forged summary could therefore flip an
oracle permission, substitute an arbitrary policy digest, or reuse the primary
thread digest as the allegedly distinct fresh control while retaining `passed=true`.

The positive fixture now derives its permission values and required
finding/blocker anchors from each real case oracle, uses the native case's real
recovery-oracle values, passes through `sanitized_case_receipt`, and independently
reproduces an empty `match_oracle` result before certification. Three independent
mutations exercise the unbound oracle, policy, and native-control projections. On
the partially repaired validator, the focused command above reports exactly three
`ValueError not raised` subtest failures in 1.007 seconds. This is an offline
ledger/test repair only: no Skill, manifest, case oracle, runner, evaluator, model,
network, Fable, install, or live authority changed.

## Seventh nested-receipt repair green

Certification now loads the exact successor corpus descriptors and uses each case to
bind the expected phase count and preserved oracle permission projection. Passed
native evidence requires three non-negative usage phases; exact primary and fresh
result/recovery envelopes; a sanitizer-shaped compaction receipt whose event counts
agree with its event list; distinct and internally consistent primary, resume, and
fresh thread digests; and equivalent primary/fresh recovery permission gates.
Ordinary cases require one phase and reject native/fresh-control material.

Installation receipts require their exact sanitizer fields, equal source/installed
Skill digests, and source/installed package manifests equal to the authorized arm.
Isolation receipts require every visible static policy value plus the exact digest
of the complete runner policy including normalized case workspace/tool roots.
Result and recovery receipts reject truncated fields, invalid output-schema enums,
duplicate blocker identities, contradictory completion projections, and case-oracle
permission mismatches. The seven independent false-green mutations and both
authentic holdout paths now pass the focused test.

The focused certification module passes 30/30 in 4.730 seconds and the cumulative
suite passes 114/114 in 6.100 seconds. Both official validators, Ruff check and
format-check over 19 files, verify/impact, both dry-runs, all 21 JSON documents,
working-tree diff hygiene, and package preservation pass. Current identities are
engine `f7a8e8b4c5dc95faa85c93698a777d1ff69eb4646e1248cb7c6fda9003260d6a`,
snapshot `a4d9a22b9237b982791d47e1425d4c54a6ac563341fc82c2b7087113177e17d2`,
ledger `355938448c26de624fc8bf7b51de6617395cfa1c2e780b4b18f5d3b20f8555c3`,
and impact token
`04e734cd65c8b2220be5ad4c754c143096634cebbdc634a9f8d531c253be397b`.
The shipped package remains
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.

An isolated archive of frozen public commit
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2` reproduces semantic
`fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
public-bound impact contains only corpus and holdout invocation descriptors and is
authority-ready. Live authority remains null, and exact cost remains 18-to-20 calls,
585,209-to-637,027 combined tokens, and 2,911.874-to-3,187.085 seconds. The archive
was removed. No Skill, manifest, case oracle, runner, evaluator, model, network,
Fable, install, publication, or external mutation ran.

## Eighth fresh review launch

The frozen product repair is
`e11dcdac42d2d36a26d0afcad5a946db70353dc7` over baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`. A clean detached local clone reproduced
30/30 focused tests in 4.744 seconds and 114/114 cumulative tests in 6.131 seconds,
both official validators, Ruff check/format-check, verify/impact, both dry-runs, 21
JSON documents, exact package/public identities, baseline-range diff hygiene, and a
clean final status. The temporary clone and public archive were removed.

This administrative launch record does not change the product tree. A new
`fork_turns=none` read-only reviewer will receive the immutable baseline and repair,
the frozen Outcome/exclusions, and a neutral request to audit the complete diff and
all prior blocker classes, reproduce the seven nested-receipt probes, trace real
sanitizer/runner reachability, and hunt any new completion blocker. Its durable
terminal output destination is agent task `/root/cert_engine_nested_final_review`.
The reviewer may use only local detached clones and offline validators; repository
writes, model/live corpus/live holdout calls, network, Fable, Goal actions, install,
plugin/marketplace mutation, Git ref changes, push, and publication are forbidden.

## Eighth fresh review and producer-binding NOT-YET

Fresh read-only reviewer `/root/cert_engine_nested_final_review` audited exact
administrative candidate `1a93f781d8f21d0918326bac47d4f3297c228552` and product
repair `e11dcdac42d2d36a26d0afcad5a946db70353dc7` from a detached local clone. The
review returned `NOT-YET` with four P1 findings:

1. Impact counts the native corpus case once although its producer performs initial,
   resume, and fresh-control model calls. Exact live-call scope is therefore 20 to
   22, not the persisted 18 to 20; historical token/wall estimates remain unchanged.
2. Native recovery receipts are schema-valid but not bound to the source case's
   recovery oracle, and primary/fresh receipts compare only permission gates rather
   than every producer-equivalent recovery-state field. Synthetic writer/phase/gate
   drift and a fresh-only `current_revision` drift certified.
3. Before/after compaction phases validate locally but do not require the same
   rollout-path identity or an append-consistent event history. An unrelated after-
   resume rollout path certified.
4. Sanitized required classification/blocker evidence is not rebound to the case
   oracle, while failed public arms accept producer-impossible timeout/exit/result
   combinations. Removing all required classifications from `compaction-recovery`,
   or pairing `timed_out=true` with exit zero, certified.

The reviewer independently reproduced 30/30 focused, 114/114 candidate, 97/97
baseline, the exact nested test, both official validators, Ruff, dry-runs, 21 JSON
documents, and diff hygiene. It confirmed engine
`f7a8e8b4c5dc95faa85c93698a777d1ff69eb4646e1248cb7c6fda9003260d6a`,
snapshot `a4d9a22b9237b982791d47e1425d4c54a6ac563341fc82c2b7087113177e17d2`,
ledger `355938448c26de624fc8bf7b51de6617395cfa1c2e780b4b18f5d3b20f8555c3`,
impact token
`04e734cd65c8b2220be5ad4c754c143096634cebbdc634a9f8d531c253be397b`,
the exact shipped/public identities, null authority, and unchanged historical
token/wall estimates. The administrative delta is ExecPlan-only; the 49-entry
product projection is identical at
`d280f7bf2f2675cc66b251551ad3526d7db8fda1472b886f1b919a02e158fda1`.
No prohibited action ran.

Root accepts these as the next bounded repair class pending independent local RED
reproduction. No Skill, manifest, case oracle, runner, or evaluator change is
indicated. If aggregate sanitizer hashes cannot prove required anchor membership
without exposing raw text, an artifact-only privacy-safe digest projection is the
allowed bounded extension; it carries no live model cost.

## Eighth producer-binding RED

Root independently reproduced all four review classes with one exact offline command.
A one-case impact containing only `pre-freeze-compaction` reports one call instead of
three. Five corpus mutations then drift both recovery writers from the source oracle,
drift only the fresh `current_revision`, substitute the after-resume rollout path,
remove direct required classifications, or remove all required anchored
finding/blocker evidence. Two holdout mutations retain a complete failed-public arm
while setting timeout with exit zero or deleting its result. Every mutation
certifies on the eighth-review candidate.

The current sanitizer hashes identities and aggregate anchor lists but does not
retain privacy-safe membership digests needed to re-evaluate the producer's
delimiter-aware identity and anchor predicates without exposing raw model text. The
bounded clean-break receipt repair will add only case-folded identity-match and
anchor-member digests; this is artifact evidence, not a case-oracle or runner change.
Recovery marker order can remain producer-compatible because the exact source oracle
is available and contains only three markers.

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_certification_engine.CertificationImpactTests.test_native_case_counts_initial_resume_and_fresh_model_calls tests.test_certification_engine.CertificationReceiptAndCliTests.test_certified_state_accepts_only_reachable_bound_evidence tests.test_evaluation.HappyCodexEvaluationTests.test_sanitized_case_receipt_preserves_auditable_fields -v

reports nine failures in 1.213 seconds: the call-count assertion, all seven new
producer-binding false greens, and the missing privacy-safe sanitizer projection.
No model, live runner, network, Fable, install, or external mutation ran.

## Eighth producer-binding repair green

The impact planner now has an explicit per-case model-call projection tied by test to
the exact set of native cases: thirteen ordinary cases contribute one call each and
`pre-freeze-compaction` contributes initial, resume, and fresh-control calls. The
persisted historical corpus count is corrected from 14 terminals to 16 model calls;
the adaptive holdout adds four to six, so the exact approval range is 20 to 22. Token
and wall estimates already aggregate all native phases and remain 585,209 to 637,027
combined tokens and 2,911.874 to 3,187.085 seconds. This current correction
supersedes the 18-to-20 call counts preserved in earlier chronological receipts.

The sanitizer adds only sorted SHA-256 projections for case-folded identities,
delimiter-aware identity matches, and individual anchors, plus a boolean Goal-pause
handoff projection. Raw identities, anchors, gates, prose, and paths remain absent.
Certification uses those projections to reproduce every direct and anchored
classification/blocker predicate, duplicate and completion rule, accepted-baseline
rule, and required Goal-pause handoff in the frozen case oracle. A failed public arm
is accepted only in the producer-reachable post-blind form: complete telemetry and
result, exit zero, no timeout, and nonempty oracle failures.

For native recovery, certification deterministically rebuilds the exact source case
fixture offline, applies the source post-compaction transition, and binds all four
expected commit/tree identities, the transition receipt, every source recovery-
oracle field, order-insensitive marker sets, and normalized agent receipts. Primary
and fresh revisions/trees must agree. Before/after compaction receipts must name the
same rollout, have different content identities, and preserve an append-prefix event
history. The nine original RED failures plus the supplementary Goal-pause and full
Git-state counterexamples are green without changing the Skill, manifest, case
oracle, runner, or evaluator.

The focused certification module passes 31/31 in 4.981 seconds and the cumulative
suite passes 115/115 in 6.346 seconds. Both official validators, Ruff check and
format-check over 19 files, verify/impact, both dry-runs, 21 JSON documents, diff
hygiene, and package preservation pass. Current identities are engine
`80b98910ea8834d9fbbf4f6cddb002667b9b8db1545548f53687b10ebfc96132`,
snapshot `60b666f33580735c50d295a4a8bc22be85c6481727858c3bc2b1a4baccccb9e1`,
ledger `ff0067bedde3387124645433fc15630099c12764d65f1b67189aa16909cfd9f7`,
and impact token
`65e1ac2f301ebf1c1dc5c172de9528a09f4e4bbca2c64776ca89a7b344d5e1ab`.
The shipped package remains
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.

An isolated archive of frozen public commit
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2` again reproduces semantic
`fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
public-bound impact contains only corpus and holdout descriptors, reports 20 to 22
calls, and is authority-ready. Live authority remains null. The archive was removed;
no model, live runner, network, Fable, install, publication, or external mutation
ran.

## Ninth fresh review launch

The frozen producer-binding repair is
`e15887042d4a1df271abf46ab97d6bef5da7426f` over baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`. Its 49-entry product projection,
excluding only this ExecPlan, is
`c10fcdff74c60c3cdc43dffa4e96cf0e59187c056a3398659ef4ab44972c8866`.

A clean detached local clone reproduced 31/31 focused tests in 4.962 seconds and
115/115 cumulative tests in 6.357 seconds. Both official Skill/plugin validators,
Ruff check and 19-file format-check, verify/impact, both dry-runs, all 21 JSON
documents, baseline-range diff hygiene, shipped-package preservation, public archive
reconstruction, public-bound impact, and clean final status passed. Exact engine,
snapshot, ledger, and impact-token identities matched the preceding repair receipt;
the public semantic/artifact identities and corrected 20-to-22-call scope also
matched. The temporary public archive was removed. No model, live corpus, live
holdout, network, Fable, Goal action, install, plugin/marketplace mutation, Git ref
change, push, or publication ran.

This administrative launch record does not change the product projection. A new
`fork_turns=none` read-only reviewer will receive the immutable baseline and product
repair, the verbatim operative request and frozen Outcome/exclusions, and a neutral
request to audit every diff unit and obligation. It must reproduce all eighth-review
producer-binding probes; trace sanitizer, impact, runner, source-oracle, recovery,
compaction, and holdout producer reachability; verify the corrected 20-to-22-call
scope and privacy-safe receipt projection; and hunt any new completion blocker or
over-strict unreachable acceptance path. Its durable terminal output destination is
agent task `/root/cert_engine_producer_final_review`. Only local detached clones and
offline validators are allowed; repository writes, model/live evaluation, network,
Fable, Goal actions, installation, activation, Git ref mutation, push, and
publication are forbidden.

Phase 1 completed in that same fresh reviewer session before candidate disclosure.
The reviewer inspected only detached baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`, tree
`c27536825a34421522fbf1b3b759f2cc63aa8144`, then removed its temporary snapshot.
It emitted 27 stable independent obligations, `HC04-01` through `HC04-27`, covering
the frozen outcome/exclusions, module and stdlib boundaries, canonical separated
identities, exact read-only impact/cost, single-ledger semantics, legacy retirement,
persisted pre-live authority, package/runtime/fixture/runner/holdout preservation,
evidence safety, deterministic fail-closed behavior, offline closure, and exact fresh
review. Root's SHA-256 over UTF-8 canonical lines `ID<TAB>text<LF>` is
`7fe6d7b67f90813af551a925de8ad76d9cda570347bb6ecd6d23b0c1db00c9fb`.

The Phase-1 baseline inventory covered 56 tracked paths, 14 corpus cases, three
holdout cases, 22 legacy result/index files, Python imports, CLI surfaces,
identity/digest functions, legacy-result references, and shipped-package paths. It
read policy, public/evaluation documentation, both old runners, relevant contract
tests, metadata, and case/holdout envelopes. It did not inspect the source worktree,
candidate, diff, this ExecPlan, historical-result bodies, prior findings, writer
narrative, Root conversation, or candidate evidence, and ran no validation or
prohibited action. Detailed obligation text remains in the durable terminal record
for `/root/cert_engine_producer_final_review`.

## Ninth fresh review and terminal-evidence NOT-YET

The same uncontaminated reviewer then audited exact product
`e15887042d4a1df271abf46ab97d6bef5da7426f` and administrative head
`595cc7d7a76e263be9728a24ca9f41fb5e79ddb1`. It verified product tree
`85b0c8a1e9136ee5e89a49cee9bb205828e2655c`, administrative tree
`438eb1014d6e706f23da294d39e394fd3b521854`, the sole excluded ExecPlan
delta, and the 49-entry product projection
`c10fcdff74c60c3cdc43dffa4e96cf0e59187c056a3398659ef4ab44972c8866`.
Its first terminal rendering was platform-filtered after the audit completed; the
same reviewer session reissued the unchanged conclusion without rerunning or adding
analysis. Verdict: `NOT-YET` with four P1 terminal-evidence findings:

1. A live-authority response is content-addressed but need only be nonempty, so an
   explicit rejection of the exact request still grants authority.
2. Impact cost is derived exactly, but the ledger accepts any dictionary as its
   persisted historical-cost receipt, including the empty object used by the
   certification fixtures.
3. Native compaction binds one rollout path, changed whole-file hashes, and an event-
   type prefix, but carries no prior byte length or after-prefix digest. A rewrite is
   therefore indistinguishable from an append at terminal validation.
4. Fresh-review evidence is reachable and content-addressed but otherwise only
   required to be nonempty. A payload without verdict, exact reviewed source/scope,
   reviewer receipt, obligation coverage, or blocker state certifies.

The reviewer independently reconciled 16 corpus plus four-to-six holdout model calls
to the exact 20-to-22 range and the persisted 585,209-to-637,027 token and
2,911.874-to-3,187.085 second estimates. It passed the offline unit/validator/Ruff/
CLI/JSON/diff matrix and package, public, legacy-retirement, projection, identity,
authority-null, and preservation checks. It found no authentic-producer over-strict
rejection, no separate material producer race, and no excluded or external action.
The runtime exposed the configured evaluation target `gpt-5.6-sol`/`high` but no
separately attestable effective reviewer model/effort; this is disclosed, not
substituted.

Root reproduced the union before product edits. A digest-correct response stating an
explicit rejection passes `validate_live_authority`; replacing the current exact
historical-cost receipt with `{}` passes `validate_ledger`; the complete reachable-
certification test passes with review evidence containing only
`reviewed_source_commit`; and the sanitizer/validator source contains no byte-length
or prefix-digest material from which append consistency could be proven. These are
accepted false greens, not requests for broader architecture.

The minimum repair is terminal-evidence only: require a canonical affirmative
response derived from the exact approval request; validate the persisted cost
envelope exactly; add privacy-safe rollout byte-length/prefix proof to the native
receipt; and require a small strict fresh-review receipt binding a `GO` verdict,
exact reviewed source/product scope, reviewer/session/effective-profile disclosure,
the frozen obligation manifest and diff inventory, limitations, and zero unresolved
material blockers. The append receipt adds audit metadata inside the clean-break
internal runner schema but changes no model call, prompt, fixture, oracle, permission,
comparison, adaptive, Skill, manifest, or shipped Runtime behavior. The review
receipt is evidence schema, not a controller or general reviewer orchestration
protocol.

Invalidated evidence is limited to engine/snapshot/ledger/impact identities, native
receipt and certification tests, the current ninth review, and downstream offline
identity receipts. There is no current live authority, corpus successor, holdout,
install, or release receipt to invalidate. Required rerun cost is the focused RED/
GREEN, cumulative 115-test-class suite, official validators, Ruff, verify/impact,
dry-runs, JSON/diff/package/public checks, and one new exact fresh review. Expected
model cost remains zero; the pending live approval scope remains 20 to 22 calls and
is not authorized or run.

## Ninth terminal-evidence RED

Two exact offline commands now reproduce all four accepted findings before any
production edit. The first runs the historical-cost, authority, sanitizer, and
producer compaction probes. It reports four tests with two failures and two errors in
0.546 seconds: `{}` historical cost and an explicit rejection do not raise; the
sanitizer omits rollout byte count/prefix identity; and the production compaction
receipt has no prefix-length interface or byte-count receipt. The second runs the
complete reachable Git certification fixture after replacing its substantive
review payload with a later content-addressed one-field payload. It reports one
`ValueError not raised` failure in 0.863 seconds.

The positive fixture now carries a proposed minimal review envelope binding `GO`,
review task/session, configured/effective profile, read-only permissions, baseline,
source commit/tree, snapshot/engine/authority, exact non-review evidence digests,
obligation/diff/query/path coverage digests and counts, limitations, and unresolved
material findings. The existing validator accepts both that envelope and the later
one-field replacement, which isolates the missing schema rather than making the
positive path unreachable. No production, Skill, manifest, case, oracle, model,
network, Fable, install, or external action changed or ran.

## Ninth terminal-evidence repair green

Live authority now accepts exactly one affirmative response derived from the already-
validated approval-request digest:
`APPROVE HAPPYCODEX LIVE COST <approval-request-sha256>`. The request binds snapshot,
impact including exact cost, token, and every invocation; any rejection, paraphrase,
stale digest, or extra text fails. The historical-cost receipt is mechanically rebuilt
from the 14 per-case costs/call counts and adaptive two-to-three-pair policy, then
compared to the ledger as an exact object rather than a type.

The native producer now records rollout byte count on both phases and, after resume,
the SHA-256 of the prefix whose length equals the complete pre-resume rollout. The
sanitizer retains only count and digest; terminal validation requires a null prefix
on the before phase, after-prefix equality to the before whole-file digest, a strictly
larger after byte count, the same privacy-safe path identity, changed whole-file hash,
and the existing event append prefix. The runner also records a local failure if its
own receipt is not append-consistent. No rollout bytes or path prose enter evidence.

Fresh-review JSON now has one strict versioned terminal envelope rather than an
opaque object. It requires `GO`, reviewer task/session, configured/effective profile,
read-only/no-network permissions, exact prior baseline and successor source/tree,
snapshot/engine/authority, exact non-review evidence digests, positive and fully
covered obligation/diff inventories, query/path inventories, limitations, and zero
unresolved material findings. The validator independently recomputes the Git diff and
inspected-path manifests. A later content-addressed one-field review, `NOT-YET`, wrong
source/evidence/diff, incomplete coverage, or retained blocker is rejected.

All original REDs and the added relationship counterexamples are green. The focused
certification module passes 31/31 in 5.219 seconds and the cumulative suite passes
116/116 in 6.475 seconds. Both official validators, Ruff check and 19-file format-
check, verify/impact, both dry-runs, all 21 JSON documents, diff hygiene, exact
snapshot equality, shipped-package preservation, and isolated public reconstruction
pass. Current identities are engine
`3df4d26aa9df66a5ea9b472bddc7923c1d3f24a430adbd3c69fa744731bbaec8`,
snapshot `d36e582e7a4f9351e893d8b9591076912940343ccf353e6e6e20abb0e662227e`,
ledger `9e7de1b85ab7b542504ff3948053347c96a2a758dcebd12d81cfb9615eaa2bf9`,
and impact token
`68f00b5c573a58209f99bdc82b1d0d9784f3b40b23a654014a096b20380b9760`.

The shipped package remains
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`.
Frozen public commit `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` again reproduces
semantic `fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
public-bound impact is authority-ready at 20 to 22 calls. Live authority remains null,
cost remains 585,209 to 637,027 tokens and 2,911.874 to 3,187.085 seconds, and no
model, live evaluation, network, Fable, install, publication, or external mutation
ran. A tenth exact fresh review remains mandatory.

## Tenth fresh review launch

The frozen terminal-evidence repair is
`e29ddc872b9446e1d13dce5ba73dcdc200c63bad` with tree
`25cd795ca50d89da7a779130055bf5b405fa177e` over baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`. Its 49-entry product
projection, excluding only this ExecPlan, is
`38ac643470370cbfb6df8efcdf80891d89c3789b8f8caae8860866126cad6d2f`.

A clean detached local clone reproduced 31/31 focused tests in 5.101 seconds and
116/116 cumulative tests in 6.477 seconds. Both official Skill/plugin validators,
Ruff check and 19-file format-check, verify/impact, both dry-runs, all 21 JSON
documents, baseline-range diff hygiene, shipped-package preservation, public archive
reconstruction, public-bound impact, exact current snapshot equality, and clean final
status passed. Engine, snapshot, ledger, impact token, package, public identities,
null authority, corrected cost, and 20-to-22-call scope match the preceding repair
receipt. The temporary public archive is removed; the detached preflight clone will
be removed after launch. No prohibited action ran.

This launch record is administrative and leaves the product projection unchanged. A
new `fork_turns=none` read-only reviewer will receive the immutable baseline and
repair plus the verbatim operative request and a fresh contract-only obligation
phase. It must audit the entire range and every diff unit, independently exercise all
ninth-review RED/GREEN relationships, test authentic producer reachability and
over-strict rejection, recompute cost, and hunt any new completion blocker without
using prior findings or writer narrative. Its durable terminal output destination is
agent task `/root/cert_engine_terminal_evidence_final_review`. Only local detached
clones and offline validators are allowed; repository writes, model/live evaluation,
network, Fable, Goal actions, installation, activation, ref mutation, push, and
publication are forbidden.

Phase 1 completed in that same fresh reviewer session before candidate disclosure.
It inspected only detached baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`, tree
`c27536825a34421522fbf1b3b759f2cc63aa8144`, plus the installed process Skill used
to enforce review isolation, and then removed its clean temporary clone. It emitted
20 stable candidate obligations `HC04-O01` through `HC04-O20`; Root's SHA-256 over
UTF-8 canonical lines `ID<TAB>text<LF>` is
`c9f418868bb828efd75b9a1a0ea92360edc9b797b8092a638f5738e63df1a55d`.

The obligations independently cover exact scope/exclusions, clean-break modularity
and legacy retirement, three identity domains, read-only impact and historical cost,
single-ledger and persisted authority semantics, corpus/evaluator/package/compaction/
holdout/blinding/adaptive preservation, evidence hygiene, exact shipped Runtime, and
offline closure. Seven additional baseline facts bind path/count and historical/public
identities; three limitations disclose static-only Phase 1, candidate isolation, and
bounded historical/test reads. It did not inspect the current branch/worktree,
candidate/admin commits or diff, this task ExecPlan, prior reviews/findings, writer
narrative, or Root conversation, and ran no test, validator, model, live evaluation,
network, install, Fable, Goal, ref, or source-write action. Detailed text and baseline
receipts remain in the durable Phase-1 terminal record for
`/root/cert_engine_terminal_evidence_final_review`.

## Tenth fresh review and architectural stop

The same isolated reviewer completed Phase 2 against exact product commit
`e29ddc872b9446e1d13dce5ba73dcdc200c63bad`, tree
`25cd795ca50d89da7a779130055bf5b405fa177e`, baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`, and administrative head
`f1b07be4dbe4d9a67707d0736521f8ce882c8e54`. It verified that the administrative
delta contains only this ExecPlan and that the 49-entry product projection remains
`38ac643470370cbfb6df8efcdf80891d89c3789b8f8caae8860866126cad6d2f`. All 20
frozen obligations were mapped under manifest
`c9f418868bb828efd75b9a1a0ea92360edc9b797b8092a638f5738e63df1a55d`.
The reviewer classified its `HC04-O08` historical-cost evidence as limited because
the v21 corpus costs were reproducible but the cited v23 holdout receipts were not
reachable in the supplied history. Its configured/effective model and effort were
not exposed by the review surface. These are disclosed limitations, not a substitute
for the material findings below.

The terminal receipt is `NOT-YET` with an explicit over-optimization verdict of
`YES`. It confirmed five blockers:

1. Live authority is bypassable through genuine runner seams. Corpus execution in
   `evaluation/corpus/engine.py:2006-2028` and holdout execution in
   `evaluation/holdout/engine.py:212-217,254-265` accept syntactically valid digest
   strings and can reach the evaluator/pair runner without loading and validating the
   persisted authority used by `evaluation/live.py`.
2. Fresh-review evidence is not bound to the frozen obligation manifest or the
   correct product projection. `evaluation/core/ledger.py:863-879` validates positive
   and equal counts but not the frozen manifest digest; the accepted test receipt at
   `tests/test_certification_engine.py:1295-1329,1496-1505,1553-1572` uses two
   invented obligations. `_review_diff_receipt` at
   `evaluation/core/ledger.py:753-794` reconstructs 47 units by including this task
   ExecPlan, while the frozen product boundary has 46 changed units before the
   separately attested administrative plan.
3. An artifact-only refresh with zero live calls can be planned by
   `evaluation/core/impact.py:559-563`, but authority rejects a zero-command scope at
   `evaluation/core/ledger.py:459-465` and certification always requires authority at
   `evaluation/core/ledger.py:1985-1987`. That state is therefore impossible to
   certify.
4. The authentic holdout comparator can label candidate-pass/public-fail as `better`
   under `evaluation/holdout/compare.py:15-24`, but terminal validation rejects the
   timed-out or nonzero public arm under
   `evaluation/core/ledger.py:1543-1553,1895-1935`. The producer and consumer
   disagree on a reachable outcome.
5. Impact can plan a partial pending holdout at four to six calls under
   `evaluation/core/impact.py:580-614`, while `evaluation/live.py:147-150` requires
   the complete manifest pair set. The reported minimal rerun cannot be executed.

Root independently reproduced the core relationships read-only: the direct corpus
and holdout entry points perform digest-shape checks without persisted-authority
validation; the review validator does not compare its obligation digest to the frozen
manifest; baseline-to-product raw diff has 47 units only when this administrative
plan is included, versus the 46-unit product boundary; zero-call refresh, failed
public-arm comparison, and partial-holdout planning each reach the contradictory
paths above.

The ordinary offline envelope still passes: 31/31 focused and 116/116 cumulative
tests, both official validators, Ruff check and format check, verify/impact, both
dry-runs, 21 JSON documents, diff hygiene, legacy absence, package/public identities,
chronology, and null authority. Those green checks are insufficient because their
oracles encode or omit the contradictory reachable states. No model call, live
evaluation, network, install, Fable, push, publication, ref mutation, or product write
ran during the review or Root reproduction.

This is an architectural stop, not another bounded receipt-only repair. A coherent
next change crosses runner-entry authority, the zero-call/live refresh state machine,
the review/product-boundary contract, holdout failure semantics, partial impact/live
scope, and historical-cost provenance. Continuing one finding at a time would deepen
the already confirmed over-optimization. Product code remains frozen pending an
explicit user choice between a simplifying clean-break refactor, a deliberately
narrow repair with accepted complexity, or abandoning this 0.4 candidate.

If a repair/refactor is authorized, its minimum offline rerun is focused RED/GREEN
coverage for all five relationships, the cumulative 116-test suite plus new tests,
both official validators, Ruff, CLI verify/impact and dry-runs, JSON/diff/package/
public checks, and a new fresh isolated review. The code repair itself requires no
live model cost; the previously estimated 20-to-22 live calls remain unapproved. If
holdout runner, comparator, oracle, or evaluator behavior changes, prior behavior or
holdout receipts affected by that semantic change become invalid and must receive a
new frozen impact/cost estimate before any live run. No expensive behavior, holdout,
or full review rerun is authorized at this stop.

## Simplification-refactor authorization and freeze

The operative user clauses already authorize a high-benefit internal clean-break
refactor without compatibility and then direct Root to define the Goal and execute.
They do not authorize changing shipped Runtime bytes, live cost, Fable, or any other
Outcome boundary. The tenth review does not create a new Outcome: its five findings
are in-contract defects in the certification engine. Root therefore resolves the
previous architecture-choice stop in favor of a simplifying repair, using that
verbatim authorization rather than treating Goal continuation as an amendment.

Fresh baseline-only challenger `/root/cert_engine_simplification_challenger` compared
four materially distinct designs at baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e` / tree
`c27536825a34421522fbf1b3b759f2cc63aa8144`: stateless receipt scanning, SQLite,
append-only JSONL, and an atomic JSON snapshot ledger with a pure planner and thin
authority-gated executor. It selected the last option at design saturation. Stateless
scanning cannot persist pre-call authority atomically; SQLite adds an opaque migration
surface unnecessary under one writer; JSONL adds replay and superseded-state recovery.
The selected design matches the repository's inspectable single-ledger boundary.

The challenger inspected baseline policy, package/public surfaces, evaluator runners,
holdout policy/manifest, and relevant tests in a removed temporary archive. It did not
inspect candidate code, this task ExecPlan, result JSON, later commits, Root context,
or prior reviews. One bounded `tests/test_evaluation.py` read indirectly exposed a few
historical snapshot status/failure labels; the challenger excluded them from its
reasoning, so the receipt is useful but not represented as strictly uncontaminated.
No prohibited action ran.

Root accepts the challenger's planner/executor/ledger boundary but rejects a new
`certify.py`, persisted `inflight` controller, retry state, and external ledger: the
existing `evaluation.cli` plus `evaluation.live` can be the sole coordinator, the
tracked `current.json` is the already-frozen single ledger, and controller/recovery
state is outside the Outcome. The frozen simplification is:

1. `evaluation.cli` is the only live command surface. The ledger validator returns a
   non-serializable authorized-invocation capability after validating the exact
   persisted authority. Corpus and holdout modules expose read-only list/dry-run
   commands plus capability-gated leaf execution; raw digest strings can no longer
   reach a model runner.
2. Native review remains the required external HappyCodex completion gate, persisted
   in this ExecPlan and an administrative Git revision. The evaluator no longer
   implements a second reviewer protocol or attempts to infer obligation coverage,
   query work, or product-tree review from self-authored JSON. Terminal evidence keeps
   content-addressed corpus/holdout receipts; the external exact-product review still
   excludes only this ExecPlan. This changes an internal clean-break receipt schema
   under B-01 while preserving O-07 itself.
3. Certification derives the exact impact from the authority-bearing source ledger.
   Nonzero live scope requires the exact authority; zero-live artifact/install/receipt
   refresh requires authority to remain null and may certify from exact prior coverage
   plus source identity. No fabricated zero-call authority is introduced.
4. Any holdout invalidation expands to the complete ordered manifest because the
   adaptive runner always starts at pair one and may reach pair three. A partial
   pending pair set is normalized to that executable scope, so impact and live dispatch
   share one contract.
5. Holdout quality compares only completed, exit-zero, non-timeout arms. Infrastructure
   timeout/nonzero results abort the pair instead of becoming evidence that either
   product is better; an exit-zero oracle failure remains an authentic failed arm and
   can still produce `better`. Producer and terminal validation share this rule.
6. Historical cost retains observed estimates but gains exact durable provenance. The
   locally retained v23 raw artifacts reproduce run receipt
   `bb2fa16edfd82c3da004d630bcdc87a098488ae483a1026b012ce117447fd580`,
   summary `f301f23d0d841deaef538cf07d9fba36705ebb175a3a1e4f099bb68cfc91ea3d`,
   and ordered pair receipts
   `18164c21533563b15bc483996e0f9a8db6c2080b7e3bf819dd2a003948395c82`,
   `27c1bcbf3566379b7c71255fadddcda5aa82509d3f01d15a170933a527de5f2c`,
   and `10b6cf8a40bdb9d1097d287d80a9c7106686f6b6c19458984366994833f2c3a2`.
   The reachable baseline plan blob is
   `a5b16c5edb54324ee0a7a2efb17a7d7fdef3f207`; only these privacy-safe
   identities and derived metrics enter the ledger, never raw output.

This refactor intentionally invalidates the current engine/snapshot/ledger/impact
identities, the tenth review, machine-review-receipt tests, direct-runner tests, and
holdout infrastructure-failure semantics. The v23 quality receipt is not reusable as
0.4 behavior evidence after the runner rule changes; its immutable raw cost metrics
remain valid historical observations. There is no 0.4 live authority, corpus,
holdout, certification, install, or release receipt to invalidate. The current full
20-to-22-call pending scope already covers the changed runner and holdout policy; no
cost increase is introduced and no live call is authorized.

Before production edits, RED must prove all five tenth-review relationships plus the
recovered cost provenance. GREEN requires focused tests, the cumulative suite, both
official validators, Ruff, verify/impact, both dry-runs, JSON/diff/package/public
checks, and one new fresh isolated exact-product review. Review-protocol removal is a
code deletion and external-gate clarification, not a waived review. No expensive
behavior or holdout run occurs until that review is `GO` and the exact maximum cost
receives explicit user approval.

## Simplification relationship RED

RED revision `b239487` adds only tests and no production change. One exact offline
command exercises six named relationships and reports six tests with five failures
and two errors in 1.707 seconds: a one-pair pending holdout remains one pair; impact
cost has no provenance; machine certification still contains a reviewer protocol;
fabricated digest strings reach the corpus evaluator before the holdout subcase can
run; a real Git-backed zero-live artifact refresh raises because authority is
unconditionally required; and both timeout and nonzero holdout arms enter blind
quality comparison. The existing error/failure messages map one-to-one to the frozen
design and do not depend on a model or external service.

Ruff check/format and diff hygiene pass for the RED revision. No product support file,
Skill, manifest, case, oracle, runner, evaluator, ledger, live authority, model,
network, Fable, install, or publication action changed or ran. The next write is the
single coherent implementation; splitting these relationships into independent
patches would recreate the contradictory intermediate states this refactor removes.

## Simplification coherent GREEN

The coherent implementation now matches the frozen planner/executor/ledger design.
`evaluation.live` is the only live dispatcher and mints a non-serializable in-process
capability only after exact persisted-authority validation. Corpus and holdout leaf
commands retain list/dry-run behavior but reject live execution without that
capability; each leaf rebinds the exact invocation settings and package identities
before a runner can start. The adaptive holdout scope is always the full manifest,
while its receipt preserves manifest execution order. Native review is removed from
the evaluator schema and remains the external exact-product HappyCodex gate recorded
here. Certification derives impact from the source ledger, requires authority only
for nonzero live scope, and accepts a null-authority zero-live transition with exact
prior coverage. Shared completed-execution quality rejects timeout/nonzero
infrastructure failures before either arm enters comparison. Historical estimates now
carry the frozen baseline, corpus, selected-receipt, holdout-run/summary, and three
pair-receipt identities.

The exact six-test RED command is GREEN at 6/6 in 2.368 seconds. The final cumulative
offline suite is GREEN at 120/120 in 7.055 seconds. Both official Skill and plugin
validators pass; Ruff check and format-check over 19 files pass; CLI verify, impact,
corpus dry-run, and holdout dry-run pass; all 21 tracked JSON documents parse; and
baseline-range/working-tree diff hygiene passes. Root's post-GREEN diff audit also
closed four second-order inconsistencies before freeze: adaptive authority pairs are
compared canonically while run receipts retain manifest order; corpus capability
execution rechecks the package identity; a later 0.4 full rerun need not fabricate
prior coverage merely because its lineage is incremental; and the invocation
capability cannot be pickled into a reusable receipt.

Current identities are engine
`e9bc0470dfa4abeecbd9f8fe63aea2bd9cd54e1b9ef7aa5ffb78e925d868b0de`,
snapshot `b27fa24202b3ab7f3d0789e99698386a12963f661af0ebc73c683cb97bcb893a`,
ledger `582a9cd3051d7971bf1b957d626670a156421098b9d942c7d6addbbac5bc7ca7`,
and impact token
`eae29a5acef7219d1ac6b1813032aaadfed8dd6e7ee1d762b194ce8420f4afea`.
The shipped package remains semantic
`c5030e99dd7cd1681148c069775671c5720bb8dd366930ff90f61cbc54cdfc05`
and artifact
`0c83dbc694cb98bf811dd2d1c199b5d2aa734c484476a638884e775289c1d934`;
the four shipped-package paths are byte-identical to the baseline. Frozen public
commit `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` reproduces semantic
`fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`
and artifact
`77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
public-bound impact is authority-ready at 20 to 22 calls. The coherent diff is net
negative at 342 added and 425 deleted lines. Live authority remains null. No model,
live corpus, live holdout, network, Fable, install, plugin mutation, push, or
publication ran.

## Simplification candidate and final review launch

The coherent semantic candidate is
`24ace04dd2ffc194014511434171fd3ad045feea`, tree
`a5031a243f46a67f76dbe76528c4d22615ae0b0b`, over immutable baseline
`2836d7363db364807a2ec384dc1b6c2cc13df95e`. Its 49-entry product projection,
computed as SHA-256 over the newline-terminated `git ls-tree -r` manifest after
excluding only this ExecPlan, is
`5f186f09b2268d4266d48956863a98d2f9d85597abfb0b356087d33e2cd0d54e`.
The baseline-to-candidate product diff has 46 `--no-renames` units and raw manifest
SHA-256 `c6d4eb51958e2bee11be00acb7848374e6f017f28d83a3e40f4b4d6032a08198`.
The semantic commit carries the mandatory ExecPlan trailer; this launch record is the
only uncommitted administrative delta.

A clean detached local clone of that exact candidate reproduced 120/120 tests in
6.896 seconds, both official validators, Ruff check and 19-file format-check, CLI
verify/impact and both dry-runs, all 21 JSON documents, baseline-range diff hygiene,
shipped-package preservation, frozen public reconstruction, public-bound impact, and
a clean final status. Engine, snapshot, ledger, impact token, candidate package,
public package, null authority, 20-to-22 calls, and two public-bound invocation
descriptors exactly match the preceding GREEN receipt. The detached clone and public
archive were removed. No model, live evaluation, network, Fable, installation,
activation, plugin/marketplace mutation, Goal mutation, push, publication, or Git ref
change ran.

The HappyCodex Skill now requires one new `fork_turns=none` read-only reviewer. Its
first phase receives only the immutable baseline and the verbatim operative request
to freeze candidate-independent obligations. Only after that durable freeze may it
receive the exact semantic candidate, product projection, diff manifest, and this
review brief: audit every product diff unit; reproduce all six RED/GREEN relationships
and Root's four post-GREEN consistency checks; verify the simplified external review
boundary, source-ledger/zero-live state machine, completed-execution semantics, cost
provenance, package/public preservation, and exact offline envelope; then hunt any
new completion blocker and give `GO` or `NOT-YET` plus an explicit over-optimization
verdict. The reviewer may use only removed temporary clones and offline tools. Source
writes, model/live evaluation, network, Fable, install, activation, plugin mutation,
Goal actions, ref changes, push, and publication are forbidden.

## Validation envelope

Candidate offline commands, exact live-run costs, required reruns, and review launch
records will be frozen before their respective actions. Fable is not a gate for this
task. External push, PR, active-plugin mutation, manifest/cachebuster edit, or release
publication requires a later explicit user request.

## Checkpoint

- Milestone: semantic candidate `24ace04` and its clean detached preflight are GREEN;
  all five architectural contradictions and historical provenance are repaired, and
  only the fresh exact-product review remains open in the offline phase.
- Goal: active `019f780e-925e-7193-8bd2-0a04d6efe31e`; its objective is the
  Normalized Outcome plus all frozen preservation, exclusion, offline validation, and
  live-cost gates in this document.
- RED/GREEN: simplification RED `b239487` is durable at six tests, five failures and
  two errors; semantic candidate `24ace04` is GREEN at 6/6 focused and 120/120
  cumulative tests with both official validators and the complete offline envelope.
- Next: freeze candidate-independent obligations, disclose `24ace04`, and complete the
  fresh isolated exact-product review; repair only a confirmed in-contract blocker.
- Product/support writes: semantic candidate paths are frozen during review;
  shipped-package paths remain closed.
- Owned paths: `evaluation/`, `tests/`, `AGENTS.md`, and this ExecPlan; shipped-package
  paths remain closed.
- Missing facts: fresh exact-product review receipt, explicit user cost decision, and
  any later live successor receipts.

## Retrospective

Fill only after every completion gate closes.
