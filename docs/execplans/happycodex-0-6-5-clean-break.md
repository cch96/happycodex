# HappyCodex 0.6.5 clean break

Protocol: `HappyCodex/0.6.5-bootstrap`

Status: `CALIBRATION_3_AUTHORIZED_PENDING_LAUNCH`

Restore guard: verify this exact worktree, ref, resource receipt, Git state,
current batch, and protected-resource snapshot. Conversation summaries and
other tasks are not authority.

## Outcome and authority

Build public HappyCodex `0.6.5` directly from released `v0.6.0`, preserving its
compact Runtime, corpus fixtures, holdout comparator, isolation, resource
claims, costs, and fail-closed release boundary. Replace the remaining
multi-oracle generation-6 protocol with one provider-neutral generation-7
parse/reduce/report/replay boundary and a separate effect gate. No old schema,
task, ledger, evidence, alias, migration, dual read/write, or fallback.

Direct execution anchors, each UTF-8 plus LF SHA-256:

- `好的执行吧`:
  `092bba03db327e3feea788e30c57c31c6c5dd320c7603512e2143c9b23a61be5`;
- `目标改为 0.6.5`:
  `aa6177e195fd2614b08dd58455e33422661444d019ac164816251372acf49b1b`;
- `你在执行这个的时候也要按照0.6.5的来`:
  `47c548b30d1b569c3438e9f80d3901a6793db805264454ff2ab8ccceaa82cf83`;
- base correction `你的修改是基于0.6来的吧`:
  `6671315a28dd929e5670a3f33f03ca94a4b6708c97983717fd7da0c251a24b23`;
- release goal `好的，你看看怎么改，改完就发布0.6.5吧`:
  `09558913501aae4b9601883f309f1ac53c64c197e9307a5c30c43a711b281f8c`.

The correction makes released `v0.6.0`, not the 0.5.5 sibling, the sole product
base. The 0.6 semantic-core sibling and 0.5.5 typed corpus are design/test
donors only and never release ancestry.

These anchors authorize the agreed offline implementation, tests, commits,
claims, reconciliation, and candidate preparation. User approval is required
only for paid/live model work, external install/activation/publication/config
mutation, destructive external effects, Outcome expansion, or acceptance
reduction. Calibration, corpus, holdout, exact-final/Fable, isolated install,
cutover, push, tag, GitHub Release, and publication remain separate gates.
The release-goal anchor authorizes preparing those gates and completing public
`0.6.5` after their exact candidate, invocation, destination, and effect
identities exist. It does not waive a required gate or authorize an unbound
effect from a dirty worktree.

## Immutable baseline

- Released base commit:
  `e679c3d5cb83d6170fcd6f38f067892603c309da`.
- Released base tree:
  `ead6d31e8670118dfeb4a2f015a0a1d2c7ad8f28`.
- Annotated tag object:
  `v0.6.0` = `a665dec9220d0065fdf34f375b937170222bee48`,
  peeled to the base commit.
- Worktree:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6.5`.
- Branch/ref: `refs/heads/codex/happycodex-0.6.5`.
- Writer: current Root only, owner `happycodex-0.6.5-root`.
- Resource receipt:
  `/home/caichenghang/.codex/happycodex-0.6.5-from-v0.6.0-resource-claim.json`,
  SHA-256
  `16888a91aaf89e007b8305b53c8828b0131e947de5d2a07c06590177f1dcd10d`.
- Test disposition:
  `docs/execplans/happycodex-0-6-5-test-disposition.json`, SHA-256
  `3fd89ce7060f28439a206aa94e70fbaf35c324f7b296f3dfcecafa61f8e8af9d`.
- Protected resources:
  `docs/execplans/happycodex-0-6-5-protected-resources.json`, SHA-256
  `4069f04e1f42c4cfb707dc6081ffb417b2649bd7ffd651fab1766d11138f79cd`.
- Base suite: 169/169 GREEN; sorted test-ID digest
  `0d5bbcf5756e545f21ed4f6739dfd44a360fa4bf50eec0e21c8787cabab40359`.
- Seventeen corpus cases: 86,689 bytes and 1,070 lines.
- Runtime: 145 lines and 1,114 words.
- Base ledger is valid but uncertified `refresh_required`; all six evidence
  gates remain pending. No old evidence is reused.

The preliminary
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6.5-clean-break`
line is superseded because its base was 0.5.5. It is frozen read-only and is not
an authority, product donor, or candidate.

