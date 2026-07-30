# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint and exact authority

This plan is the durable current index for the 0.6 contraction. Accepted Batch 2
source is commit `87401b512032ec8cccd134f51d6bb7c56f6e8ea9`. The Batch 3
plan-only baseline is commit `91c743150caefe4652bf17a13f2e9b7cc81f15b4`,
tree `e98d62722d13a1cfe47b591c670253bf9b40a1d3`. The active ledger
SHA-256 remains
`b4e269d2c64fa0c4d246b1102aa4b366dd22afa250bc44089e7eda45a955228f`;
it is the empty generation-6 genesis and derives `refresh_required`.

Root reads, decides, grants, and verifies. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, is the sole writer. The mode-`0600` claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
binds this worktree, ref, and plan. It stays held. No replacement writer,
delegation, merge, cherry-pick, or cross-task grant is allowed.

The operative amendment is exactly `好的 执行吧`. Its UTF-8 SHA-256 is
`090a0814415d60fa61a0eeb425afe4fb83536bf25391dcf6a1fbeff4954bbcb9`
without a newline and
`c3ddfefbb057c1a88fe458584f0a6643c203fb44db75300a62d064f800e79255`
with one newline. It authorizes the offline product, test, and documentation
batches below. It does not authorize any model call, live calibration, corpus,
holdout, exact-final review, install, publication, marketplace/config/cache
mutation, or activation.

Batch 3 repair ownership consists only of:

```text
evaluation/core/{identity,impact,ledger,schema}.py
evaluation/contracts-v6.json
evaluation/corpus/engine.py
evaluation/executor-role.json
evaluation/cases/pre-freeze-compaction.json
evaluation/README.md
README.md
tests/{test_certification_engine,test_contracts,test_evaluation,test_holdouts}.py
docs/execplans/happycodex-0-6-bounded-redesign.md
```

Grant `HC06BR-G-024RP-recovery-boundary` is plan-only and may edit only this
ExecPlan. It adds the case path above to the later narrow same-batch repair; it
does not itself authorize product, schema, validator, fixture, or test changes.

## Frozen normalized Outcome

HappyCodex 0.6 is a smaller reachable protocol. Shipped Runtime guides one fixed
Executor per task/worktree; Root grants and verifies; one obligations/evidence
table holds durable work; correction is event-driven. The same unchanged
failure is not retried. One coherent repair wave is allowed; if one
boundary-level alternative still fails, control returns to the user. Lifecycle
is only `working -> candidate_frozen -> exact_final -> closed`.

The evaluator uses one strict direct terminal validator rather than a generic
semantic controller. Behavioral fixtures and risk inventory remain, while
mechanical structure, wording, formatting, and per-file allocation tests do
not stand in for behavior.

Authority belongs to Root/Host orchestration. Repository code does not
authenticate task/message/turn provenance. A plan, approval digest, claim, or
effect intent is content binding and audit history, not permission. Ordinary
repository validation remains reachable without a local issuer, private seal,
or positive-path trust monkeypatch.

One canonical `EffectIntent` binds candidate, gate, exact invocation/profile,
cost ceiling, units, resources, output, and approval content. Execution
atomically consumes `intent_digest + unit` through no-follow `O_EXCL`, writes to
an absent no-follow output, and produces a typed result. Durable consumption
prevents reuse.

Release persistence has exactly three record types:

1. `ReleaseCandidate`: Git source commit/tree, normalized package identities,
   evaluator manifest, external role digest, public baseline, and snapshot.
2. `GatePlan`: gate, exact profile, cost ceiling, units, resources, output, and
   approval-request/content digests.
3. append-only `GateReceipt`: immutable typed result and predecessor/tip
   binding.

Pending gates, coverage, receipt tip, freeze eligibility, failure, and
certification are derived rather than stored. One reachable CLI writer owns
schema validation, prior-Git comparison, predecessor comparison, atomic
replacement, and receipt append.

Calibration is the fixed retained control routed through corpus execution.
Calibration, full corpus, adaptive blind holdout, artifact receipt, exact-final
review, and isolated install are distinct persisted gates. Publication and
activation are later external gates. Model-reaching gates require separate
exact Host authority and cost basis.

Identity retains reachable Git archive commit/tree, normalized package,
evaluator bundle, external role/config, frozen public baseline, and case/holdout
identities. Snapshot settings are only model, effort, and timeout. A successful
live corpus receipt additionally binds the actual Codex version, its binary
content digest, and the invocation profile; no executable path is persisted.
The evaluator inventory is one exact closed Python/JSON set and one manifest
digest. Unknown inputs fail closed. Any evaluator-bundle change invalidates the
full corpus, all holdouts, and artifact receipt.

