# HappyCodex 0.4.1 convergence

Protocol: `HappyCodex/0.3` (active 0.4.0 maintainer runtime)
Invocation: `$happycodex:happycodex`
Writer: Root only for the mutable resources listed below
State: contract frozen; implementation not started
Resume: restore this file and reconcile Git, tests, Goal, worktree, agents, and gates before any write, review, or completion.

## Outcome and baseline

**Operative sources.** Current Codex task
`019fa9c7-0d4c-72e0-b920-7231a4dab31c`, user plan turn
`019faa10-e00f-75d1-a392-1cdbf6f098da`, item `item-92`, SHA-256
`c5ebab432ca06d054d971f98c5c9bda9d6cecdf250b24f71293b183986e92eb0`;
budget question turn `019faa13-3753-7820-9a01-b9345bca7330`, item `item-102`,
SHA-256 `653f3936eaf713b623af0018622509b65de17c776da7d9662b42c3c885b65ed7`;
and direct continuation/amendment turn `019faa15-4a99-7283-9aee-06148df64285`,
item `item-107`, SHA-256
`3c0077c9863e135c710592c17be11511b5b335651d358b3c71e76ec015de4189`.
The amendment replaces the inherited Runtime budget with a 300-line target,
340-line hard ceiling, 2,600-word target, and 3,000-word hard ceiling. It changes
only the Runtime/template budget and its tests; no product or evidence existed to
invalidate.

**Normalized outcome.** First ship a clean-break HappyCodex 0.4.1 from public 0.4.0:
resource-scoped single writers, family hardening and repair batches, compact current
ExecPlans, `protocol_review_mode`, fresh evidence, exact-final review, public release,
personal upgrade, and retained 0.4.0 rollback. Then use separate successor tasks and
ExecPlans to resume the two named long tasks and port the protocol to the frozen 0.5
candidate. No controller, Task State JSON, compatibility reader, dual write, schema
alias, Evidence DAG, automatic old-task evidence conversion, or unapproved live cost.

**Frozen protocol contract.**

- The lifecycle is `implementation → focused_hardening → candidate_frozen →
  exact_final → closed`. Open families, active writes, incomplete reviewer union, or
  unreconciled grants prohibit `exact_final`; any product-source change returns to
  hardening and invalidates all candidate evidence and final reviews.
- Root assigns stable finding IDs and `family_id` values. A family shares an invariant
  and implementation boundary. Each family scans source/identity, type/cardinality,
  ordering/terminal state, alias/mutability/TOCTOU, serialization/replay, and all
  consumers/failure propagation. Every surface needs a counterexample, positive case,
  evidenced `N/A`, or open status.
- Reviewers of one candidate all reach terminal state before Root unions, reproduces,
  and groups findings. A frozen `repair_batch` may contain coupled families and several
  narrow grants/commits; sibling findings add RED coverage and enlarge the batch.
  Full final review never runs mid-batch.
- Focused reviewers may see history, the family ledger, counterexamples, and repair
  story; their receipts are non-neutral hardening evidence only. Exact-final reviewers
  receive exact frozen product bytes and neutral instructions without that material or
  a preferred verdict.
- A closed family recurring in final review requires replacement or strengthening of
  its frozen abstraction boundary and removal of old bypasses. A second recurrence
  after boundary replacement stops automatic repair and requires user choice to expand
  the refactor, change the contract, or abandon.
- One owner exists per shared mutable resource. Every task names worktree, branch/ref,
  ledger, external-output namespace, and activation target. Disjoint resources may run
  concurrently; any overlap rejects the second writer.
- The ExecPlan is a current index: target at most 8,000 words and hard limit 12,000.
  It keeps frozen contract, open claims/families, current grant, candidate identity,
  valid evidence, invalidation edges, and pending gates. Closed detail becomes a
  checkpoint, Git revision, receipt digest, and invalidation link; complete history
  remains on a reachable Git ref or approved content-addressed archive. Missing,
  inconsistent, or tampered summaries fail closed and recover along that chain.
