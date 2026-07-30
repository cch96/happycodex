# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Current checkpoint and authority

This plan supersedes the four-module semantic-controller and evidence-DAG
Outcome. It is the current index, not a migration history. The recovery
checkpoint is branch `codex/happycodex-0.6-bounded-redesign`, worktree
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign`,
commit `ba56bfa835830169d3c8c799082516188bb4e575`, tree
`444c63a4d6b03782c8dafb776497aa410d79d135`. G019 terminal-receipt SHA-256 is
`ea2b2a3a09bbdda149b7c138367af93ba41896d45d91a8863336c31926c03e4e`.
The active ledger SHA-256 is
`b52d43128ef303f58f059a6f95195802914775ca1281a49648ae726ad6fd571c`;
it is anchored-empty and noncertified.

The same Root reads, decides, grants, and verifies. The same fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, is the sole writer. The existing mode-`0600` claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
continues to bind this worktree, ref, and ledger. It is not released or replaced.
No new Root, replacement writer, delegation, cross-task coordination, merge,
cherry-pick, or migration is allowed.

The operative amendment is exactly:

```text
好的 执行吧
```

Its UTF-8 SHA-256 is
`090a0814415d60fa61a0eeb425afe4fb83536bf25391dcf6a1fbeff4954bbcb9`
without a newline and
`c3ddfefbb057c1a88fe458584f0a6643c203fb44db75300a62d064f800e79255`
with one newline. It authorizes the offline product, test, and documentation
work below and, after those batches are accepted, separately scoped preparation
and reanchor of a new candidate source. It does not authorize a model call,
live Executor/corpus/holdout, exact-final, install, publication, marketplace,
configuration or cache mutation, or activation.

## Frozen normalized Outcome

Contract HappyCodex 0.6 into a smaller, reachable protocol. Shipped Runtime is
guidance for one fixed Executor per task/worktree: Root grants and verifies,
work is tracked in one obligations/evidence table, and correction is event
driven rather than timer driven. The same unchanged failure must not be retried.
One coherent repair wave is allowed; after one boundary-level alternative still
fails, return to the user. Lifecycle is only `working -> candidate_frozen ->
exact_final -> closed`.

Delete explicit `ProgressKey`, `AttemptKey`, family, repair-batch, recurrence,
and generic facts/action/effect-controller bookkeeping. Delete the generic
semantic package after consumers move to one strict direct protocol-result
validator, preferably `evaluation/protocol.py`; create no adapters subsystem.
Keep behavioral corpus fixtures and affected-surface inventory for real risks,
but remove mechanical six-surface tables and structure-as-correctness tests.

Authority belongs to Root/Host orchestration. Repository code does not
authenticate task, message, or turn provenance, and a grant file is audit
content rather than security provenance. A future official host attestation may
be accepted at the boundary. Ordinary repository execution must remain
reachable without a repo-local fake issuer, private seal factory, or monkeypatch.

One canonical `EffectIntent` binds candidate identity, gate, exact
invocation/profile, cost ceiling, units, resources, and output. Execution makes
one atomic durable `intent_digest + unit` no-follow `O_EXCL` consumption, writes
to an absent no-follow output, and produces one typed result receipt. Remove
`TrustedHostContext` and the multi-class capability/PID/nonce plus
authority/attempt/resource/output/phase claim ladder. The intent proves content
binding and audit history, not permission.

Release persistence has exactly three record families:

1. `ReleaseCandidate`: Git source commit/tree, normalized package digest, one
   evaluator-bundle digest, external role/config digest, and public baseline.
2. `GatePlan`: gate, exact invocation/profile, cost ceiling, units, resources,
   output, and the initial affected scope needed by that gate.
3. append-only typed `GateReceipt`: immutable result and predecessor/tip binding.

Pending gates, coverage, receipt tip, freeze eligibility, failure, and
certification are derived. They are never stored as caches or mirrored in a
second lifecycle state machine. A single reachable CLI transition/writer owns
schema validation, prior-Git comparison, atomic replacement, and receipt
append; operators never hand-edit a double ledger.

Executor calibration becomes fixed `corpus --calibrate` execution of the
retained calibration case. It still requires a distinct exact cost approval,
but has no separate capability mechanism. Corpus quality, blind adaptive
holdout, exact-final, isolated install, publication, and activation remain
distinct outcomes and gates. Artifact receipt binds the candidate; it is not a
quality gate.

Identity retains Git archive commit/tree, normalized package, evaluator bundle,
external role/config, public baseline, and the actual model and Codex version in
live receipts. Drop exact Python/Git/rg paths and hashes and category/scope
digest algebra. Any semantic evaluator change conservatively reruns every
affected full gate.

Claims remain narrow: one task-duration worktree/ref lease, a separate
activation-target lease, Git CAS for refs, exact grants for task-owned paths,
and `O_EXCL` for effect units and outputs. Disjoint worktrees are never globally
blocked, and one effect does not require overlapping evaluator claims.

## Preserved safety contract

Generation 6 remains a clean break: no migration, alias, dual write, fallback,
old reader, prior evidence reuse, or coverage reuse. Future evidence strictly
postdates a Git-reachable source and binds its normalized `git archive`.
Prior-Git successor comparison remains mandatory. Anchored-empty state cannot
certify. Raw model events, secrets, hidden oracle bodies, and unsanitized output
stay outside Git.

Duplicate primary keys, malformed terminal streams, extra terminals, unsafe or
aliased paths, raw/ledger divergence, and unrecognized inputs fail closed.
Baseline failures remain explicit and cannot silently become accepted.
Recovery uses this plan, Git, receipts, the live claim, and the same fixed
Executor; summaries, copied handles, replacement writers, or cross-task grants
cannot restore authority. Candidate preparation uses the official cachebuster
exactly once for that new candidate. Isolated install never mutates source.
Activation retains paired package/config/cache rollback and is separately
authorized.

The accepted G018 source `59fb8d5449991078bd27933e9bbf8f88c7b6f0cd`
and G019 reanchor are historical checkpoints only. The first future product
commit invalidates that candidate, its archive identities, and its empty ledger.
Nothing is migrated from it. The existing 259-test GREEN is a baseline, not
proof of this Outcome. Fable5/max and the fresh Challenger findings remain
read-only design evidence and are not rerun merely to restate the contract.

The affected-surface inventory is concrete: Runtime guidance and template;
terminal protocol parsing and corpus/receipt consumers; effect intent,
consumption, output, and CLI dispatch; candidate/plan/receipt persistence and
prior-Git transitions; package/evaluator/role/public identities; corpus,
adaptive holdout, exact-final, install, publication, activation, recovery, and
rollback. A batch must inspect callers across these surfaces when its change can
reach them; the inventory is risk routing, not a mechanical completion table.

## Three GREEN implementation batches

Each batch begins with a private intent, verifies the claim before every
write/stage/commit, changes only its listed paths, runs focused RED before repair
where behavior changes, ends with the full offline suite GREEN, commits a
Git-reachable checkpoint, and returns to Root for acceptance. A path may appear
in a later batch only for the later concern named there.

### Batch 1 — Runtime and direct protocol boundary

Owned paths:

```text
skills/happycodex/SKILL.md
skills/happycodex/references/execplan.md
evaluation/protocol.py
evaluation/corpus/engine.py
evaluation/core/receipt.py
evaluation/core/identity.py
evaluation/live.py
evaluation/semantic/__init__.py              delete
evaluation/semantic/types.py                 delete
evaluation/semantic/canonical.py             delete
evaluation/semantic/parse.py                 delete
evaluation/semantic/decide.py                delete
tests/test_semantic_core.py                   delete
tests/test_evaluation.py
tests/test_certification_engine.py
tests/test_contracts.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