## Frozen design

- Public release/tag is `0.6.5` / `v0.6.5`; a later separately authorized
  cachebuster may produce one `0.6.5+codex.<stamp>`.
- Wire identity is `schema_generation=7`,
  `engine_generation="0.6.5"`, with domains
  `happycodex/schema7/<record-kind>`.
- Semantic package is exactly `__init__.py`, `model.py`, `codec.py`,
  `reducer.py`, and `replay.py`, with at most 20 explicit exports.
- Input is immutable `MachineFacts + ModelObservation`; the reducer alone
  derives typed findings, embedded blockers, one `NextAction`, `StateKey`, and
  `ActionKey`; report, receipt, impact, ledger, certification, and replay
  consume that same result.
- `StateKey` contains semantic task binding, source/candidate, typed findings,
  blockers, accepted evidence, and required decision inputs. It excludes
  resource, admin, authority, approval, receipt ordering, timestamps, sessions,
  and launch state.
- `ActionKey` is derived only from the reducer-produced action and its
  `StateKey`, exact target/scope, falsifier, and evidence-source identity.
- Receipt sequence/previous hash owns ordering and tamper evidence only.
- `GatePlan` is one exact user-approved paid/external scope. `LaunchKey` binds
  each prepared unit and prevents duplicate launch. Proven pre-provider
  `NO_EFFECT` failure consumes only that launch; provider-reached, billable, or
  ambiguous work consumes its `ActionKey` and cannot auto-retry.
- Local preflight completes before authority is requested or consumed.
  Infrastructure repair and offline reconciliation need no new user approval.
- Runtime lifecycle remains the compact 0.6 shape, renamed only if necessary to
  `implementation -> candidate -> exact_final -> closed`. One invariant-family
  RED matrix, one coherent repair, one full GREEN, and at most one focused
  review occur per wave.
- Codex is the only implemented provider adapter. Claude/Fable is reference
  design provenance only and is never invoked unless the user explicitly asks.
- `evaluation/holdout/compare.py` stays independent.

The base cases are already compact. There is no A2 transition validator, no
old-to-new runtime adapter, and no 326-line temporary holdout compatibility
layer.

## Coherent batches

1. `P0`: freeze released source, all donor test dispositions, protected
   external state, and the exact offline baseline.
2. `A`: add the generation-7 core and invariant-family RED matrix; atomically
   convert the 17 compact cases and every protocol/receipt/impact/ledger/corpus
   caller; replace effect identity with GatePlan/ActionKey/LaunchKey; delete
   generation-6 protocol/schema paths; full offline GREEN.
3. `B`: align Runtime, authorization text, schema-7 genesis ledger, metadata,
   docs, package inventory, and public surfaces; delete retired concepts;
   prove Runtime/package/holdout/CLI boundaries; full offline GREEN.
4. `C`: inventory first, then remove superseded evaluator/test assets, prove
   normalized artifact and source identity, revalidate protected resources,
   full offline GREEN, and freeze one Git-reachable source candidate.

One internal batch permit and terminal receipt may cover a few coherent
commits. Boundary is `(batch, failed_gate, scope_digest)`: one coherent repair
is allowed; a second identical boundary failure or two batches without their
declared deliverable stops for replan. This is plan cadence, not Runtime state.

## Completion and external gates

Offline source completion requires all retained/replacement tests GREEN, zero
undeclared test deletion or weakened oracle, exact classification/deletion
inventories, Runtime at most 262 lines and 2,400 words, five semantic files and
at most 20 exports, plugin/Skill validators, normalized package identity,
protected-resource equality, and a Git-reachable source candidate.

