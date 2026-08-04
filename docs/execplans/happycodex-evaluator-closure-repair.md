# HappyCodex Evaluator Closure Repair

## Contract

- Phase: `candidate_frozen`; this is not certification or release.
- Current Root grant: `PHASE 8 COMMIT GRANT` to the fixed sole writer
  `/root/fixed_evaluator_closure_executor`.
- User amendment, verbatim: `提交，然后更新本地，插件`. Normalized authority:
  commit this candidate now; local plugin activation is a separate later effect.
- Outcome: make the observed A/B/C REDs green as one clean-break evaluator wave
  while preserving packaged-product bytes and the four-record boundary.
- Source: clean `main` commit
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`, tree
  `8847db04e110445bd8ca125917d9b424f959a272`.
- Target branch: `codex/happycodex-evaluator-closure-repair` in worktree
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.5-main-release`.
- Product preservation: `skills/happycodex` remains tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`, byte-identical to `v0.6.5`.
- Frozen pre-commit identities: tracked full-index diff
  `21eda4e83a185d6dce952936fd3c726d0503b126d0f4cdfce102c30b98607be9`;
  pre-update ExecPlan
  `4c030290dd5bed5b6be4e4f2a55f6135557704753d4942b24fa3e737bcd7bd99`.
- One exact stage and commit are authorized. Model, provider, network, plugin,
  install, cache, release, push, tag, PR, merge, and other writes are forbidden.

## Frozen scope

- A — one-shot effect: the same EvalSpec, authority, and invocation cannot
  succeed in two caller-chosen execution roots; characterize the missing
  authority-scoped host namespace without adding a ledger or record type.
- B — evidence truth: bind the canonical report to raw, require exact-final
  inspection before its canonical report, compare runtime evaluator components
  to EvalSpec, and bind exact-final manifest lineage to the frozen source.
  Existing malformed/orphan fail-closed coverage is reused; unknown native item
  coverage was absent and receives one parser RED.
- C — simplification: product identity is package-only with commit/full-tree
  provenance non-identifying; a single-role change requires full evaluation;
  supported modes remain full, exact-final-only, oracle replay, and offline-only;
  token qualification is ex-post rather than an enforceable pre-effect cap.

Exactly four evaluator durable record types remain. No compatibility, migration,
active ledger, evidence graph, generic subset/mixed-authority engine, new phase,
gate, daemon, monitor, reviewer, or release-eligibility predicate is in scope.

## Authorized paths

- This ExecPlan; `evaluation/README.md`, `cli.py`, `holdout.py`, `host.py`,
  `identity.py`, `manifest.py`, `provider.py`, `records.py`, and `verify.py`.
- `tests/attestation_fixtures.py`, `test_attestation_clean_break.py`,
  `test_attestation_cli.py`, `test_attestation_contract.py`,
  `test_attestation_flow.py`, `test_fixed_host_transaction_v2.py`,
  `test_stage_profiles.py`, `test_stateless_records.py`, and
  `test_trust_boundary_repair.py`.

No production module may be added. No fixture/schema JSON, AGENTS, Skill,
product, install, cache, active plugin, release-profile eligibility, or external
path may change. The external claim artifact remains forbidden; fixed-writer
identity and exact path scope are recorded here instead.

## RED obligations

| ID | Falsifier | Target evidence | State |
| --- | --- | --- | --- |
| A-ROOT | A second execution root reaches the same authorized provider invocation. | Cross-root transaction test fails because the second provider is reached. | RED observed |
| B-RAW | A resealed Attestation can substitute a different sanitized report for its raw canonical report. | Raw-backed verification accepts the substitution. | RED observed |
| B-ORDER | Exact-final accepts an inspection completed only after the canonical report. | Exact-final Attestation incorrectly passes. | RED observed |
| B-RUNTIME | Runtime evaluator component drift is not compared with EvalSpec. | Verification accepts a drifted evaluator checkout. | RED observed |
| B-SOURCE | Exact-final manifest/source lineage fields and projection bytes are not exhaustively rebound. | An unreachable placeholder source lineage remains accepted. | RED observed |
| C-PRODUCT | Product record identity changes with source provenance or external role config despite identical package bytes. | Equal-package records differ. | RED observed |
| C-MODE | One fixture change promises a selective one-unit model rerun. | Invalidation returns one unit instead of full evaluation. | RED observed |
| C-TOKEN | Token limits are presented as an enforceable pre-effect cap rather than ex-post qualification. | Contract/API exposes token totals as the same launch cap. | RED observed |
| B-SCOPE | A manifest self-selects README-only review scope, excludes evaluator source, claims dirty-worktree component digests, and supplies a fake diff. | Exact-source validation accepts the incomplete projection and false source evidence. | Focused GREEN |
| C-WALL | A 1ms remaining wall authorization launches a unit with a 30s runner timeout. | Provider runner receives more wall authority than remains. | Focused GREEN |
| C-AUTH | A forged prior full proposal and resealed prior authority/Attestations compose with current exact-final. | Mixed verification returns `verified=true`. | Focused GREEN |
| C-CLI | Documented verify/release commands cannot supply previous EvalSpec and two exact authority bindings. | Retained exact-only composition is unreachable through CLI. | Focused GREEN |

## Checks and stop conditions

Implement one coherent wave, run focused standard-library attacks, then exactly
one cumulative `python3 -B -m unittest discover -s tests -v`, followed by
`git diff --check`. Recompute evaluator/module LOC and product tree. Stop on
prestate drift, any need to edit a non-authorized path, any provider/model/
network/install/release effect, Python above 3,600 total or a production module
above 600, or any need for a fifth record, lifecycle, gate, compatibility layer,
generic engine, release eligibility, exact-final, reviewer, or ungranted effect.

## Current checkpoint

- Latest-byte independent review verdict: `GO`.
- Root cumulative verification: `158/158` GREEN in 66.597 seconds.
- Prestate matches the frozen branch, parent commit/tree, product tree, empty
  index, eighteen tracked modifications, and one ExecPlan exactly.
- The reviewed bytes now transition to `candidate_frozen`; only their exact
  commit is authorized. Plugin activation remains a later separate authority.

## Phase-2 design index

- A: bind one immutable host-effect marker namespace into the trusted host
  contract. Validate all no-effect prerequisites before O_EXCL consumption;
  consume before caller-root artifacts or provider reach. Recovery is absent;
  no retry or recovery surface is retained.
- B: require raw and Attestation reports to match exactly, reject secret-bearing
  transformation, close native item/order grammar, compare all four evaluator
  component identities before effect and during verification, and replace the
  source check with one exhaustive frozen-manifest validator.
- C: keep ProductArtifact package identity plus reconstruction provenance only;
  move role config to EvalSpec/effective unit identity, link by explicit package
  identities, expose only the four named evaluation decisions, and enforce
  calls, remaining wall, and per-unit timeout before effect while treating tokens only as typed
  ex-post qualification.
- Invalidation rule: any material single-role/provider identity change selects
  `full_evaluation`; only exact-final inputs select `exact_final_only`, oracle
  changes select `oracle_replay`, and deterministic-only changes select
  `offline_only`. No arbitrary subset or mixed authority composition remains.

## Phase-1 receipt

- Writer: fixed sole writer `/root/fixed_evaluator_closure_executor`; no child
  writer or delegation was used.
- Git: branch `codex/happycodex-evaluator-closure-repair`; unchanged HEAD
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`; unchanged tree
  `8847db04e110445bd8ca125917d9b424f959a272`.