## Preserved safety

Generation 6 is a clean break: no migration, alias, dual write, fallback, old
reader, prior evidence reuse, or coverage reuse. Evidence strictly postdates a
Git-reachable source and binds its normalized `git archive`. Prior-Git
successor comparison remains mandatory. Empty state cannot certify. Raw model
events, secrets, hidden oracle bodies, and unsanitized output stay outside Git.

Duplicate keys, malformed terminal streams, extra terminals, unsafe or aliased
paths, raw/ledger divergence, unrecognized inputs, and baseline drift fail
closed. Baseline failures remain explicit. Recovery uses this plan, Git,
receipts, the live claim, and the same fixed Executor; copied summaries or a
replacement writer cannot restore authority.

Candidate preparation uses the official cachebuster once for the new candidate.
Isolated install never mutates source. Activation retains paired
package/config/cache rollback and needs separate authority. Claims remain
narrow: one task-duration worktree/ref lease, a distinct activation-target
lease, Git CAS, exact path grants, and atomic effect-unit/output creation.

The affected-surface inventory is concrete: Runtime and template; terminal
parsing and receipt consumers; effect intent/consumption/output/dispatch;
candidate/plan/receipt persistence and prior-Git transitions; package,
evaluator, role, public, case, and holdout identities; corpus, adaptive
holdout, exact-final review, install, publication, activation, recovery, and
rollback. It routes risk; it is not a checklist that manufactures completion.

## Accepted implementation batches

### Batch 1 — Runtime and direct protocol

Batch 1 established the four-phase Runtime, one obligations/evidence table, and
strict direct terminal validation. Corpus, receipt, and live consumers moved
before the generic semantic package and its construction tests were deleted.
All 17 corpus fixtures remained. The accepted repair made already-clean
temporary repositories produce a distinct successor commit without recreating
deleted code. Runtime and template are 235 lines and 1,689 words. The accepted
full suite was 221 tests GREEN.

### Batch 2 — Effects and release persistence

Batch 2 replaced legacy effect/release bookkeeping with the three release
records and one `EffectIntent` route. It added a real CLI ledger transition and
fixed calibration route, atomic collision/no-follow protections, strict Git
and snapshot binding, derived status, and fresh empty genesis. Follow-up
repairs closed empty-success, aliased-ledger, dispatch-drift, model-scope, and
adaptive-holdout false greens. Accepted commit is
`87401b512032ec8cccd134f51d6bb7c56f6e8ea9`; the final accepted suite was 163
tests GREEN. Verify and all four dry-run routes remained zero-live.

## Batch 3 — Identity, documentation, deletion proof

Batch 3 replaces evaluator classification/subset identity with one exact closed
inventory and manifest. It preserves Git/package/evaluator/role/public/case/
holdout/invocation identities and all Batch 2 safety. It removes structural
minimums, phrase/heading checks, and prose-based controller assertions while
retaining Runtime/package budgets and forbidden-link checks.

Behavioral acceptance proves exactly three record types, no stored derived
state, at most four lifecycle phases, one effect-intent route, conservative full
invalidation, unknown-input refusal, and zero dry-run effects. READMEs describe
real Host authority, audit-only repository bindings, and distinct gates.

Private intent receipt is
`HC06BR-G-024-batch3-identity-docs-deletion.intent.json`, SHA-256
`e0f6b0eb498692798b349883aab332e8f06392c372bd9f0027de77f9a03e158e`.
Focused RED ran six tests and produced two failures plus one error, output
SHA-256
`f4f2a5969e478c0f74976444a4828b0d050d0dc470e68929b99b800f552a8855`.
It proved the old inventory surfaces remained, bundle drift reran only receipt,
live Codex identity was absent, and obsolete structure tests still existed.
The RED receipt SHA-256 is
`401a1f0c1698452325641ba90cdc13d3ed7091bf02f45e103bf6c82cff0b112f`.

The current 12-test focused set is GREEN, output SHA-256
`408a6c83223d473bfa79b1a54fbad894a91d8aa750852b2944e4f1fa67d6fcf2`.
The first full run exposed one stale test reference to the deleted production
lifecycle constant; it was migrated to the shared schema enum. The final full
suite is 163 tests GREEN, output SHA-256
`e8564624e5888bf897bee7c03f0f510fdc80615b8785cd16ca240ef0494e701f`.
Verify, expected-exit-2 impact, Executor dry run, calibration dry run, corpus dry
run, and holdout dry run all match their expected exits. Every dry run reports
nine zero effect counters. Their output SHA-256 values are respectively
`804ee1e1`, `a41780ae`, `e4713eb5`, `d3cf5dc6`, `375ab9a2`, and
`d5cb2410`. The active ledger digest remains unchanged.