Only after source freeze may a separately authorized task plan calibration,
corpus, adaptive holdout, isolated install, exact-final, active cutover,
push/main/tag/GitHub Release, or publication.

## Current checkpoint

A release-preflight audit reopened the first frozen checkpoint without changing
the product package. Root reproduced five material evaluator findings:

- `HC-065-PREFLIGHT`: corpus and holdout consumed `ActionKey` before local
  fixture, install, schema, and workspace preparation, so zero-model
  infrastructure failures incorrectly burned exact authority.
- `HC-065-INVOCATION`: a GatePlan carried an argv/cwd/env profile, but the
  provider call checked only model, effort, and timeout substrings instead of
  binding the actual Host resources and complete provider invocation.
- `HC-065-CADENCE`: the ledger required every GatePlan before the first
  receipt, making it impossible for calibration actual cost to become the
  historical basis of corpus and holdout.
- `HC-065-HOST`: model-reaching helpers had no process-local capability and no
  supported exact request/run/receipt route under the mandated
  `python3 -m evaluation.cli` entrypoint.
- `HC-065-IMPACT`: the exact Host profile/resource set did not bind the
  persisted source-derived impact and cost-envelope receipt.

The bounded hardening changes no Runtime or shipped package bytes. It moves
ActionKey consumption to the exact provider edge after complete local
preflight, records `NO_EFFECT` or conservative ambiguous failures, binds the
canonical Host descriptor and exact provider argv/cwd/closed-env/schema/
timeout/binary, and requires one open plan with strict
`GatePlan -> GateReceipt -> next GatePlan` cadence. One immutable Host-minted
capability now binds every live helper; offline `request` and `receipt` commands
prepare but never apply records, while `host-run` mints and uses the capability
in one process. Every model request additionally binds its impact receipt
digest. Focused RED reproduced all five findings before implementation.

- Corrected `v0.6.0` worktree/ref/ledger claim is verified.
- P0 is committed at `b0ab3aa`; the initial generation-7 semantic core is
  committed at `ebc94ec`.
- Batch A is committed at `ec6202f`. Generation-6 schema/protocol paths are
  deleted; all 17 corpus cases, three holdouts, callers, receipts, and the
  effect boundary use generation 7 and GatePlan/ActionKey/LaunchKey.
- The semantic package remains exactly five files, has 17 public exports, and
  is 1,122 lines after removing evaluator-only corpus/oracle parsing.
- The complete Git-reachable offline suite is 183/183 GREEN at `ec6202f`;
  corpus, holdout, and Executor dry-runs report zero effects, and CLI verify is
  healthy with every evidence gate pending.
- Batch B is committed at `66ccebf`. Its complete suite is 183/183 GREEN; all
  official dry-runs, CLI verify, Skill validation, and plugin validation pass;
  it aligned Runtime policy, version/public metadata, the generation-7 genesis
  ledger, maintainer documentation, and launch terminology.
- Batch C source is committed at `3a8e7d7`. The v0.6.0 baseline has 169 test identities;
  the candidate has 159 unchanged identities, ten exact replacements, and 14
  added generation-7 invariants. The exact mapping is persisted in the test
  disposition inventory.
- Mechanical test flattening removed only overridden generation-6 bodies:
  `tests/test_evaluation.py` fell from 5,169 to 2,047 lines while retaining the
  same 86 active IDs and
  `4ac14406aaccf7ef637bb12ad405a866c224e527cd4590006d27e34d352d5bac`
  sorted-ID digest. The post-hardening 192-test digest is
  `68bd2feefe28a9cd713313fd3424ce2e3be175f1c572eb3a2280fb31fb54635e`.
- The frozen source tree is
  `799199be73b0d995fda2d52ee8b50bd92692efe1`. Its normalized package
  artifact is
  `bbc82a07445104820fb4e2108dde252fcce1883136e34e5ef1733eb3984b8b33`,
  semantic identity is
  `9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a`,
  Executor role is
  `f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da`.
