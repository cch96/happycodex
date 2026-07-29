# HappyCodex 0.4.1 convergence

Protocol: `HappyCodex/0.3` (the active 0.4.0 maintainer runtime)
Invocation: `$happycodex:happycodex`
State: `closed`; 0.4.1 released and activated under explicit review/test waivers
Review mode: `none`
Writer: none after final claim reconciliation
Resume: read this complete current index and reconcile its one selected checkpoint, Git,
claims, tests, agents, and gates before any write, review, or completion.

## Outcome, authority, and exclusions

Ship a clean-break HappyCodex 0.4.1 from public 0.4.0 with resource-scoped single
writers, family hardening, bounded repair recurrence, compact current ExecPlans,
`protocol_review_mode`, fresh evidence, neutral exact-final review, public release,
personal upgrade, and retained 0.4.0 rollback. After closure, separate successor tasks
and fresh ExecPlans resume the two named long tasks and port the same semantics to the
frozen 0.5 candidate; no 0.4.1 or old 0.5 product evidence transfers.

The direct implementation amendment is the 4,187-byte user message beginning
`PLEASE IMPLEMENT THIS PLAN: # HappyCodex 0.4.1 RB-008 有界收敛重构`, received in
task `019fa9c7-0d4c-72e0-b920-7231a4dab31c`; exact UTF-8 SHA-256:
`54d9bc3107decb4395002fd6d7167adae9e82aaa4fb593aa95dee211a66588ea`.
It selects the expanded `RB-008` boundary refactor, including terminal-wave
recurrence and the stateless resource-claim helper, but grants no live evaluator,
release, publication, installation, or activation action.

The user's exact `corpus/holdout 不用了` waiver has UTF-8 SHA-256
`3c9083ac67b403ae56f4622124b6291d97d46950553ee941dac50eff3c50a0c2`.
It waives only final-candidate corpus and holdout for this unchanged Outcome. Offline
checks, focused and exact-final reviews, release install/readback, activation, rollback,
and disclosure remain mandatory. The active ledger therefore has zero live calls,
zero authority, and only the review gate.

The user then canceled the focused falsification with exact text `证伪 不用了`,
UTF-8 SHA-256
`d2b577b327a5d2fe9bf62a42db66906860936c3d70122d8887ca467c56da0db3`,
and immediately authorized direct release with exact text `直接发布吧`, UTF-8
SHA-256
`159f03284929fd4af91d6202bb517d690641358d70203203f6831aa795dce347`.
Together these waive the one focused bypass review and the three neutral exact-final
reviews for this exact `e4ad487` product plus final cachebuster-only metadata. They do
not waive offline validation, exact install/readback, publication integrity, personal
activation byte equality, rollback rehearsal, or disclosure of skipped gates.

After personal activation the user removed the rollback-copy requirement with exact
text `不用考虑从回滚副本`, UTF-8 SHA-256
`49c44c1bfaf75a594924ceb4f6162664020b6219c42f5a7c38dbc1dfab87545b`.
The retained 0.4.0 source is therefore not used as release evidence and no downgrade
rehearsal is claimed.

No controller, Task State JSON, Evidence DAG, compatibility reader, dual write, old
schema alias, model-generated `family_id`, incremental certification, old-task
migration, or automatic stale-claim release may be added. Existing public/personal
0.4.0 bytes, cache, active tasks, other worktrees, and marketplace state remain
unchanged until their later gates.

## Frozen protocol contract

- Lifecycle is `implementation → focused_hardening → candidate_frozen → exact_final
  → closed`. Product-source change returns to hardening and invalidates the candidate,
  post-source evidence, and every exact-final review.
- Root assigns stable finding IDs and groups one invariant plus implementation boundary
  into `family_id`; models do not. Each family disposes source/identity,
  type/cardinality, order/terminal state, alias/mutability/TOCTOU,
  serialization/replay, and consumers/failure propagation through a counterexample,
  positive check, evidenced `N/A`, or open state.
