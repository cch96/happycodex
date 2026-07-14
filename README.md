# HappyCodex 0.3

HappyCodex is a lightweight reliability workflow for long-running Codex
implementation. It helps complex changes keep their acceptance criteria across
exploration, implementation, compaction, and fresh review while Codex's native
plan, agents, Goal, Git, tests, and review remain the execution engine. It adds
instructions only: no hook, controller, daemon, or parallel writer.

Its state model is deliberately small: the ExecPlan stores the durable completion
contract, Native Plan stores the current execution cursor, and Git and tests store
facts. Goal is optional and only enabled when the user explicitly requests it.

## When to use it

Use HappyCodex for cross-cutting refactors, public-contract changes, migrations,
persistence or concurrency work, and tasks likely to span compaction. Skip it for
small localized edits where its evidence and review steps would cost more than the
risk they remove.

## Install

Add the GitHub marketplace, then install the plugin:

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation so the bundled skill is discovered.

## Use

Invoke it explicitly when you want the workflow:

```text
Use $happycodex:happycodex for this cross-cutting refactor. Preserve every acceptance
criterion and finish with fresh native review.
```

Goal remains optional. If you request unattended or automatic continuation without
selecting Goal, HappyCodex asks once; without approval, it continues with the native plan:

```text
Use $happycodex:happycodex with Goal for this compaction-prone migration.
```

### Optional Fable review

Native review remains the default. Opt in explicitly when you want an independent
second reviewer:

```text
Use $happycodex:happycodex with Fable 5 max review when available.
```

Fable defaults to `max`; a task or `AGENTS.md` may select another supported effort.
Both reviewers inspect the same frozen candidate independently, preferably in
parallel, and the Root reproduces their findings before editing.

## What it adds

- one Root writer and an immutable task baseline;
- an early committed ExecPlan with frozen obligations and acceptance evidence;
- an independent boundary challenger for exhaustive system claims;
- system-boundary coverage across entries, persisted routing, producers and
  consumers, workers, deployment, recovery, migration, and legacy paths;
- optional bounded read-only investigation with Root reproduction;
- vertical RED/GREEN milestones and semantic commits;
- compaction recovery from the ExecPlan, Native Plan, Git, and tests;
- two-stage fresh review: independent discovery first, frozen-contract mapping
  second, with at most one unanchored post-fix re-review;
- behavioral micro tests and blinded paired holdouts for workflow releases.

It adds no Agent runtime, scheduler, daemon, hook, MCP server, custom persistence,
or review implementation. Short localized work should remain in the Root.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

Version 0.3 replaces the narrower acceptance-evidence workflow with durable
boundary freeze, fact-based recovery, neutral staged review, and a measured
release gate. The release process keeps 0.2 active until those gates pass.