- Release-effect hardening is committed at
  `52cc79a6239bb84485520cc0d6d79e50ba91748f`, tree
  `bc7618f36ceb38120545e2bb58e6adfb611bda51`; exact impact-receipt
  binding is committed at
  `b74aad6d6a572419ab6bf578f8a110ce48a38b12`, tree
  `83eb141c7bbff74b3540891f6ff91f3131468dc3`. Its full suite is
  192/192 GREEN; current evaluator manifest is
  `29f5bd7ea734641c3b9e8be4f4e041a0d55f569c2a5704f106c8dc667339babb`
  and snapshot is
  `72b37d796b033fd146a1402620b8de90915f2bcafe5a24b577da9ca564b943b7`.
- The sole generation-7 ReleaseCandidate is
  `908a926287fa01cb8e4b4cf591b2a90d108a0b9bfe3d39affa7f39e9908f187e`;
  current ledger identity is
  `be4777979e04b4544623488f930192851b10f2bc32db2863faf706b5db1398e3`.
  All six evidence gates remain pending and no old evidence is reused.
- Protected active-plugin, cache, marketplace, and Codex configuration hashes
  exactly match the frozen P0 inventory.
- No live model, network, install, activation, push, tag, GitHub Release, or
  publication effect has occurred.
- The private calibration resource claim is
  `/home/caichenghang/.codex/happycodex-0.6.5-calibration-resource-claim.json`,
  SHA-256
  `b39707bfe43103ded573ecbeb0b705d016a67239ff8e71a6a2de6c964d806064`;
  it binds the exact claim, output, and record roots under one owner token.
- The persisted source-derived calibration impact receipt is
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration/impact.json`,
  SHA-256
  `72ac0a00c98887b14a4dfeae68a55c83bd81332f4eb09180ac6542427c763dbe`.
  It binds one `subthreshold-control` phase at `gpt-5.6-sol`/`high`, a
  300-second timeout, and conservative ceilings of one evaluator process,
  100,000 uncached-input tokens and 10,000 output tokens. It records no prior
  candidate actual as historical basis.
- Offline request preflight produced private GatePlan
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration/plan.json`,
  file SHA-256
  `68f0168cea501a8bbd368d301a7ed7bdf17738ef6a28083f454b397470e68538`,
  plan SHA-256
  `bb5d518858d20cc38ed25a3b89b184f81740f17991721a9fa3719df9012fc89a`,
  and request SHA-256
  `0c528a98371fc7ddb9227aafa88b35edb2e84140954432afc74ca803b981a05b`.
  It created only the private plan file: zero launches, fixtures, workspaces,
  model calls, network calls, receipts, installs, or publications. The output
  root remains absent and the launch-claim root remains empty.
- The current-task user returned the requested canonical line verbatim:
  `AUTHORIZE HappyCodex 0.6.5 gate calibration exactly once for request 0c528a98371fc7ddb9227aafa88b35edb2e84140954432afc74ca803b981a05b`.
  Its UTF-8-plus-LF SHA-256 is
  `b6936c738ef48995964abed40c1523c189b113763f2a8d9d7dcb97bc784d54c3`.
- The exact GatePlan was atomically appended to the ledger; its predecessor was
  `be4777979e04b4544623488f930192851b10f2bc32db2863faf706b5db1398e3`
  and the resulting ledger is
  `2c406458c85987d28f53f1d759b2291d0455bae7bca57bccf87d1e854141129d`.
- The default Host launch stopped before reservation because
  `validate_launch(..., plan=plan)` reconstructed the default infrastructure
  digest as a replacement launch. Private NO_EFFECT record
  `preflight-no-effect.json`, SHA-256
  `60b2b2871f1856472200798a9f244d2401bf1819f775fb9e03e7bf40916c98da`,
  became the one distinct infrastructure generation. It preserved the
  ActionKey, provider invocation, candidate, impact, and cost ceiling.
