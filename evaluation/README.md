# Behavior corpus

`run_corpus.py` builds each JSON fixture in a fresh temporary Git repository,
packages only the plugin runtime/metadata (never this evaluation directory), installs
it into an isolated `CODEX_HOME`, and starts a fresh ephemeral read-only Codex task.
The model sees the fixture and neutral prompt, not the case oracle. Results and usage
are written to the requested output directory; keep raw runs outside the repository
and commit only sanitized summaries and digests.

The evaluator itself never writes. `execplan_condition` records a durable fact rather
than an action. `protocol_may_product_write` asks whether Root may immediately change
product files before any mandatory user or control-plane action; ExecPlan writes do
not count. The other `protocol_may_*` fields carry review and completion gates, so
read-only evaluation is not mistaken for a missing implementation permission.
`finding_classifications` makes stable baseline/candidate identities machine-checkable
instead of relying on whether a free-text summary repeats a keyword.
`decision` is only coarse next-step routing: safety cases accept either continued
remediation, a user stop, or an incomplete hold when the gates and evidence agree.

Validate fixture/schema coverage without a model call:

```bash
python3 evaluation/run_corpus.py --dry-run
```

Run one case:

```bash
python3 evaluation/run_corpus.py --case receipt-mismatch --output /tmp/hc-results
```

Run the complete candidate corpus by omitting `--case`. Compare a public-0.2 arm
with the same model, effort, timeout, fixtures, prompts, and oracles. Never put the
arm mapping or expected result in a task-visible repository or prompt.

After the final candidate review is green, inspect the frozen three-pair holdout plan
without a model call:

```bash
python3 evaluation/run_holdouts.py --dry-run
```

Run the blinded adaptive comparison against an immutable public-0.2 checkout:

```bash
python3 evaluation/run_holdouts.py \
  --candidate . \
  --public /path/to/public-0.2 \
  --output /tmp/happycodex-holdouts
```

The runner commits a nonce-protected alias mapping before either arm runs, persists
the blind decision before reveal, always runs a second pair after a non-regressing
first pair, and uses the third only for split or uncertain results. A regression
rejects immediately. The 25% release gate uses only cumulative uncached-input plus
output tokens and wall time; separate input/output ratios are diagnostic. Raw events
and identity-bearing metadata remain in the external output directory.
