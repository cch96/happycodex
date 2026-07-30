# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint and exact authority

This plan is the durable current index for the 0.6 contraction. The accepted
checkpoint is commit `594c252a5fbda0d39e6eef4a813eed1d50bc060f`, tree
`203b307b1c1117dc5b905e27d4faddc49dc29197`, on branch
`codex/happycodex-0.6-bounded-redesign`. Its source is `S_release`
`b3b79dca1cb3c990ad0c849172ea24aed8c3cab9`, tree
`20d039576d27d3ca927c0ade702131290eae948f`, version
`0.6.0+codex.20260730115707`.

The generation-6 ledger contains exactly one `ReleaseCandidate`, one
`calibration` `GatePlan`, and no receipts. Its canonical SHA-256 is
`c28cbecfcb4d24ade3f7552f09507375961dbfdfd720f6b816801d647a5e2f09`
and file SHA-256 is
`384fdaef79814779b7c6f0dc45a7e69f4d33b060b3304a76ba760fa2837fa48f`.
It still derives `refresh_required`, empty coverage/failures, and all six
pending gates; it stores no derived state, live authority, or evidence.

Root reads, decides, grants, and verifies. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, is the sole writer. The mode-`0600` claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
binds this worktree, ref, and plan. It stays held. No replacement writer,
delegation, merge, cherry-pick, or cross-task grant is allowed.

Grant `HC06BR-G-028B-global-config-contraction` is preparation-only. Its
mode-`0600` intent SHA-256 is
`07f65d49de826ae7d68a6e7a04f321edccffd2b4341e3927957c86b8fae2283d`.
It authorizes only the ledger, this index, the exact active-ledger test
correction, and two private directories described below. It grants no model,
live, receipt, install, publication, activation, configuration, plugin,
marketplace, cache, branch/main, push/tag, or claim-release effect.

## Frozen normalized Outcome

HappyCodex 0.6 is a smaller reachable protocol. Shipped Runtime guides one fixed
Executor per task/worktree; Root grants and verifies; one obligations/evidence
table holds durable work; correction is event-driven. The same unchanged
failure is not retried. One coherent repair wave is allowed; if one
boundary-level alternative still fails, control returns to the user. Lifecycle
is only `working -> candidate_frozen -> exact_final -> closed`.

The evaluator uses one strict direct terminal validator rather than a generic
semantic controller. Behavioral fixtures and risk inventory remain, while
mechanical structure, wording, formatting, and per-file allocation tests do
not stand in for behavior.

Authority belongs to Root/Host orchestration. Repository code does not
authenticate task/message/turn provenance. A plan, approval digest, claim, or
effect intent is content binding and audit history, not permission. Ordinary
repository validation remains reachable without a local issuer, private seal,
or positive-path trust monkeypatch.

One canonical `EffectIntent` binds candidate, gate, exact invocation/profile,
cost ceiling, units, resources, output, and approval content. Execution
atomically consumes `intent_digest + unit` through no-follow `O_EXCL`, writes to
an absent no-follow output, and produces a typed result. Durable consumption
prevents reuse.

Release persistence has exactly three record types:

1. `ReleaseCandidate`: Git source commit/tree, normalized package identities,
   evaluator manifest, external role digest, public baseline, and snapshot.
2. `GatePlan`: gate, exact profile, cost ceiling, units, resources, output, and
   approval-request/content digests.
3. append-only `GateReceipt`: immutable typed result and predecessor/tip
   binding.

Pending gates, coverage, receipt tip, freeze eligibility, failure, and
certification are derived rather than stored. One reachable CLI writer owns
schema validation, prior-Git comparison, predecessor comparison, atomic
replacement, and receipt append.

Calibration is the fixed retained control routed through corpus execution.
Calibration, full corpus, adaptive blind holdout, artifact receipt, exact-final
review, and isolated install are distinct persisted gates. Publication and
activation are later external gates. Model-reaching gates require separate
exact Host authority and cost basis.

