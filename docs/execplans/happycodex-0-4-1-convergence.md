# HappyCodex 0.4.1 convergence

Protocol: `HappyCodex/0.3` (active 0.4.0 maintainer runtime)
Invocation: `$happycodex:happycodex`
Writer: Root only for the mutable resources listed below
State: skeleton
Resume: restore this file and reconcile Git, tests, Goal, worktree, agents, and gates before any write, review, or completion.

## Outcome and baseline

**Operative sources.** Direct user request in the current Codex task on 2026-07-28:
implement the supplied “HappyCodex 0.4.1 收敛流程修复与 0.5 移植计划”, then the
direct amendment “好的继续” after replacing the old Runtime budget with a 300-line
target, 340-line hard ceiling, 2,600-word target, and 3,000-word hard ceiling. Exact
message anchors and SHA-256 values remain an open freeze field.

**Normalized outcome.** First ship a clean-break HappyCodex 0.4.1 from public 0.4.0:
resource-scoped single writers, family hardening and repair batches, compact current
ExecPlans, `protocol_review_mode`, fresh evidence, exact-final review, public release,
personal upgrade, and retained 0.4.0 rollback. Then use separate successor tasks and
ExecPlans to resume the two named long tasks and port the protocol to the frozen 0.5
candidate. No controller, Task State JSON, compatibility reader, dual write, schema
alias, Evidence DAG, automatic old-task evidence conversion, or unapproved live cost.

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

## Convergence Ledger

| Family | Invariant / boundary | Members | Scan surfaces | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `F-CONV-001` | Review eligibility is phase- and evidence-exact across Runtime, evaluator, receipts, recovery, and every consumer. | `protocol_may_review`, hardening/final distinction, source invalidation | source/identity; type/cardinality; order/terminal; alias/mutability/TOCTOU; serialization/replay; consumers/failure propagation | open | `RB-001` | pending RED | 0 |
| `F-CONV-002` | Writer uniqueness applies exactly to shared mutable resources, not globally to unrelated worktrees. | worktree, branch/ref, ledger, evidence output, activation target | same six surfaces | open | `RB-001` | pending RED | 0 |
| `F-CONV-003` | Current-index recovery is bounded, complete, content-addressed, and fail closed. | checkpoint chain, no-commit ref/archive, compaction, multi-repo identity | same six surfaces | open | `RB-001` | pending RED | 0 |

## Checkpoint

- Milestone: skeleton and baseline; next: freeze exact sources, affected surfaces, and RED batch.
- Last green: baseline has `F-BL-001`; no candidate product write exists.
- Owned dirty paths: only this new ExecPlan.
- Goal: none.
- Agents/reviewers: none launched.
- Pending gates: skeleton commit, contract freeze, RED, GREEN, focused hardening,
  final version/cachebuster, fresh genesis/evidence, exact-final reviews, any separately
  authorized live behavior evaluation, public release, personal upgrade, rollback, and
  downstream successor task creation.

## Retrospective

Fill only after closure; never expose it as review evidence.
