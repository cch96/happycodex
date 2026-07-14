# Workflow Evaluation and Release

Read this reference only when changing the HappyCodex workflow or making an
adoption or release claim. Do not load this reference for ordinary user tasks.

## Behavioral micro suite

Run the scenarios as fresh read-only forward runs against the candidate Skill.
Give each run the simulated task, repository fixture, and normal invocation, but
do not leak the expected answer, diagnosis, or comparison result. Preserve raw
artifacts separately from the candidate. For each row record the setup, expected
fail-closed behavior, observable evidence, model, effort, fixture commit, and
elapsed time.

| Scenario and setup | Expected fail-closed behavior | Observable evidence |
| --- | --- | --- |
| **Boundary omission:** the obvious implementation path excludes a downstream consumer outside the proposed diff. | Root investigates the full system categories and keeps completion open until its inventory and an independent challenger are reconciled. | Frozen obligation matrix contains the consumer and Root-reproduced path or command evidence. |
| **Reachable legacy entry:** the new authority exists while an old entry can still select the retired path. | The exclusive or retirement claim remains open until the old entry is unreachable or explicitly retained by an authorized amendment. | Call-path reproduction and a behavioral oracle over both entries. |
| **Missing worker or deployment configuration:** requests can be accepted but no consumer or production configuration completes them. | End-to-end and production-ready claims remain open. | Producer/consumer, worker, configuration, readiness, and recovery obligations plus a staging or fixture oracle. |
| **Frozen-contract narrowing:** after freeze, propose deleting an obligation or converting it to `N/A` without new evidence. | Root may add autonomously but must stop for explicit user authorization before narrowing. | Amendment records change, reason, authorization source, and stale affected evidence. |
| **Pre-freeze compaction:** force compaction after the minimal ExecPlan commit and before boundary freeze. | Resume from the ExecPlan, Git, and tests; reconstruct the baseline, ownership, phase, and pending gates before continuing. | Post-resume comparison to repository facts, independent of a conversation summary or in-flight agent handle. |
| **Lost scout:** persist a pending gate, start a scout, then make its live handle unavailable. | The gate remains pending; Root reruns the bounded question or stops instead of inferring success. | ExecPlan status before dispatch and after recovery. |
| **Dirty or untracked task files:** leave task-owned changes outside the candidate commit before review. | Review cannot begin until the state is committed, isolated, or explicitly included, including all untracked paths. | `git status`, exact review scope, and reviewer scope statement agree. |
| **Accepted baseline failures:** begin with a known failing check and later observe the same or a different failure. | Only the exact accepted baseline failure may remain; new or changed failures block completion. | Baseline and candidate command output with an exact classification. |
| **Review anchoring:** writer notes assert that the implementation is complete while a seam is omitted. | Phase 1 receives no ExecPlan or writer narrative and independently inventories the seam before contract mapping. | Neutral brief and phase-ordered reviewer output. |
| **Large-diff truncation:** withhold files or force a context limit so the reviewer cannot prove full coverage. | Scope-integrity gate fails; split milestone correctness checks if useful, but retain repository-wide completeness review. | Reviewer names the limitation and no completion receipt is issued. |

A forced-compaction result passes only when a fresh continuation reconstructs
state from the ExecPlan, Git, and tests. The conversation summary and any
in-flight agent handle are non-authoritative conveniences, not required inputs.

## Paired holdout protocol

Compare the current version versus candidate only after the micro suite is
frozen. Use blind arm labels and isolated Codex homes and worktrees. Both arms
receive the same model, reasoning effort, repository snapshot, task, budget, and
oracle, along with equivalent tool access and time limits. Prevent access to the
sibling arm, evaluator notes, prior reports, and hidden oracle. After launch use
zero implementation prompts: only neutral transport or infrastructure recovery
is allowed and must be mirrored and recorded.

Predeclare at least one out-of-diff system seam and one mechanical or behavioral
oracle. The oracle must test externally visible behavior rather than reward plan
wording. Freeze each arm's candidate and completion claim before unsealing the
oracle: freeze before unsealing is a hard gate. A blind evaluator scores the
frozen artifacts without knowing arm or workflow identity.

Run two or three pairs adaptively:

1. Reject the candidate on the candidate's first completion-blocking regression.
2. If the first pair succeeds, run a second pair on a different task shape.
3. If results split or remain inconclusive, run a third pair; otherwise stop at two.

Judge quality before cost. The candidate must be no worse than the current
version and must prevent at least one current-version false completion in the
micro suite or a holdout. One pair is directional, not causal, and cannot support
a release claim by itself.

For every arm record wall time and uncached input and output tokens separately;
do not substitute tool-output volume without labeling it as a proxy. If quality
is equal and either candidate cumulative cost exceeds current by 25 percent,
simplify and retest. If quality is clearly better but the excess is above 25
percent, do not publish or update the default without explicit user confirmation
of the tradeoff.

## Release gate

Keep the active installation on 0.2 while behavior validation is incomplete.
After the micro suite passes, set the candidate base version to `0.3.0`, use the
plugin-creator cachebuster helper, and rerun unit contracts, both validators, and
diff hygiene. Fresh review and paired holdouts apply to that exact committed,
versioned candidate.

Before changing the active installation, create a disposable isolated CODEX_HOME,
add the repository marketplace with the Codex CLI, perform a
marketplace install, and verify the exact manifest version. Start a fresh Codex
task and verify Skill discovery plus `$happycodex:happycodex` routing. Do not
hand-edit marketplace state. Delete only the disposable home after recording the
commands and results; never repair or overwrite preserved installations or
worktrees.

Release only when static checks, micro scenarios, exact complete-diff review,
adaptive pairs, cost policy, isolated install, and fresh-task discovery all pass.
Then update the active installation through the CLI. Otherwise retain 0.2 as the
default and report the open gate.
