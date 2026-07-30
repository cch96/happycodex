# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint and exact authority

This plan is the durable current index for the 0.6 contraction. The accepted
release source is `S_release` commit
`b3b79dca1cb3c990ad0c849172ea24aed8c3cab9`, tree
`20d039576d27d3ca927c0ade702131290eae948f`, on branch
`codex/happycodex-0.6-bounded-redesign`. Its plugin version is
`0.6.0+codex.20260730115707`; its accepted offline baseline is 163/163 GREEN.

The fresh generation-6 ledger now contains exactly one `ReleaseCandidate`, no
plans, and no receipts. Its canonical ledger SHA-256 is
`6074d0d09626150da6e46451c28b693bae59f7d3553f5edffe1cd31c03a542ef`;
it derives `refresh_required`, empty coverage and failures, and the six pending
gates `calibration`, `corpus`, `holdout`, `receipt`, `review`, and
`isolated_install`. It stores no derived state, live authority, or evidence.

Root reads, decides, grants, and verifies. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, is the sole writer. The mode-`0600` claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
binds this worktree, ref, and plan. It stays held. No replacement writer,
delegation, merge, cherry-pick, or cross-task grant is allowed.

Grant `HC06BR-G-027-fresh-release-candidate-reanchor` authorizes only
`evaluation/results/current.json` and this ExecPlan. Its mode-`0600` private
intent SHA-256 is
`6e715b4aa232382434ac38459e2d93a4d0b9fe39b86d37f3f428d80b531eb70b`.
Same-batch correction `HC06BR-G-027R-active-candidate-test`, addendum intent
SHA-256
`fdbcd9e57c2ed64a85880a4d67b869c703672170681952698233abc1659c95a7`,
adds only `tests/test_certification_engine.py`. Together they permit one
candidate append, one exact active-ledger test correction, and one direct-child
commit from `S_release`; they permit no plan, receipt, plugin, production,
external configuration, installation, model, live, publication, activation,
branch/main, or claim-release effect.

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

The accepted Batch 3 line is `da5877727e3a595a9fe691c8936dcabaed5ae564`
followed by recovery contraction
`2313e47f9c1485dedefe256bccb7af32c6551edf` and cross-binding
`183c91106260cca297f30ef344b457d8258c2afc`. Recovery Manifest now retains
only repositories, exact claim, one safe ref or content-addressed archive,
writer, tests, ordered reproduced agents, and ordered gates. Manifest writer,
test counters, agents, and gates directly equal their recovery-oracle
counterparts; schema and canonical marker validation remain separate. The
post-commit checkpoint ran 163/163 GREEN, output SHA-256
`b4c69132f802490500cb8c8558b0c5ecc8d3420f172bd13e755ee2f96508b0a7`.
Verify, expected-exit-2 impact, and all four dry runs matched expected exits;
every dry run reported nine zero effect counters.

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

## Bounded release-source preparation

### Accepted S_release source

`S_release` was prepared as a cachebuster-only source boundary. The protected
external prestate bytes remain:

```text
~/.codex/config.toml
575ececef691e8c3cc18e20ba40c648ce17d1b3a5a3cb9b02750e914e8f5344a
~/.agents/plugins/marketplace.json
752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe
~/.codex/agents/happycodex_executor.toml
d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275
/home/caichenghang/plugins/happycodex/.codex-plugin/plugin.json
1fb2d73ae9774ab99a78a3ae5d449493a5d19e77860fb6952abc9a09b5733990
/home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/.codex-plugin/plugin.json
1fb2d73ae9774ab99a78a3ae5d449493a5d19e77860fb6952abc9a09b5733990
```

The active source and loaded-cache manifests remain byte-identical to each other
and unchanged. The `config.toml` digest is transaction prestate, not the
repository `evaluation/executor-role.json` digest. Any later calibration or
install grant must separately bind the then-current external Executor config.

### Fresh reanchor — one candidate only

The candidate was recomputed from accepted `S_release`, not copied from an old
candidate. It binds:

```text
source commit
b3b79dca1cb3c990ad0c849172ea24aed8c3cab9
source tree
20d039576d27d3ca927c0ade702131290eae948f
package artifact
4e2b300bfc7c49c4eccad46a198e79f15c28680f2e4e6f041fabcc995ad3621e
package semantic
9cd5a507a8a9561c8af6751917b430b1cb29c238810b7c32bcff15c39044965a
engine manifest
6ad3f01334725c83cc031ad9a9abfadf4922d62143e160e7defa4d37cf22a10a
repository Executor role
f1effcc84e7ed24f6d54c972e2e412db42a3e46a6d92565e6d61b358128305da
public baseline
514cea60053bab5303e86e6cacaa0260e960b3fe1670a658e2df1a6965ce978c
snapshot
e1f67f2bfcf1470a1c181a7e54fd4e318456c0dab2861a1b7e76d7443dba50fd
candidate seal
d5e64387acdadfc2cacff8a63be2f0fa237f0bbff4e020fabc6485f9ac9f4665
```

The private input was mode `0600`, SHA-256
`fd0931ccc75608aea22c232ee2400e9243ba77f1e046ba200d19ccc6c34e3914`.
The canonical genesis predecessor was
`09fd486ca4b12699ef42c94e596d584b3ad527aa7ea3054dc0a7a2d674b34ebe`.
The CLI append succeeded exactly once. Before commit, the ordinary verifier
must fail closed because the worktree ledger differs from prior Git, while the
direct repository-aware validator must pass. Commit only the ledger, this plan,
and the exact active-ledger test correction as a direct child of `S_release`;
after commit, the ordinary verifier and all zero-live checks must pass.

The first full precommit run was 162/163 because the active-ledger test still
required the empty genesis after this authorized append. Isolated genesis,
apply, stale-predecessor, successor, schema, and archive tests already retain
genesis semantics. The corrected active-ledger test now uses repository-aware
validation and asserts one typed candidate, zero plans/receipts,
`refresh_required`, the exact six pending gates, and empty coverage/failures.
Its focused run and the full 163-test suite are GREEN.

Calibration, corpus, adaptive holdout, artifact receipt, exact-final review,
and isolated install each remain separate later authority gates. This reanchor
forbids model/provider calls, Executor pilot, live corpus or holdout,
exact-final review, install or reinstall, `codex plugin add`,
marketplace/cache/config mutation, publication, push, tag, release, activation,
claim release, and main/worktree switching.

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
