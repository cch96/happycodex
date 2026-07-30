# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint, authority, and current state

G035 starts from fresh candidate commit
`0d5dba15013d760474d25292b9b12a81f1e92c00`, tree
`ddd7f27763c9e9c73a77bd6319032739fcf7e940`, direct child of hardened
transport commit `825962522c8ba6abb8dea3f7f7f04b8029e339fe`, on branch
`codex/happycodex-0.6-bounded-redesign`. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, remains the sole writer. The mode-`0600` task claim
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
stays held.

G029 retired the consumed zero-model epoch to exact genesis. Its user
authorization SHA-256 is
`3caf565f22a8865c08185294fa405d8e56b565fbb7a28204382d20e25d6dfa07`,
intent SHA-256 is
`c92aed24739a1ab259026ac373a93897d213f04de810a3b8764a2a3e8664da70`,
and mode-`0600` terminal-receipt SHA-256 is
`45ad30d093cb0da0dd5e97b0417de7e3ecbb2e8abf04893c13982e398d6b16df`.

G033 terminal receipt is mode `0600`, SHA-256
`25fbf4da1acafe135db817fe3af4e6bce74249a23eae70975c6706253a20fad4`.
G034 user authority reuses the exact repair authorization digest
`2a8747b454439e3cd14ef3b845abc946a26406a70cedfaafa1abf6971cc8a016`;
its mode-`0600` intent SHA-256 is
`b08235cf146e8f4141bfafaf1d6009db8a1ca1be9f685f87dcdd3b6341b0fc6b`.
Its terminal-receipt SHA-256 is
`739c708786ab829c101a47420b13308d11b61065f0f84af653096b88423c2ac1`.
Root then granted `HC06BR-G-035-fresh-calibration-gateplan-after-transport-repair`
under the same exact user authority. G035 intent SHA-256 is
`f73bcdc623dfb2379f5e611b6fca947b0acf939045bfc8407e5658c851e1fb11`.

## Fresh candidate and one-shot transition

The candidate was recomputed from the exact committed repair source:

```text
source commit
825962522c8ba6abb8dea3f7f7f04b8029e339fe
source tree
36aa681a5c7bd7ab5dd29e2df96d52d965c41fc2
package artifact
4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e
package semantic
9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a
engine manifest
d0c505c8b7dc6b37b0bcf65c61137d90d640126bec55deea7792474fdf9528b6
Executor role
f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da
public baseline
514cea60053bab5303e86e6cacaa0260e960b3fe1670a658e2df1a6965ce978c
snapshot
725624bb5b7243db7a52f05e68b6894973e30fa1e80b144137ef7a0730bb93dc
created_at
2026-07-30T14:35:33Z
candidate seal
704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e
```

The private input `/tmp/happycodex-g034-release-candidate.json` is mode `0600`,
886 bytes, file SHA-256
`e20e4458b963df5d6667445c54e2dceaa5642eba08ebea5735b43e265a32bdb6`.
It passed repository-aware validation before the only apply:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli apply \
  --expected 09fd486ca4b12699ef42c94e596d584b3ad527aa7ea3054dc0a7a2d674b34ebe \
  --record /tmp/happycodex-g034-release-candidate.json
