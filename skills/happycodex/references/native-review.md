# Fresh native review

Read this reference completely after implementation checks and before freezing the
candidate. Native review is required and read-only. It supplements tests; it does
not replace mechanical or behavioral acceptance.

## Freeze scope and evidence

Normalize task state before review. Prefer a clean task-only commit and a clean
worktree. Record:

- the immutable task baseline and exact candidate HEAD;
- the contract-freeze commit and current ExecPlan path;
- the complete task diff from `git diff <task-baseline>..HEAD`;
- focused and cumulative verification evidence;
- accepted baseline failures and explicit exclusions;
- every task-owned staged, unstaged, and untracked path if a clean commit is
  impossible.

If task ownership is ambiguous, isolate the task before review. When committed state
is impossible, include the baseline range and all task-owned staged, unstaged, and
untracked changes as one scope; list task-owned untracked paths explicitly. Do not
silently omit preserved or user-authored state that can affect the result.

Build a neutral brief in a temporary file outside the repository. Include only the
original outcome, immutable task baseline, contract-freeze commit, candidate HEAD,
complete task diff instructions, verification evidence, accepted baseline failures,
owned dirty paths, and exclusions. Omit the writer's implementation narrative,
self-review, decisions, surprises, historical findings, defense, desired verdict,
and repair story.

## Launch the dedicated reviewer

Inherit the configured review model; do not hard-code a model slug. Request max
effort and use the strongest supported read-only authorization:

    codex review -c 'model_reasoning_effort="max"' - < "$review_brief"

Never silently downgrade model or effort. If `max` is unavailable, disclose the
failure before relying on a lower explicitly authorized setting.

The `codex review` CLI accepts either a selector or custom instructions. A custom
prompt conflicts with `--base`, `--commit`, and `--uncommitted`, so the neutral
prompt must tell the reviewer to inspect the exact recorded Git range and owned
paths itself. Do not combine stdin instructions with selector flags.

Default to one fresh review invocation with the following phases in order.

## Phase 1: independent discovery and correctness

Do not read the ExecPlan, its history, or writer narrative during this phase. Start
from the original outcome, immutable baseline, candidate, repository, and task diff.
Build an independent obligation inventory. Trace changed and unchanged surfaces that
could falsify the outcome, including entry points, persisted state, producers and
consumers, workers, deployment, recovery, and legacy paths.

Perform correctness and adversarial review of the complete task diff. Check defaults,
boundaries, type semantics, malformed input, unrelated behavior, established callers,
safety, data integrity, and production failure modes. Preserve the independent
inventory before continuing.

## Phase 2: contract completeness mapping

Now read only the ExecPlan's contract-bearing sections: original outcome, baseline,
frozen obligation matrix, acceptance oracles, authorized amendments, and current
evidence. Do not read Decision Log, Surprises & Discoveries, writer self-review,
historical findings, Review State, or Outcomes & Retrospective.

Map the independent inventory to the frozen contract and implementation. Report
missing obligations, uncovered acceptance, stale evidence, unimplemented production
or retirement work, and other completeness failures. Do not let the writer's
inventory erase an independently discovered surface.

## Scope integrity

The reviewer must state the inspected baseline, candidate, Git ranges, dirty paths,
and whether it covered the full repository-wide completeness surface. Any truncation,
unavailable diff, or inability to prove full coverage fails the review gate.

When one context cannot cover a large diff, split correctness review by semantic
milestone or disjoint range. Each split remains fresh and read-only. Afterward retain
one repository-wide completeness review against the original outcome and frozen
contract; never substitute sampling for scope integrity.

## Reproduce and classify findings

The Root independently reproduces every actionable finding against the current
candidate:

- `confirmed`: add a RED regression oracle when practical, repair, reach GREEN,
  and rerun focused and required cumulative checks;
- `rejected`: retain exact counter-evidence and do not edit merely to agree;
- `unresolved` and completion-blocking: stop for the user.

A finding is completion-blocking when it can violate the original outcome,
acceptance, safety or data integrity, production operation, or an exhaustive or
retirement claim. Do not depend on undefined P0/P1 labels. A literal zero-finding
result is unnecessary; only reproduced completion blockers prevent closure.

## Fresh re-review

At most one fresh re-review is permitted after confirmed fixes change the candidate.
The Root must run that one fresh re-review after checks. Give it the same immutable
baseline, complete current diff, current verification evidence, accepted baseline
failures, exclusions, and the two ordered phases.

Omit all prior findings, dispositions, and repair narrative so it judges
independently. Never review only the fix. If that re-review reports a confirmed or
unresolved material defect, stop and report without changing the candidate; any fix
requires a newly authorized review cycle.

## Review receipt

Record only the task baseline, contract-freeze commit, candidate, command or detached
task identifier, configured model, requested/actual effort, scope statement, result,
and evidence freshness. Do not store findings or repair narrative in the ExecPlan.
Desktop detached review may substitute only when it can guarantee the same exact
scope, staged neutral brief, read-only behavior, and scope-integrity output.