Root independently reproduced 163/163 and the CLI matrix but did not accept
commit `da5877727e3a595a9fe691c8936dcabaed5ae564`. Source inspection found that
the `recovery_manifest` contract and `evaluation/core/ledger.py` still persist
and enforce a nested convergence/family/status/repair-batch/recurrence state
machine. That is active production schema and validation, not historical
fixture prose, and it violates the frozen deletion boundary.

The required same-batch correction is narrow. Recovery Manifest keeps
repositories, the exact resource claim, exactly one selected safe ref or
content-addressed archive, fixed writer, test counts, terminal agents whose
receipts were reproduced, and gates. Delete the entire convergence object and
all family, status, repair-batch, and recurrence fields from
`contracts-v6.json`, the pre-freeze fixture payload, ledger validation, and
behavioral tests. Do not reinterpret or retain those fields through an alias,
derived fallback, renamed wrapper, or compatibility reader.

`evaluation/cases/pre-freeze-compaction.json` is the only added corpus path.
After canonicalizing its reduced manifest, recompute the embedded Recovery
Manifest marker and every exact oracle anchor derived from those bytes.
Historical prose in every other corpus or holdout case remains untouched.

Also delete or behaviorally replace
`tests/test_evaluation.py::test_fixed_behavior_inventory_exercises_041_convergence`.
Its positive checks for legacy convergence wording are structure/phrase
presence, not protocol evidence. Replacement coverage must validate the reduced
Recovery Manifest's retained fields, reject removed fields through exact schema,
exercise selected-checkpoint exclusivity and claim/test/terminal-agent
invariants, and prove canonical content/marker/oracle rehashing. It must not
require deleting historical prose elsewhere.

The plan-only repair intent SHA-256 is
`327cee26a16785728d9f9f91899a06ea6b240cb680a91d8866f491a2a47888b9`;
its Root addendum SHA-256 is
`0c32ca2e0695001ac55dc922682408a146561ff33c35f1897834452346993e99`.
The prior terminal receipt remains evidence of the rejected checkpoint, not
Batch 3 acceptance. Product repair requires a new exact Root grant, focused RED
showing the active legacy boundary, focused GREEN, full post-commit offline
GREEN, the same zero-effect CLI matrix, and a new terminal receipt.

Root granted `HC06BR-G-024R-recovery-manifest-contraction` at baseline
`4416258dca44178fdde24804eb07323b74e986c4`. Focused RED command was:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_evaluation.HappyCodexEvaluationTests.test_recovery_manifest_binds_current_index_and_one_checkpoint tests.test_evaluation.HappyCodexEvaluationTests.test_recovery_manifest_rejects_removed_state_machine_fields
```

It ran two tests with one failure and one error: the fixture still exposed
`convergence`, while the current schema rejected the reduced manifest. Output
SHA-256 is
`f8c674dfa5328309018f478d70b449d9842cbb9a65afcee14561aba445439793`;
the mode-`0600` RED receipt SHA-256 is
`d30dd2f715e38c2a03bc2da07bec133e0b6be70d99b1fac485951a938e822fdc`.

Focused GREEN is 2/2, output SHA-256
`4e41ee0d288e23cd1809def95d77c0d8b023c42fee2095d6ea8fcc2b65f0b1d2`.
Because certification tests clone committed `HEAD`, an ordinary dirty-tree full
run correctly exposed the old committed fixture against the new loaded schema.
A temporary Git-reachable snapshot of the exact five-file diff ran all 163
tests GREEN, output SHA-256
`3aa5148d71b00ef1c8ae809eba78cd4f3050a4584a16f1bc6d3915eb1142fb7b`.
Repair commit `2313e47f9c1485dedefe256bccb7af32c6551edf` then reproduced
163/163 GREEN, output SHA-256
`b7328a35957d4dea882140010c74eb5a2a82b51fd0b043dccd6356d87c7efb17`.

Precommit CLI results are verify 0, impact 2 as expected, and all four dry runs
0 with nine zero effect counters. Verify and impact output SHA-256 values are
`c23a36d7` and `e574d468`; dry-run outputs remain `e4713eb5`,
`d3cf5dc6`, `375ab9a2`, and `d5cb2410`. The active ledger digest remains
unchanged.

Root withheld acceptance after independently re-signing three schema-valid
manifest changes: gates to `user_selection`, passed tests to 20, and agent id to
`OTHER`. Each remained accepted while the recovery oracle retained the original
facts. Grant `HC06BR-G-024R2-recovery-cross-binding` therefore requires direct
equality for writer, ordered gates/pending gates, the three test counters, and
ordered agent objects; marker and schema validation remain unchanged.

Focused RED command was:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_evaluation.HappyCodexEvaluationTests.test_recovery_manifest_cross_binds_oracle_facts
```