- That launch reached the provider once, which consumed ActionKey
  `02091acd8ad5ec02b2929006e21f88421c7d3057517d5c4542d0a926ec0711f9`.
  The provider rejected the structured-output request with HTTP 400
  `invalid_json_schema`: nested anchor objects lacked required
  `additionalProperties:false`. No terminal usage event exists, so immutable
  result
  `ebc6a8946f94ba646febbda8f22698fa72e8da12840e6126fca1003cb9d25476`
  conservatively records the full approved ceiling rather than claiming zero
  cost. The same stderr also shows an attempted Cloudflare MCP OAuth worker,
  reopening closed-tool-surface proof.
- Failed calibration receipt
  `783d983c23b4bf625badf7c506fda3cc15eb08e1ffc8c15d831d3485b776b118`
  binds the consumed result. Its private file SHA-256 is
  `d374f242a229794ebf8af735c379636519d49af719cb2fb32d8cfa48d1e26ec6`;
  the failed terminal ledger is
  `73b9300bc1a63c0006b7c8fdd6fc707a977327a763eb7ceef120171fe4210874`.
- New findings `HC-065-LAUNCH-RECONSTRUCTION`,
  `HC-065-TRANSPORT-SCHEMA`, and `HC-065-MCP-CLOSURE` are candidate-new
  evaluator failures. The consumed ActionKey and approval are never retried or
  transferred.
- One coherent offline repair began with three focused RED invariants: a
  default launch could not validate against its own GatePlan; projected
  provider object schemas were not recursively closed; and the neutral profile
  did not declare the complete disabled feature set. The repair now derives
  one canonical default infrastructure generation, self-validates every
  requested launch before writing its GatePlan, projects a provider-only
  strict typed-anchor union, requires every provider object property, and
  explicitly disables apps, MCP/browser/computer/image surfaces, hooks,
  memories, goals, multi-agent, plugin sharing, remote plugins, and workspace
  dependency installation.
- A real isolated candidate-plugin probe reports an empty MCP list, contains
  HappyCodex in the effective prompt, and contains neither Cloudflare nor app
  instructions. The six-test repair slice is 6/6 GREEN in 2.484 seconds.
  Shipped package identity remains
  `bbc82a07445104820fb4e2108dde252fcce1883136e34e5ef1733eb3984b8b33`
  and semantic identity remains
  `9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a`;
  the repaired evaluator manifest is
  `9efd480fbc65088bb0bd14e9cdd01f7801bf8579a27125faa733dcd44ef335f0`
  and snapshot is
  `62d501d7e9974cdf1b286be6587b1e67f6ada1dc73814141d195e03909f473ac`.
- Next action is to commit this repair source, create a fresh successor
  candidate/genesis with no transferred plan, receipt, authority, or evidence,
  run the full offline suite, and derive a new calibration request.
- The coherent repair source is committed at
  `402fedc26f891f6977174e57d3cb79ed680ffa0f`, tree
  `4fc2791b1c4b1e1a9bed1888eba6e11791712596`. A fresh generation-7 genesis
  now binds successor candidate
  `8999589309204ed0a10546ca96f2a3b2048777c2491c159e7dc72e2fad60765e`
  and has ledger identity
  `f11e10b2d59f8847c025ba9218291aa36ed9d91578be487514290614f2b3c24b`.
  Its plan and receipt arrays are empty. The failed predecessor ledger remains
  Git-reachable at `bead2f7`; no predecessor plan, receipt, approval, model
  result, cost basis, or evidence is migrated or reused.
- The successor refreeze is committed at `a84ce56`. Its complete offline suite
  is 193/193 GREEN in 11.699 seconds. CLI verify reports
  `refresh_required`, no failed receipts, all six gates pending, evaluator
  manifest
  `9efd480fbc65088bb0bd14e9cdd01f7801bf8579a27125faa733dcd44ef335f0`,
  and snapshot
  `62d501d7e9974cdf1b286be6587b1e67f6ada1dc73814141d195e03909f473ac`.
  Executor, calibration, corpus-control, and holdout dry-runs all report zero
  launches, consumed actions, fixtures, outputs, receipts, workspaces,
  subprocesses, model calls, and network calls. Skill and plugin validators
  pass.
