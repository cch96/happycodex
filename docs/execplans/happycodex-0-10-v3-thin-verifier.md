# HappyCodex 0.10 v3 thin-verifier clean break

## Verbatim request

> 这六个你觉得是否有过度优化或者过度思考，都是必要的吗
>
> 好的你觉得怎么改比较好，是否有更好更优雅的方案
>
> 好的执行吧

## Outcome

Produce one local, unreleased, incompatible HappyCodex 0.10 source candidate.
Keep Codex responsible for planning, delegation, writing, and review reasoning;
reduce the repository evaluator to a deterministic thin verifier; and keep the
external host responsible for authority, provider effects, clocks, recovery,
and release readback. The public Skill must remain small, proportional, and
explicit about when native explorers, workers, Challenger, and Exact-final are
actually useful.

This is a new user-authorized candidate after the independent 0.10 v2
candidate received a terminal `NOT_YET`. It is not an automatic repair or a
continuation of that frozen candidate.

## Workspace, source, and mutable paths

Work only in `/tmp/happycodex-0.10-v3-thin-verifier` on branch
`codex/happycodex-0.10-v3-thin-verifier`, derived from
`ce2a905e15f091c1fd6b4dcfbe3630b56f5e48b4`. The worktree and index were clean
at admission. The baseline offline suite ran 166 tests with exactly three
failures: current version was not greater than released `0.9.2`, exact-final
accepted an old/self-selected source projection, and an old source identity
could reach authority acceptance for a new dirty `EvalSpec`.

Only these paths may be added, changed, or deleted:

- `AGENTS.md`
- `docs/execplans/happycodex-0-10-v3-thin-verifier.md`
- `.codex-plugin/plugin.json`
- `README.md`
- `README.en.md`
- `skills/happycodex/SKILL.md`
- `skills/happycodex/references/execplan.md`
- `skills/happycodex/agents/openai.yaml`
- `evaluation/README.md`
- `evaluation/__init__.py`
- `evaluation/canonical.py` (optional new module)
- `evaluation/cli.py`
- `evaluation/holdout.py`
- `evaluation/host.py` (deletion or reduction to pure request construction is allowed)
- `evaluation/identity.py`
- `evaluation/manifest.py`
- `evaluation/oracle.py`
- `evaluation/policy.py`
- `evaluation/provider.py`
- `evaluation/records.py`
- `evaluation/schemas.py` (optional new module)
- `evaluation/spec.py` (optional new module)
- `evaluation/verify.py`
- `evaluation/hidden-oracles-v1.json`
- `evaluation/manifest-v1.json`
- `evaluation/provider-fixtures-v1.json`
- `evaluation/report-schemas-v1.json`
- `tests/attestation_fixtures.py`
- `tests/fake_external_host.py`
- `tests/test_attestation_clean_break.py`
- `tests/test_attestation_cli.py`
- `tests/test_attestation_contract.py`
- `tests/test_attestation_flow.py`
- `tests/test_fixed_host_transaction_v2.py`
- `tests/test_stage_profiles.py`
- `tests/test_stateless_records.py`
- `tests/test_thin_verifier.py` (optional new test module)
- `tests/test_trust_boundary_repair.py`

All edits are reversible local source edits made with `apply_patch`. Offline
standard-library validation may create only disposable test output outside the
repository. Do not stage, commit, push, tag, publish, install, activate, invoke
a production provider/model, use network-backed evaluation, update a
marketplace or cache, or mutate external role profiles, credentials, rollback
state, the original dirty worktree, or the frozen v2 worktree.

Preserve the exact published `v0.6.5:skills/happycodex` tree
`d9e525a267fbf36669d409ba1b4b009a6beeeea5`. The index must remain empty. No
compatibility reader, migration, alias, dual write, mutable ledger, controller,
scheduler, general evidence graph, or fifth durable record type is allowed.

## Design decision

Use three explicit trust domains:

1. Codex-native workflow owns plans, agent routing, implementation, and review
   reasoning. The product Skill tells the root when to use native Explorer or
   Worker and reserves fresh custom Challenger and Exact-final profiles for
   decision-changing, high-risk boundaries.