Identity retains reachable Git archive commit/tree, normalized package,
evaluator bundle, external role/config, frozen public baseline, and case/holdout
identities. Snapshot settings are only model, effort, and timeout. A successful
live corpus receipt additionally binds the actual Codex version, its binary
content digest, and the invocation profile; no executable path is persisted.
The evaluator inventory is one exact closed Python/JSON set and one manifest
digest. Unknown inputs fail closed. Any evaluator-bundle change invalidates the
full corpus, all holdouts, and artifact receipt.

## Preserved safety

Generation 6 is a clean break: no migration, alias, dual write, fallback, old
reader, prior evidence reuse, or coverage reuse. Evidence strictly postdates a
Git-reachable source and binds its normalized `git archive`. Prior-Git
successor comparison remains mandatory. Empty state cannot certify. Raw model
events, secrets, hidden oracle bodies, and unsanitized output stay outside Git.

Duplicate keys, malformed terminal streams, extra terminals, unsafe or aliased
paths, raw/ledger divergence, unrecognized inputs, and baseline drift fail
closed. Baseline failures remain explicit. Recovery uses this plan, Git,
receipts, the live claim, and the same fixed Executor; copied summaries or a
replacement writer cannot restore authority.

Candidate preparation uses the official cachebuster once for the new candidate.
Isolated install never mutates source. Activation retains paired
package/config/cache rollback and needs separate authority. Claims remain
narrow: one task-duration worktree/ref lease, a distinct activation-target
lease, Git CAS, exact path grants, and atomic effect-unit/output creation.

The affected-surface inventory is concrete: Runtime and template; terminal
parsing and receipt consumers; effect intent/consumption/output/dispatch;
candidate/plan/receipt persistence and prior-Git transitions; package,
evaluator, role, public, case, and holdout identities; corpus, adaptive
holdout, exact-final review, install, publication, activation, recovery, and
rollback. It routes risk; it is not a checklist that manufactures completion.

## Accepted implementation

Batch 1 established the four-phase Runtime and direct terminal protocol. Batch 2
established the three release records, one `EffectIntent` route, atomic
consumption/output, prior-Git transitions, derived state, and adaptive holdout.
Batch 3 replaced evaluator subsets with one closed sixteen-module inventory and
manifest, retained all 17 corpus cases and three holdout pairs, and removed
wording/formatting proxies for behavior. Runtime/template remain 235 lines and
1,689 words; the accepted offline suite is 163 tests.

The recovery manifest binds repositories, claim, safe ref or archive, writer,
tests, agents, and ordered gates. Schema enumeration fixes four lifecycle
phases. Ledger and CLI tests exercise candidate/plan/receipt appends, exact
identities, successor comparison, and zero-effect dry runs. Unknown Python/JSON
evaluator inputs, aliased ledgers, package drift, and false success fail closed.
Repository content never claims Host provenance or permission.

## Bounded release-source preparation

### Accepted S_release source

`S_release` was prepared as a cachebuster-only source boundary. The protected
external prestate bytes remain:

```text
~/.agents/plugins/marketplace.json
752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe
~/.codex/agents/happycodex_executor.toml
d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275
/home/caichenghang/plugins/happycodex/.codex-plugin/plugin.json
1fb2d73ae9774ab99a78a3ae5d449493a5d19e77860fb6952abc9a09b5733990
/home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/.codex-plugin/plugin.json
1fb2d73ae9774ab99a78a3ae5d449493a5d19e77860fb6952abc9a09b5733990
```

The active source and loaded-cache manifests remain byte-identical to each other
and unchanged. Calibration separately binds the external Executor TOML, not
ambient auto-maintained global configuration.

### Fresh reanchor — one candidate only

The candidate was recomputed from accepted `S_release`, not copied from an old
candidate. It binds:

```text
source commit
b3b79dca1cb3c990ad0c849172ea24aed8c3cab9
source tree
20d039576d27d3ca927c0ade702131290eae948f
package artifact
4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e
package semantic
9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a
engine manifest
6ad3f01334725c83cc031ad9a9abfadf4922d62143e160e7defa4d37cf22a10a
repository Executor role
f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da
public baseline
514cea60053bab5303e86e6cacaa0260e960b3fe1670a658e2df1a6965ce978c
snapshot
e1f67f2bfcf1470a1c181a7e54fd4e318456c0dab2861a1b7e76d7443dba50fd
candidate seal
d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665
```

