# HappyCodex

HappyCodex is a thin reliability Skill for complex Codex implementation work.
Codex's native plan, agents, Goal, Git workflow, compaction, tests, and review remain
the execution engine.

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

## Use

Invoke `$happycodex` for long, cross-cutting, public-contract, or compaction-prone
implementation. Goal creation still requires an explicit user request.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```
