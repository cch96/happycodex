# HappyCodex

[简体中文](README.md)

*Open-source guidance for reliable high-risk engineering work in OpenAI Codex.*

HappyCodex keeps high-risk task facts in a task-local, unversioned ExecPlan,
binds its full bytes to a consumer-native immutable candidate identity for
final review, and observes each external effect after one attempt. It is
portable guidance, not a controller, authority system, ledger, scheduler, or
retry engine.

## When to use it

Use it for cross-system changes, public contracts, migrations, persistence,
concurrency, destructive or production effects, exhaustive claims, and long
work likely to cross context compaction. Keep bounded reversible local work on
Codex's native Plan.

## Install and invoke

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation, then invoke:

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

The Skill's flow is:

1. Record the Outcome, authorization boundary, consumer, effects, checks, and
   stop facts in a task-local unversioned ExecPlan.
2. Route a scout, supporting body, or worker to the smallest bounded native agent while keeping one writer per overlap.
3. Freeze the complete consumer input closure as an immutable Git tree, package, image, revision, or equivalent identity.
4. Give a high-risk candidate one fresh no-history blocker-only Exact-final review; attempt each effect once.
5. Close truthfully as achieved, not achieved, or unknown.

Raw ExecPlans stay out of product Git; durable knowledge is separately
distilled into an ADR, runbook, or contract with a named post-task consumer.

Read the [HappyCodex Skill](skills/happycodex/SKILL.md) for the exact authorization,
delegation bridge, advisory stop, candidate freeze, review, and effect rules.

[See GitHub Releases for published versions and verification status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
