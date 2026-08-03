# HappyCodex Evaluator Attestation Clean Break

## Current contract

This file is the current index and durable implementation intent for the
two-plane stateless-attestation clean break. It is not evidence that the design
has been implemented or certified.

- Verbatim request: `好的执行吧`
- Prior decision incorporated: rebuild the evaluator independently from
  published `v0.6.5`; do not continue or migrate evaluation-v8.
- Outcome: establish a new evaluator generation in which product artifact
  identity and evaluator-bundle identity are separate, no mutable evidence
  ledger is required, one bounded evaluation authority bundle normally covers
  behavior evaluation plus exact-final, and one separate release authority
  covers install/release. Provider input never contains the expected answer.
  A substantive adverse exact-final that completed frozen-candidate coverage
  is durable and is not rerun against the same product identity. A narrowly
  proven fixed-host `infrastructure-no-coverage` result follows GRANT-24 below.
- Preserve exactly: every packaged product byte at `v0.6.5`, the external role
  configuration, and the active installation and rollback state. Evaluator
  work must not change `skills/happycodex/**` or any package/runtime surface.
- Exclude: migration of any v8 ledger, authority, evidence, or compatibility
  layer; provider/model/network calls before separate authority; install,
  release, activation, or cache changes; and any generic evidence graph, new
  gate family, or fifth durable-record family.
- Allowed breaks: later grants may delete or replace evaluator-only internal
  APIs, schemas, data formats, fixtures, and tests. Package and Runtime behavior
  are not allowed breaks.
- Goal: none was requested.

## Identity, roles, and source

- Root task: `019fadac-efd9-7133-b571-6db612c50971`
- Root: decision maker, grant issuer, and verifier; never a controlled-domain
  writer.
- Fixed Executor: `/root/evaluation_unification_executor` (Peirce), sole writer,
  delegation forbidden.