- Active 0.6.0 plugin source/cache bytes, normalized cache manifest
  `8b69be2632bf5c6f72736a09d1d3c815acf26ed7fcd4a9e6ed55e0092fcfbed0`,
  marketplace, and Codex configuration still match the protected-resource
  inventory. No install, cutover, publication, push, tag, or release effect
  occurred.
- Next action is to acquire distinct private resources, persist a successor
  impact receipt, and generate a newly bound calibration request. No live call
  may occur without the new exact current-task authority.
- The distinct successor calibration resource receipt is
  `/home/caichenghang/.codex/happycodex-0.6.5-calibration-2-resource-claim.json`,
  SHA-256
  `6907fd31f6d2074e6988b548ff4bb7ea63a7fe35d78bdaeb854d5eadbb9511f6`.
  It exclusively binds new `calibration-2` claim, output, and record roots;
  the output root remains absent and the launch-claim root remains empty.
- Successor impact receipt
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration-2/impact.json`,
  SHA-256
  `6d6d80fd5d807d6aeb6672e5138b936cb5568afeafc6927814180a9110b35429`,
  binds candidate `8999589`, evaluator snapshot `62d501d`, Codex 0.146.0
  binary `cb5e8c`, the new private roots, and one
  `subthreshold-control` call at `gpt-5.6-sol`/`high` with the same
  conservative ceilings: one model call, 100,000 uncached-input tokens,
  10,000 output tokens, and 300 seconds. It has no historical-success basis.
- Offline request preflight wrote only private GatePlan
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration-2/plan.json`,
  file SHA-256
  `2ababb72e56a4287463e9305c9eac749d0a9e2a6181d8aa0feaade06d7b86604`,
  plan SHA-256
  `c521a48c7cc46e310850ad50a21d3d7ea1ab139b1baf92b6f5eff4ffe63e199d`,
  and approval-request SHA-256
  `ee2938188fc0cb0783fbc6dd887742008ab400a7a5dbbabd8574c17a7f025a10`.
  It also successfully reconstructed and validated the exact default launch
  before requesting authority. The repository ledger remains
  `f11e10b2d59f8847c025ba9218291aa36ed9d91578be487514290614f2b3c24b`;
  zero launch, ActionKey consumption, fixture, workspace, model, network,
  receipt, install, or publication effect occurred.
- The only acceptable next authority is the exact canonical line:
  `AUTHORIZE HappyCodex 0.6.5 gate calibration exactly once for request ee2938188fc0cb0783fbc6dd887742008ab400a7a5dbbabd8574c17a7f025a10`.
- The current-task user returned that canonical line verbatim. Its
  UTF-8-plus-LF SHA-256 is
  `ee0d893c8be0742be3b4d7bc66513ad350aa752eb15e70e706d32d362d6fe5d6`,
  exactly matching the private GatePlan. This grants one application and one
  provider-reaching launch only; it grants no retry, corpus, holdout, review,
  install, activation, push, tag, publication, or release effect.
- The exact GatePlan was atomically appended to predecessor ledger
  `f11e10b2d59f8847c025ba9218291aa36ed9d91578be487514290614f2b3c24b`;
  the authorized open-plan ledger is
  `e205f270ddce7632e25d4b8274ad60e10fa8c458857f7c8df2ec9b786d43f95c`.
  No launch or external effect occurred during this transition.
- The authorized launch reached the provider exactly once and consumed
  ActionKey
  `4880d209779a5589fea2e587bb13718a31f3483b4d27f6c72354a5b1c9a7609a`
  under LaunchKey
  `c6e278d618a17118b33afbd643b695a087d29bccc38e383601abac7647a3ec52`.
  It was not retried.
- The provider returned one structurally valid terminal observation and a
  terminal usage event, but semantic post-validation failed with
  `invalid Recovery Manifest or summary`. Immutable launch result
  `aad932ae6ca3742d264ecdd489aad2f996d6b3be9e5321b6ab84a8a254e12769`
  therefore records `failed/ambiguous` and conservatively charges the full
  approved ceiling. Raw external event, stderr, and result file SHA-256 values
  are respectively
  `484a838418a2542387223e9e38a1abe7867a7648a912d6717ccdbd979e1f306f`,
  `cc4e03678599c1496aed1e62397875861ed9413c37078de6a04f460eaac5df95`,
  and
  `d2bfeaefa4b4211f0fc226498a37f4cf23ec53a78ee51600fd3b18c42019f8c9`.
