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

- Phase: `grant31_exact_final_not_yet`, terminal and mechanically reconciled.
  Durable intent is commit/tree `f65878205536cbfca2aed04b41755167be6a4fdc` /
  `6c2f387fda9dc1966d47f5501b029934dceeead9`; this receipt is the commit
  carrying this checkpoint. Exact authority request `e9295933...` and authority
  digest `05825e35...` bound the unchanged spec `bfc93edb...`, product/baseline
  `d77ecb6a...` / `ec4fc2df...`, and twelve-call cap.
- All five behavior units were success/pass. All six concurrently frozen
  holdout arms were success/pass; the three candidate scores equal baseline
  (`2/2`, `1/1`, `1/1`) and every candidate passed its absolute oracle.
  Candidate/baseline tokens are 33,389/32,297 and wall milliseconds are
  22,661/21,055; both reported ratios are within 1.25. Mapping reveal was
  `2026-08-03T16:03:09.998190Z` and the holdout judgment is GREEN.
- The sole exact-final provider call completed successfully but returned
  `coverage.complete=false` and `decision=NOT_YET`, with the finding that its
  read-only command environment failed to launch and the frozen projection
  therefore could not be completely inspected. Attestation `4f18f6bb...` is
  verdict `fail` with diagnostics `fatal:coverage.complete` and
  `fatal:decision`. Stateless replay reproduces exactly that sole failure while
  retaining the GREEN holdout.
- Final prefix is `12/12/12/12`; cumulative usage is 12 calls, 144,010 input
  tokens, 3,270 output tokens, and 121,195ms, within every cap. Auth staging is
  absent. No call was retried or recovered, and no package, Runtime, evaluator,
  source, config, install, release, activation, cache, marketplace, or rollback
  effect followed. Release remains excluded; a new Root decision is required
  for any repair or new evaluation identity.

### GRANT-33 simplification receipt

- The first exact-only bridge was deleted when its 162-line module plus branches
  exceeded the 3,200/600 limits. Only the derived exact-final helper-file read
  remained; behavior permissions stayed byte-exact. Full offline was `117/117`.

### GRANT-35 request receipt

- Fresh request/spec/host/source `78be8bc8...` / `dfd9f9ab...` / `cbb93a5a...` /
  `acdd2624...` bound candidate/baseline `d77ecb6a...` / `ec4fc2df...`, high/max
  profiles and `12/600000/100000/2400000/0`. Source was clean, self-contained,
  hidden-blind, and atomically published with zero prefix.

### GRANT-36 terminal receipt

- Phase: `exact_final_not_yet`. Intent commit/tree are `b1b4327...` /
  `4ce435c...`; exact authority `78be8bc8...` minted one process-local bundle
  identity `19ff5a08...`. Pre-effect claims, credentials, zero prefix, frozen
  request/spec/host/source, twelve invocations, profiles, mapping, and cap were
  exact. No retry or recovery occurred.
- Core was `5/5` success/pass. All six holdout arms froze success/pass before
  reveal. Unified judgment was GREEN: candidate/baseline tokens `34,056/32,741`
  passed strict 1.25; pair scores were `2/2`, `2/1`, `1/1`. Wall
  `40,108/25,161` exceeded 1.25 but is diagnostic-only. A status formatter used
  one obsolete field name after freeze; offline replay reconciled the complete
  eleven-unit prefix without another provider effect.
- Exact-final reached the provider once and completed, but returned
  `coverage.complete=false` and `decision=NOT_YET`: it said the frozen source
  and durable evidence were not inspectable from supplied summaries. It emitted
  zero command-execution items. Attestation `8c7e8ad6...` is durably fail with
  `fatal:coverage.complete` and `fatal:decision`.
- Stateless replay reproduces the sole failure with holdout GREEN. Final usage
  is 12 calls, 144,386 input, 4,396 output, and 149,246ms, within all caps; all
  12 raw/claim/Attestation records remain outside the repository and auth
  staging is absent. Release is excluded and unchanged bytes cannot rerun this
  review. No package, Runtime, config, install, activation, cache, marketplace,
  or rollback effect occurred; further action requires a new Root decision.

### GRANT-37 durable intent

- Root authorized one offline exact-final contract repair at clean commit/tree
  `9896309...` / `99ae68f...`. Freeze RED for mandatory frozen-cwd inspection,
  zero-tool GO rejection, path-neutral identity, and an exact-only refresh bound
  to the eleven raw-backed GREEN prerequisites.
- Add no gate, record, receipt, case, generic continuation/replay engine, model
  call, request, install, or release. Preserve the ordinary twelve-unit bundle,
  behavior permissions, package and immutable GRANT-36 evidence. If a readable
  solution recreates the prior continuation family or exceeds 3,200/600, stop
  after RED instead of compressing or widening the protocol.

### GRANT-37 RED stop receipt

- Phase: `exact_final_contract_red`, terminal under the authorized stop rule.
  Intent commit/tree are `b49838e...` / `6df8b47...`. Three focused
  characterizations fail as required: the exact-final input omits mandatory
  command/cwd/host-fact instructions; a zero-command `GO` verifies; and moving
  an otherwise identical fixed host changes an ordinary invocation identity.
- The only implementation delta is 44 test lines. Production evaluator Python
  remains 3,018 lines, leaving 182 under the 3,200 ceiling; `provider.py` is
  already at its 600-line file ceiling. The previously abandoned readable
  exact-only bridge alone required a 162-line continuation module plus schema,
  host, invalidation, and composition branches. This stricter contract cannot
  fit the remaining budget without recreating that family or minifying code.
  Per grant, implementation and the full suite stopped after RED.
- No evaluator, package, Runtime, config, external evidence, model, request,
  install, release, activation, cache, marketplace, or rollback effect occurred.