The private input was mode `0600`, SHA-256
`fd0931ccc75608aea22c232ee2400e9243ba77f1e046ba200d19ccc6c34e3914`.
The canonical genesis predecessor was
`09fd486ca4b12699ef42c94e596d584b3ad527aa7ea3054dc0a7a2d674b34ebe`.
That historical CLI append produced the accepted candidate-only reanchor
checkpoint as a direct child of `S_release`; its repository-aware validation,
ordinary postcommit verification, and 163-test suite passed. The current
active ledger has advanced to the exact one-plan state below, so the old
zero-plan checkpoint is not a current-state assertion.

Calibration, corpus, adaptive holdout, artifact receipt, exact-final review,
and isolated install each remain separate later authority gates. This reanchor
forbids model/provider calls, Executor pilot, live corpus or holdout,
exact-final review, install or reinstall, `codex plugin add`,
marketplace/cache/config mutation, publication, push, tag, release, activation,
claim release, and main/worktree switching.

## Calibration plan preparation

G028A stopped with an uncommitted plan after irrelevant global-config drift.
G028B restored the exact Git predecessor through `apply_patch`, invalidated
that attempt, and appended the corrected plan once through the CLI. This is two
operational applies across stopped attempts but exactly one final append
relative to Git. The canonical predecessor is
`6074d0d09626150da6e46451c28b693bae59f7d3553f5edffe1cd31c03a542ef`.
Corrected plan SHA-256 is
`bc359f594b933a72272e91cd91286bea65f0e91a98c4200ca5435479f9b8c678`.
The candidate and source identities are unchanged. The real private base and
`calibration-claims` child below are mode `0700`; `calibration-output` remains
absent:

```text
/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665
/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665/calibration-claims
```

The exact profile SHA-256 is
`72870436ea09ca1458a9f9da0fbcca128cb24226890eee3cf0092bba3aeca8de`.
It binds `gpt-5.6-sol`, `high`, `300000` ms, arm `candidate`, this absolute
worktree, and only `PYTHONDONTWRITEBYTECODE=1`. Its persisted argv is
`python3 -c <script>` followed by exactly `corpus --calibrate --plugin
<worktree> --output <base>/calibration-output --model gpt-5.6-sol --effort high
--timeout 300 --arm candidate`. The script rejects any other argv, parses with
the repository parser, loads the current ledger, requires its sole plan to be
the candidate-bound calibration plan with no receipts, builds every unit via
`evaluation.live.build_effect_intent`, and calls
`evaluation.cli.run_authorized` with the exact claims root. It contains no plan
or request digest and creates no authority or provenance.

The compact labeled resource-bundle canonical preimage is:

```json
{"candidate":{"candidate_sha256":"d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665","engine_manifest_sha256":"6ad3f01334725c83cc031ad9a9abfadf4922d62143e160e7defa4d37cf22a10a","executor_role_sha256":"f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da","package_artifact_sha256":"4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e","package_semantic_sha256":"9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a","snapshot_sha256":"e1f67f2bfcf1470a1c181a7e54fd4e318456c0dab2861a1b7e76d7443dba50fd","source_commit":"b3b79dca1cb3c990ad0c849172ea24aed8c3cab9","source_tree":"20d039576d27d3ca927c0ade702131290eae948f"},"codex":{"binary_sha256":"cb5e8cb8a333a408ce6adbe0d4fad1845c69772c2216af7c1f88c98a11460dc6","version":"codex-cli 0.146.0"},"external":{"executor_toml_sha256":"d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275"},"host_route":"evaluation.cli.run_authorized","paths":{"claim_root":"/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665/calibration-claims","output_root":"/home/caichenghang/.codex/happycodex-0.6-calibration-d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665/calibration-output"},"profile_sha256":"72870436ea09ca1458a9f9da0fbcca128cb24226890eee3cf0092bba3aeca8de","resource_bundle_type":"happycodex-0.6-calibration","schema_version":1,"unit":{"case_id":"subthreshold-control","semantic_input_sha256":"432ccf406316d95f9d122b9bb0602043cd64b1be6d541f01d9f9aba58df59c8d","snapshot_case_sha256":"d919711682049ce81f21649645fcc341dc34d0abda876a0a3c0fdc25e0e52d9d"}}
```

