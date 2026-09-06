# HappyCodex

[简体中文](README.md)

*Reliability guidance for consequential and long-running work in OpenAI Codex.*

HappyCodex adds task boundaries, collaboration, review, and operation recovery
conventions while using Codex's native planning and implementation capabilities.
It is portable guidance; host permissions and actual results remain authoritative.

## How it helps

- Complete small coherent tasks directly; select models and subagents when an independent question or substantial work benefits.
- Keep bulky investigation with the child and return conclusions, evidence, and unresolved issues.
- Coordinate actual overlapping writes and use review proportional to risk and user requirements, avoiding a routine second review after a completed one.
- Preserve necessary facts across compaction; check targets and existing authority before shared, destructive, public, or paid operations.
- Inspect authoritative state after uncertain outcomes, preserve receipts, and avoid blind retries.

Version 2.0 uses native plans and notes as needed, replacing the fixed ExecPlan
template and default hooks. Model and effort choices follow available
configuration and task needs; the product does not pin model identifiers.

## Install and invoke

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation, then invoke:

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

Read the [HappyCodex Skill](skills/happycodex/SKILL.md) and, before a consequential
operation, its [operation and recovery reference](skills/happycodex/references/effects.md).

For cutover, use the new plugin and isolated configuration for new tasks. Update
personal roles separately if they still require the old sole Executor, fixed
grants, or per-edit intent/receipt protocol; plugin installation does not change
those roles. Preserve active tasks' ownership and recovery material. Starting a
new task does not authorize repeating an unresolved operation.

[See GitHub Releases for published versions and verification status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