- Reviewers of one candidate all reach terminal before Root reproduces their union and
  freezes a repair batch. Siblings found before terminal GREEN join that batch with
  RED coverage and expanded authority. Exact-final never runs mid-batch.
- A repair wave is terminal GREEN only when its batch and six surfaces are frozen,
  focused and cumulative checks pass, and its revision and evidence digest are durable.
  A later Root-confirmed same-family material finding, or credible safety/data-integrity
  `unknown`, increments recurrence whether or not the family was closed. Rejected,
  impossible, or nonmaterial findings do not.
- First recurrence sets `boundary_required`: only boundary writes may establish one
  authoritative choke point, remove bypasses, and rescan all six surfaces. After
  boundary GREEN, exactly one history-aware focused bypass falsification may close it.
  Infrastructure failure or reviewer pollution is replaced without consuming that
  falsification; product change invalidates it. A second recurrence after boundary
  repair stops for user choice to expand refactor, change contract, or abandon.
  Independent new families use their own instance batches.
- Ledger grammar is `Status: open | boundary_required | closed`,
  `Repair batch: <id>/instance | <id>/boundary`, plus recurrence count. During
  RED/repair/reconciliation, authorized writes require review mode `none`. When a
  stable wave's only gate is focused review, writing stops and mode is
  `focused_hardening`. `stop_for_user` permits neither writing nor review. Exact-final
  requires all families closed, no active write/reconciliation/finding/blocker/repair
  gate, and mode `exact_final`.
- One owner exists per shared mutable resource. Every task names worktree, branch/ref,
  ledger, output namespace, and activation target. Sorted CAS claims must all succeed
  before product writes and the owner token is verified before every write. Git claims
  live in the common Git directory; file/output/activation claims live beside the
  resource. Conflict, unwritable location, stale or unknown ownership fails closed
  without timeout. Disjoint resources may run concurrently.
- The ExecPlan is a current index: target 8,000 words, hard limit 12,000. It retains
  frozen contract, open claims/families, grant, candidate, valid evidence and
  invalidation, and pending gates. Closed history becomes reachable checkpoint,
  revision/archive, receipt digest, and invalidation relation. Recovery reads this
  index and exactly one selected authoritative checkpoint, never unbounded history;
  inconsistency, missing/tampered summary, unknown writer/worktree, missing agent,
  unreproduced receipt, or unaccepted failure fails closed.
- Existing recovery `marker_ids` bind one content-addressed Recovery Manifest kept in
  the ExecPlan or approved archive. It contains namespaced repository revision/tree
  tuples, all resource claims, exactly one selected ref or archive, writer, tests,
  agents, gates, phase, family status, batch kind, and recurrence. Compaction preserves
  those facts exactly.
- 0.4.1 accepts fresh genesis and either complete refreshed coverage or this exact
  waiver. Exact-final reviewers see exact frozen product bytes and neutral briefs, not
  this ledger, history, counterexamples, repair story, or preferred verdict. Focused
  reviewers may see them but cannot substitute for exact-final.
- The user plan allows Runtime/template up to 340 lines and 3,000 words, with
  300/2,600 targets. Repository maintainer packaging additionally requires at most 262
  lines and 2,400 words; it is an extra size guard, never authority to remove semantics.

## Source and mutable-resource ownership

Immutable public baseline revision:
`730c6a59d4f15eab9b40895e7ea9e0f4ee3522f5`, tree
`a7a0d228f8368244bb8799acd491646430c81ef9`.

