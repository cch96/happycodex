# Certification engine

The evaluator is maintainer-only, pure-standard-library support code. It is excluded
from the shipped plugin. The sole command surface is:

```bash
python3 -m evaluation.cli verify
python3 -m evaluation.cli impact
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
```

`verify` validates the complete classified engine inventory and the tracked evidence
ledger. `impact` is read-only: it reports exact invalidated cases/pairs, downstream
gates, live-call range, and historical combined-token/aggregate-call-wall estimates.
The wall estimate is summed exposure, not elapsed runtime under bounded concurrency.
A live run is not authorized by either command.

## Identities and evidence

The engine records three independent identities:

- semantic inputs: case/holdout data, prompt/schema/comparison policy,
  runtime-semantic package projection, model, effort, timeout, and arm;
- harness inputs: every executable fixture/install/invoke/blind/control/authority
  module and exact Python/Codex/Git/rg toolchain identities; Python also binds the
  standard-library tree, shared-library closure, and resolver bytes;
- artifact inputs: receipt serialization and sanitization only.

Every evaluator Python module and JSON case/schema is explicitly classified. An
unknown module fails validation. Semantic or execution-affecting harness changes fail
closed to the exact live gates; artifact-only changes require no model call.

`results/current.json` is the only active ledger. Its `refresh_required` state cannot
be promoted by offline checks. `certified` requires a Git-reachable successor whose
normalized Git package artifact, engine manifest, and source pending impact match the
snapshot, plus strictly later content-addressed corpus and holdout evidence for every
refreshed item. Nonzero live scope also requires the exact authority to be persisted
before that successor commit; zero-live artifact transitions require no authority but
do require strictly post-source, content-addressed `offline_summary` evidence. That
summary binds the source ledger bytes and current artifact identity for a `receipt`
gate, and binds the exact source/installed package receipt for `isolated_install`.
The coverage manifest marks every current case and pair either refreshed or, under one
explicit exact corpus/holdout waiver, waived. Mixed, partial, and prior dispositions
fail closed; 0.4 evidence remains Git history with no active reader, alias, migration,
or compatibility path. Corpus and holdout receipts bind the impact token, authority,
source engine, cases, package/toolchain, adaptive policy, and cost gate. Impact and
execution share complete input validation. Fresh Native review remains an external
HappyCodex/ExecPlan gate over the exact product diff; the evaluator defines no review
receipt.

## Offline and live commands

Inspect one or every corpus case without a model call:

```bash
python3 -m evaluation.cli corpus --list
python3 -m evaluation.cli corpus --case receipt-mismatch --dry-run
```

`impact` emits an `impact_token`, but that hash is not approval. After the user
approves the exact printed maximum cost and invocations, a maintainer must persist a
`live_authority` receipt in `current.json` with a current-task user source and exact
package/settings/scope descriptors. The verbatim approval response must be the
canonical line `APPROVE HAPPYCODEX LIVE COST <approval-request-sha256>`; arbitrary
nonempty prose, including a rejection, grants nothing. The ledger's historical-cost
envelope must also exactly equal the source-derived receipt. Only then may the same
fresh token be bound to a live corpus run whose output stays outside the repository:

```bash
python3 -m evaluation.cli impact --public /path/to/public-checkout
```

Persisted authority validation mints an immutable process-local capability. Corpus
and holdout propagate and rebind it at every model-reaching evaluator, pair, and
subprocess seam; callers cannot substitute a digest string or a mutable descriptor.

Without `--public`, impact stays useful for cost inspection but reports
`live_authority_ready: false` when a holdout refresh is pending.

```bash
python3 -m evaluation.cli corpus \
  --bind-impact <exact-impact-token> \
  --output /tmp/happycodex-corpus
```

Inspect the blinded adaptive holdout plan:

```bash
python3 -m evaluation.cli holdout --dry-run
```

The same persisted authority must separately name the exact adaptive holdout
invocation. Compare the immutable public `v0.4.0` package with raw output outside
both source trees:

```bash
python3 -m evaluation.cli holdout \
  --candidate . \
  --public /path/to/public-checkout \
  --bind-impact <exact-impact-token> \
  --output /tmp/happycodex-holdouts
```

Raw events and identity-bearing metadata stay external. Only sanitized summaries,
digests, fixed fixtures, and the explicit ledger state may be tracked.

A completed exit-zero result with oracle failures is negative behavior evidence: corpus
persists its failing summary, while holdout freezes the blind decision, reveals the
mapping, and persists the regression receipt. Timeout, nonzero exit, or exception is
infrastructure failure and aborts before summary or reveal promotion.

This repository's maintainer release workflow—not ordinary HappyCodex Skill Runtime—
uses three independent exact-final roles: correctness/QA `max`,
release/preservation `max`, and simplification `high` (escalate for a large diff,
recurrence, legacy bypass, or unresolved complexity). Give every role its own fresh
session and durable output; only that role's two phases share a session. After their
clean union, run the complete corpus once with at most four workers and stable
case-order projection. Holdout pairs stay serial and adaptive; only the current pair's
two blinded arms overlap, with stable alias projection. Corpus and holdout never
overlap.
Track unique simplification blockers per release. Only a later authorized amendment
may merge roles, after three consecutive releases with no unique simplification blocker.

Review identity binds product tree, reviewer role config, and review toolchain; its
change invalidates exact review only. Behavior identity binds semantic package,
evaluator semantic/harness inputs, settings, and evaluator toolchain. Artifact identity
binds normalized package bytes and install receipt. Invalidate only evidence consuming
the changed layer; ambiguity fails closed as semantic change.

No call is retried automatically. Infrastructure failure ends the authorized attempt;
this workflow authorizes no rerun. A later attempt requires a separately persisted exact
invocation and a new canonical user cost approval; the prior grant cannot be reused.

Historical per-call wall times imply a conservative 21–40 minute planning band for a
complete corpus plus adaptive holdout under this schedule. This is not a live
measurement or certification claim, and bounded concurrency does not reduce token cost.
