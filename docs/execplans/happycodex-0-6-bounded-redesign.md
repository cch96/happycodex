# HappyCodex 0.6 Contraction — Current Index

Protocol: `HappyCodex/0.5`

## Checkpoint and exact authority

This plan is the durable current index for the 0.6 contraction. The accepted
Batch 3 checkpoint is commit
`183c91106260cca297f30ef344b457d8258c2afc`, tree
`65b8210bb938f540f44b9348e58c91077080da1a`, on branch
`codex/happycodex-0.6-bounded-redesign`. Its current offline baseline is
163/163 GREEN. The active ledger SHA-256 remains
`b4e269d2c64fa0c4d246b1102aa4b366dd22afa250bc44089e7eda45a955228f`;
it is the empty generation-6 genesis and derives `refresh_required`.

Root reads, decides, grants, and verifies. Fixed Executor
`/root/bounded_redesign_executor`, role `happycodex_executor`,
`gpt-5.6-sol/high`, is the sole writer. The mode-`0600` claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json`, SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`,
binds this worktree, ref, and plan. It stays held. No replacement writer,
delegation, merge, cherry-pick, or cross-task grant is allowed.

Grant `HC06BR-G-025-release-source-contract` is plan-only and authorizes only
this ExecPlan. Its private intent SHA-256 is
`92fa593a12105f9ebafa111340119e0c1fe16364c1fba99973a36a77d3da23c8`.
It defines two future commits but authorizes neither. G025 permits no ledger,
plugin, test, production, external configuration, installation, model, live,
publication, activation, branch/worktree, or claim-release effect.

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

The next two commits are separate Root acceptance boundaries. Neither may be
started from G025 authority, and acceptance of the first does not authorize the
second.

### S_release — cachebuster-only source

After Root accepts the G025 plan commit, a new exact grant may prepare
`S_release`. Its default tracked paths are only
`.codex-plugin/plugin.json` and this ExecPlan. Before any mutation it rechecks
the accepted Git baseline, held claim, clean index/worktree, and these protected
external prestate bytes:

```text
~/.codex/config.toml
575ececef691e8c3cc18e20ba40c648ce17d1b3a5a3cb9b02750e914e8f5344a
~/.agents/plugins/marketplace.json
752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe
~/.codex/agents/happycodex_executor.toml
d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275
/home/caichenghang/plugins/happycodex/.codex-plugin/plugin.json
1fb2d73ae9774ab99a78a3ae5d449493a5d19e77860fb6952abc9a09b5733990
```

Any drift stops. The `config.toml` digest is transaction prestate, not the
repository `evaluation/executor-role.json` digest. A later calibration or
install grant must separately bind the then-current external Executor config;
this source step cannot pre-authorize it.

Run the official plugin-creator helper exactly once, with its default UTC
cachebuster:

```text
python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py .
```

Do not hand-edit the version and do not invoke this or another cachebuster
helper a second time. The result must differ from the prestate and match exactly
`^0\.6\.0\+codex\.[0-9]{14}$`, with one `+codex.` suffix. Validate it with:

```text
python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Then run the full 163-test offline suite, `verify`, expected-exit-2 `impact`,
and the Executor, calibration, corpus, and holdout dry runs. Every dry run must
retain all nine zero effect counters. Recheck Runtime and ExecPlan budgets,
the exact closed evaluator and plugin inventories, the version regex, both
protected repository and external prestate bytes, and `git diff --check`. The
commit diff may contain only the two default paths. Tests or production files
require a genuine behavioral RED against current `HEAD` plus a new Root
path-correction grant before any such mutation. Root must independently
reproduce and accept the resulting `S_release` commit.

### Fresh reanchor — one candidate only

Only after Root accepts `S_release` may a separate exact grant reanchor the
fresh genesis. Its source commit is exactly the accepted `S_release`, and its
only tracked paths are `evaluation/results/current.json` and this ExecPlan.
Construct one complete `ReleaseCandidate` input outside tracked repository
state. Recompute and exactly bind the reachable source commit/tree, normalized
Git archive and package identities, closed engine manifest, repository
Executor-role digest, frozen public baseline, and complete snapshot. No
identity or digest may be copied from the pre-cachebuster candidate.

With the worktree ledger still byte-equal to the Git genesis, append exactly
that one record through:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.cli apply \
  --expected <exact-canonical-genesis-digest> \
  --record <mode-0600-release-candidate-input-outside-repository>
```

The result must contain one candidate, zero plans, and zero receipts; derive
`refresh_required`; retain all six pending gates; and contain no live
authority, evidence, coverage reuse, or gate success. Commit only the ledger
and this plan. The reanchor commit must strictly descend from `S_release`.
Root acceptance of that commit is still not authority for any later gate.

G025 and both source-only boundaries forbid model/provider calls, Executor
pilot, live corpus or holdout, exact-final review, install or reinstall,
`codex plugin add`, marketplace/cache/config mutation, publication, push, tag,
release, activation, claim release, and main/worktree switching. G025 itself
also forbids every ledger mutation.

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