It ran one test with three subtest failures, proving all three mismatches were
accepted. Output SHA-256 is
`de7dfd31362923ed09359d99ba3a3e8993f46d709aa25f545366dcf7a20dcc22`;
the mode-`0600` RED receipt SHA-256 is
`dc4248d09cccfe2ba042c81c8ecbc3da43454045522698e11ea4091960175a88`.

The cross-binding focused set is 2/2 GREEN, output SHA-256
`fb803d54ebf5c063d543999bff2222b4cc9a62d76f33f218a5d15458611d5ec8`.
Canonical discovery remains 163/163 GREEN, output SHA-256
`415bbfd54c58903cf04abd74eb221ece0ff91899ed5891d166b546e5af1dd09f`.
Precommit verify is 0, impact is expected exit 2, and all four dry runs are 0
with nine zero effect counters. Their output SHA-256 values are respectively
`17455511`, `bb08900b`, `e4713eb5`, `d3cf5dc6`, `375ab9a2`, and
`d5cb2410`. The active ledger remains
`b4e269d2c64fa0c4d246b1102aa4b366dd22afa250bc44089e7eda45a955228f`.

The closed inventory has sixteen declared Python modules plus fixed and dynamic
JSON inputs. Discovery compares the real evaluator tree to that set: an
unlisted Python module, an unknown JSON document, or a missing declared input
refuses identity construction. Result/evidence outputs are the only deliberate
JSON exclusions. Each manifest entry contains path, byte count, and content
digest; the canonical payload produces one manifest digest. No per-subsystem
selection survives.

Snapshot validation requires the exact three settings and the single evaluator
digest. Every corpus and blinded-pair semantic input binds that same bundle.
Impact planning remains selective for changed case identities or package
artifact-only install impact, but bundle drift is deliberately conservative:
all 17 corpus cases, all three holdout pairs, corpus, holdout, and receipt are
required. Model/effort/timeout drift also reruns both quality gates. A live
corpus invocation resolves Codex internally, hashes the executable bytes,
captures the reported version, and binds that digest into the profile without
serializing the resolved path.

The deletion proof is behavioral. Schema enumeration fixes the four accepted
lifecycle phases. Ledger tests validate and transition only candidate, plan,
and receipt records, then recompute all status projections. Authorized corpus
and holdout entrypoints expose only arguments, exact intent mapping, and claim
root. Real CLI tests append through predecessor comparison and exercise all
dry-run routes with zero effect counters. Runtime tests retain the shipped
surface, combined line/word ceiling, forbidden evaluator links, and hidden-file
detection, while no longer treating exact sentences, headings, table rows,
source formatting, or individual file length as protocol behavior.

Documentation must stay aligned with those executable boundaries. In
particular, it cannot claim that repository content proves Host provenance,
that a persisted approval is permission, or that one completed quality gate
authorizes another. The final audit therefore compares README claims against
the callable entrypoints, ledger fields, gate order, and sanitized receipt
shape rather than accepting prose alone.

## Budgets and final checks

Runtime remains capped at 262 lines and 2,400 words, with 2,200 preferred.
Current combined Runtime is 235 lines and 1,689 words. This plan stays between
1,500 and 2,500 words.

Evaluation production currently measures 6,073 Python lines across the exact 16
declared modules. The 4,000–4,500 target is directional, not an acceptance
quota; this batch deletes identity and test semantic duplication but does not
compress unrelated evaluator behavior merely to hit a number. The actual final
measurement must remain reported.

Final offline commands are:

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

Dry runs must create no model call, intent, consumption, fixture, output,
workspace, network call, or receipt. Unknown commands and evaluator inputs fail
closed. The active ledger and plugin/market/config bytes must remain unchanged.

After Batch 3 is committed and accepted, this amendment permits only a new,
separately scoped candidate-source preparation and fresh reanchor. Live
calibration, corpus, holdout, exact-final review, isolated install, publication,
and activation still each require later exact authority. No prose, digest,
intent, plan, claim, or successful offline test grants those effects.
