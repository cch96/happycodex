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
gates, live-call range, and historical combined-token/wall estimates. A live run is
not authorized by either command.

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
before that successor commit; zero-live artifact transitions require no authority.
The coverage manifest marks every current case and pair as refreshed or prior. Prior
coverage requires a strictly older digest-bound 0.4 certified ledger; validators
revalidate that chain and recompute its snapshot-to-successor impact, so pending scope
cannot authorize reuse by itself. Corpus and holdout run receipts bind the impact
token and authority digest; validators also bind the exact source engine, cases,
package/toolchain identities, adaptive policy, and cost gate. Impact and execution
share the same complete corpus/holdout schema validation. Fresh Native review remains
an external HappyCodex/ExecPlan completion gate over the exact product diff; the
evaluator deliberately defines no reviewer protocol or review receipt. Historical
v1-v21 ledgers remain reachable in Git and have no active-tree reader, alias,
migration, or compatibility path.

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
invocation. Compare an immutable public checkout with raw output outside both source
trees:

```bash
python3 -m evaluation.cli holdout \
  --candidate . \
  --public /path/to/public-checkout \
  --bind-impact <exact-impact-token> \
  --output /tmp/happycodex-holdouts
```

Raw events and identity-bearing metadata stay external. Only sanitized summaries,
digests, fixed fixtures, and the explicit ledger state may be tracked.

A holdout arm contributes quality evidence only after a completed, exit-zero runner
execution whose pass status agrees with its oracle failures. A timeout or nonzero exit
is infrastructure failure and aborts the pair; it is never scored as candidate quality.
