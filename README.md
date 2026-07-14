# HappyCodex

HappyCodex is a small Codex plugin for long or cross-cutting implementation
work. It packages one Skill; Codex's built-in Goal, plan, agents, Git workflow, tests,
compaction recovery, and native review remain the execution engine.

## What it adds

- one Root writer and a concise working agreement;
- conditional, orthogonal read-only scouts for genuinely independent unknowns;
- Root reproduction of scout evidence and evidence-driven replanning;
- RED/GREEN implementation slices with useful Git checkpoints;
- fresh factual native `codex review`, preferring GPT-5.6-sol max and allowing only a
  disclosed authorized fallback at or below max, followed by at most one post-fix
  re-review against the same baseline;
- recovery from Goal, native plan, Git, tests, and review results.

It adds no custom agent runtime, scheduler, daemon, hook, MCP server, review process, or
persistence layer. Short, localized work should stay in the Root without delegation or
Goal overhead.

## Use

Invoke `$happycodex` for work that is multi-phase, likely to cross compaction, or
wide enough that independent contract and consumer tracing can reduce omissions. Goal
creation still requires an explicit user request.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

The Skill deliberately relies on the installed Codex CLI's native review surface rather
than maintaining a second review implementation.
