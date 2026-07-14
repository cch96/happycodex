# HappyCodex

HappyCodex is a lightweight reliability workflow for long-running Codex
implementation. It helps complex changes keep their acceptance criteria across
exploration, implementation, compaction, and fresh review while Codex's native
plan, agents, Goal, Git, tests, and review remain the execution engine.

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
- explicit acceptance evidence and baseline-failure accounting;
- coverage of contract propagation, adversarial compatibility, and residual
  consumers without prescribing an Agent count;
- optional bounded read-only investigation with Root reproduction;
- RED/GREEN implementation and evidence-driven replanning;
- fresh complete-diff native review with at most one unanchored post-fix re-review;
- recovery and completion reconciliation against native state and Git.

It adds no Agent runtime, scheduler, daemon, hook, MCP server, custom persistence,
or review implementation. Short localized work should remain in the Root.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```