- Mutations: this plan plus four authorized test files. The authorized
  `tests/test_stage_profiles.py` remained unchanged. No evaluator,
  product, JSON, AGENTS, external, index, commit, or remote bytes changed.
- Focused command: `python3 -m unittest -v` with the nine fully qualified RED
  tests for placeholder lineage, cross-root replay, forged report substitution,
  runtime drift, full invalidation, package-only identity/config, exact-final
  ordering, malformed/unknown native items, and token qualification.
- Evidence: current production failed every intended RED assertion. It accepted
  placeholder lineage, the second execution root, a fully resealed report
  substitution, drifted runtime components, post-report inspection, and an
  unknown native item; returned selective invalidation; retained config and a
  whole-record foreign key in product identity surfaces; and lacked the
  effect-cap/token-qualification split.
- One initial cross-root run had a test-only missing parent-directory setup
  error. The test setup was corrected without changing shared fixtures and the
  isolated rerun then failed only because `HostEvidenceError` was not raised.
  An earlier multi-file patch was rejected atomically on an unmatched anchor and
  had no partial effect.
- Offline-only effect: temporary files/repos created by stdlib tests. Model,
  provider, network, install, release, cache, stage, commit, push, tag, and PR
  effects: zero.
- Read-only checks: exact branch/head/tree/status inventory, task diff review,
  line counts, and `git diff --check` (pass). This receipt records RED only and
  makes no completion decision.

