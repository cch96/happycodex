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

- semantic inputs: case/holdout data, prompt/schema/policy contract, runtime-semantic
  package projection, model, effort, timeout, and arm;
- harness inputs: every executable fixture/install/invoke/blind module;
- artifact inputs: receipt serialization, sanitization, and impact projection.

Every evaluator Python module and JSON case/schema is explicitly classified. An
unknown module fails validation. Semantic or execution-affecting harness changes fail
closed to the exact live gates; artifact-only changes require no model call.

`results/current.json` is the only active ledger. Its `refresh_required` state cannot
be promoted by offline checks. Historical v1-v21 ledgers remain reachable in Git and
have no active-tree reader, alias, migration, or compatibility path.

## Offline and live commands

Inspect one or every corpus case without a model call:

```bash
python3 -m evaluation.cli corpus --list
python3 -m evaluation.cli corpus --case receipt-mismatch --dry-run
```

After an exact persisted user cost approval, copy the `approval_token` from a fresh
`impact` receipt and run live corpus output outside the repository:

```bash
python3 -m evaluation.cli corpus \
  --case receipt-mismatch \
  --approve-impact <exact-impact-token> \
  --output /tmp/happycodex-corpus
```

Inspect the blinded adaptive holdout plan:

```bash
python3 -m evaluation.cli holdout --dry-run
```

After separate approval, compare an immutable public checkout with raw output outside
both source trees:

```bash
python3 -m evaluation.cli holdout \
  --candidate . \
  --public /path/to/public-checkout \
  --approve-impact <exact-impact-token> \
  --output /tmp/happycodex-holdouts
```

Raw events and identity-bearing metadata stay external. Only sanitized summaries,
digests, fixed fixtures, and the explicit ledger state may be tracked.
