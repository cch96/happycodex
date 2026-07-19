# HappyCodex

HappyCodex is a lightweight reliability protocol for long-running and high-risk
Codex implementation. It keeps the system boundary and acceptance contract durable
without replacing Codex's native plan, agents, Goal, Git, tests, or review.

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

## Use

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

For a qualifying task, HappyCodex separates three kinds of state:

- one repo-resident ExecPlan stores the durable completion contract;
- Native Plan stores only the current execution cursor;
- Git, tests, logs, and runtime observations store facts.

Root remains the only writer. Read-only challengers and reviewers provide independent
counterexamples. For unattended continuation without Goal approval, HappyCodex asks once;
it creates or changes Goal only when you explicitly request it. Declining keeps Native Plan
active. Otherwise an existing Goal is only an objective pointer and cannot silently override
a different ExecPlan Outcome.

### Optional Fable review

Request an independent external review explicitly:

```text
Use $happycodex:happycodex with Fable 5 max review when available.
```

The external reviewer receives the same frozen synthetic product scope and neutral
brief as native review, never the writer's preferred verdict. Fable 5 at `max` is the
default absent an exact user or scoped-policy override. Root reproduces the union of
findings without voting. A required unavailable reviewer stops completion; “when
available” permits a disclosed skip.

## What it adds

- an early durable contract for compaction-prone work;
- Root-first system-boundary discovery plus one fresh challenger for strong claims;
- typed claims that cannot be silently narrowed;
- vertical RED/GREEN milestones and fact-based recovery;
- exact product-tree review isolated from the ExecPlan and original history;
- honest completion only after evidence, scope, review, and ownership close.

The plugin adds no hook, controller, scheduler, daemon, app, MCP server, custom
persistence, or Task State JSON. Its runtime is one Skill, one ExecPlan reference,
and UI metadata.

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