Current worktree:
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.4.1-convergence`.
Branch/ref: `codex/happycodex-0.4.1-convergence` /
`refs/heads/codex/happycodex-0.4.1-convergence`.
Ledger: `evaluation/results/current.json`.
Output namespace: `/home/caichenghang/.codex/happycodex-0.4.1-rb008`.
Activation target: `/home/caichenghang/plugins/happycodex`.

The no-service claim receipt is
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/resource-claim.json`;
owner token is
`8258dd405f3826d6c2b7aceea77dfdb4a2fcb23f63e1b7f687ff1bd7c09d6298`.
It binds all five resources above. Worktree/ref claims use the Git common directory;
ledger, output, and activation use resource-adjacent atomic claim directories. The
active adjacent ledger claim is control state, not product input, and must be released
before focused review so the candidate worktree is clean.

Current grant `RB-008/boundary` may modify Runtime/template and the stateless claim
helper; shared lifecycle, receipt, recovery, coverage and ledger validators; direct
fixtures/oracles/tests; fresh `current.json`; unreferenced active-ledger summaries; and
this ExecPlan. It may not touch installed/public 0.4.0, marketplace/activation,
public/release refs, other worktrees/tasks/ledgers, or run corpus/holdout/model calls.

## Claims Ledger

| ID | Claim | Evidence / closure | State |
| --- | --- | --- | --- |
| `C-01` | Writer uniqueness is per overlapping mutable resource; disjoint worktrees/resources can run concurrently. | Atomic collision, concurrent-disjoint, partial rollback, common-dir, adjacency, and tamper tests. | verified |
| `C-02` | Same-family repair is bounded by terminal GREEN, first recurrence boundary repair, one bypass falsification, then closure or user gate. | Runtime/template, Recovery Manifest transition rules, durable GREEN revision; focused falsification explicitly waived. | closed by user waiver |
| `C-03` | Review/write/user-stop/exact-final states are mechanically exclusive through one raw/oracle/receipt/recovery boundary. | Transition matrix, missing-plan, open finding/blocker/repair gate, orphan blocker, lifecycle, and positive exact-final tests GREEN. | verified |
| `C-04` | Recovery is current-index plus one content-addressed checkpoint and fails closed on unknown or tampered facts. | Multi-repo Recovery Manifest, marker projection, claim receipt, post-commit compaction equivalence and tamper tests GREEN. | verified |
| `C-05` | 0.4.1 is a fresh-only clean break with no prior reader/disposition and exact zero-live waiver projection. | Ledger verify/impact and fresh/waived negative tests GREEN; exact-final explicitly waived. | closed by user waiver |
| `C-06` | Public invocation stays `$happycodex:happycodex`, and final 0.4.1 installs and upgrades safely. | Public tag install and personal source/cache readback are byte-equal; downgrade rehearsal explicitly removed. | closed |
| `C-07` | No live evaluator call occurs without a fresh exact authority. | Current ledger has null authority, empty invocations, zero cost/calls; corpus/holdout waived. | verified |
| `C-08` | Runtime/template retain full semantics within both applicable budget envelopes. | 261 lines and exactly 2,400 words; contract and official validators GREEN. | verified |

## Convergence Ledger

