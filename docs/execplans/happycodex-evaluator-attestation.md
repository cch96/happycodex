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

### Active grant: GRANT-17

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

### Active grant: GRANT-18

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

- Phase: `live_authority_intent_pending_commit`. GRANT-17 repair commit/tree
  are `40686ef5163bbd9fa4a23223bff106502a3017be` /
  `3f06667194de306aa1d32e72bb5780047069b0fd`; the coherent repair commit changed
  only this plan, existing evaluator files/schema, and affected tests.
- RED covered the five diagnosed transaction gaps and forged-prefix,
  known-failure, cap, orphan, cross-process, process-group, and adverse-review
  paths. The focused suite was 88/88 GREEN in 7.750s; the single cumulative suite
  was 101/101 GREEN in 7.769s. Diff, AST, schema-load, replay, and static-budget
  checks passed. Production evaluator Python is 2,777 lines, largest module 556;
  this plan remains below 3,000 words.
- The invalid request `52657eb39b065a00edb411f3e525a684996cd3c31c2dd82d6239f7784922cd39`
  was never consumed. Its evidence-empty root moved atomically and recoverably to
  `/home/caichenghang/.codex/happycodex-evaluator-attestation-release.invalid-52657eb3`.
  No file from it was reused after quarantine.
- A fresh mode-0700 root was generated from the repair commit. New EvalSpec /
  authority request are
  `f3bb8c6c2551441fcc7e751adcadbdb1927e0fd5950f2d79b9fc08c6866a1591` /
  `f21ff642c3925164c2b89b4e45efc0864895c83dfd701e8825fe656b0e9dd233`.
  Candidate/baseline ProductArtifact records are
  `d77ecb6af42ad35a6cf4f37787b6b7472bffe1faf4a103e145742bd2fe115fed` /
  `ec4fc2dfb65be9ce8cc8d725a878d4166844cbd1ebbb686a4396116c17ecc9bf`;
  host policy/contract are
  `81b577bfaab4122842cbffacd960c846da9aed15b2e7f2efe740a215cb42e83b` /
  `0652d84a248a910ecda8815442b94bfb23688134a116e5ad3775d0f371b8a8f8`.
- Evaluator bundle/provider/oracle/harness identities are
  `4f38b83a91d90f5b170d5c1e27b21f26643e631976f10d4b98aa33c9c8d7bf38`,
  `0df713cbac6eea38af29144bec01152c94c266e406c51302cdac364a0a295abf`,
  `c4e033ffe6ffcb91cf31254cbad2c87b28995e8915d06e80ef5ba4b801778934`,
  and `a6c47f6aaabcfa844838602ba72230c28e81d28487c13dc7d58c3e854de8abf`.
- The exact-final projection has 33 Git-verified files and one isolated synthetic
  commit/tree `a474ef066c188d84cec1c05590a3cbcbf0c66835` /
  `2120e71bec6aee910ff66d527adeb1cdbeaf161d`. Manifest/diff SHA-256 are
  `fbd5b2d7531b5bc2fa67104f55d35a364e5a35c6a862b6b749cfac2df7d97ff0` /
  `4f8f8dcea68ebb645cfe5981933ba15cf430b89269efbdceaf50af8109f98d23`.
- CLI rematerialization is byte-identical. The spec contains exactly five core,
  six blinded holdout, and one exact-final unit under a twelve-call cap; mapping
  and oracle material are absent from provider input. All fresh claims, raw,
  Attestation, and unit directories are empty; no auth, JSONL, or tool-bin exists.
- The bound Codex 0.146.0 binary exposes every fixed exec flag and all 29
  explicitly disabled features. The fixed policy validates the external role
  config by whole-file SHA and unique exact byte blocks and binds the literal
  behavior instructions. Exact-final remains neutral and read-only.
- `skills/happycodex` remains tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; role-config SHA-256 remains
  `d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`;
  binary SHA-256 remains
  `cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6`.
- Provider/model/network calls, authority consumption, claims, raw events,
  Attestations, install, release, and activation effects are all zero.
- GRANT-18 starts from clean HEAD/tree
  `3caa7151fa0c82d194fe268ada373f211dc62c69` /
  `9a9848b261f85a51004a567527daa871c4e826d0` and empty external inventories.
  Stage commands are the exact order-1, order-2, and order-3 unit sets already
  bound in `authority-request.json`; no later stage begins unless the prior
  stage is fully durable, successful, within cap, and identity-clean.
