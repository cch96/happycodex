---
name: happycodex
description: Use for high-risk, cross-system, destructive, public-contract, migration, persistence, concurrency, exhaustive, long-running, or compaction-prone Codex work that needs a durable execution boundary.
---

# HappyCodex

Use HappyCodex as portable guidance around native Codex plans, Git, tests,
diffs, and agents. Do not turn it into a controller, ledger, scheduler,
authorization system, or retry engine.

## Qualify the work

Keep bounded, reversible, local work on the native Plan, tests, and diff. Use
one repository ExecPlan when work is high-risk, cross-system, destructive,
public-facing, hard to reverse, or likely to cross context compaction. If local
work grows into those conditions, write the plan before the next risky edit.

Treat the user, workspace, maintainer, and selected configuration as
non-adversarial but fallible unless evidence says otherwise. Verify relevant
identity and state. Prefer the smallest control that protects the real risk.

## Freeze one static ExecPlan

Copy `references/execplan.md` to the repository policy path or
`docs/execplans/<task-slug>.md`. Keep exactly one plan for the task. Record only:

- the verbatim request and normalized Outcome;
- the workspace or project boundary, external resources and effects,
  preservation, and exclusions;
- baseline failures and allowed breaks;
- checks, done conditions, stop conditions, and recovery steps; and
- an optional design decision when the work creates a durable external
  contract with an independent consumer.

Do not use a separate PRD or `run.md` as a HappyCodex control record. A durable
product-design deliverable for an independent consumer may remain an explicitly
scoped product artifact. Keep Outcome, workspace, and external-effect
boundaries in the one ExecPlan; record only the selected boundary and artifact
link, never its full text. Do not store mutable NOW state, phase history, prompt
digests, or review history. Reconstruct live state from Git, tests, tools, and
the native plan. Keep evaluator or maintenance bytes outside product guidance.

## Use native permissions and bound effects

Use native Codex permissions; do not model or repeat them in HappyCodex. Within
the active workspace, perform reversible work needed for the Outcome and derive
changed paths from Git at closure. An allowed capability does not add work
outside the user's request.

If completion requires a materially different Outcome or an unrequested
external, destructive, or costly effect, return that decision to the user.

Never persist secrets or raw events in product bytes. If durability is required
while commits are forbidden, keep the index untouched and stop until the user
selects a reachable ref, content-addressed archive, or other durable
location. Never claim durability from an uncommitted working tree alone.

Attempt each external effect once. Retry only after proving the prior attempt
ended before the effect. On a partial or ambiguous effect, stop all mutation,
inspect read-only state, and return the exact uncertainty to the user. Do not
add a latch, recovery controller, compatibility reader, migration, or dual
write to encode that stop.

## Write and recover simply

Allow only one writer at a time for overlapping mutable paths or resources. A
single agent may write directly. Use additional agents read-only when their
independent evidence can change a decision; do not require custom agents,
specific models, effort levels, host handles, or optional telemetry.

After compaction, reread the whole ExecPlan, inspect live Git and external
state, identify every owned change, and rerun the checks needed to recover
current facts. Treat summaries as hints, not authority or state. Stop on
workspace, source, index, effect, or trust-boundary drift.

Run focused real-path checks during implementation and the cumulative relevant
suite before closure. Report accepted baseline failures exactly; never call a
suite green when they remain. Account for staged, unstaged, and untracked dirt,
effects, skipped checks, and required facts that remain unverified.

## Review in proportion to risk

Use no mandatory review for reversible local work or work whose only added risk
is compaction. Use at most one read-only pre-challenge when the decision shapes
architecture and is hard to reverse. Run at most one fresh blocker-only final
review for a public, external, irreversible, or otherwise high-risk candidate.

Give a final reviewer the frozen Outcome, envelope, accepted baseline failures,
checks, and exclusions without prior findings or a desired verdict. Admit only
a reproduced failure of a frozen obligation or a candidate-new material safety
or correctness regression reachable through the frozen workflow. Do not block
on style, naming, optimization, alternative designs, speculative hardening,
unfrozen tests, or unrelated pre-existing issues.

A reproduced in-envelope blocker may trigger one coherent repair and one fresh
replacement final review. After that, any blocker or required unknown stops and
returns to the user. Reviews cannot change the Outcome or envelope, create new
obligations, or justify reruns of unchanged bytes.

## Close truthfully

Finish only when the Outcome and preservation rules hold, required real paths
pass, accepted failures are unchanged, all dirt and effects are accounted for,
and no required unknown remains. Disclose skipped or unverified gates and
out-of-envelope uncertainty. Do not infer publication, installation,
activation, or other external success without direct verification.
