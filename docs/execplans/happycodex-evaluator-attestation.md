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

### Active grant: GRANT-04

GRANT-04 is the final bounded host-contract closure in this working wave, owned
by token `5a63e381-1ff8-4675-9c10-c81da14e1de2`. Exact clean prestate is commit
`02cd5d4c7dd91fe21ebe77b539d1513c07797129`, tree
`b1dabfb6dd87b13559be809664769db7bdd82736`; preserved `skills/happycodex`
tree is `d9e525a267fbf36669d409ba1b4b009a6beeeea5`. Writes remain limited to this
plan, `AGENTS.md`, `evaluation/**`, `tests/**`, and this branch, with one commit
maximum. Offline/temp subprocesses are allowed; product/config changes,
provider/model/network/install/release/activation effects, other refs, a fifth
record, scheduler, graph, signing system, and PKI are forbidden. A same-family
trust bypass or need for a wider trust system is an immediate `NOT YET` return.
This is the durable intent persisted before GRANT-04 implementation.

Root reproduced four new falsifiers: `F5`, resealing every Attestation under a
different authority still verifies; `F6`, resealing an arbitrary sanitized
event digest still verifies; `F7`, exact-final may exist after a fixed-holdout
aggregate resource failure; and `F8`, holdout may start before behavior freezes.
The related source blockers are an arbitrary CLI proof-verifier executable,
logical-only invocation identity, no provider-visible response schema, and
stored diagnostics not checked against oracle recomputation.

The finite repair adds one exact external-host contract to `EvalSpec`, binding
trusted proof-verifier/provider binary, tool config, permission profile, and
workspace/cwd policy identities. Its digest enters every invocation, authority
request, Attestation proof challenge, and CLI executable verification. Public
versioned report schemas enter the affected provider projection without hidden
values. Proof challenges bind authority, spec/request, invocation/claim,
raw/terminal/report/sanitized identities, artifact where applicable, and host
contract. Verification enforces behavior freeze before holdout start and a
successful six-arm reveal/oracle/aggregate decision before exact-final starts.
Failure prefixes remain valid; no executor or model scheduler is introduced.

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

Authorization text and raw provider events are authenticated inputs, not new
durable record families. Raw events remain outside the repository; an
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
exact finite set of provider invocations for required behavior cases, three
fixed holdout pairs, and one
neutral exact-final, with a cumulative call/token/time ceiling. Each planned
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

Model cases are limited to low/high-risk qualification, midflight escalation,
goal divergence, no-commit/secret decisions, same-task compaction,
no-summary/no-handle reconstruction, the fixed holdouts, and exact-final.
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
| `O-REAL` | Real provider terminals and raw-event digests cannot be forged by sanitized records. | Fabricated success verifies without its bound external terminal. | Fake-provider positive/negative E2E, then separately authorized real path. | fake-provider verified; live open |
| `O-RELEASE` | Release binds exact artifact, valid attestations, isolated install, destination, and rollback. | Semantic-only or stale attestation can release different bytes. | Offline refusal matrix and separately authorized isolated release proof. | offline verified; live open |

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

- Phase: `candidate-pre-freeze`; GRANT-04 host-contract closure complete
  offline. Candidate freeze and exact-final have not started.
- Selected checkpoint source: `v0.6.5` commit/tree recorded above.
- Baseline: one authorized run recorded above; unchanged 204/205 known failure.
- GRANT-04 exact prestate is the commit/tree in its active-grant section. Root
  falsifiers `F5`-`F8` first ran 0/4: each failed because the expected
  `VerificationError` was absent. The identical focused set is now 4/4 GREEN;
  original `F1`-`F4` remain GREEN.
- The final cumulative command
  `python3 -m unittest discover -s tests -v` returned exit `0`, `Ran 62 tests
  in 5.943s`, `OK`. It includes full raw-subprocess evidence, bound fake
  verifier and unbound-binary refusal, claims/recovery, failure prefixes,
  release refusal, public-schema/invalidation, stage-order, relabelling, and
  diagnostics-tamper coverage.
- GRANT-04 adds an exact host contract and public response schemas. Every unit,
  authority request, and proof challenge binds the contract; the challenge
  also binds authority, EvalSpec/request, invocation/claim, raw, terminal,
  report, sanitized events, and exact artifact. The CLI hashes and checks the
  configured verifier executable before use. Behavior must freeze before
  holdout starts; holdout must freeze, reveal, and pass hidden/aggregate
  judgment before exact-final. Aggregate failure without exact-final remains a
  valid terminal prefix; an already-called exact-final is rejected.
- No model scheduler, signing system, PKI, graph, ledger, gate family, or fifth
  record was added.
- Static evidence: `git diff --check` and Python compilation passed; evaluator
  production Python is 2,083 lines, largest module 517 lines; plan remains
  below 3,000 words; durable type inventory is exactly four; unknown evaluator
  inputs fail closed; `skills/happycodex` remains
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5` with no product diff.
- Provider/model/network calls: `0`. Install/release/activation effects: `0`.
- The four typed formats and stateless verifier are implemented; no task
  `ProductArtifact`, `EvalSpec`, `Attestation`, `ReleaseReceipt`, authority, or
  exact-final result has been persisted or executed.
- Open effects: real provider, exact-final, isolated install, release, and
  activation remain unrun and unauthorized. This grant stops before
  exact-final.
- Recovery: read this entire file, verify branch/worktree/source/status and
  owner token and GRANT-04 prestate, then reconcile only authorized paths. Do
  not continue into effects from this grant or conversation context.
