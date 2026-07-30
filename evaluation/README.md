# Certification engine

The evaluator is maintainer-only standard-library support code and is excluded
from the shipped plugin. Its public command surface is:

```bash
python3 -m evaluation.cli verify
python3 -m evaluation.cli impact
python3 -m evaluation.cli apply --expected DIGEST --record RECORD.json
python3 -m evaluation.cli executor --dry-run
python3 -m evaluation.cli corpus --calibrate --dry-run
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
```

`verify` validates the closed evaluator inventory and the sole active ledger.
`impact` derives conservative invalidation without authorizing work. `apply`
atomically appends one complete release record with predecessor comparison.
Every dry run reports zero launches, consumed actions, fixtures, outputs,
workspaces, subprocesses, model calls, network calls, and receipts. Live model
execution is reachable only through the Host-only `run_authorized` boundary.

## Closed identity and fresh evidence

The evaluator has one exact input inventory: every declared evaluator Python
module, `contracts-v7.json`, `executor-role.json`, every corpus case, and the
holdout manifest and cases. Unknown or missing Python and JSON inputs fail
closed. The canonical inventory has one `manifest_sha256`; it has no
classification, subset, or tool-path digest. Any evaluator-bundle change
invalidates the full corpus, all holdouts, and the artifact receipt.

A source snapshot records only:

- model, effort, and timeout settings;
- the evaluator manifest;
- normalized package artifact and semantic identities;
- the external Executor role digest;
- the frozen public-0.2 identity;
- every corpus-case and holdout-pair semantic identity.

Source identity comes from a reachable normalized `git archive`, not dirty
working-tree bytes, and binds its commit and tree. A live corpus receipt adds
the actual Codex version and binary-content digest plus the model invocation
profile. It records no executable path or machine toolchain identity.

`results/current.json` is the only active evidence ledger. Generation 7 starts
as the empty `{candidate, plans, receipts}` genesis and derives
`refresh_required`; offline checks cannot promote it. There is no old reader,
alias, migration, dual write, parser fallback, evidence reuse, or coverage
reuse. Evidence commits must strictly descend from and postdate their reachable
candidate source.

The comparison arm remains exactly public-0.2 at commit `3b9c11f`, tree
`4708ebc`, with its frozen package identities and four-file Runtime surface.
Other public bytes or receipts cannot be relabeled as that arm.

## Host authority and content binding

Repository data does not authenticate user, task, message, turn, or session
provenance. A `GatePlan`, approval digest, `ActionKey`, or `LaunchKey` is
audit-bound content, never permission. Root/Host orchestration must
independently possess current-task authority and choose to enter
`run_authorized`; the repository cannot manufacture or recover that authority.

The authorized boundary reloads the active ledger, requires an active
nonfailed candidate and its next persisted plan, and reconstructs every exact
launch. `StateKey` binds the gate facts; reducer output plus exact
target/scope/falsifier/evidence source derives `ActionKey`; `LaunchKey` binds
the infrastructure generation, invocation, output, and approval content. The
supplied launch set must equal the persisted plan exactly.

For each unit the evaluator:

```text
validates candidate, plan, launch, paths, binary, and package identities
  -> reserves LaunchKey and the absent no-follow output
  -> completes local fixture/mapping/workspace preflight
  -> atomically consumes ActionKey immediately before provider work
  -> emits a typed result for the eventual GateReceipt
```

Action consumption is durable and cannot be retried or deleted. A proven
pre-provider `NO_EFFECT` result consumes only its launch and permits one
replacement with a distinct infrastructure generation; provider-reached,
billable, or ambiguous work consumes `ActionKey`. Claims are private
mode-`0600` regular files beneath a pre-existing mode-`0700` root. Collisions,
partial sets, unsafe unit names, aliases, symlinks, output drift, or an output
inside the repository/evaluated package refuse before the corresponding
effect. Raw model events, secrets, unsanitized streams, and hidden oracle
bodies stay outside Git.

## Release records and gates

The ledger persists exactly three record types:

1. `ReleaseCandidate` binds Git source, package, evaluator, external role,
   public baseline, and snapshot.
2. `GatePlan` binds one gate's exact profile, cost ceiling, units, resources,
   output, and approval-request/content digests.
3. `GateReceipt` appends one immutable typed result with evidence commit and
   predecessor/tip binding.

Pending gates, coverage, receipt tip, freeze eligibility, failure, and
certification are derived, never stored. The only writer uses prior-digest
comparison, no-follow reads, an adjacent temporary regular file, atomic
replacement, and directory synchronization.

Calibration, full corpus, adaptive blinded holdout, artifact receipt,
exact-final review, and isolated install are distinct persisted gates. The
first three are independently model-reaching and require their own exact Host
authority and cost basis. Publication and activation remain later external
authority boundaries; neither is implied by certification or installation.
Activation retains paired package/config/cache rollback state.

Maintainer evaluation also proves native same-task compaction and distinct
no-summary/no-handle reconstruction from durable facts. Writer identity cannot
be replaced. Behavior comparison uses fresh isolated homes/tasks, identical
model, effort, fixture, prompt, timeout, and oracle, and reveals arms only after
results freeze. The first completion-blocking regression rejects; after first
success a second distinct pair runs, with a third only for split or uncertain
results. At equal quality, uncached input plus output tokens and wall time each
remain within 25% of public-0.2.