```

The command ran once, exited zero, and was not retried. The resulting ledger
canonical SHA-256 is
`b8df2ccff931fb0ea2dd542d85632929f23814d6095926d2d93bda241b319998`
and file SHA-256 is
`f8a03a8a3c2b5c8fa2063400df40e4d53b458d44b191145c298c5f4ffcb55022`.
It contains exactly this candidate, zero plans, and zero receipts. It derives
`refresh_required`, all six pending gates, empty coverage/failures, and no
certification. No old evidence was migrated or reused.

## Fresh calibration GatePlan

G035 authorizes only one calibration `GatePlan`, the narrow active-state test,
this index, and their direct-child commit. It grants no calibration approval,
execution, `EffectIntent`, claim consumption, model/provider call, receipt,
evidence, or later gate. The fresh base and claims child are mode `0700`; claims
are empty and `calibration-output` is absent:

```text
/home/caichenghang/.codex/happycodex-0.6-calibration-704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e
/home/caichenghang/.codex/happycodex-0.6-calibration-704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e/calibration-claims
```

All earlier calibration bases, claims, outputs, and private records remain
immutable recovery anchors and are never reused. The new private input
`/tmp/happycodex-g035-calibration-gateplan.json` is mode `0600`, 3,040 bytes,
file SHA-256
`948ff939b2d005dfbd7084fc875c2581999ca55ccb7709585f198c7ecdb53f70`.

The profile preserves the retired strict script shape and changes only the
candidate-derived external paths. It binds this exact worktree, only
`PYTHONDONTWRITEBYTECODE=1`, `gpt-5.6-sol/high`, `300000` ms, arm `candidate`,
and argv `python3 -c <strict script> corpus --calibrate --plugin <worktree>
--output <fresh output> --model gpt-5.6-sol --effort high --timeout 300 --arm
candidate`. The script rejects argv drift, loads the sole candidate-bound
calibration plan, requires zero receipts, reconstructs every unit with
`evaluation.live.build_effect_intent`, and routes only through
`evaluation.cli.run_authorized` with the fresh claims root. It contains no
plan/request digest. Profile SHA-256 is
`e07856bb5af3cb0a98d519d2707648adde837dd49929b91a83b401f30cb7c915`.

The compact resource-bundle canonical preimage is:

```json
{"candidate":{"candidate_sha256":"704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e","engine_manifest_sha256":"d0c505c8b7dc6b37b0bcf65c61137d90d640126bec55deea7792474fdf9528b6","executor_role_sha256":"f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da","package_artifact_sha256":"4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e","package_semantic_sha256":"9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a","snapshot_sha256":"725624bb5b7243db7a52f05e68b6894973e30fa1e80b144137ef7a0730bb93dc","source_commit":"825962522c8ba6abb8dea3f7f7f04b8029e339fe","source_tree":"36aa681a5c7bd7ab5dd29e2df96d52d965c41fc2"},"codex":{"binary_sha256":"cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6","version":"codex-cli 0.146.0"},"external":{"executor_toml_sha256":"d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275"},"host_route":"evaluation.cli.run_authorized","paths":{"claim_root":"/home/caichenghang/.codex/happycodex-0.6-calibration-704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e/calibration-claims","output_root":"/home/caichenghang/.codex/happycodex-0.6-calibration-704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e/calibration-output"},"profile_sha256":"e07856bb5af3cb0a98d519d2707648adde837dd49929b91a83b401f30cb7c915","resource_bundle_type":"happycodex-0.6-calibration","schema_version":1,"unit":{"case_id":"subthreshold-control","semantic_input_sha256":"899234c5dd32e5330c1976c70e1ace63085ba36ef242a4f617c7304d9a900d7e","snapshot_case_sha256":"899234c5dd32e5330c1976c70e1ace63085ba36ef242a4f617c7304d9a900d7e"}}
```

Its SHA-256 is
`23420aeb8a4ffb5ee5852ddef067e10028f8ed83ff987ab578f17dccb2d462d1`,
the plan's sole resource digest. Global config and models cache are excluded:
neither is an input.

The canonical approval-request object is:

```json
{"allowed_effects":["one isolated temporary repository, home, and package install","one subthreshold-control Codex execution phase","external output, effect claim, and result artifacts under the bound roots"],"candidate_sha256":"704b3fb16008d7d527c4fab7328aa6d84717374884a9c62358c554dbccac9f6e","cost_ceiling":{"model_calls":1,"output_tokens":100000,"uncached_input_tokens":1000000,"wall_milliseconds":360000},"cost_semantics":{"acceptance_limits":"token and wall ceilings are conservative post-run receipt acceptance limits, not an in-flight billing cutoff","historical_basis":"no accepted generation-6 historical cost exists","model_calls":"one external Codex execution phase, not internal provider turns","preemptive_bound":"the 300-second subprocess timeout is the only preemptive cost bound"},"exclusions":["all other live gates","active config, plugin, marketplace, and cache mutation","publication and activation"],"gate":"calibration","profile_sha256":"e07856bb5af3cb0a98d519d2707648adde837dd49929b91a83b401f30cb7c915","request_type":"happycodex-0.6-calibration","resource_bundle_sha256":"23420aeb8a4ffb5ee5852ddef067e10028f8ed83ff987ab578f17dccb2d462d1","schema_version":1,"unit":"subthreshold-control"}
```

Its SHA-256 is
`87adab8557b37df8b8502acf552de47973d584f2324fec32ea985c9ee2ade93d`.
The exact future approval line, including its trailing LF, is:

```text
APPROVE HAPPYCODEX 0.6 CALIBRATION 87adab8557b37df8b8502acf552de47973d584f2324fec32ea985c9ee2ade93d
```

Those bytes have SHA-256
`8f6d0ec79f7d35d9a2b6bcad52e360d13ed95a848d4a23fa598efc9456cf4606`.
It is not yet authority. The plan is an audit/cost binding, never permission.
`model_calls=1` means one external Codex execution phase, not internal provider
turns. The 300-second subprocess timeout is the only preemptive bound; token
and 360-second ceilings are conservative post-run acceptance limits.
Generation 6 has no accepted historical cost.

The plan was schema/repo validated before the only apply. Its created-at is
`2026-07-30T14:47:31Z` and seal is
`265e4895a2ed896f31d20619bb106476211683b9c96ba75eec37ddaf329d4c55`.
The apply ran once from canonical predecessor
`b8df2ccff931fb0ea2dd542d85632929f23814d6095926d2d93bda241b319998`,
exited zero, and was not retried. The ledger canonical SHA-256 is
`403a33d817e574b453b67f6a1d09307395af05e20d29889a525620ec86b29fe1`;
file SHA-256 is
`70903e9511ff1539ddd147742743ecf48b22f8db07b68319f540a4f767ed436e`.
It contained the unchanged candidate, exactly this plan, and zero receipts;
derived state remains `refresh_required`, six pending gates, empty
coverage/failures, and uncertified.

## Frozen protocol and safety

HappyCodex 0.6 has one fixed Executor per task/worktree; Root grants and
verifies. Runtime lifecycle is only
`working -> candidate_frozen -> exact_final -> closed`. One obligations/evidence
table holds durable work, correction is event-driven, and the same unchanged
failure is never retried.

Release persistence has exactly `ReleaseCandidate`, `GatePlan`, and append-only
`GateReceipt`. Pending gates, coverage, receipt tip, freeze eligibility,
failure, and certification are derived. One canonical `EffectIntent` binds the
candidate, gate, invocation, cost, resources, output, approval content, and
unit. Consumption is durable and one-shot before model-reaching work.
Repository plans, digests, claims, and approval content are audit bindings, not
Host authority or provenance.

Generation 6 is a clean break: no migration, alias, dual write, fallback,
prior-evidence reuse, or coverage reuse. Evidence must strictly postdate its
Git-reachable source and bind normalized archive/package/evaluator/role/public
identities. Unknown evaluator inputs, package drift, aliased paths, duplicate
records, malformed output, and baseline drift fail closed. Raw model events,
secrets, hidden oracles, and unsanitized output stay outside Git.

The shipped Runtime/template remain 235 lines and 1,689 words. The evaluator
has one closed sixteen-module Python inventory, 17 corpus cases, and three
adaptive holdout pairs. Dry runs must remain zero-effect. Active plugin,
marketplace, cache, configuration, publication, activation, branch/main, and
task-claim changes always require separate exact authority.

## Reproduced boundary and minimal repair

The consumed calibration reached a pre-model executable boundary. After its
effect claim was reserved and its unit output directory created, the isolated
environment put `<temp>/bin` first in `PATH` before populating that directory.
The first plugin command could not even spawn:

```text
FileNotFoundError: [Errno 2] No such file or directory: 'codex'
```

There is no model/provider call, token usage, successful plugin installation,
result, retry, or alternate PATH evidence. The old anchors remain untouched:

```text
claim
/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665/calibration-claims/effect-b16619b73ae086e79f296708de3ccf91a46efbbe000a8c679bee5c4142ecade3
mode 0600
sha256 6123fbd0ccc6fba981d1d19cddf3bd9c5496711efed38ea8e2c1ef086ee12b26
intent 2a5bc9a9c4e0dd1be7602c254c20fcd8e98eaf214b92503cadcf245a7d476b24
unit subthreshold-control