2. The repository evaluator owns only canonical serialization, identities,
   closed schemas, fixed topology, deterministic scoring, and stateless
   relationship verification over caller-supplied immutable records.
3. The external boundary owns user authority, provider invocation,
   idempotency/one-shot enforcement, trustworthy time, attempt history,
   cumulative effect wall time, recovery decisions, and release readback.

The only durable record types are `ProductArtifact`, `EvalSpec`, `Attestation`,
and `ReleaseReceipt`; unknown types fail closed. Product identity excludes
evaluator bytes. `EvalSpec` identity keeps provider input, oracle, and harness
components separate so source drift invalidates only necessary work.

Define one canonical immutable topology used by construction and validation:
five behavior units, six fixed holdout units representing three concurrent
candidate/baseline pairs, and one exact-final unit. Provider inputs are
allowlisted and mapping-blind. Score holdouts only after all six authenticated
terminal outputs are frozen; a caller-supplied reveal timestamp is not proof
and must not exist in the contract.

Exact-final input is derived from a fixed review policy, the immutable product
artifacts, a readable immutable `ReviewProjection`, and a fixed response
schema. `ReviewProjection` is embedded and hashed input, not a fifth durable
record. Exclude caller-authored prompts, filesystem paths, arbitrary obligation
lists, and arbitrary workflow/preservation claims. The one-shot effect subject
binds candidate artifact plus review-policy/contract identity, not an authority
nonce. For unchanged candidate and review-policy identity, an adverse or
unknown exact-final terminal is final. An explicitly authorized policy change
creates a different effect; repository code validates identities and cannot
manufacture that authority.

Every external observation records attempt wall milliseconds and cumulative
effect wall milliseconds. A recovered, proven pre-provider no-effect attempt
must remain included in the signed cumulative wall of the eventual terminal;
release qualification uses that cumulative value. Ambiguous or partial effects
stop without retry. Production repository code does not invoke providers or
implement retry orchestration; tests may use a fake external boundary.

Checks metadata must be mechanically derived from the candidate snapshot and
actual check results, including `candidate_snapshot_sha256`; it may not contain
hand-maintained line counts or claimed results. Keep evaluator Python at most
3,200 lines where practical, never above 3,600, with no production module over
600 lines.

## Execution and review boundary

Use one active writer for all overlapping product/evaluator/test paths. A
read-only Explorer may inventory constraints or scenarios without proposing a
parallel implementation. The root owns this plan, scope checks, candidate
freeze, and final decision. Writer replacement or compaction does not relax
scope; reconstruct from this plan plus live Git and test state.

Before final review, freeze an immutable review bundle containing the candidate
commit/tree source, exact changed-path projection, candidate snapshot digest,
policy identity, mechanical check results, and preservation evidence. Run
fresh forward-use scenarios against the Skill, then exactly one fresh,
read-only, blocker-only Exact-final against that frozen bundle. A changed
candidate invalidates the verdict. `NOT_YET` or required `UNKNOWN` terminates
this candidate; do not enter an automatic repair/review loop.

## Checks, Done, and stops

Required checks are:

- focused tests for the six v2 review findings and the three live baseline
  failures;
- full offline standard-library tests with zero failures;
- canonical topology, closed-schema, source-drift, effect-identity,
  mapping-blindness, cumulative-wall, release-readback, and generated-checks
  adversarial tests;
- Python compile/import and production import-DAG checks;
- Skill `quick_validate` and plugin `validate_plugin`;
- evaluator line budgets and per-module limits;
- `git diff --check`, exact changed paths, empty index, protected-tree digest,
  and unchanged original and v2 worktrees;
- fresh forward-use scenarios and one terminal blocker-only Exact-final.

Done means the public 0.10 surfaces and thin verifier implement the stated
contract, every required mechanical check passes, no required evidence is
unknown, the frozen final review is `GO`, and no forbidden effect occurred.

Stop before further mutation on source/index/path drift, protected-tree drift,
scope expansion, an unexplained test regression, evaluator budget breach,
unverified required identity, missing authority, or any partial or ambiguous
external effect. After compaction, reread this plan and inspect live Git, test,
and tool state; never treat this static file as a live-state ledger.
