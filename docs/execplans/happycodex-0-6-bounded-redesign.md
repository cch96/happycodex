# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint and authority

G037 starts from commit
`48ae9dab69bb6488fd395bf555192fb84aae7f28`, tree
`8c9870b4fc4752e0e305f2721359e9d140080a1f`, on
`codex/happycodex-0.6-bounded-redesign`. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, remains the sole writer.

The held mode-`0600` task claim is:

```text
/tmp/happycodex-0.6-bounded-redesign-resource-claim.json
sha256 7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926
owner token 9bb64b0b657a5988407f63345fee2df1b9745bba59847a863efc4d7939512904
```

G037 intent is mode `0600`, SHA-256
`88e4ab6b1dc097067f192e425fda5552ba577a5b206a8d607097e193f1a0b7c3`.
It was persisted before tracked mutation. Root then relayed an exact user
override before any fresh-plan effect: skip the fresh `GatePlan`, resource
bundle, approval request/line, output/claim epoch, and private plan input.
The override narrows G037 to contracted source, one product candidate, full
offline acceptance, one commit, and one terminal receipt.

## Why G037 exists

G036 consumed its exact calibration authority once. The provider returned HTTP
400 `invalid_json_schema` at `properties.reason`: a bare internal `$ref` did
not point to a provider-visible top-level definition. The attempt created one
durable effect claim and raw external error artifacts, but no successful model
completion, token usage, sanitized result, `GateReceipt`, or historical cost
basis. It was not retried.

The immutable G036 receipt is mode `0600`, SHA-256
`a973cc6a382955f31ba80af387c25dae8c5fd3a6a4e5aca348195df47c5111bb`.
Its candidate, plan, request, claim, and output are consumed recovery anchors.
The old approval request
`87adab8557b37df8b8502acf552de47973d584f2324fec32ea985c9ee2ade93d`
is never reusable.

## Contracted design

The internal schema remains strict. Provider projection recursively expands
only exact bare references of the form `{"$ref":"name"}` from the closed
contract definition map, deep-copies the expansion, and removes
`uniqueItems`. Unknown, cyclic, or non-bare references fail closed. The
provider schema therefore contains neither `$ref` nor `uniqueItems`, while
internal validation still rejects duplicate arrays.

The declarative `mcp` invocation-profile field and the fake
`orchestrator.mcp.enabled=false` CLI override are deleted. Offline regression
uses a fresh isolated home and proves:

```text
codex mcp list --json => []
codex debug prompt-input => no <apps_instructions>
```

The profile still disables apps and remote plugins through supported feature
flags. Neither regression calls `codex exec`, a model, a provider, or the
network.

Release identity now has one clean split:

- `ReleaseCandidate` binds only Git-reachable product source, normalized
  package artifact/semantics, and the fixed Executor role.
- Every `GatePlan`, when one is separately authorized later, binds the exact
  current evaluator snapshot through `snapshot_sha256`.

Repository-aware candidate validation compares the archived product identity
to the record and the current product package/role to that archive. Evaluator-
only descendants therefore preserve the product candidate. Product package or
role drift invalidates it. Repository-aware ledger validation requires every
persisted plan, including non-model gates, to bind the current snapshot;
model-gate plans additionally bind exact units, model, effort, timeout, and arm.

## Current product candidate

The contracted candidate is:

```text
source commit
825962522c8ba6abb8dea3f7f7f04b8029e339fe
source tree
36aa681a5c7bd7ab5dd29e2df96d52d965c41fc2
package artifact
4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e
package semantic
9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a
Executor role
f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da
created_at
2026-07-30T15:56:08Z
candidate seal
84e6c7f529dab0583b93bb74b0428027ceea83d986f56be9ed4d4086aaaa24fb
```

The current evaluator identities are not candidate fields:

```text
engine manifest
c2ea7af25a3536d30ae7c9717d724ec63f6830ff4ba32c7509b71dc634f5f126
snapshot
b0cfd51cf27fe588bfb67e7f1f17569aca835c730eb637d2f2cb2e9df840337e
```

`evaluation/results/current.json` contains exactly that candidate,
`plans=[]`, and `receipts=[]`. Before this document edit its canonical SHA-256
is `5329bb9e4cb76bef8005fb4387763648e94605a8f493349aa8984be2961a1f03`
and file SHA-256 is
`83fabbf4227817caadc5eb272dd1dcb464c91e3beb4d746b09306b09c005fffd`.
Repository-aware validation succeeds. Derived state is `refresh_required`;
all six gates are pending, calibration is unplanned, coverage and failures are
empty, and certification is false.

No G037 calibration base, claims directory, output directory, candidate input,
or plan input was created. No resource digest, approval digest, approval line,
cost authority, or effect intent exists for G037. Any future calibration plan
starts under a separate exact user grant.

## Frozen protocol and safety

HappyCodex 0.6 has one fixed Executor per task/worktree; Root grants and
verifies. Runtime lifecycle is only
`working -> candidate_frozen -> exact_final -> closed`. One
obligations/evidence table holds durable work, correction is event-driven, and
the same unchanged failure is never retried.

Release persistence has exactly `ReleaseCandidate`, `GatePlan`, and append-only
`GateReceipt`. Pending gates, coverage, receipt tip, freeze eligibility,
failure, and certification are derived. A plan is an audit/cost binding, never
permission. One canonical `EffectIntent` is durably consumed before any
model-reaching work.

Generation 6 is a clean break: no migration, alias, dual write, fallback,
prior-evidence reuse, or coverage reuse. Unknown evaluator inputs, package
drift, aliased paths, duplicate records, malformed output, and baseline drift
fail closed. Raw model events, secrets, hidden oracles, and unsanitized output
stay outside Git.

Active plugin, marketplace, cache, configuration, publication, activation,
branch/main, task-claim, and live-gate changes always require separate exact
authority. G037 changes none of them.

## G037 tracked scope

G037 changes only:

```text
evaluation/corpus/engine.py
evaluation/contracts-v6.json
evaluation/core/identity.py
evaluation/core/ledger.py
evaluation/results/current.json
tests/test_evaluation.py
tests/test_certification_engine.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

`tests/test_contracts.py` was authorized but not needed. Runtime Skill
Markdown is unchanged.

## Acceptance and next gate

Required offline checks are:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli verify
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli impact
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli executor --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --calibrate --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli holdout --dry-run
git diff --check
```

Before commit, `verify` and `impact` may fail only because `load_ledger`
requires the worktree ledger to equal `HEAD`. After the single G037 commit,
both must be GREEN. All dry runs must report nine zero effect counters.

The pre-document full suite is 169/169 GREEN. Final acceptance also proves the
Runtime remains within 262 lines, 2,200 target words, and 2,400 hard-ceiling
words; this ExecPlan remains within 350 lines and 2,200 words.

G037 stops after one Git-reachable direct-child commit, post-commit offline
GREEN, and one mode-`0600` terminal receipt. It performs zero model/provider/
network calls and creates no `GatePlan`, approval artifact, live evidence, or
`GateReceipt`. Root alone decides whether a later task should plan calibration.