| Family | Invariant and boundary | Six-surface disposition | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- |
| `F-CONV-001` | One central state boundary governs raw result, oracle, receipt, recovery, and completion eligibility. | Identity and three modes; finding/blocker cardinality; lifecycle order; no prose readiness; raw/receipt replay; all consumers and failure propagation covered by RED/GREEN. | `closed` by explicit focused-review waiver | `RB-008/boundary` | Semantic revision and 163-test GREEN; no focused verdict | 2 |
| `F-CONV-002` | Writer ownership is exact for five shared-resource roles and permits disjoint concurrency. | Canonical identity; one owner per overlap; sorted acquire/release; race/tamper/TOCTOU; receipt/manifest replay; helper/runtime/template consumers covered. | `closed` by explicit focused-review waiver | `RB-008/boundary` | Six claim tests GREEN, including truly concurrent disjoint acquisition | 1 |
| `F-CONV-003` | Recovery is bounded, namespaced, content-addressed, complete, and fail closed. | Multi-repo/ref/archive/resource identity; one manifest/checkpoint; persist/recover order; unknown facts block; marker/receipt replay; fixture/ledger/runtime consumers covered. | `closed` by explicit focused-review waiver | `RB-008/boundary` | Recovery/tamper/compaction and install readback GREEN | 1 |
| `F-CONV-004` | Active 0.4.1 evidence is fresh-only and binds exact package/toolchain/waiver identities. | Fresh genesis; refreshed-or-exact-waiver cardinality; post-source order; no prior/ambient alias; ledger serialization; impact/validator/test failures covered. | `closed` by explicit focused-review waiver | `RB-008/boundary` | Clean-break tests and exact zero-live ledger GREEN | 1 |
| `F-CONV-005` | Cost authority distinguishes observed receipts from conservative history. | Closed details at reachable `RB-004` checkpoints. | `closed` | `RB-004/instance` | Focused GO retained in Git history | 0 |
| `F-CONV-006` | Public comparison identity is exact public 0.4.0. | Closed details at reachable `RB-005` checkpoints. | `closed` | `RB-005/instance` | Focused GO retained in Git history | 0 |
| `F-CONV-007` | Durable marker/path classifications use stable, nonblank, alias-safe identities. | Closed details at reachable `RB-006` checkpoints. | `closed` | `RB-006/boundary` | Eleventh focused GO retained in Git history | 0 |
| `F-CONV-008` | Fixed oracles enforce contract-valid alternatives symmetrically. | Closed details at reachable `RB-006` checkpoints. | `closed` | `RB-006/boundary` | Eleventh focused GO retained in Git history | 0 |
| `F-CONV-009` | Structured output keeps literal anchors, receipt domains, blockers, and lifecycle legible without fixture hints. | Closed details at `49fefed21e14cdd35633b75f865d7b7b7a735ed2`. | `closed` | `RB-007/boundary` | Thirteenth focused GO retained in Git history | 0 |
| `F-CONV-010` | A usable hardening plan with in-contract defects permits RED/repair while blocking completion. | Closed details at `49fefed21e14cdd35633b75f865d7b7b7a735ed2`. | `closed` | `RB-007/boundary` | Thirteenth focused GO retained in Git history | 0 |

`RB-008` is one frozen coupled boundary batch. Its terminal GREEN requires all four
open families to have frozen six-surface dispositions, cumulative checks, durable
revision and evidence digest. They then become `open` with boundary batch while one
history-aware choke-point bypass review is the sole gate. A material same-family
finding after that boundary repair is the second recurrence and must stop for the
user; Root will not add another patch automatically. A genuinely independent family
may start its own instance batch.

## Current checkpoint and evidence

Selected authoritative checkpoint is semantic GREEN revision
`e4ad487c54b1620a6b1df69f0e2c2c65c3316e7e`, tree
`33a582931d7a1ce14ad9437d731ab6a8375c466b`. Its filtered product manifest excluding
only this ExecPlan is
`9e6250758fdc4673ca372b60b68b746be45b0bdd4325c5781acf02f6ad52877d`;
filtered product tree is `f7f26601e4b68b5ee15df60e42c2466e3835a94a`.
Authorization checkpoint is `148da5dd83fd86bf7e1de1e2a0fe9ddd338a9b76`;
RED checkpoint is `20f376dd42e956c665677329e5691bbb88cf62e6`. No Goal,
agent, or reviewer is active; all prior review receipts are terminal and reconciled.

