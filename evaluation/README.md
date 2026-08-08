# HappyCodex v3 thin verifier

This maintainer-only evaluator is not part of the installed plugin runtime. It
is a deterministic verifier over immutable inputs supplied by a separate,
trusted execution boundary. It has exactly four durable record types:
`ProductArtifact`, `EvalSpec`, `Attestation`, and `ReleaseReceipt`. Unknown
types and unknown fields fail closed; there is no compatibility reader,
migration, active ledger, or general evidence graph.

## Trust domains

Codex-native workflow owns planning, routing, implementation, and review
reasoning. The repository evaluator owns canonical serialization, closed
schemas, product and evaluator identities, the fixed topology, offline oracle
scoring, and stateless relationship verification. The external boundary owns
user authority, provider and release effects, global one-shot/idempotency,
trusted time, effect history, recovery decisions, evidence authentication, and
release readback.

Repository code can construct an unsigned authority request. It cannot create
or infer user authority. `evaluation.verify` therefore requires injected
external authority and evidence validators. `evaluation.host` is only a pure
adapter that seals an externally supplied terminal statement after checking
its digest and recomputing its assessment; it does not validate the signature
or perform an effect.

## Fixed evaluation

One `EvalSpec` contains the single canonical 12-unit topology: five behavior
units, six holdout units forming three fixed concurrent pairs, and one neutral
exact-final. Component identities keep provider input, private oracle, and
harness changes separate.

Behavior and holdout provider inputs come only from the production manifest,
fixed cases, closed schemas, and product guidance. They cannot contain hidden
oracles, mappings, expected answers, desired verdicts, or history. Exact-final
input is derived only from the fixed review policy, both immutable
`ProductArtifact` values, a readable immutable `ReviewProjection`, and the
fixed response schema. There is no caller prompt, path, obligation list,
preservation claim, workflow claim, or repair history in that contract.

The exact-final effect subject binds the candidate artifact and fixed review
contract, not an authority nonce or `EvalSpec` identity. Thus the same
candidate under the same policy has one effect identity. A landed adverse or
malformed report and an `unknown` terminal stop that effect; repository code
cannot authorize a friendlier rerun.

Each external attempt records both its own wall milliseconds and cumulative
wall milliseconds for the effect. A sequence must start at attempt zero, be
contiguous, bind the exact prior-record history digest, and contain only
authenticated, zero-use `not_landed` predecessors. A `landed` or `unknown`
attempt is terminal. The final cumulative value must equal the sum of every
signed attempt wall value and remain within the unit cap. Evaluation applies
the absolute cap to the sum of all terminal cumulative values.

Holdout mappings remain outside provider input. Scoring does not inspect them
until exactly six authenticated landed terminals exist. Each revealed mapping
must match its commitment and label one candidate and one previous-product arm.
Candidate score must meet the baseline in every pair, aggregate candidate
input plus output tokens must be no more than 1.25 times baseline, and the
corresponding wall ratio is retained only as a diagnostic. No caller-supplied
reveal timestamp exists.

Release uses separate user authority and a separately authenticated one-shot
terminal. Verification succeeds only for a complete `landed` receipt whose
readback exactly matches the destination, product, target, installed plugin
projection, and rollback identity.

## Command surface

The CLI exposes only deterministic construction, qualification, validation,
inventory, and offline checking:

```bash
python3 -B -m evaluation.cli inventory
python3 -B -m evaluation.cli materialize --help
python3 -B -m evaluation.cli qualify --help
python3 -B -m evaluation.cli authority --help
python3 -B -m evaluation.cli validate RECORD_OR_REVIEW_PROJECTION.json
python3 -B -m evaluation.cli checks --help
python3 -B -m evaluation.cli verify
```

`authority` emits a qualified unsigned request and labels authority as
unauthenticated. The CLI has no external authenticator, so `verify` returns
`UNVERIFIED` with a nonzero exit code instead of treating JSON or a local hash
as proof. An external boundary must call the typed `evaluation.verify` API with
its validators.

`checks` first requires the repository HEAD, tree, worktree, and reconstructed
Git snapshot to equal the supplied `ReviewProjection` candidate. It then runs
the fixed offline unit, import, Skill, plugin, and diff checks directly. Its
line counts are decoded from the candidate snapshot itself, and its output is
bound to `candidate_snapshot_sha256`; it accepts no claimed count or result.

## Explicit non-proofs

These records do not by themselves prove who authorized an effect, that an
external signature is genuine, that a provider was invoked at most once, that
a clock or no-effect observation is trustworthy, that an `unknown` effect is
safe to repeat, or that a release destination contains the claimed bytes.
Those guarantees remain external and must be checked through the injected
validators and authenticated readback. Without them, the honest result is
`UNVERIFIED`, never success.