- New finding `HC-065-RECOVERY-MANIFEST-PREDICATE` is a harness
  contradiction: the neutral prompt asks for recovery controls, the ordinary
  subthreshold fixture intentionally has no Recovery Manifest, and
  `canonical_report_from_result` nevertheless requires exactly one manifest
  marker for every non-null recovery object. The returned observation had the
  expected `qualifies=false`, `not_required`, and implementation direction;
  this is not accepted as quality evidence and provides no historical-success
  cost basis.
- Failed calibration receipt
  `5dd8715ef76a8b3037ff06ca2ec8585f4556f4d343b32e444b36f717846591a9`
  binds that immutable result and evidence commit `7f58f3f`. Its private file
  SHA-256 is
  `112acba5aac9ec72d329f27aa2fab2e68b99e93bb915a8d3dbf41c704d123a8b`;
  the failed terminal ledger is
  `5251d1cb974dd7a592c2b331641a2edc2d45ae980c6ff5284599e47c64a53198`.
  The authorization, ActionKey, LaunchKey, and failed candidate are terminal
  and cannot be reused or retried.
- The bounded offline repair preserves the existing fail-closed rule that a
  non-null recovery summary must bind exactly one content-addressed Recovery
  Manifest. It changes only the provider instruction so `recovery` must be
  `null` unless the reviewer has found and validated that manifest. Allowing
  unmanifested recovery would weaken evidence; adding a synthetic manifest to
  the ordinary subthreshold fixture would contaminate the calibration control.
  The repair requires one prompt-contract RED, the affected focused tests, the
  full offline suite, and a fresh successor candidate/genesis before any new
  calibration request.
- RED reproduced the exact omission:
  `test_live_projection_has_one_reducer_owned_boundary` failed because the
  provider prompt had no Manifest-presence condition. The implementation adds
  one sentence requiring `recovery: null` unless exactly one valid Recovery
  Manifest was inspected and forbidding synthetic markers; schema, semantic
  parser, manifest validator, fixture, Runtime, and shipped package are
  unchanged.
- The affected six-test slice is 6/6 GREEN in 0.953 seconds, including
  fail-closed Recovery Manifest validation, prompt secrecy, zero-effect
  dry-run, provider schema projection, and the real isolated no-MCP probe.
  Repaired evaluator manifest is
  `d9b7cad5bd6e61875e8e233a8eb24e034d7cf50deae4d1075edbea6ca259251d`
  and snapshot is
  `c4c18319ae33c806cbef32df1d27eba8fca5df089de8bdcbe075ee3f2880c9e6`;
  package artifact and semantic identities remain unchanged.
- The recovery-predicate repair source is committed at
  `ad20dbf60535f574e98e7b5adaccc6397d204c69`, tree
  `358560f2e392b23efa9e9ae26a3bf3e69fe8a455`. A fresh generation-7
  genesis binds successor candidate
  `0da306eb5055bc2db9baff77ef5a2bdd98dad80766a9e7b239843ad9ec3dc40d`
  and ledger
  `b23bef69aef8f398f00ecedf680336bccf17129f8ade66217c22c7fd86fe35ea`.
  Its plan and receipt arrays are empty. Both failed predecessors remain
  Git-reachable; no prior authority, launch, result, receipt, cost basis, or
  evidence is migrated or reused.
- The third successor refreeze is committed at `182d653`. Its complete suite
  is 193/193 GREEN in 11.309 seconds. CLI verify reports no failed receipts,
  all six gates pending, evaluator manifest
  `d9b7cad5bd6e61875e8e233a8eb24e034d7cf50deae4d1075edbea6ca259251d`,
  snapshot
  `c4c18319ae33c806cbef32df1d27eba8fca5df089de8bdcbe075ee3f2880c9e6`,
  and ledger
  `b23bef69aef8f398f00ecedf680336bccf17129f8ade66217c22c7fd86fe35ea`.
  All official dry-runs report zero effects; Skill and plugin validators pass.