The frozen RED receipt is
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/red-matrix.txt`, 41,940 bytes,
186 lines, SHA-256
`1e8c4ca107e89c57c2674c16668d7f973c3e96bb197259a93adda5b8fbf168f8`.
Its 16 bounded tests produced 15 failures and two errors before repair, covering state
eligibility, missing plans, exact-final blockers/orphan blockers, Recovery Manifest,
fresh coverage, Runtime recurrence, bounded recovery, and atomic claims.

Current GREEN facts under pinned PATH
`/home/caichenghang/.codex/packages/standalone/releases/0.146.0-aarch64-unknown-linux-musl/bin`
plus its `codex-path` and system bins:

- 163/163 unit tests pass in 8.169 seconds.
- Ruff check and format-check pass; both official Skill/plugin validators pass.
- Corpus lists 17 cases and holdout lists three pairs; both dry-runs pass without a
  model call. Twenty-seven JSON files parse and 21 Python files parse as AST.
- Runtime/template total 261 lines and 2,400 words; `git diff --check` passes.
- Claim helper has six GREEN tests: overlap gives exactly one winner, disjoint five-key
  sets both win concurrently, partial acquisition rolls back, stale/tampered ownership
  blocks without release, ref uses common-dir, and file claim is resource-adjacent.
- `python3 -m evaluation.cli verify` reports status OK, engine manifest
  `ad0a4e83323f0f981ed0b342c82c7a84b6087e9a0bebe2cc32491fda878b3a9b`,
  snapshot `796b3a2752020562b1984c9b87d27ddb571c9a73a7221eda0f6a40aeb151c153`,
  ledger `8ec6e8de6bf4fc2f0b382a8867f84561671d7d33093b633ca8d2a46cdfaa2d0c`,
  state `refresh_required`, null authority, and only `review`.
- Impact token is
  `5477b0d0a40e92fcadcdb12063f2d3648570500bcf43f469ca10491ede7e3fd1`;
  corpus/holdout scopes and proposed invocations are empty, live calls/tokens/wall are
  all zero, and cost approval is false.
- Package semantic/artifact SHA-256 values are
  `b8db5a56384cd5341efd4cc61a3601e950d00a4ee0e8e8bce464a5a37282c795` /
  `af541d4ea57becdd7c15f194222567862478adcff9b61a38e1aeaeea6b32887b`.
  Codex is 0.146.0, SHA-256
  `cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6`;
  rg is 15.2.0, SHA-256
  `e36d0eb52e70696bdf1781392722e05a21bb91d3b7b762ef5ec20e5df2ec687b`.
- Post-commit recovery checks for exact Recovery Manifest binding, same-task versus
  fresh-task gate/state equivalence, false-equal state rejection, and durable
  post-compaction transition are 4/4 GREEN.
- Fresh isolated local marketplace root is
  `/home/caichenghang/.codex/happycodex-0.4.1-rb008/install.g60ays`. The installed
  cache reports enabled `0.4.1+codex.20260728205019`; source/cache package manifests
  both equal `694c6a07…05d4`, and source/cache Skill SHA-256 both equal
  `cdb1d9bab8b78b7cd85e7466523c4aa2e5a2cac5024dd30789b8369f3ede5411`.
  Canonical install readback receipt SHA-256 is
  `89082cfc0d39efb0987a9b8ee7d9805c0bd7044ed5eb8d99f50a583f57e471f3`;
  no model, public source, or personal installation was touched.

The final reconciliation command is predeclared as
`resource_claim.py release --receipt
/home/caichenghang/.codex/happycodex-0.4.1-rb008/resource-claim.json`, with stdout
persisted at
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/resource-release.json`.
The only accepted release receipt has SHA-256
`1d13a3bd9b8c58be8c5549634f1c0b320f8ccc1af7cc7fef4f8a585830a10ead`,
status `released`, owner token `8258dd40…6298`, and resource count five. Once it
exists and every claim directory is absent, no product write remains authorized,
`RB-008` is terminal GREEN, `F-CONV-001..004` are open boundary families awaiting
their single bypass falsification, and review mode is `focused_hardening`.

The four removed `offline-summary-*` artifacts are absent from the active ledger;
their exact bytes remain reachable in Git history. No active evidence references them.
The official plugin-creator cachebuster helper set the final version to
`0.4.1+codex.20260729085734`; no marketplace file was hand-edited.

