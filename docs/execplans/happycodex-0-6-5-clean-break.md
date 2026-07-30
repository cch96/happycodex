# HappyCodex 0.6.5 clean break

Protocol: `HappyCodex/0.6.5-bootstrap`

Status: `CANDIDATE_FROZEN`

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
the product package. Root reproduced four material evaluator findings:

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

The bounded hardening changes no Runtime or shipped package bytes. It moves
ActionKey consumption to the exact provider edge after complete local
preflight, records `NO_EFFECT` or conservative ambiguous failures, binds the
canonical Host descriptor and exact provider argv/cwd/closed-env/schema/
timeout/binary, and requires one open plan with strict
`GatePlan -> GateReceipt -> next GatePlan` cadence. One immutable Host-minted
capability now binds every live helper; offline `request` and `receipt` commands
prepare but never apply records, while `host-run` mints and uses the capability
in one process. Focused RED reproduced all four findings before implementation.

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
  `bc7618f36ceb38120545e2bb58e6adfb611bda51`. Its full suite is
  192/192 GREEN; current evaluator manifest is
  `a14e68d73f3792dfe12a9e97acb8e161d2d8a04388e96d6704be872d7ff016ed`
  and snapshot is
  `fd82883281a720abbcff6bdf2967b222719854bf3e9f77f134b074465ca980a0`.
- The sole generation-7 ReleaseCandidate is
  `908a926287fa01cb8e4b4cf591b2a90d108a0b9bfe3d39affa7f39e9908f187e`;
  current ledger identity is
  `be4777979e04b4544623488f930192851b10f2bc32db2863faf706b5db1398e3`.
  All six evidence gates remain pending and no old evidence is reused.
- Protected active-plugin, cache, marketplace, and Codex configuration hashes
  exactly match the frozen P0 inventory.
- No live model, network, install, activation, push, tag, GitHub Release, or
  publication effect has occurred.
- Next action: create private exact calibration claim/output/record roots, run
  the offline request preflight, and present its one canonical line to the user.
  Do not call a model until that exact line is returned. A successful
  calibration receipt then supplies the cost basis for the corpus plan; no
  future GatePlan is pre-authorized.
