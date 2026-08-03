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
  An adverse exact-final result is durable and is not rerun against the same
  product identity.
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

The user approved one offline `fixed-host-transaction` closure. Verified
prestate is clean commit/tree `220befd6c10b6b72d41ea3d70019023dd2bd21bd` /
`3c4fd90320071c34c86932c87e1900aff6cce4b2`; active request/spec are
`52657eb39b065a00edb411f3e525a684996cd3c31c2dd82d6239f7784922cd39` /
`7e99db10ef712147ed3f77aa3233f6349c503e6a01c78f3a3db94cccace4dcbe`,
with empty evidence directories and absent quarantine target
`/home/caichenghang/.codex/happycodex-evaluator-attestation-release.invalid-52657eb3`.

Root reproduced five same-family gaps: exact-final discards its real mapping
reveal timestamp; auth/spawn failures can leave claim plus raw without an
Attestation; timeout kills only the parent; the host checks stage prerequisites
but not verified durable prefix/failure/cumulative cap before every launch; and
schema-valid adverse exact-final reports can be rejected by record validation.
This batch must make reveal metadata round-trip, preflight all mechanical paths,
guard cleanup, classify spawn failure as pre-provider/no-effect, kill/reap the
process group, verify known raw/Attestation prefix and authority, enforce the
fixed cap before launch, preserve each representable terminal after claim, and
type exact-final decision as `GO|NOT_YET` while durably retaining every adverse
report. Fixed holdout-pair concurrency remains unchanged.

Only this plan, existing evaluator modules, schemas, and affected tests are
owned. No new module/runner/gate/record, Runtime/product/oracle/case/threshold,
real `codex exec`, provider/model/network/install/release, paid authority, or
evidence reuse is allowed. Write RED, one repair wave, one focused suite, then
one cumulative suite and static budgets. Only after GREEN+commit may the active
root move recoverably to the exact quarantine and a fresh empty request be
generated. Any different semantic failure or identity/path drift pauses.

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

## Baseline

Command, run once in the new clean worktree:

```text
python3 -m unittest discover -s tests -v
```

Exact terminal result: exit `1`; `Ran 205 tests in 14.889s`; `FAILED
(failures=1)`. The sole failure was
`test_certification_engine.GenesisAndCliTests.test_active_ledger_has_exact_generation7_candidate`:
the checked-in ledger contains post-genesis evidence rather than the test's
exact genesis object. All other 204 tests passed. No dependency was installed.
This is the published source's already recorded post-evidence genesis-fixture
failure (`docs/execplans/happycodex-0-6-5-clean-break.md` records the same
204/205 state and exact test identity), so it is accepted only as an unchanged
baseline characterization. It must not be relabelled GREEN or inherited as an
acceptance condition for the new evaluator.

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
candidate aggregate tokens and wall time must each be no more than `1.25` times
the previous released product; no old named public arm is part of this design.

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

- Phase: `fresh_request_awaiting_separate_authority`. GRANT-19 intent commit was
  `587dcf2fffe5293f4a79a3aeb591c87596d32ab1`; source repair commit/tree are
  `b53bb183d85efe28a73a5a800898dc8b10c11b2b` /
  `b4f2ec9b2ce9327c97bd27c26b8081758e994f52`. It changed only provider policy,
  raw verification, provider fixtures, README, and three existing test files.
- Narrow RED produced exactly three expected errors. Focused tests were 50/50
  GREEN in 2.298s; the single cumulative offline suite was 103/103 GREEN in
  7.895s. Static/JSON/AST checks passed; evaluator Python is 2,781 lines with a
  556-line maximum. Runtime, hidden oracle, response schema, thresholds, product
  tree, role config, and binary did not change.
- The complete failed GRANT-18 root is recoverably preserved at
  `/home/caichenghang/.codex/happycodex-evaluator-attestation-release.failed-grant18-f21ff642`
  with units/claims/raw/Attestations `5/5/5/0`; it was not read or reused after
  archive. The fresh mode-0700 root has `0/0/0/0`, no auth/JSONL/tool-bin, and no
  failed authority or evidence.
- Fresh candidate/baseline records remain
  `d77ecb6af42ad35a6cf4f37787b6b7472bffe1faf4a103e145742bd2fe115fed` /
  `ec4fc2dfb65be9ce8cc8d725a878d4166844cbd1ebbb686a4396116c17ecc9bf`.
  EvalSpec/request are `256a710ff7967b5f33788424fba825247ab756292c8fe07555ed12e912380acb` /
  `04666961ef899ee9b51ca8e80a0aae1d368369adae94c44cc203388fe7d3b7d9`.
  Profile/host-policy/host-contract identities are
  `061a4a014fe2230e14485e4ce3a0751bb3d50c4f5cbf38a1b5e4ff582d83f8b7`,
  `900bd6ce3822fbd7c2cb45eebd975fbc8c4df91644843b8289f142daad651882`,
  and `b8b51f13b2542f3b25c8689c1ebfcf2b09a8c29b305cb5747466c6fde6ce0543`.
- Bundle/provider/oracle/harness identities are `361e20c227b368ed26292406e93f2040a84774d36ffee868e9bab23e5588e789`,
  `f1d31e912ce5fa7996916583d436bed1bd0a03f123c204ba6fa128c20779c60a`,
  `a0bc97fa8659a4204973e321b4d1b5cf21ffd2725d210899b330a8af4b8cdf17`,
  and `a6c47f6aaabcfa844838602ba72230c28e81d28487c13dc7d58c3e854de8abf3`.
- Frozen synthetic commit/tree are `7ad3d79279ff68da8c0b5cacf9681251e3b95712` /
  `c7a990370665cbdc3c15978746fc008b6f4c427d`; manifest/diff SHA-256 are
  `fe5f945b4fd5cacc6b38a137aa9e42853a8db590762ed54187e6cd412d051ea3` /
  `6307507aeb06872e84721c711dd32f619f3fe465a2df44f8abf56e218f4f9a2e`.
- Next launch metadata is fixed without a new gate: run
  `qualification-low-risk` as the internal canary; on pass run the other four
  behavior units concurrently, then three holdout pairs concurrently, then
  exact-final. The exact canonical approval line is
  `APPROVE HAPPYCODEX EVALUATION 04666961ef899ee9b51ca8e80a0aae1d368369adae94c44cc203388fe7d3b7d9`.
  This request has not been approved or executed.
- Product tree/config/binary SHA-256 remain
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`,
  `d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`,
  and `cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6`.