output
/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665/calibration-output/subthreshold-control
mode 0700, empty, result.json absent
```

The real regression extends the existing isolated-home boundary and executes
`codex --version` through the returned environment's own `PATH`. It compares
against `codex_identity()["version"]`; it uses neither a mock, absolute
shortcut, nor hard-coded toolchain version. On the parent source:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_evaluation.HappyCodexEvaluationTests.test_isolated_home_strips_parent_task_context
ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'codex'
```

The minimal repair establishes one order invariant:

1. validate source auth;
2. populate the private native tool bin;
3. construct the isolated home/environment with that bin first in `PATH`;
4. install the candidate.

`isolated_home` now prepares `<temp>/bin` before returning. `evaluate_case` and
the existing sandbox test reuse that exact prepared directory; the late
duplicate preparation is removed. There is no adapter, fallback PATH,
`~/.local/bin`, external symlink, retry, monkeypatch, or compatibility route.
The focused real-PATH regression and existing sandbox isolation test are GREEN.

## Consumed epoch retirement

The retired epoch is recoverable from parent `c587f8e9ee4a07b34fcba00e7a1ae0fe3fe299eb`.
It contained candidate
`d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665`,
plan `bc359f594b933a72272e91cd91286bea65f0e91a98c4200ca5435479f9b8c678`,
and request
`44430bbff160bc4288f6d5a08ec99b78ac1082fb8e1851da0844393145e45014`.
Its exact approval line is consumed and cannot be reused:

