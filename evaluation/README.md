# Certification engine

The evaluator is maintainer-only standard-library support code. It is excluded
from the shipped plugin. Its sole command surface is:

```bash
python3 -m evaluation.cli verify
python3 -m evaluation.cli impact
python3 -m evaluation.cli executor --dry-run
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
```

`verify` validates the classified engine inventory and the sole active ledger.
The three dry-runs inspect exact work without creating a capability, consuming a
claim, making a fixture/output/workspace, invoking a model, or using the network.
`impact` currently fails closed because generation 6 has no persisted cost
envelope or exact future invocation. No standalone CLI argument, environment
variable, impact token, ledger record, or prose response is live authority.

## Identities and fresh evidence

The engine records independent identity layers:

- semantic inputs: cases, holdouts, strict terminal/schema/comparison policy,
  the semantic package, model, effort, timeout, and arm;
- harness inputs: every executable evaluator module plus the exact resolved
  Python, Codex, Git, rg, and sandbox binary path/hash/version identities;
- artifact inputs: receipt projection, sanitization, and the exact external
  `evaluation/executor-role.json` contract.

Every evaluator Python module and case/holdout JSON input is classified as
semantic, harness, or artifact. Unknown inputs fail closed. Impact planning and
execution use the same strict input schema from `evaluation.core.ledger`.

`results/current.json` is the only active evidence ledger. Generation 6 is a
fresh `refresh_required` genesis: all three authorities are null, calibration and
accepted evidence are empty, receipt head and certification are null, and the
pre-anchor source, planned impact, and planned invocations are null. G015U keeps
that genesis in candidate `S2`; future G016 alone may anchor its reachable
Git archive. Offline checks and summaries cannot promote it to `certified`.

The comparison arm is exactly `public-0.2`: commit `3b9c11f`, tree `4708ebc`,
the frozen artifact/semantic digests, and only `SKILL.md`,
`agents/openai.yaml`, `references/external-review.md`, and
`references/task-packets.md`. Public-0.4 bytes or receipt fields cannot be
relabeled as that arm.

There is no reader, alias, migration, dual write, prior-coverage reuse, or parser
fallback for older evidence. Evidence commits must strictly descend from the
anchored source and remain reachable from `HEAD`. Source identity comes from
`git archive`, not dirty working-tree bytes, and binds source commit/tree,
normalized package artifact and semantics, engine manifest, and external
Executor role digest.

## Effect authority and claims

Live authority can originate only in private trusted host metadata for the
current task/message/turn. The host binding includes root/source/Executor task,
owner, destination, lineage, role config, repository, outcome, message, turn,
content, session, thread, permission, and claim identities. Semantic enforcement
must return `ALLOW`. The validator then seals `GateCapability` only from the
persisted plan, trusted authority, and reducer report; callers cannot supply
authority, AttemptKey, resources, or output claims. The exact effect order is:

```text
read-only persisted-plan, identity, path, schema, and provenance validation
  -> enforce ALLOW and mint GateCapability
  -> namespace lock plus complete collision preflight
  -> O_EXCL authority/AttemptKey/resource/output claim set
  -> ClaimedCapability
  -> O_EXCL exact unit claim
  -> authorized fixture/mapping/workspace/output effect
  -> bind exact argv/cwd/env/timeout/PID into one-shot PhaseProof
  -> invoke_codex spends only that proof
```

Claims are mode-`0600` no-follow files in the resolved Git common directory's
precreated mode-`0700` `happycodex/effect-claims/v6` namespace. A collision
or partial/reused set refuses before another claim or effect. Claims are durable
consumption: no retry or deletion occurs. Gate/claimed capabilities, copied
proofs, wrong process/invocation, and spent proofs refuse before subprocess.

Raw outputs require an explicit absolute absent path under an existing real
parent, outside the repository and every evaluated plugin. Symlinks, implicit
temporary destinations, parent creation, and in-repository output reject before
effects. Raw model events, secrets, unsanitized streams, and hidden oracle bodies
stay outside Git; only sanitized summaries, hashes, fixed fixtures/prompts,
hidden-oracle hashes, and executable evaluation code may be tracked.

## Recovery and future gates

Maintainer evaluation proves native same-task compaction and a distinct
no-summary/no-handle reconstruction from durable repository/control facts. It
also proves copied or serialized capabilities, cross-task authority, replacement
writers, wrong role/config/session/thread/destination/lineage/claim bindings, and
concurrent recovery cannot reconstruct permission.

Executor calibration, corpus, and adaptive holdout are three future authority
gates. Each first needs a persisted source-derived cost envelope and complete
exact invocation, then its own canonical current-task user approval. Calibration
has no inherited historical cost; only one separately authorized bounded pilot
may establish a sanitized actual-cost basis. Corpus authority cannot authorize
holdout, and neither authorizes installation or release.

Read-only behavior comparisons use fresh isolated homes/tasks and identical
model, effort, fixture, prompt, timeout, and oracle. Arm identity is revealed
only after results freeze. The first completion-blocking regression rejects; a
first success requires a second distinct pair, and a third is used only for a
split or uncertain result. At equal quality, uncached input plus output tokens
and wall time must each remain within 25% of public 0.2.

Release-source preparation, exact-final review, isolated install, release, and
activation remain later separate gates. Release preparation uses the official
plugin-creator cachebuster helper exactly once; isolated install never reruns it.
Activation is atomic and retains the paired prior package/config/cache state for
rollback.
