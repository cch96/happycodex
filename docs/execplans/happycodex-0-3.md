# HappyCodex 0.3 ExecPlan

## Original Outcome

Implement the user-approved “HappyCodex 0.3: Codex-native reliable execution
protocol” plan. The outcome is a Skill-only redesign with no hooks, external
controller, or Task State JSON. Root remains the only writer; read-only scouts,
boundary challengers, and reviewers may gather evidence. Durable state is split
between a repository-tracked ExecPlan, Codex Native Plan, and Git/tests. Goal is
used only when the user explicitly enables it.

The implementation must prevent five observed failure modes:

1. narrowing the system boundary before implementation;
2. silently weakening a frozen completion contract;
3. losing task state across compaction;
4. anchoring fresh review on the writer's narrative; and
5. treating a single paired experiment as sufficient validation.

It must preserve the approved workflow details: immediate ExecPlan durability,
independent exhaustive-claim boundary challenge, evidence-backed obligation
states, semantic vertical milestones, cumulative verification, staged fresh
native review, fail-closed completion, behavioral micro tests, adaptive two-to-
three-pair holdout evaluation, a 25 percent equal-quality cost gate, and release
only after validation.

## Baseline and Ownership

- **Immutable task baseline:** `3b9c11fac1f97df75263e0bfc6421c575e04e8b2`
- **Branch:** `main`, initially aligned with `origin/main`
- **Initial worktree:** clean
- **Writer:** Root only
- **Preserved external worktrees:** existing detached/feature/evaluation
  worktrees are not task-owned and must not be modified or removed
- **Goal:** not enabled; the user did not explicitly request Goal
- **Current phase:** baseline freeze and durable-plan bootstrap

## Accepted Baseline Failures

None.

Baseline evidence on 2026-07-14:

- `python3 -m unittest discover -s tests -v`: 15 passed
- `quick_validate.py skills/happycodex`: passed
- `validate_plugin.py .`: passed

## Pending Gates

| Gate | Status | Evidence required |
| --- | --- | --- |
| Independent boundary challenge | pending | Read-only return plus Root reproduction |
| Completion-contract freeze | pending | Obligation matrix and contract-freeze commit |
| Skill implementation | pending | Vertical milestone commits with tests |
| Static and micro validation | pending | Validators and behavioral scenarios |
| Fresh native review | pending | Complete-diff review receipt and dispositions |
| Paired holdout | pending | Two or three blinded pairs and cost accounting |
| 0.3 release | pending | All completion gates satisfied |

## Contract Sections

The following sections are intentionally empty until boundary evidence is
reconciled: System Boundary and Obligations, Acceptance Oracles, Milestones,
Evidence Ledger, Contract Amendments, and Review Receipt. Review findings and
writer narrative must not be stored in those contract sections. Retrospective is
written only after completion.
