# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint, authority, and current state

The accepted repair source is commit
`91e72ba255f3e9e4b4e8746e859bb59357a12e09`, tree
`ae276c2a0a1295647da0301a20043cfeb6d92bbf`, direct child of
`c587f8e9ee4a07b34fcba00e7a1ae0fe3fe299eb`, on branch
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

Root then granted `HC06BR-G-030-fresh-candidate-after-path-repair`. Its
mode-`0600` intent SHA-256 is
`40bf06334af170266829811b794e96d900d705b8a80efb50195a2b80841a6e84`.
G030 authorizes only one fresh `ReleaseCandidate`, the narrow active-state
test, this index, and their direct-child commit. It grants no `GatePlan`,
receipt, evidence, cost, model/provider work, live gate, install, publication,
or activation effect.

## Fresh candidate and one-shot transition

The candidate was recomputed from the exact committed repair source:

```text
source commit
91e72ba255f3e9e4b4e8746e859bb59357a12e09
source tree
ae276c2a0a1295647da0301a20043cfeb6d92bbf
package artifact
4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e
package semantic
9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a
engine manifest
ffdc07be358c664d4c710e187350f3289c6e0b9f8321d77fa291a5465797c47d
Executor role
f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da
public baseline
514cea60053bab5303e86e6cacaa0260e960b3fe1670a658e2df1a6965ce978c
snapshot
68d17de6ffca4b4a3f6dc3a04c2d1d98f64ffb8eb6aed9c031a0171cdbe41bd1
created_at
2026-07-30T13:24:47Z
candidate seal
12f7bce171d89f8e0f8da5d255872879048fa3e7ef6f8bb73f75005293516b85
```

The private input `/tmp/happycodex-g030-release-candidate.json` is mode `0600`,
886 bytes, file SHA-256
`e3bc0eb81be8659054f973c99ee898d566683164ebc41a074cc2604b1c3766a3`.
It passed repository-aware validation before the only apply:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli apply \
  --expected 09fd486ca4b12699ef42c94e596d584b3ad527aa7ea3054dc0a7a2d674b34ebe \
  --record /tmp/happycodex-g030-release-candidate.json
```

The command ran once, exited zero, and was not retried. The resulting ledger
canonical SHA-256 is
`84c43fc00ae1d72b5626a163ef76d96ea003288ec4037d765908dfa19f8eb1c2`
and file SHA-256 is
`2710cc09be6985ab9827267d26c130e63821a5675f02e8bb8dc3aac40197c429`.
It contains exactly this candidate, zero plans, and zero receipts. It derives
`refresh_required`, all six pending gates, empty coverage/failures, and no
certification. No old evidence was migrated or reused.

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

G030 changes exactly:

```text
evaluation/results/current.json
tests/test_certification_engine.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

The active-ledger test asserts the exact fresh candidate and its seal, zero
plans/receipts, `refresh_required`, all six pending gates, empty
coverage/failures, and no certification. Isolated genesis, append, successor,
schema, archive, and prior-Git drift tests remain unchanged.

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

`verify` and `impact` must return zero on the candidate-only ledger. All four dry
runs must return zero with nine zero effect counters. Runtime/package/version,
marketplace, active source/cache, old effect claim/output, evaluator inventory,
budgets, and exact diff must remain protected. Global config and models cache
are not inputs and must not be modified.

After Root accepts this candidate-only commit, the next separately authorized
gate is a fresh calibration `GatePlan` bound to candidate
`12f7bce171d89f8e0f8da5d255872879048fa3e7ef6f8bb73f75005293516b85`.
G030 stops before any `GatePlan` construction.