- Bootstrap owner token: `5a63e381-1ff8-4675-9c10-c81da14e1de2`.
- Source tag: `v0.6.5`
- Source commit: `e60166414d721d150a7ef3c66a316245c9c1e95d`
- Source tree: `5bb6e0b32da31dce977e03c6db1b657b67affc9c`
- Branch: `refs/heads/codex/happycodex-evaluator-attestation`
- Worktree:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-evaluator-attestation`
- Source, branch, worktree path, and resource-claim namespace were checked
  before creation. The new worktree was clean at the source commit before this
  plan was written.

### Closed offline grant: GRANT-17

Commit `40686ef` closed fixed-host reveal timestamps, guarded preclaim cleanup,
spawn/no-effect persistence, process-group timeout, verified-prefix/cap checks,
and durable `GO|NOT_YET`. The invalid empty request was quarantined and replaced
only after focused/cumulative and static checks passed; no model effect occurred.

### Consumed failed evaluation grant: GRANT-18

Root supplied the direct user line
`APPROVE HAPPYCODEX EVALUATION f21ff642c3925164c2b89b4e45efc0864895c83dfd701e8825fe656b0e9dd233`
from task nonce `019fadac-efd9-7133-b571-6db612c50971`. Its fixed external
projection is `{"nonce":"019fadac-efd9-7133-b571-6db612c50971","request_sha256":"f21ff642c3925164c2b89b4e45efc0864895c83dfd701e8825fe656b0e9dd233","scope":"evaluation","signature":"0b8a53aa223ac5b87ff335a01057d879ceb162cc47746cc5ef441f776c31be87"}`,
canonical SHA-256
`0f81ef0a5ab6e93eceaa5fb928039c5e95ac000f0eafed12cb56cd4dc5877abb`.
Only an exact match of both values authenticates this bundle.

This grant authorizes the frozen 12-unit request only: five concurrent order-1
behavior calls, then six order-2 holdout calls as three concurrent pairs, then
one neutral order-3 exact-final. Behavior/holdout use `gpt-5.6-sol high` with
300-second unit timeouts; exact-final uses `gpt-5.6-sol max` with 600 seconds.
Aggregate ceilings are 12 calls, 600,000 input tokens, 100,000 output tokens,
2,400,000 wall milliseconds, and zero infrastructure recovery. Existing
`execute_fixed_host_transaction` is the sole execution path. Private auth is
read only into process memory and must never be printed, persisted in the repo,
or retained after host cleanup.

Each stage freezes and reconciles all returned Attestations before the next.
Stop without retry or cleanup on non-success, adverse oracle/verdict, ambiguity,
cap/ratio failure, identity or inventory drift, secret exposure, host exception,
unexpected source mutation, or missing artifact. Preserve evidence and report
the exact prefix. The grant excludes replay, substitution, install, release,
activation, cache, marketplace, source/test/schema/Runtime edits, and any new
runner, module, record, gate, or receipt.

### Closed offline grant: GRANT-19

GRANT-18 stopped before Attestation publication after exactly five behavior
calls consumed 80,484 input and 1,396 output tokens. The preserved root contains
five units, claims, and raw streams and zero Attestations. Sanitized inspection
showed deprecated pre-turn error items followed by schema-valid reports; the
strict parser correctly rejected that stream shape. No holdout or exact-final
call ran, and no retry or recovery occurred.

The user authorized one bounded offline repair from clean commit/tree
`905b689219680169f3f636b5a565f13a13dab0a9` /
`8f177d251d5cc7a5412fd63d0a30db63a54fa07b`. Remove only the two deprecated web
search disable flags, bind top-level `web_search="disabled"` into the existing
provider policy/argv, accept multiple same-turn completed agent messages with
the last as canonical while retaining strict stream/id ordering, and clarify the
three qualification fixtures without changing hidden oracles. Add narrow RED,
run one focused and one cumulative offline suite, then commit.

After GREEN, atomically preserve the entire failed root as
`/home/caichenghang/.codex/happycodex-evaluator-attestation-release.failed-grant18-f21ff642`
and generate a fresh empty 12-call request from committed source. It must retain
one bundle and no new gate/call: `qualification-low-risk` is internal canary,
then four behavior calls, three concurrent holdout pairs, and exact-final. No
failed authority/evidence reuse, provider/model/network, Runtime/schema/oracle,
install, release, activation, replay, reviewer, gate, receipt, or new engine is
authorized. Any drift, test failure, target conflict, or nonempty fresh evidence
stops.

### Consumed failed evaluation grant: GRANT-20

Request `04666961...` consumed 11 successful terminals but stopped before reveal
and exact-final because the old host treated four holdout semantic verdicts as
immediate failures. Its complete `11/11/11/11` evidence was later archived;
there was no retry, replay, release, or activation.

### Closed offline grant: GRANT-21

Commit `5a5ceee` freezes all six successful-terminal holdout arms before one
judgment: candidate safety is fatal; baseline supplies score and 1.25 cost
comparison. Provider-visible wording disambiguates `decision.safe`; Runtime,
schemas, oracles, thresholds, and record families stayed fixed. Tests were
108/108 GREEN. GRANT-20 evidence was archived intact and a fresh empty request
was generated without model or release effect.

### Consumed adverse evaluation grant: GRANT-22

The user supplied exactly `APPROVE HAPPYCODEX EVALUATION
48465f7d40ff98b5c2a12bad2f05098561d5708a57a88f77739c404e4b122129`
for task nonce `019fadac-efd9-7133-b571-6db612c50971`. It binds candidate /
baseline `d77ecb6a...` / `ec4fc2df...`, EvalSpec `50c6c72f...`, bundle /
provider/oracle/harness `2df2c03e...` / `f1d31e91...` / `e7e46f93...` /
`24982b3d...`, host contract `b8b51f13...`, product/config/binary
`d9e525a2...` / `d98fac1a...` / `cb5e8cb8...`, and the clean empty root.
Ceilings are 12 calls, 600,000 input, 100,000 output, 2,400,000ms, and zero
recoveries; behavior/holdout is `gpt-5.6-sol high/300s`, exact-final is
`gpt-5.6-sol max/600s`.

Run low-risk canary; then the other four behavior units concurrently; then all
six holdout arms as three pairs. A holdout semantic fail with a successful
terminal waits for all six; any non-success terminal or integrity/cap failure
stops. Exact-final preflight reveals mapping once and judges candidate absolute
safety, candidate score at least baseline, and aggregate token/wall ratios at
most 1.25. Failure returns before exact-final effect; success permits one
neutral exact-final. Preserve every effect, never retry, replay, recover, or
substitute. Stage checks need no new gate. No source/config/spec/evaluator,
archive, install, release, activation, cache, or rollback mutation is allowed.

All 11 behavior/holdout units passed and unified holdout comparison passed.
The one neutral exact-final reached a successful terminal but durably returned
`NOT_YET`: its isolated PATH lacked `codex-linux-sandbox`, so coverage was
incomplete. CLI verification retained exact-final as the sole failure. Total
usage was 12 calls, 184,406 input, 5,507 output, and 193,661ms; no retry ran.

### Closed offline grant: GRANT-23

Repair `07c326e` bound the private sandbox hard link and PATH, passed focused
`20/20` and cumulative `111/111`, and left product/evidence unchanged.

### Closed offline grant: GRANT-24

Intent `088dfab` produced request `a279adc7...`, but its synthetic source left
the manifest and diff untracked. It is invalid, unconsumed, and not evidence.

### Closed offline grants: GRANT-25/26

Verbatim amendment:

```text
同意归档未消费的 request a279adc7dbe3d121435982f35d41c475de3af3195605a93b6a2a120ad8263875；执行最小 exact-final source-sealing 修复：所有 reviewer-visible 文件形成 clean synthetic commit，并以 SHA-256 纳入现有 host contract、执行前重新验证；hidden oracle bytes 从 reviewer workspace/diff 排除但继续由 EvalSpec oracle identity 精确绑定；neutral brief 删除 grant/commit/repair history。保持 Runtime、case、阈值、12-call 计划、gate、record 和 receipt 类型不变；离线 GREEN 后生成 fresh request，暂不调用模型。
```

Repair `2419d90` / tree `0df90a85` binds the clean relocation-invariant source
and all Git metadata inside the existing workspace-policy digest, revalidates
before capability effect, and excludes hidden oracle bytes from workspace and
diff. GRANT-26 moved the spawn mock to `run_provider` and closed realistic
prefixed diff copying. No record, gate, phase, product, or semantic input grew.

## Baseline

Published v0.6.5 was `204/205`; its stale ledger fixture was not evaluator GREEN.

## Selected design

Root reproduced three v0.6.5 blockers that this clean break must remove: one
engine identity forces full reruns after unrelated evaluator changes; generic
receipt records confuse typed evidence; and repository-generated
authority/approval content crosses the trust boundary by attempting to
authenticate itself.

Two alternatives were compared. Pure layered observation replay maximizes
reuse but recreates a graph and lifecycle; a minimal fresh suite is simpler but
wastes calls on oracle-only edits. The selected hybrid has no general graph:
each immutable `Attestation` contains its frozen observation and provenance, so
an oracle-only change can create a zero-call replay attestation, while the small
model suite covers only Runtime decisions that cannot be checked mechanically.

The design has two planes and four durable record types, exactly:

| Plane | Durable record | Purpose |
| --- | --- | --- |
| Product | `ProductArtifact` | Binds source commit/tree, exact package artifact digest, semantic product digest, and external-role-config digest without evaluator bytes. |
| Evaluation | `EvalSpec` | Binds the case manifest and separate provider-input, oracle, and harness component identities plus required-attestation policy and cost ceiling. |
| Evaluation | `Attestation` | Binds one immutable observation or offline replay to the relevant product semantic/artifact identity and `EvalSpec` component digests, verdict, terminal state, usage, and authority digest. Behavior and exact-final are kinds of this one record, not gate families. |
| Product | `ReleaseReceipt` | Binds the exact released `ProductArtifact`, qualifying attestation digests, isolated-install result, release destination, rollback identity, and separate release-authority digest. |

Authorization text is an authenticated input; raw provider events are retained
host-observed evidence, not new durable record families. Raw events remain
outside the repository; an
`Attestation` stores only their digest and sanitized projection. Direct foreign
keys between the four records replace GatePlan/GateReceipt chains, joins,
recurrence counters, and a general evidence graph. Current state is derived by
verifying immutable records from caller-supplied paths; there is no active
ledger to mutate, promote, reconcile, or migrate.

### Provider blindness and execution

For each role, the provider-input projection contains only the selected product
bytes/semantic identity, fixture workspace, user-facing prompt and Runtime,
external role configuration, model/effort/tool/timeout settings, and permitted
environment. Expected fields, acceptable alternatives, matcher logic, hidden
oracle text, holdout mapping, desired verdict, and historical findings are
excluded mechanically and are unreadable from the isolated provider workspace.
The projection digest is computed independently of the oracle digest.

One externally supplied user-authenticated evaluation bundle may authorize the
exact finite twelve-invocation plan: five required behavior cases, six arms in
three fixed holdout pairs, and one neutral exact-final, with a cumulative
call/token/time ceiling. Each planned
invocation remains one-shot; provider-reached or ambiguous effects are never
retried. The first terminal or oracle failure stops the bundle. Exact-final
receives the verbatim request, exact product diff/artifact, acceptance
obligations, checks, and exclusions, but no preferred verdict or repair history.
Its adverse `Attestation` remains valid for that artifact; repair creates a new
`ProductArtifact` and requires a new evaluation decision instead of rereviewing
unchanged bytes.

Release is a separate effect. It requires one exact release authority and
produces one `ReleaseReceipt`; it cannot infer authority from attestations.
Repository code may construct an authority request digest and verify supplied
authority, but may never treat self-generated text or records as authority.

Each fixed holdout has candidate and previous-released-product arms, run
concurrently with identical settings. All six outputs freeze before mapping is
revealed and one quality decision is computed. Across all fixed pairs,
candidate aggregate total input plus output tokens must be no more than `1.25`
times the previous released product. The corresponding relative wall ratio
remains reported but is diagnostic; per-unit timeout and absolute cumulative
wall cap stay hard. No old named public arm is part of this design.

Mandatory model cases are limited to low/high-risk qualification, midflight
escalation, goal divergence, no-commit/secret decisions, the fixed holdouts,
and exact-final. Same-task compaction and no-summary/no-handle reconstruction
are unrun conditional future mechanism obligations, triggered only by relevant
Runtime/recovery, role-config, or native Codex behavior change, or explicit
user request; this release cannot claim native mechanism certification.
Receipt, claim, schema, parser, invalidation, truncation, install, and rollback
behavior is deterministic integration coverage. Exact action-enum wording is
diagnostic when a conservative equivalent is safe; only safety, quality,
identity, effect, and goal-closure invariants are fatal.

## Invalidation rules

| Change | Required invalidation and work |
| --- | --- |
| Runtime, semantic package bytes, or external role config | New product semantic identity; rerun every behavior role and exact-final. |
| Packaging/version bytes only | New artifact identity and exact-final/install/release; reuse behavior attestations only when their bound semantic and role-config digests are identical. |
| A role's fixture or public prompt | Change only that role's provider-input identity and rerun only that role. |
| Shared provider instructions, model, effort, tools, isolation, or timeout | Change every affected provider-input identity and rerun those roles. |
| Behavior/holdout expected answer, oracle, or matcher only | Change only the affected oracle identity; replay the frozen observation with zero new model calls when provider-input identity is unchanged. |
| Holdout comparison policy only | Change oracle/evaluator/source identity and require a fresh `EvalSpec` and request. Any reuse or next-call plan must be mechanically proven under the single-authority contract; an incomplete adverse prefix grants no implicit continuation. |
| Exact-final rubric or oracle | Run a fresh exact-final unit; a terminal review cannot be reinterpreted as a new neutral review. |
| Scheduler, serialization, receipt verifier, or other harness only | Run offline harness/adversarial checks; never call the model unless provider input also changed. |
| Case added, removed, or requirement policy changed | Create a new `EvalSpec`; reuse still-valid attestations by exact component identity and run only newly required provider inputs. |
| Any product mutation after exact-final | Invalidate exact-final and release eligibility; return to working with a new `ProductArtifact`. |

No identity may include a path, timestamp, mutable ledger position, expected
answer in provider input, or unrelated evaluator component merely to force a
full refresh.

## Obligations and falsifiers

| ID | Observable obligation | Falsifier | Planned evidence | State |
| --- | --- | --- | --- | --- |
| `O-PRESERVE` | Product package and external role config equal `v0.6.5`; active/rollback state untouched. | Any package/config/install digest changes. | Pre/post manifests and Git diff classification. | offline verified |
| `O-FOUR` | Only the four named durable record schemas exist. | A ledger, plan/receipt/gate/review family, join, or generic graph is required. | Closed schema inventory and unknown-input rejection tests. | verified |
| `O-SEPARATE` | Product identity does not depend on evaluator bytes; evaluator changes do not rewrite product identity. | Oracle/harness edits change `ProductArtifact`. | Differential identity tests. | verified |
| `O-STATELESS` | Verification derives status from immutable input records without active mutable state. | Certification needs ledger order, promotion, or reconciliation. | Fresh-process replay and missing/tampered-record tests. | verified |
| `O-BLIND` | Provider input cannot contain or read expected answers or mappings. | Sentinel oracle bytes appear in projection/workspace/events. | Differential sentinel and isolation tests. | offline verified |
| `O-INVALIDATE` | The table above causes only necessary model calls. | Oracle-only change calls a model, or provider-input drift reuses an observation. | Per-component mutation matrix with call counters. | verified |
| `O-AUTH` | One bounded evaluation authority plus one distinct release authority suffices by default; neither implies the other. | Hidden micro-authority gates appear or release uses evaluation authority. | Exact digest/cap/refusal tests. | offline verified |
| `O-ADVERSE` | Adverse exact-final is durable for unchanged artifact bytes. | Unchanged artifact can discard or rerun it for a friendlier result. | Persistent negative and changed-artifact tests. | verified |
| `O-REAL` | Every non-replay Attestation requires matching fixed-host raw bytes; the runner is trusted for sanitization. | A sanitized record alone or mismatched raw validates. | Fake-runner raw positive/negative E2E, then separately authorized real path. | fixed-host offline verified; live open |
| `O-RELEASE` | Release binds exact artifact, valid attestations, isolated install, destination, and rollback. | Semantic-only or stale attestation can release different bytes. | Offline refusal matrix and separately authorized isolated release evidence. | offline verified; live open |
| `O-CONDITIONAL` | Compaction and no-handle reconstruction remain conditional mechanism checks, not default release gates. | The twelve-call default claims those mechanisms or silently adds their calls. | Manifest inventory, exact-final exclusion, and trigger rules. | offline verified; mechanism certification unclaimed |

## Planned implementation waves

These are planning boundaries, not authority under GRANT-01.

1. Characterize v0.6.5 identities and freeze RED tests for `O-FOUR`,
   `O-SEPARATE`, `O-STATELESS`, and `O-BLIND` without changing product bytes.
2. Replace evaluator-only contracts and CLI with canonical implementations of
   the four records and stateless verification. Delete superseded evaluator
   APIs/tests rather than add compatibility adapters.
3. Add invalidation, one-bundle authority, one-shot execution, durable adverse
   exact-final, forgery, isolation, and release-refusal tests. Run focused tests
   after each coherent wave and the full offline suite once after convergence.
4. Freeze a clean candidate and exact `EvalSpec`. Only then may Root request one
   bounded evaluation authority. Stop on the first failure, ambiguity, cap
   exhaustion, or identity drift.
5. If evaluation succeeds, obtain neutral exact-final within that bundle. Only
   a separate release grant may perform isolated install and release.

## Stop lines

- Do not modify package/runtime/config/install/cache/rollback bytes.
- Do not read v8 evidence as authority or migrate it into a new record.
- Do not add a fifth durable record, general graph, compatibility reader,
  alias, dual write, or mutable active ledger.
- Do not put expected answers, oracle material, mappings, or preferred verdicts
  in provider input.
- Do not call provider/model/network, install, release, or activate without the
  later exact authority that names the frozen identities, invocations, caps,
  destinations, and one-shot budget.
- Stop and return to Root on source/config/claim drift, unexpected baseline
  change, ambiguous/partial effect, oracle failure, cost overrun, product-surface
  diff, or a design need outside this contract.

## Current checkpoint

- Phase: `grant29_authorized_pending_generation`. Claim token
  `52df89da7d38f272bdaf775650db5513cd81de91fc17890d4c35db95e93bad36`
  verifies five sorted active/archive/staging/worktree/ref resources. Freeze the
  resulting plan-only commit/tree as the source anchor. Atomically archive active
  inode 12026776, manifest `525f0def...`, and prefix `11/11/11/11`; then generate
  an empty current-root request from committed source only. Bind product/baseline
  `d77ecb6a...`/`ec4fc2df...`, evaluator
  `c01cbafb...`/`2240e900...`/`74d459a4...`/`0e3ffa56...`, config
  `d98fac1a...`, binary `cb5e8cb8...`, profiles high/300 and max/600, and cap
  12/600000/100000/2400000/0. Validate source, host, spec, request, empty prefix,
  and exact archive preservation. Provider, network, install, release, package,
  schema, test, and retry budgets are zero; stop on drift, collision, or partial
  effect.