## Phase-2 partial receipt

- Writer and source remain unchanged: fixed Executor
  `/root/fixed_evaluator_closure_executor`, branch
  `codex/happycodex-evaluator-closure-repair`, HEAD
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`, tree
  `8847db04e110445bd8ca125917d9b424f959a272`, product tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; index remains empty.
- Partial authorized mutations cover the plan; seven evaluator modules
  (`cli.py`, `host.py`, `identity.py`, `manifest.py`, `provider.py`,
  `records.py`, `verify.py`); central test fixtures; and six authorized test
  files. No unlisted path was changed.
- Implemented but unverified partials include package-only ProductArtifact,
  explicit artifact foreign keys, separated effect/token fields, explicit
  decision modes, exact report equality/order checks, runtime component checks,
  authority+invocation effect-marker plumbing, and the exhaustive source
  manifest validator. These are not claimed coherent or GREEN.
- Blocking source evidence: `evaluation/holdout.py:73-76` reads role config from
  ProductArtifact and `evaluation/holdout.py:116` reads
  `previous_product_record_sha256`. The module validates the closed EvalSpec, so
  an augmented compatibility object cannot safely bypass either dependency.
- Verification stopped before focused or cumulative tests. The required single
  cumulative run has not occurred. `git diff --check` currently reports one
  trailing blank line in `evaluation/identity.py`; it was not cleaned after the
  stop condition.
- Transient evaluator LOC is 3,495, under the 3,600 aggregate hard stop, but
  `provider.py` is 739 lines, `records.py` 602, and `verify.py` 613, each above
  the 600-module hard stop. The incomplete wave therefore also requires a new
  Root grant to consolidate/delete before any further implementation.
- Effects remain offline repository edits and read-only inspection only. No
  model/provider/network/install/cache/plugin/release/stage/commit/push/tag/PR,
  exact-final, review, or external write occurred.
- Required decision: either extend the exact path grant to
  `evaluation/holdout.py` and explicitly authorize corrective continuation from
  this exact partial dirt, including deletion/consolidation back under all LOC
  limits, or direct another disposition. No retry, rollback, cleanup, or
  completion decision was inferred.

## Phase-2A corrective receipt

- Writer and source remained fixed: sole Executor
  `/root/fixed_evaluator_closure_executor`, branch
  `codex/happycodex-evaluator-closure-repair`, unchanged HEAD
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`, unchanged source tree
  `8847db04e110445bd8ca125917d9b424f959a272`, and unchanged product tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`. No delegation occurred.
- The added caller surface now reads role configuration from EvalSpec and the
  previous package artifact foreign key. Exact-source validation was
  consolidated into `identity.py`; `provider.py` contains only the thin
  provider-error adapter. No production module or record type was added.
- One authority/invocation marker in the authority-bound host namespace is
  consumed with O_EXCL before caller-root preparation or provider reach.
  Same-root, cross-root, and cross-process attacks prove one-shot behavior.
- Raw canonical reports now equal Attestation reports exactly; known
  secret-bearing reports fail, exact-final inspection must precede its
  canonical report, and runtime evaluator components are rebound. Root later
  disproved the receipt's claims about complete synthetic source scope, source
  component identity, diff truth, and hard remaining-wall enforcement; those
  claims are withdrawn for Phase-3 repair.
- Product foreign keys are package-artifact identities; role configuration is
  EvalSpec/effective-unit state. Invalidation returns only `full_evaluation`,
  `exact_final_only`, `oracle_replay`, or `offline_only`. Calls and wall time
  remain effect caps; tokens are actual-usage qualification. Exact-only
  composition verifies its two concrete authorities and exact prerequisite
  hashes without a generic subset engine.
- Focused sweep: the eight explicitly authorized test modules, 142 tests, all
  GREEN. Required single cumulative command:
  `python3 -B -m unittest discover -s tests -v`; 142 tests, all GREEN. No other
  cumulative discovery run occurred.
- Final evaluator Python LOC is 3,393. Largest production modules are
  `records.py` 598, `verify.py` 596, and `host.py` 595; every module is below
  600 and aggregate size remains below the 3,400 repository gate.
- Effects were limited to the authorized repository files and offline temporary
  test repos/files. Model, provider, network, install, cache/plugin, release,
  external write, stage, commit, push, tag, and PR effects were zero. Root must
  independently verify and decide the next phase or closure.

## Phase-3 intent

- Replace manifest-selected review scope with one closed repository projection:
  `.agents`, `.codex-plugin`, `README.md`, `evaluation` except the hidden oracle,
  `skills`, and `tests`; all other tracked paths are excluded.
- Bind a named-ref-reachable strict source descendant to an explicit baseline,
  derive evaluator components from source-commit bytes, recompute the fixed
  binary/full-index/no-renames diff, and reject hidden-oracle bytes from every
  included file and the diff.
- Delete the phantom recovery cap and unused report redaction path. Clamp every
  runner timeout to remaining authorized wall time before marker consumption.
- Retain only the concrete previous-full plus current-exact authority composition,
  validate both proposals against their exact EvalSpecs, and expose its closed
  inputs through `verify` and `verify-release`. No generic binding registry,
  record, mode, phase, or release predicate is introduced.

## Phase-3 corrective receipt

- Writer and immutable source remained fixed: sole Executor
  `/root/fixed_evaluator_closure_executor`, branch
  `codex/happycodex-evaluator-closure-repair`, HEAD
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`, source tree
  `8847db04e110445bd8ca125917d9b424f959a272`, and product tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`. The index remained empty;
  no delegation occurred.
- Exact-source review scope is independently derived from the source commit:
  `.agents`, `.codex-plugin`, `README.md`, `evaluation` except the hidden
  oracle, `skills`, and `tests`, with every other tracked path excluded. The
  source is a named-ref-reachable strict descendant of an explicit named
  baseline; both commits and trees are exact. Package, Runtime, evaluator
  components, projected bytes, and the binary/full-index/no-renames diff are
  recomputed from Git objects. Complete hidden-oracle bytes are rejected from
  every included file and the diff. README-only scope, fake diff, unreachable
  lineage, source-component substitution, old-source/new-dirty-spec, hidden
  oracle, relocation, and post-policy tamper attacks are GREEN.
- The effect cap now contains only model calls and wall milliseconds. Before
  marker consumption or provider reach, runner timeout is clamped to the
  smaller of the unit timeout and remaining cumulative wall authorization; a
  1ms cap supplies at most 1ms. Current-call overrun remains durable evidence
  before stop. No recovery field, retry mechanism, `_redact`, or
  `sanitize_events` API remains.
- Mixed verification requires the previous EvalSpec plus exactly the prior
  full and current exact binding inputs. It recomputes the full proposal from
  the previous EvalSpec and the exact proposal from the current EvalSpec,
  exact prerequisite hashes, mapping reveal, and holdout state. A forged and
  resealed prior product semantic is rejected. Both `verify` and
  `verify-release` expose the three explicit inputs; an end-to-end CLI mixed
  verification is GREEN. No generic registry or fifth record was added.
- Focused Phase-3 command covered 12 named attacks and was GREEN. The one newly
  authorized cumulative command was exactly
  `python3 -B -m unittest discover -s tests -v`: 148 tests, all GREEN in
  59.114 seconds. No second cumulative discovery run occurred.
- Evaluator Python is 3,464 lines total. Largest modules are `host.py` 599,
  `records.py` 598, and `verify.py` 588; every production module is below 600
  and the total is below 3,600. Runtime remains 148 lines and 1,145 words.
  Product tree remains byte-identical to `v0.6.5`.
- Effects remained authorized repository edits plus offline temporary
  files/repos from tests. Model, external provider, network, install, cache/plugin, release,
  external write, stage, commit, push, tag, and PR effects were zero. This
  receipt reports evidence only; Root must independently verify and decide any
  next phase or closure.

## Phase-4 narrow corrective intent

- Root grant: `PHASE-4 NARROW CORRECTIVE GRANT — ROOT-REPRODUCED RESIDUALS`;
  writer, branch, HEAD, tree, product tree, empty index, and authorized dirt
  were reverified before this intent. This plan update precedes Phase-4 test or
  production mutation.
- Add five focused falsifiers before repair: concurrent selected calls cannot
  each receive the whole remaining cumulative wall; combined exact plus any
  non-exact oracle/input drift must select `full_evaluation`; exact diff is
  invariant to source-repository `diff.external`/textconv configuration; and
  single-authority verification rejects purported mixed-only inputs; and the
  fixed twelve-call materializer and durable EvalSpec validator reject any
  non-exact model-call cap, including thirteen, instead of emitting or accepting
  a proposal-invalid record.
- Repair only `host.py`, `identity.py`, `verify.py`, `manifest.py`, and the
  single corresponding invariant in `records.py`, plus the named
  authorized test modules as needed. Preserve exact-only one-call behavior,
  the four frozen invalidation modes, ordinary single-full CLI verification,
  source-derived diff bytes, and one-shot effects. Add no scheduler, generic
  Git hardening, authority engine, mode, record, gate, or lifecycle surface.
- After focused RED then GREEN, run exactly one new cumulative
  `python3 -B -m unittest discover -s tests -v`, then only diff, LOC, product,
  index, and status checks. No closure decision is authorized.
- Focused RED observed before production repair: two concurrent holdout runners
  received 20 seconds against 10 seconds remaining; combined behavior plus
  exact oracle drift selected `exact_final_only`; repository `diff.external`
  changed the recomputed diff; single-authority verification ignored mixed-only
  inputs; and both materializer and resealed durable record accepted a
  thirteen-call cap for the fixed twelve-call plan.

## Phase-4 narrow corrective receipt

- Fixed sole Executor; no delegation. Branch, HEAD
  `c87a754639ae33c9e35d6eeb5ad6bbb1aa8fb2c4`, source tree
  `8847db04e110445bd8ca125917d9b424f959a272`, empty index, authorized dirt,
  and product tree `d9e525a267fbf36669d409ba1b4b009a6beeeea5` remained fixed.
- Remaining wall is divided across every remaining invocation selected by the
  exact authority proposal before marker/provider reach. The concurrent attack
  now receives at most 10 seconds total; exact-only retains its one-call share.
- Combined exact plus non-exact oracle/input drift selects `full_evaluation`;
  exact-only and non-exact-oracle-only retain `exact_final_only` and
  `oracle_replay`. Exact diff uses `--no-ext-diff --no-textconv` in production
  and its real snapshot fixture, invariant to repository external-diff config.
- Single-authority evidence rejects supplied previous-spec/binding inputs while
  ordinary single-full verification remains input-free. Materialization and
  durable EvalSpec validation both require model calls to equal the fixed unit
  count; twelve passes and thirteen fails.
- Five focused REDs were reproduced, then all five and ten regressions were
  GREEN. The only Phase-4 cumulative command was
  `python3 -B -m unittest discover -s tests -v`: 153/153 GREEN in 64.509s; no
  second discover ran.
- Evaluator remains below 3,600 lines and every module below 600. Effects were
  authorized edits and offline test temporaries only; no model, external
  provider, network, install, cache/plugin, release, stage, commit, push, tag,
  or PR effect occurred. Root independently verifies and decides closure.

## Phase-5 one-condition receipt

- Exact invocation plus oracle-component drift reproduced exact-only. Shared
  replay/exact needs now select full; 7/7 focused tests passed. No cumulative
  run; state stayed fixed and Root owns verification.

## Phase-6 receipt

- Root-level managed blobs now join descendants in the closed projection.
  Profiles and host policy require only `command_execution`. Three REDs became
  GREEN; nine adjacent tests passed. No cumulative run. Diff, limits, product,
  index, and prohibited effects remain Root-verifiable; Root decides closure.

## Phase-7 receipt

- Four permission mutations reproduced acceptance. One fixed permission factory
  now drives declaration and exact validation; the focused test and six argv/
  policy regressions passed. No cumulative run; Root verifies and decides.