Implement the four-phase Runtime and one obligations/evidence table. The direct
validator accepts only the exact terminal protocol object, rejects duplicate or
derived-state injection, and returns the strict permission/result projection
needed by corpus and receipts. Migrate consumers before deleting semantic
modules and their internal-structure tests. Preserve all 17 corpus fixtures and
behavioral assertions. Acceptance requires no import of `evaluation.semantic`,
no public generic controller types, Runtime at most 262 lines and preferably
2,200 words with 2,400 hard, exact fixture inventory, and full offline GREEN.

Derived consumer inventory is source-bound: Root reproduction plus the exact
production import search found only `evaluation/corpus/engine.py`,
`evaluation/core/receipt.py`, and `evaluation/live.py` outside the semantic
package; `evaluation/live.py:22` was the omitted Batch 1 consumer. Batch 1 owns
that file only to remove its semantic import and adapt the call site to the
direct protocol interface or a non-controller content-binding seam. Deleting
`TrustedHostContext`, the capability/claim/phase ladder, and changing any effect
behavior remain exclusively Batch 2 work.

Batch 1 produced commit `99579b37`, but Root did not accept it after an
independent full-suite run reproduced two errors: `_release_fixture`
unconditionally removed the already-deleted semantic directory. This is a
same-batch integration miss before acceptance, not recurrence. Repair grant
`HC06BR-G-021R-fixture-repair` makes removal conditional and permits an empty
commit only in the temporary fixture so an already-clean source still gains the
distinct Git successor required by the test; it never recreates semantic files.
The two focused tests moved from two errors, output SHA-256 `ff3496bd`, to GREEN,
output SHA-256 `778bbcf9`; the complete 221-test suite is GREEN with output
SHA-256 `ebafc4ff`. `verify` and existing Executor/corpus/holdout dry runs pass;
`impact` remains expected `refresh_required`. `corpus --calibrate --dry-run`
remains an explicitly Batch 2 command and its current unknown-argument result is
not repaired under this test-only grant.

