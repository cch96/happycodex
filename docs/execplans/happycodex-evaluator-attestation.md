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

### Last grant: GRANT-11 (stopped)

Under the active user amendment `同意将 compaction/reconstruction 降为
conditional mechanism，按 12-call 发布路径继续`, GRANT-11 authorizes only
offline freeze/materialization. It is owned by token
`5a63e381-1ff8-4675-9c10-c81da14e1de2`. Exact clean prestate is branch
`codex/happycodex-evaluator-attestation`, commit
`46b71f3a22e2246527be543f85da9b5ae77dcce4`, tree
`32b4418162331745239a17dfe10b89f9237a2b5a`, product tree
`d9e525a267fbf36669d409ba1b4b009a6beeeea5`, evaluator bundle
`b42afeee7e878dc263e61ff7f569519bb8509d04f140911a601c05420964805b`,
Codex binary SHA-256
`cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6`,
and unchanged Executor config SHA-256
`d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`.

Repository writes are limited to this plan and one plan-only commit. External
writes are limited to one new private mode-0700 root
`/home/caichenghang/.codex/happycodex-evaluator-attestation-release`, private
JSON inputs/generated records, and empty future execution directories. Only
the existing `python3 -m evaluation.cli` may materialize the two exact products,
twelve-unit EvalSpec, validation, and one combined authority request. The host
policy/contract must close all environment, isolation, native JSONL, per-arm
Runtime, concurrency, and no-retry preimages. No test, provider/model/network,
claim, attestation, raw stream, install/cache/release/activation, authority
mint, new code/schema/runner/record/gate/ledger/graph, or product/config change
is authorized. Any identity, shape, permission, or effect ambiguity returns
`NOT YET` before paid execution.

GRANT-11 terminated `NOT YET` after an offline configuration probe produced
unexpected local files in a directory required to remain empty. No later
effect is authorized from this stopped grant.

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

- Phase: `working / NOT YET`; GRANT-11 is stopped. Paid evidence, exact-final,
  install, release, and activation have not started.
- The exact RED ran three tests and produced four assertion failures: baseline
  holdouts received candidate Runtime, a dirty temporary checkout replaced
  frozen Runtime bytes, a forged source tree was accepted, and an unavailable
  source commit was accepted. After repair the same three tests are 3/3 GREEN.
- Materialization now reconstructs both supplied ProductArtifacts from their
  exact Git source commits and external-role-config digest, rejects any
  mismatch/unavailable source, and requires the comparison products to share
  one role config. It reads Runtime as exact Git blob bytes decoded as UTF-8;
  mutable working-tree Runtime is never used.
- Candidate behavior/exact-final and candidate holdout arms bind Runtime SHA
  `07421636583ddec11308bf235fe4b49b2d0b11598944303f5287574f631d4bb5`.
  Baseline holdout arms bind exact source
  `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` Runtime SHA
  `aa090bbd0d7af6e6ac05e5afc959ee93268393f8621bd5ebf00e745d04e3ce55`.
  Profiles, tools, timeout and role config remain identical across each pair;
  mapping labels remain outside provider input.
- The twelve-call inventory, three fixed pairs, aggregate 1.25, ordering,
  first-failure stop, native evidence, host metadata, authority, four records,
  release refusal, F1-F11, and conditional-mechanism absence are unchanged.
- The affected focused command was 83/83 GREEN in 6.146s. The one cumulative
  `python3 -B -m unittest discover -s tests -v` was 86/86 GREEN in 6.022s.
  A final two-assertion fairness/source check after the exact config invariant
  was added was 2/2 GREEN in 0.070s.
- Static evidence: `git diff --check` passed; evaluator production Python is
  2,227 lines, largest module 539 lines; this plan remains below 3,000
  words; durable inventory is exactly the four named types and no active
  ledger; evaluator bundle is
  `b42afeee7e878dc263e61ff7f569519bb8509d04f140911a601c05420964805b`.
  `skills/happycodex` remains
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5` with no product diff.
- Provider/model/network calls: `0`. Install/release/activation effects: `0`.
- GRANT-11 materialized private `ProductArtifact` inputs and a twelve-unit
  `EvalSpec` at external root
  `/home/caichenghang/.codex/happycodex-evaluator-attestation-release`.
  EvalSpec record SHA-256 is
  `52a23223dabed162caf6cf7a85b4be2e6d5f406c3f6cb3ba639d876895bdfbd4`;
  its combined approval-request digest is
  `b604ef4f4164ec0363afd1988f7d388c51cb0142aa0e480097c33eb415ea4c5f`.
  These files are unexecuted and are not authority or qualifying evidence.
- The host policy passed component-hash checks and `codex debug prompt-input`
  parsed its exact permission/config overrides locally. That command did not
  contact a provider, but it unexpectedly populated the supplied isolated
  `CODEX_HOME` under `execution/units` with `skills/`, `tmp/`,
  `.sandbox_migration`, and `installation_id`. The other execution directories
  remain empty; no claim, attestation, raw stream, or authority was minted.
- Because GRANT-11 required empty future execution directories, this partial
  local effect invalidates the freeze. Nothing was deleted or retried after
  discovery. Root must decide a new exact cleanup/rematerialization grant; the
  recommended repair is a fresh external root plus a distinct disposable
  config-probe `CODEX_HOME`, never the frozen execution root.
- Open effects: cleanup/rematerialization, real provider, exact-final, isolated
  install, release, and activation remain unrun and unauthorized.
- Recovery: read this entire file and verify the recorded branch, worktree,
  source, clean status, product tree, owner token, selected evaluator bundle,
  and this GRANT-11 stopped receipt before reconciling only paths named by a
  new grant. Do not execute or treat the materialized approval request as
  authority from this grant or conversation context.