Its canonical SHA-256 is
`52541eef74610840c9f693b4e8de7c729569812eb5830044a47dca88d24ec85a`,
the plan's sole `resource_digests` member. Whole or selected models-cache and
global-config identities are deliberately excluded because neither is an
execution input. The global config was observed moving from SHA-256
`575ececef691e8c3cc18e20ba40c648ce17d1b3a5a3cb9b02750e914e8f5344a`
to `16a563c40cffbf8b4504e896e5a02ead63b639a09c30e70a35df2f59f0ca5eb0`
externally and was not modified here. The non-authoritative model rationale is
`272000` context, `272000` maximum, and `95%` effective. Recovery must not
reintroduce either whole-file binding. The repository enforces no internal
provider-turn or token cutoff; the external Executor TOML remains bound.

The exact canonical approval-request object is:

```json
{"allowed_effects":["one isolated temporary repository, home, and package install","one subthreshold-control Codex execution phase","external output, effect claim, and result artifacts under the bound roots"],"candidate_sha256":"d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665","cost_ceiling":{"model_calls":1,"output_tokens":100000,"uncached_input_tokens":1000000,"wall_milliseconds":360000},"cost_semantics":{"acceptance_limits":"token and wall ceilings are conservative post-run receipt acceptance limits, not an in-flight billing cutoff","historical_basis":"no accepted generation-6 historical cost exists","model_calls":"one external Codex execution phase, not internal provider turns","preemptive_bound":"the 300-second subprocess timeout is the only preemptive cost bound"},"exclusions":["all other live gates","active config, plugin, marketplace, and cache mutation","publication and activation"],"gate":"calibration","profile_sha256":"72870436ea09ca1458a9f9da0fbcca128cb24226890eee3cf0092bba3aeca8de","request_type":"happycodex-0.6-calibration","resource_bundle_sha256":"52541eef74610840c9f693b4e8de7c729569812eb5830044a47dca88d24ec85a","schema_version":1,"unit":"subthreshold-control"}
```

Its SHA-256 is
`44430bbff160bc4288f6d5a08ec99b78ac1082fb8e1851da0844393145e45014`.
The only canonical future grant line, including one trailing LF, is:

```text
APPROVE HAPPYCODEX 0.6 CALIBRATION 44430bbff160bc4288f6d5a08ec99b78ac1082fb8e1851da0844393145e45014
```

Those exact UTF-8 bytes have SHA-256
`c63f5b47a7a1d9126e6dd1dfbfb5559f66c870de6206b9d834a0b0b9a80a895c`.
The plan and line are audit bindings, not permission. `model_calls=1` means one
external Codex execution phase, not internal provider turns. The 300-second
subprocess timeout is the only preemptive cost bound. The one-million uncached
input, 100,000 output-token, and 360,000 ms ceilings are conservative post-run
receipt acceptance limits, not in-flight billing cutoffs; generation 6 has no
accepted historical cost.

The expected active-state test RED was its obsolete zero-plans assertion. Its
narrow replacement checks the sealed calibration plan, exact unit, no receipts,
and unchanged derived state. Isolated genesis, append, successor, schema, and
archive tests remain unchanged. No live dispatch occurred.

## Budgets and final checks

Runtime remains capped at 262 lines and 2,400 words, with 2,200 preferred.
Current combined Runtime is 235 lines and 1,689 words. This plan stays between
1,500 and 2,500 words.

Evaluation production currently measures 6,073 Python lines across the exact 16
declared modules. The 4,000–4,500 target is directional, not an acceptance
quota; this batch deletes identity and test semantic duplication but does not
compress unrelated evaluator behavior merely to hit a number. The actual final
measurement must remain reported.

Final offline commands are:

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

Dry runs must create no model call, intent, consumption, fixture, output,
workspace, network call, or receipt. Unknown commands and evaluator inputs fail
closed. The active ledger and plugin/market/config bytes must remain unchanged.

Live calibration, corpus, holdout, exact-final review, isolated install,
publication, and activation still each require later exact authority. No prose,
digest, intent, plan, claim, directory, or successful offline test grants those
effects.