The original focused RED at source `70a858aa` proved both the absent direct
protocol module and old five-phase Runtime; output SHA-256 is `bbf1cf82`. The
corrected eight-test focused set exited 0 with output SHA-256 `15d3cc86`.
Runtime/template are 235 lines and 1,689 words. The direct protocol owns exact
result validation and sanitized canonical projection; corpus and receipt
consumers use it, `live.py` remains standalone fail-closed, and the five
semantic modules plus their internal-construction test are deleted.
Because Batch 1 cannot mutate `current.json`, `ARCHIVED_MODULE_CATEGORIES`
temporarily classifies only the immutable still-anchored G019 source when
`evaluation/protocol.py` is absent. It parses no old protocol, evidence, or
schema, imports no semantic code, accepts no prior evidence or coverage, never
classifies current source, and leaves the ledger `refresh_required` and
noncertifying. Root authorized this narrow verification bridge explicitly.

### Batch 2 — Effect and release persistence

Owned paths:

```text
evaluation/live.py
evaluation/cli.py
evaluation/protocol.py
evaluation/core/impact.py
evaluation/core/ledger.py
evaluation/core/receipt.py
evaluation/core/schema.py
evaluation/core/identity.py
evaluation/contracts-v6.json
evaluation/corpus/engine.py
evaluation/holdout/engine.py
evaluation/results/current.json
tests/test_certification_engine.py
tests/test_contracts.py
tests/test_evaluation.py
tests/test_holdouts.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

Batch 2 removes production legacy phase, gate, repair-batch, and recurrence
values—including `implementation`, `focused_hardening`, `family_hardening`, and
`boundary_repair`—from `evaluation/protocol.py`, the shared schema, and the
fresh current ledger. Historical fixture prose may retain those terms only as
corpus or holdout input when still behaviorally required; it is never protocol,
schema, or ledger state. This inventory adds no case JSON paths and does not
move `evaluation/holdout/compare.py`.

Batch 2 must delete `ARCHIVED_MODULE_CATEGORIES` immediately after replacing
`current.json` with the fresh candidate/plan/receipt genesis. Acceptance must
prove that identifier and every legacy `evaluation/semantic/` path are absent
from production and tests; no archive alias, fallback, reader, evidence reuse,
or coverage reuse may replace them.

Replace the capability ladder and cached DAG with `ReleaseCandidate`,
`GatePlan`, `GateReceipt`, and `EffectIntent`. Provide one real CLI writer and a
reachable no-model transition test without patching a trust seam. Add
`corpus --calibrate`; bind its fixed case, exact cost approval, output, and
single-unit consumption. Prove atomic collision refusal, no-follow output,
write-once receipt, Git CAS/prior-Git refusal, derived pending/coverage/tip/
freeze/failure/certification, anchored-empty noncertification, and no manual
double ledger. The new generation-6 state is fresh; old ledger content is not
read or transformed. Full offline GREEN is mandatory.

### Batch 3 — Identity, documentation, and deletion proof

Owned paths:

```text
evaluation/core/identity.py
evaluation/core/impact.py
evaluation/core/ledger.py
evaluation/core/schema.py
evaluation/contracts-v6.json
evaluation/executor-role.json
evaluation/README.md
README.md
tests/test_certification_engine.py
tests/test_contracts.py
tests/test_evaluation.py
tests/test_holdouts.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