Final release source is `c20cf21233a95c35bd1f1e43e5fab4d813b52585`;
PR [#4](https://github.com/cch96/happycodex/pull/4) merged it as
`ae07140b43e04f3a39499ebd9178c77f017067b8`. Annotated tag `v0.4.1` and the
[HappyCodex 0.4.1 Release](https://github.com/cch96/happycodex/releases/tag/v0.4.1)
are public. A fresh install from that exact public tag at
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/public-install.y7fb0w` returned the
final version and matched source artifact, semantic, and Skill identities; canonical
readback receipt SHA-256 is
`b1a1e809a812dc9142579e000ee19cc28dd75a3cd0d21721335395005c8413f4`.

Personal `happycodex@personal` now reports enabled
`0.4.1+codex.20260729085734`. Active source and cache both match artifact
`af541d4e…887b`, semantic `b8db5a56…c795`, and Skill
`cdb1d9ba…5411`; canonical readback receipt SHA-256 is
`176789f65d36fc776068e394db84267453ea5258f08ceecc5238990ec51bc0f6`.

Focused choke-point review is predeclared against exact product source
`e4ad487c54b1620a6b1df69f0e2c2c65c3316e7e` and the identities above. History-aware
brief
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-e4ad487.brief.txt`
is 1,589 bytes, 169 words, nine lines, SHA-256
`c42b3aae6c704b9da063e2d7bf0905f297a9a783cabd8106791fdd29432340af`.
Durable output is
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-e4ad487.txt`.
Exact command, from this clean worktree after administrative claims release:

```text
set -o pipefail; env PATH=/home/caichenghang/.codex/packages/standalone/releases/0.146.0-aarch64-unknown-linux-musl/bin:/home/caichenghang/.codex/packages/standalone/releases/0.146.0-aarch64-unknown-linux-musl/codex-path:/usr/bin:/bin /home/caichenghang/.codex/packages/standalone/releases/0.146.0-aarch64-unknown-linux-musl/bin/codex review -c 'model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' -c 'sandbox_mode="read-only"' - < /home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-e4ad487.brief.txt | tee /home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-e4ad487.txt
```

It was read-only/no-network and history-aware, but the user canceled it before a
verdict. Native session `019fad13-aba7-7d23-8bc6-8bbe621e7386` was terminated;
the durable output is zero bytes with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Partial stderr/tool activity is not evidence and no finding or verdict is retained.
Prelaunch claim
receipt is
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-prelaunch-claim.json`;
its accepted release receipt is
`/home/caichenghang/.codex/happycodex-0.4.1-rb008/focused-prelaunch-release.json`,
SHA-256
`11454a5a487584a6a12852b1f53577220a2601f1c344a6b57f5d4425cadbff88`.

## Invalidation and historical checkpoint index

Full pre-compression history is recoverable at
`20f376dd42e956c665677329e5691bbb88cf62e6:docs/execplans/happycodex-0-4-1-convergence.md`.
The compact index never asks recovery to traverse it unless that revision is the one
selected checkpoint.

- Public baseline: `730c6a59…3522f5`.
- Last waived candidate before exact-final: `2ebb6cc5a8cd05478763381fe7861038517ba4d6`;
  invalidated by confirmed exact-final findings.
- First exact-final union checkpoint: `fbb9965`; release, QA, and simplification
  sessions `019fac8d-d81f-7fd2-9b2e-aed3567b5f13`,
  `019fac8d-d826-7ae0-b0ef-f05fe1e8d0ab`, and
  `019fac8d-d832-7e82-b5a4-ab04eb2765ea` all returned `NOT YET`. Output digests begin
  `21c45a55`, `a27f51fe`, and `6204c9b2`; their complete reproduced union is frozen in
  `RB-008` and cannot satisfy final review.
- Design authority and RED checkpoints: `148da5d` then `20f376d`.
- Fable 5 design session `40eddcce-9b0a-4f27-bf87-637ea44c867e`,
  `claude-fable-5/max`, no tools/network, cost `$1.3704`, is advisory only.
- Historical live authority
  `f7185e8e0dc3c0071d0a3c41651cd7bae79d51c98bf7c3440aa96d4214fa7ae6`
  was consumed only by its old 17-case corpus (6/17 passed); holdout never started.
  Product changes invalidated it and the explicit waiver retires any rerun. Request
  `34c96c56…2950` was never authorized or consumed. Neither authorizes current work.

## Follow-up outside this release

Create fresh successor worktrees, ExecPlans, ledgers, and evidence for the old
HappyCodex/StockAI tasks and the 0.5 port. Do not migrate old task state or evidence.

Completion must explicitly disclose that corpus/holdout, focused review, three
exact-final reviews, and the downgrade rehearsal were waived or removed and not run.

## Validation-speed side amendment

The user request `好的你改一下` (SHA-256
`ebdfcd55dce6ef0a6b8d714335738600b7f6988abb44dac70be3c5c1e464b8d2`) authorizes
only a non-activating validation-speed patch derived from clean checkpoint
`6583631a9f6d9d94e6c1424c75c84f1a6321a3ad`. Root owns the isolated worktree
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.4.1-validation-speed`,
branch `codex/happycodex-0.4.1-validation-speed`, its index and this branch-local
ExecPlan, plus the evaluator, Runtime, template, and test paths changed below. It owns
no live-output namespace or activation target. The active convergence worktree,
candidate, reviewer, ledgers, public bytes, installation, and external outputs remain
untouched.

The frozen outcome has three parts: evaluate independent corpus cases with at most four
workers while preserving selected-case result order and per-case isolated output;
evaluate the two blinded arms of one holdout pair concurrently while preserving mapping,
blind-decision, reveal, pair ordering, and adaptive-stop semantics; and make `high` the
default focused-hardening review effort, escalating focused review to `max` only for a
recurring family or unresolved material uncertainty while exact-final remains `max`.
No case or pair may be removed, no fixture/oracle/adaptive rule may change, and no live
model call, authority reuse, release, install, or activation is in scope.

Verification must prove bounded corpus overlap with deterministic order, two-arm overlap
with deterministic alias order, and the focused/default/escalation/final effort
distinction. It includes targeted and cumulative offline tests, Ruff, both validators,
JSON/AST checks, and Runtime/template budgets. Any evaluator-source change invalidates
inherited candidate evidence; this side branch will refresh only its non-authoritative
offline ledger identity and will not claim certification.

Implementation checkpoint: corpus uses a fixed four-thread bound and ordered result
projection; a holdout pair uses two threads only across its already-isolated blinded
arms, with pairs still serialized by the unchanged adaptive loop. Runtime and template
bind focused `high`, limited focused `max` escalation, and exact-final `max`. The
deterministic concurrency tests plus the cumulative suite pass 148/148 in 8.203 seconds;
Ruff check/format, both official validators, 15 AST and 29 JSON parses, diff check,
17-case/3-pair list and dry-run, and pinned `verify` are GREEN. Runtime/template remain
308 lines and 2,721 words, below the 340/3,000 hard limits. The fresh side ledger is
`refresh_required` with no authority; snapshot `b6fa8494…090a`, engine
`f2aefadc…3a1f`, and ledger `5a9fbec6…0e5`. No live call ran. The impact report's
3,757.028–4,032.239 seconds remains conservative aggregate call-wall exposure, not
elapsed time after bounded concurrency.

## Retrospective

The release closed without further product repair after `RB-008`: the bounded family
model moved repeated sibling defects to four shared boundaries, while resource-scoped
claims allowed unrelated worktrees to remain independent. The public and personal
package bytes match. This is an explicitly user-waived release, not a certified one:
the evaluator correctly remains `refresh_required` with its external review gate.