- Active 0.6.0 plugin/cache, normalized cache manifest, marketplace, and Codex
  configuration still match the protected-resource inventory. No install,
  cutover, push, tag, publication, or release effect occurred.
- The distinct third calibration resource receipt is
  `/home/caichenghang/.codex/happycodex-0.6.5-calibration-3-resource-claim.json`,
  SHA-256
  `e8c1470b8fb8637e108bca036c6af079ec7e1f8b9680e9b5434478a2bacd1c46`.
  Its new claim and record roots are private, the launch-claim root is empty,
  and the output root remains absent.
- Third impact receipt
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration-3/impact.json`,
  SHA-256
  `f360e0cb4130ff72bc55f67b3984ee64292c25349b1a34e490a121f83c396371`,
  binds candidate `0da306e`, snapshot `c4c1831`, Codex
  `0.146.0/cb5e8c`, the repaired prompt identity, the new private roots, and
  the same conservative one-call cost ceiling. Neither failed predecessor is
  treated as a historical-success basis.
- Offline request preflight wrote only private GatePlan
  `/home/caichenghang/.codex/happycodex-0.6.5-release/records/calibration-3/plan.json`,
  file SHA-256
  `70adebe344f99b31cd8db6cafb9d19fd3d888f292b8f677c07ad84163a08c46c`,
  plan SHA-256
  `1e862e62dc33acaad600fef8fb5d8bfd54948f07fa6f15c4bdfd84f2706c0701`,
  and approval-request SHA-256
  `1cf14e64236812fd203911bd18b5d6294092c0019135bd925d62c8081ee4955e`.
  It reconstructed and validated the default launch before requesting
  authority. Ledger remains
  `b23bef69aef8f398f00ecedf680336bccf17129f8ade66217c22c7fd86fe35ea`;
  zero launch, consumed action, model, network, receipt, install, or
  publication effect occurred.
- The only acceptable next authority is the exact canonical line:
  `AUTHORIZE HappyCodex 0.6.5 gate calibration exactly once for request 1cf14e64236812fd203911bd18b5d6294092c0019135bd925d62c8081ee4955e`.
- The user supplied that exact canonical line once. Its UTF-8 content with one
  trailing LF has SHA-256
  `e534f2351ac17cfe2a796d8ed69c79e746abd83842d90758d9abb6fb3abb2e14`;
  it authorizes only the already sealed third calibration GatePlan and has not
  yet been consumed.
- The immediate pre-effect check observed Host-owned global Codex config drift:
  full config SHA-256 is
  `a75ecd807b09c55e3db019cc1db975b4a6718aa3c9a784e88e54d835940feea7`
  at 4,935 bytes. The only non-timestamp change is one unrelated project trust
  entry adding 86 bytes. Projecting out that entry and `last_updated` produces
  the previously frozen 4,811 bytes and SHA-256
  `753c421f07d0eca27b07d7f134dadc07cb57e5020257e2afb32719d3ffae1ad9`.
  Global config is not an invocation input: the GatePlan uses a fresh isolated
  `CODEX_HOME`, explicit model/effort/tool arguments, and a closed environment.
  Candidate, package, role config, binary, invocation, authority, private
  destinations, and protected active installation are unchanged, so this
  unrelated Host-owned addition does not invalidate or re-mint the GatePlan.
- Applying the already sealed GatePlan to the generation-7 ledger succeeded
  exactly once. The new ledger semantic SHA-256 is
  `5d0571381313893f78c6cfe65ae2151fec2b5c0d1bb04f45feaf16a7515196f7`
  and its file SHA-256 is
  `7ac23793ac3a6a91618574cb0fe92cbe849999316d66e66970aacdd3afbbe202`.
  This transition records the pending plan only; its action and launch remain
  unconsumed, the launch-claim root is empty, the output root is absent, and no
  model or network effect has occurred.
