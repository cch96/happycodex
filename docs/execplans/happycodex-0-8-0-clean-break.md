# HappyCodex 0.8.0 simplification — current index

## Current snapshot

- Phase: `candidate_frozen`.
- Outcome: compress HappyCodex into durable guidance for one fixed writer,
  bounded repair, contextual authority, neutral review, and fail-closed
  reconciliation without adding a resource controller or compatibility plane.
- Exact user authority: “好的 执行”, contextual assent to Root's immediately
  preceding B-double-prime proposal. It authorizes exactly this local
  simplification/removal wave and one later fresh Exact-final by Root.
- Active sequencing grant digest:
  `295a2a1fd5e7e60a837b1372881237faa695b141786116842568df74e3189f3d`.
- Source/direct parent: commit
  `309a05e886c3bd7bded85256d9e1dcd3cd7284da`, tree
  `dc4a345c2b1395142087806691ebff3fc30a8e2a`.
- Prestate: clean candidate
  `97e6036d3b5abacb87c55a33338b4692a66066e8`, tree
  `4f441b896ea64bb12f79a07aac23a4b07fd15321`, branch
  `codex/happycodex-0.8-clean-break`, worktree
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.8-clean-break`.
- Fixed sole controlled-domain writer: `/root/v080_executor`. Goal: absent.
- Simplification wave: used/limit `1/1`.
- Post-Exact-final repair budget: `0/0`. A later review cannot authorize a
  repair wave.
- Relevant prestate: no active HappyCodex resource-claim directory in the
  common Git directory.

## Exact boundary

This wave may edit, restore, or delete only the fourteen candidate paths named
by Root. Its required final source-to-candidate inventory is exactly seven:

- `.codex-plugin/plugin.json`
- `README.en.md`
- `README.md`
- `docs/execplans/happycodex-0-8-0-clean-break.md`
- `skills/happycodex/SKILL.md`
- `skills/happycodex/references/execplan.md`
- `tests/test_attestation_contract.py`

Therefore `skills/happycodex/scripts/resource_claim.py`, all three evaluation
JSON files, and `tests/attestation_fixtures.py` return byte-for-byte to source;
candidate-only `skills/happycodex/scripts/resource_claim_topology.py` and
`tests/test_resource_claim.py` are deleted. All other repository paths and the
published v0.6.5 Skill tree
`d9e525a267fbf36669d409ba1b4b009a6beeeea5` remain immutable.

No push, tag, install, release, activation, marketplace/cache/config mutation,
network/model call, cleanup, migration, rollback, or other external effect is
authorized. Root alone may later dispatch one fresh neutral Exact-final.

## Frozen obligations

| Obligation | Observable requirement | State |
| --- | --- | --- |
| `REMOVE_OVEREXPANSION` | restore the source resource helper/evaluator case and delete candidate topology/helper tests | verified |
| `FOUR_PHASE_FIXED_WRITER` | retain `working`, `candidate_frozen`, `exact_final`, `closed`, one fixed Executor, and fresh neutral Exact-final | verified |
| `CURRENT_SNAPSHOT` | keep one current snapshot without task history, mutable ledger, controller, migration, or compatibility reader | verified |
| `ENVELOPE_GUARDRAILS` | new durable schema/state, cross-context coordination, or control-plane machinery outside the frozen boundary is expansion; compare removal/rollback/simplification before adding repair machinery | verified |
| `TRUTHFUL_FAILURES` | candidate failures cannot be relabeled; exhausted budgets use the existing stop-line | verified |
| `GOAL_BOUNDARY` | Goal grants no amendment, waiver, review, cost, authority, or effect | verified |
| `RECONCILIATION_LATCH` | a named derived-but-persisted latch applies only to partial/ambiguous external-effect terminals and has the exact recovery rule below | verified |
| `CONTEXTUAL_AUTHORITY` | bare continuation grants nothing unless an exact content-addressed proposal is pending; clear assent authorizes only the immediately preceding exact proposal | verified |
| `FAIL_CLOSED_SHAPE` | old or mismatched snapshot shape is unknown and returns to the user without reader or migration | verified |
| `EVALUATOR_INVARIANTS` | four records, stateless verification, holdouts/token caps/provider boundary, and original midflight case remain source-faithful | verified |
| `EXACT_SEVEN_PATHS` | final committed diff relative to source contains exactly the seven paths above | verified |

The `reconciliation latch` is derived safety state persisted only to survive
context loss; it is not a phase or evaluator record type. Activate it only for
a partial or ambiguous external-effect terminal, never for repeated local or
review falsifiers. While active, allow only read-only reconciliation,
verification, and return to the user; forbid grants, effects, candidate freeze,
and Exact-final. Clear it only after reconciliation binds exact current effect
state/prestate, Root freezes an exact bounded recovery proposal and digest, and
the user explicitly authorizes that proposal. Neither state nor action must
change. Repeated unchanged failures and exhausted repair budgets use the normal
stop-line instead.

## Checks and gate

Characterization RED: the current candidate added a second production topology
module, persistent locking/quarantine promises, task-specific resource tests,
and evaluator/fixture changes beyond the selected protocol boundary. The repair
is removal and source restoration, not another coordination mechanism.

Current candidate-freeze evidence: the 18 focused product-contract tests pass;
Skill and plugin validators pass; Python AST and all JSON parse; the five
restored paths equal source byte-for-byte; both candidate-only paths are
absent; the source-to-candidate projection is exactly the seven frozen paths;
secret and whitespace scans pass; evaluator Python totals 3,479 lines with a
599-line module maximum; the source helper is 460 lines; and the v0.6.5 Skill
tree remains exact. The cumulative gate is run only on the unified committed
candidate, so no cumulative result is recorded here yet.

The cumulative offline suite may retain only these two source-baseline failures,
with zero errors or other failures:

- `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
  with `mutation='old-source'`;
- `test_old_source_components_cannot_back_a_new_dirty_evalspec`.

This file does not embed its containing commit/tree. Final identity and
post-amend cumulative results are external Executor/Root receipts. Root then
independently verifies the exact seven-path candidate and may dispatch one fresh
Exact-final; no repair follows from that review.

Stop without retry, cleanup, or widening on prestate/config/path drift,
unexpected failure/error, ambiguous or partial effect, unavailable
`apply_patch`, an unaccounted path, source-restoration mismatch, or inability to
retain one clean local commit.