- Runtime plus template target at most 300 lines/2,600 words, with hard limits of
  340 lines/3,000 words. The public invocation remains `$happycodex:happycodex`.
  Evaluator input uses only `protocol_review_mode: none | focused_hardening |
  exact_final`; there is no compatibility alias and no model-generated `family_id`.

**Current task boundary.** This ExecPlan owns the 0.4.1 source, certification, release,
and personal-upgrade outcome. Existing-task successors and the 0.5 port are ordered
downstream outcomes that require fresh task-owned ExecPlans after 0.4.1 closure.

**Immutable snapshot.** Repository: `happycodex`; baseline revision:
`730c6a59d4f15eab9b40895e7ea9e0f4ee3522f5`; baseline tree:
`a7a0d228f8368244bb8799acd491646430c81ef9`; worktree:
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.4.1-convergence`;
branch: `codex/happycodex-0.4.1-convergence`; owner: Root.

**Mutable-resource ownership.** Owned now: this worktree/index, the branch above,
`evaluation/results/current.json` in this worktree, and this ExecPlan. Reserved but
read-only until their gates: a new 0.4.1 external evidence namespace, public release
refs, `/home/caichenghang/plugins/happycodex`, the personal installed cache, and the
active plugin. Other worktrees, branches, ledgers, evidence outputs, active tasks, and
the installed 0.4.0 bytes are preserved.

**Baseline check.** `python3 -m unittest discover -s tests -p 'test_*.py'` ran 123
tests in 7.656 seconds: 122 passed and one errored at
`test_verify_and_impact_commands_are_read_only_json` because the certified ledger is
stale against current inputs. Finding `F-BL-001` is unaccepted and open; determine
whether current toolchain drift or repository bytes caused it, then resolve through
the authorized fresh 0.4.1 genesis rather than a compatibility path.

**Independent design advice.** Fable 5 session
`40eddcce-9b0a-4f27-bf87-637ea44c867e` used `claude-fable-5/max`, no tools or
network, and cost `$1.3704`. It supported the two-phase direction but is advisory only,
not product evidence or exact-final review. Its suggestions to treat ordinary commit
hashes as sufficient no-commit evidence, auto-release unreproducible security findings,
ignore accepted baseline failures, or place phase state in every finding were rejected.

**Alternatives rejected.** Sibling scan alone lacks lifecycle and recovery semantics;
an Evidence DAG risks stale-evidence reuse; a controller/full pipeline rewrite creates
a second state machine; compatibility readers, dual writes, aliases, and in-place old
task conversion enlarge the state space without helping convergence.

## Claims Ledger

| ID | Type | Claim | Closure / falsifier | Evidence | State |
| --- | --- | --- | --- | --- | --- |
| `C-01` | outcome | Single-writer ownership is scoped to overlapping mutable resources; disjoint worktrees may run concurrently. | Protocol text plus positive and collision counterexamples. | pending | open |
| `C-02` | outcome | Family hardening and frozen repair batches precede exact-final certification. | Open-family, reviewer-union, recurrence, and source-drift tests. | pending | open |
| `C-03` | outcome | `protocol_may_review` is removed and receipts bind `none`, `focused_hardening`, or `exact_final`. | Shared schema, oracle, receipt, and ledger tests; no alias. | pending | open |
| `C-04` | outcome | ExecPlan is a bounded current index with fail-closed Git/archive recovery. | Size, tamper, no-commit, multi-repo, and compaction tests. | pending | open |
| `C-05` | preservation | Public invocation stays `$happycodex:happycodex`; 0.4 Root writer and unrelated behavior remain. | Package/runtime tests and behavior comparison. | pending | open |
| `C-06` | outcome | Exact 0.4.1 release, public install, personal upgrade, and 0.4.0 rollback are proven. | Fresh evidence, three GO reviews, install/readback, rollback rehearsal. | pending | open |
| `C-07` | premise | No live evaluator call runs without a persisted exact impact receipt and direct gate-scoped user authority. | Ledger/CLI refusal and later authority receipt. | current protocol | verified |
| `C-08` | constraint | Runtime/template report the amended 300/2,600 optimization target and never exceed the 340/3,000 hard ceiling. | Contract tests compute totals and fail at hard limits; simplification review explains any target excess. | 308 lines/2,685 words after restoring certified reviewer/no-commit semantics; 8/85 above target, 32/315 below hard ceiling | open |

## Convergence Ledger

| Family | Invariant / boundary | Members | Scan surfaces | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `F-CONV-001` | Review eligibility is phase- and evidence-exact across Runtime, evaluator, receipts, recovery, and every consumer. | `protocol_may_review`, hardening/final distinction, source invalidation | source/identity=clean-break enum RED/GREEN; type/cardinality=three exact strings; order/terminal=phase enum; alias/mutability/TOCTOU=no old key; serialization/replay=receipt and four-sibling replay GREEN; consumers/failure propagation=corpus/oracle/ledger GREEN | implementation complete; focused review pending | `RB-001` | five-test RED failed as expected; 127/128 cumulative GREEN with only old ledger open | 0 |
| `F-CONV-002` | Writer uniqueness applies exactly to shared mutable resources, not globally to unrelated worktrees. | worktree, branch/ref, ledger, evidence output, activation target | source/identity=all five named; type/cardinality=one owner per overlap; order/terminal=ownership before writes; alias/mutability/TOCTOU=overlap rejects; serialization/replay=template; consumers/failure propagation=Runtime/AGENTS tests GREEN | implementation complete; focused review pending | `RB-001` | contract tests GREEN | 0 |
| `F-CONV-003` | Current-index recovery is bounded, complete, content-addressed, and fail closed. | checkpoint chain, no-commit ref/archive, compaction, multi-repo identity | source/identity=checkpoint/ref/digest; type/cardinality=one current index; order/terminal=reconcile before writes; alias/mutability/TOCTOU=tamper fails; serialization/replay=recovery enum; consumers/failure propagation=Runtime/template/ledger GREEN | implementation complete; fresh genesis and focused review pending | `RB-001` | contract, recovery, no-commit, multi-repo tests GREEN | 0 |

## Implementation and verification boundary

`RB-001` may modify only Runtime/template/maintainer protocol text, plugin version and
change notes, evaluator shared contracts and consumers, fixed offline cases/oracles,
tests, `evaluation/results/current.json` through the canonical CLI, and this ExecPlan.
It must not modify the installed/public 0.4.0 bytes, marketplace state, other worktrees,
other task ledgers, active task state, public refs, or external evidence. Product changes
begin only after this freeze commit.

RED must prove open-family final-review rejection, focused/final receipt separation,
source drift, recurrence escalation, reviewer contamination, trusted unknown safety,
accepted baseline identity, multi-repository identity, no-commit recovery, compaction
equivalence and tamper failure, family replay for snapshot/manifest/actor-receipt/
identity siblings, and parallel disjoint-resource acceptance versus overlap rejection.
GREEN requires the full offline unit suite, Ruff, both official validators, CLI dry-run,
Runtime budgets, isolated install/invocation, and compaction recovery equivalence.
Model-reaching evaluator, live corpus/holdout, public release, active installation, and
task successor creation remain later gated operations.

## Checkpoint

- Milestone: `RB-001` implementation complete; next: commit the semantic slice, then create fresh 0.4.1 genesis and run cumulative offline gates.
- Last green: five focused RED tests initially produced four failures and one error against 0.4.0. After implementation those five pass. Full suite now runs 128 tests: 127 pass; only `F-BL-001` remains because the tracked certified 0.4.0 `current.json` points to old-schema source. The new schema, synthetic certification, four-sibling replay, accepted baseline, reviewer contamination, multi-repo, no-commit, and compaction tests pass.
- Owned dirty paths: Runtime/template/AGENTS/README/manifest, evaluator contracts/consumers, all fixed oracle JSON projections, three test modules, and this ExecPlan. Old evidence files are untouched.
- Goal: none.
- Agents/reviewers: none launched.
- Pending gates: semantic implementation commit, fresh genesis, cumulative GREEN, focused hardening,
  final version/cachebuster, fresh genesis/evidence, exact-final reviews, any separately
  authorized live behavior evaluation, public release, personal upgrade, rollback, and
  downstream successor task creation.

## Retrospective

Fill only after closure; never expose it as review evidence.
