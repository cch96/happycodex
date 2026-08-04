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

### Closed construction lineage: GRANT-17–26

These grants established one-shot fixed-host execution, strict native-event
parsing, frozen six-arm holdout comparison, a private sandbox-binary hard link,
and a clean relocation-invariant exact-final source excluding hidden oracle
bytes. GRANT-18 and GRANT-20 stopped with preserved partial prefixes; GRANT-22
consumed all 12 calls and durably returned `NOT_YET` because the exact-final
PATH lacked that sandbox alias. GRANT-24's untracked source projection is
invalid and unconsumed. Repairs through `2419d90` closed those offline defects
without changing Runtime, product identity, record families, call plan, cases,
or thresholds. Git retains the full superseded narrative and evidence.

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
| Runtime or semantic package bytes | New product semantic identity; rerun all twelve units. |
| External role config or behavior host surface | Rerun the five core and six holdout arms; exact-final keeps its neutral role identity. |
| Packaging/version bytes only | New artifact identity and exact-final/install/release; reuse behavior attestations only when their bound semantic and role-config digests are identical. |
| A role's fixture or public prompt | Change only that role's provider-input identity and rerun only that role. |
| Shared provider instructions, model, effort, tools, isolation, or timeout | Change every affected provider-input identity and rerun those roles. |
| Behavior/holdout expected answer, oracle, or matcher only | Change only the affected oracle identity; replay the frozen observation with zero new model calls when provider-input identity is unchanged. |
| Holdout comparison policy only | Change oracle/evaluator identity and require a fresh `EvalSpec`; reuse requires exact current unit and raw identities. |
| Exact-final rubric or oracle | Run a fresh exact-final unit; a terminal review cannot be reinterpreted as a new neutral review. |
| Exact source, neutral brief/instructions, or exact permission delta | Invalidate only exact-final; a one-call proposal must bind all eleven raw-backed GREEN prerequisites. |
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

- GRANT-44 durable intent, pre-provider: from clean commit/tree
  `26dce1e4ca296efe99ec6bfe4bd9e7f6efc3b18d` /
  `6278544b86610460f2c653674539cee59c91e703`, authenticate only the exact
  current-task user line for proposal `fb092ae...`; its process-local authority
  digest is `c066a43f...`. Reproduce every bound identity and the zero prefix,
  then invoke the committed fixed-host transaction exactly once for
  `exact-final` at `gpt-5.6-sol/max`, 600 seconds, under cap
  `1 / 50000 / 10000 / 600000 / 0` for calls/input/output/wall-ms/recoveries.
  Persist only the raw stream, claim, and Attestation in the claimed request
  execution root; remove private auth staging at process termination. Any
  drift, ambiguity, timeout, nonterminal result, cap violation, GO or NOT_YET is
  terminal for this grant: never retry, resume, recover, repair, or seek another
  reviewer. Git receives only this intent and a later sanitized terminal
  checkpoint. No evaluator/product/Runtime/config/request/spec/source/
  prerequisite mutation, install, release, activation, cache, marketplace, or
  release authority is authorized.
- Phase: `exact_request_ready_offline`; release remains `NOT_YET`. The frozen
  CLI-closure commit/tree are `2849916b33826f7c04435bc7f751ef77efbd53b1` /
  `86f61722e8a4e5317d798b42ff5290505252f271`. The public
  `python3 -m evaluation.cli prepare-exact-request` command is a thin adapter
  over the existing policy, host-contract, spec, and exact-only proposal
  functions. It publishes atomically, exposes no provider execution, and
  rejects collision, full-plan, adverse, missing, tampered, and over-cap input.
  Focused CLI/composition coverage passed `14/14` in 3.454s. The cumulative
  offline result is mechanically reconciled as `133/133`: 132 ordinary passes
  plus the unchanged 3,332-line evaluator satisfying the user-amended 3,400
  hard cap; the amended size test separately passed `1/1`.
- The repaired neutral source is
  `/home/caichenghang/.codex/happycodex-evaluator-attestation-exact-source-1e9ccb96965a`.
  Its synthetic commit/tree are `c26092c01c675038f2d4ead2cb991f08b5148c78` /
  `761032d51b14e579de3f54e1d0c72f6e1c1bb966`, source identity is
  `b68da2b8a7b92f2e8d8aad141ad8c679afa9cb84b6422d7e8b75738f2670f2f4`,
  and its complete reviewer diff is 1,090,559 bytes with SHA-256
  `a96333653221337ea98f20f4e41a440c607b1daaff9867d1715f848dbcfc7162`.
  The first construction used a misplaced Git `--output` argument and created
  only the 32-file projection; that exact partial directory was moved to system
  Trash before one corrected construction. A later blanket text predicate
  confused nine legitimate hidden-oracle path literals with private payload;
  the semantic check proved zero private diff paths, projected private files,
  workspace private files, or oracle-payload leakage. Git retains the detailed
  recovery lineage.
- The closed request root is
  `/home/caichenghang/.codex/happycodex-evaluator-attestation-exact-refresh-1e9ccb96965a`.
  Its authority-request digest is
  `fb092ae3247f8278adea9c9d90ce82daaa58de6b2fa95fb0c9c787b869b3fac2`;
  the displayed canonical line is `APPROVE HAPPYCODEX EVALUATION
  fb092ae3247f8278adea9c9d90ce82daaa58de6b2fa95fb0c9c787b869b3fac2`.
  That line is explicitly informational (`authoritative: false`) and grants no
  effect. The EvalSpec, evaluator-bundle, and host-contract identities are
  `4fbe975bfde3bf0705a7bf91e1eb9579dfd671d73920627d63d1a877512fba9b`,
  `c41d3f1536d7fbe52fa407dced600334ef4a99e76a3e7dbf45bf3b26bc5ee103`,
  and `d678e7c30973ce9085b27a42541350b28a091be9ba7e9af56c96cdd66e07befa`.
- The proposal selects only `exact-final`: one call, at most 50,000 input and
  10,000 output tokens, 600,000 milliseconds, and zero infrastructure
  recoveries. The conservative basis is the prior successful transport actual
  of 23,555 input tokens, 1,196 output tokens, and 31,402 milliseconds, plus the
  fixed 600-second timeout. Exactly eleven old raw-backed GREEN prerequisites
  compose under set SHA-256
  `3651b335e64d160e5793946a510f6312a3b57b7d960d7a5a70475dd3b4bd8561`.
  The prior failed exact record `6ecb2194...` and raw bytes SHA-256
  `cefae86422501af1bff44cb3b8d828a36eb0caeb7879bacd68f19ded55124a0e`
  remain immutable and excluded.
- Fresh-process materialization reproduced `eval-spec.json` byte-for-byte; the
  public validator accepted all four product/spec records and exactly eleven
  prerequisite attestations. Public inventory remains closed to four durable
  record types, has no active ledger, and reports the current evaluator bundle.
  Request inventory is 116 files with SHA-256
  `da4b22e104a0dd8238f7650691556b83709cb62e9c620f50c41f453ac7a80d5d`.
  The request has zero execution prefix and no supplied authority. Runtime and
  plugin bytes still equal `v0.6.5`; no provider/model/network, install,
  release, activation, cache, marketplace, rollback, or retry effect occurred.
  Exactly one future neutral exact-final provider call is requested, but it is
  not authorized by this repository content or checkpoint.
