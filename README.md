# HappyCodex

HappyCodex is a lightweight reliability protocol for long-running and high-risk
Codex implementation. One fixed Executor writes; Root decides, reproduces, and
verifies. The boundary stays durable without replacing native Codex execution.

## When to use it

Use HappyCodex for cross-system changes, public contracts, migrations, persistence,
concurrency, destructive or exhaustive claims, and work likely to span compaction.
Clearly local low-risk edits should stay on the normal Native Plan/test/diff flow.

## Install

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation so it discovers the installed Skill.
Version 0.6 targets Codex 0.145 or newer.

## Use

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

For a qualifying task, HappyCodex separates three kinds of state:

- one repo-resident ExecPlan stores the durable completion contract;
- Native Plan stores only the current execution cursor;
- Git, tests, logs, and runtime observations store facts.

For every qualifying task, 0.6 uses this fixed routing:

- Explorer: `gpt-5.6-terra` at `high`, read-only.
- Challenger: `gpt-5.6-sol` at `high`, read-only.
- Executor: `gpt-5.6-sol` at `high`, the sole writer.
- Root decision and reproduction: `gpt-5.6-sol` at `max`, read-only.
- Exact-final review: `gpt-5.6-sol` at `max`, fresh isolated read-only session.

Pin model and effort explicitly at dispatch or through verified custom-agent profiles;
a role name alone is not proof. If the host cannot report the effective pin, HappyCodex
stops before writing. The same model may review, but the Root or Executor session may not.

Read-only exploration may run concurrently. Root grants exact writes to one recorded
Executor thread and verifies every receipt; a second or replacement writer is rejected.
For unattended continuation without Goal approval, HappyCodex asks once. It creates or
changes Goal only when you explicitly request it; declining keeps Native Plan active.

## What it adds

- an early durable contract for compaction-prone work;
- Root-first system-boundary discovery plus pinned Explorer and Challenger roles;
- typed claims that cannot be silently narrowed;
- one fixed Executor across vertical RED/GREEN milestones and recovery;
- exact product-tree review isolated from the ExecPlan and original history;
- honest completion only after evidence, scope, review, and ownership close.

The plugin adds no hook, controller, scheduler, daemon, app, MCP server, custom
persistence, or Task State JSON. Its runtime is one Skill, one ExecPlan reference,
and UI metadata.

## What's new in 0.4

Version 0.4 preserves the certified HappyCodex runtime behavior and public invocation.
It adds an auditable source-release boundary backed by content-addressed corpus and
holdout certification, strict authority/evidence chronology, and a zero-live
artifact/install transition.

## What's new in 0.4.1

Version 0.4.1 separates focused family hardening from neutral exact-final review.
It scopes the single writer to shared mutable resources, batches sibling findings by
invariant, makes review mode explicit in evaluator receipts, and keeps ExecPlans as
bounded current indexes with fail-closed recovery.

## What's new in 0.4.2

Version 0.4.2 reduces validation wall time without deleting behavior coverage.
Corpus evaluation uses at most four workers with stable result ordering; each adaptive
holdout pair runs its blinded candidate/public arms concurrently while pairs remain
serial. Live attempts are consumed atomically before dispatch so failures cannot reuse
the same approval, including across linked worktrees. Focused hardening defaults to
`high`; exact-final review remains `max`.

## What's new in 0.5

Version 0.5 is a narrow 0.4.2 successor. It fixes the GPT role matrix, makes one
Executor the only writer, keeps Root on decision/reproduction, and requires exact-final
review to use a different fresh session. It adds no compatibility reader, controller,
daemon, or second protocol.

## What's new in 0.6

Version 0.6 contracts the evaluator to one direct terminal protocol, one fixed
Executor, one audit-bound `EffectIntent` route, and a fresh ledger containing
only candidate, plan, and receipt records. Root/Host orchestration owns actual
authority; repository plans, approval digests, and intents bind exact content
but cannot grant permission or authenticate provenance. Calibration, corpus,
adaptive holdout, artifact receipt, exact-final review, isolated install,
publication, and activation remain distinct gates. The standalone model routes
are dry-run only unless the Host enters the authorized boundary with the exact
current plan and intents.

## What's new in 0.3

Version 0.3 is a clean-room replacement of the internal 0.2 workflow. It freezes a
durable system-boundary contract before implementation, restores execution from
repository facts after compaction, and isolates fresh review from the writer's plan
and conclusions. Public installation and `$happycodex:happycodex` invocation remain
unchanged.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```