```text
APPROVE HAPPYCODEX 0.6 CALIBRATION 44430bbff160bc4288f6d5a08ec99b78ac1082fb8e1851da0844393145e45014
```

Because its effect intent is durably consumed, retry is forbidden. The repair
also changes source and evaluator identities, so retaining or editing that
candidate/plan would create false continuity. Exact user authority therefore
retired the epoch by `apply_patch` to fresh genesis. The old Git commit and
external claim/output remain immutable recovery anchors; nothing was deleted.

G029 changed exactly:

```text
evaluation/corpus/engine.py
tests/test_evaluation.py
evaluation/results/current.json
tests/test_certification_engine.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

G035 changes exactly:

```text
evaluation/results/current.json
tests/test_certification_engine.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

G031 and G034 changed exactly the same three tracked paths. G035 now asserts
the exact hardened candidate and calibration plan, zero receipts,
`refresh_required`, all six pending gates, empty coverage/failures, and no
certification. Isolated genesis, append, successor, schema, archive, and
prior-Git drift tests remain unchanged.

## G032 terminal and G033 repair

G032 approval request
`28a53f918bfe871542f3d92615bb085aca56f7e9a25625d598e04cd0662fe4e7`
was consumed exactly once. The provider returned HTTP 400
`invalid_json_schema`: `properties.open_gates.uniqueItems` is not permitted.
A Cloudflare MCP invalid-token warning independently exposed that the declared
disabled profile did not mechanically disable orchestrator MCP. The stored
command exited one after one attempted Codex phase, with zero successful model
completions and zero observed token usage. No metadata, result, GateReceipt,
retry, or historical calibration basis exists. Its Git source, private receipt,
and external claim/output remain immutable recovery anchors.

G033 user repair authority, UTF-8 plus one LF, has SHA-256
`2a8747b454439e3cd14ef3b845abc946a26406a70cedfaafa1abf6971cc8a016`.
It permits only `evaluation/corpus/engine.py`, `tests/test_evaluation.py`,
`evaluation/results/current.json`, `tests/test_certification_engine.py`, and
this ExecPlan. It permits no model/provider call, install, live gate, effect
reservation, retry, active configuration/package/cache change, or release.

The repair retains `OUTPUT_SCHEMA` as the strict internal contract and adds one
pure recursive provider projection that deep-copies it while removing only
keys named `uniqueItems`. Only `response-schema.json` uses that projection;
Python validation still rejects duplicates. One evaluator argv builder serves
fresh and resume phases and obtains exactly one native
`-c orchestrator.mcp.enabled=false` override from one helper. A real isolated
`codex debug prompt-input` regression proves the CLI accepts that override and
omits `<apps_instructions>` without `codex exec`, provider contact, or install.
The consumed epoch is Git-recoverably retired to exact fresh genesis; G033
appends no candidate, plan, receipt, or evidence.

## Acceptance and next gate

Required offline checks are:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli verify
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli impact
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli executor --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --calibrate --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli holdout --dry-run
git diff --check
```

Before commit, `verify` and `impact` must each return two with empty stdout and
the sole exact error `worktree ledger differs from prior Git ledger`; no other
error is accepted. After commit, `verify` returns zero and `impact` returns the
expected zero because the exact candidate is committed. Full tests run both
before and after commit. All four dry runs must return zero with nine zero
effect counters. Runtime/package/version,
marketplace, active source/cache, retired and fresh external states, evaluator
inventory, budgets, and exact diff must remain protected. Global config and
models cache are not inputs and must not be modified.

After Root accepts the G035 plan commit, calibration execution requires the
exact approval line above plus a separate bounded execution grant. G035 stops
without `EffectIntent`, claim consumption, model/provider work, evidence, or
`GateReceipt`.