Reduce identity to the retained release identities and live receipt model/Codex
facts. Delete tool-path hashes, category/scope algebra, per-file LOC quotas,
schema minimum-line checks, formatting/phrase budgets, and every legacy import
or structure-presence assertion. Tests must exercise the real CLI entrypoint,
not a monkeypatched positive path. Acceptance proves exactly three persisted
record families, at most four lifecycle phases, one effect-intent transition,
no stored derived status, generic semantic package absent, no legacy controller
or trusted-context ladder symbols, and full offline GREEN.

## Semantic budgets and checks

Semantic budgets replace file allocations: at most four lifecycle phases, three
persisted record families, one effect-intent transition path, and zero stored
derived status. Generic semantic package production is zero after Batch 1.
Evaluation production has a directional target of 4,000–4,500 lines; readability
and deletion of semantic duplication matter more than per-file quotas. Runtime
is at most 262 lines and 2,400 words, preferably 2,200. This current-index plan
stays between 1,500 and 2,500 words.

Every batch runs, as applicable:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli verify
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli impact
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --calibrate --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli corpus --dry-run
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli holdout --dry-run
git diff --check
wc -l -w skills/happycodex/SKILL.md skills/happycodex/references/execplan.md
wc -l -w docs/execplans/happycodex-0-6-bounded-redesign.md
rg -n 'evaluation\\.semantic|TrustedHostContext|ProgressKey|AttemptKey' evaluation tests
```

Dry runs must create no model call, effect intent, unit consumption, fixture,
output, authority, or receipt. Unknown commands or schema inputs fail closed.

## Claims, open risks, and next boundary

| Claim | Required closure |
| --- | --- |
| `O-RUNTIME` | four-phase guidance and event correction preserve convergence without hash bookkeeping |
| `O-PROTOCOL` | direct strict result validation preserves every retained behavior fixture |
| `O-EFFECT` | one reachable EffectIntent path gives atomic, bounded, auditable execution |
| `O-RELEASE` | candidate/plan/receipt persistence derives all status through one CLI writer |
| `P-SAFETY` | clean-break evidence, archive ordering, strict parsing, recovery, install isolation, and rollback remain fail-closed |
| `P-QUALITY` | corpus, adaptive holdout, exact-final, install, publication, and activation remain distinct |
| `N-AUTH` | repository content never claims host provenance or self-authorizes an effect |
| `N-MIGRATION` | old ledger, semantic controller, hashes, evidence, and cached status are not reused |

Remaining known work is deliberately outside Batch 1: the capability ladder,
unreachable trusted-host positive path, cached evidence DAG, heavy identity
algebra, and structural toolchain remain for later batches. Final production LOC
is a measurement, not a per-file quota. Batch 2 must prove the CLI writer and
atomic effect path without live execution. Any outside path, identity drift,
incomplete consumer migration, or effect returns to Root.

After all three product batches are accepted, this amendment permits a new,
separately scoped candidate-source preparation and fresh reanchor. That step
uses the official cachebuster once, preserves external bytes, and creates no
live evidence. Model/live calibration, corpus, holdout, exact-final, isolated
install, publication, and activation each still require their own later exact
authority. No prose, digest, intent, plan, or successful offline test grants
those effects.
