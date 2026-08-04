# HappyCodex

[简体中文](README.md)

*Open-source skill and plugin for reliable long-running, high-risk engineering work in OpenAI Codex.*

HappyCodex is an open-source reliability workflow distributed as a Skill and
plugin for OpenAI Codex. It uses a repository ExecPlan to freeze completion
conditions; one fixed Executor performs controlled writes, while Root decides,
grants, reviews, and performs final verification. It does not replace Codex's
native Plan, Git, tests, or review.

## Suitable and not suitable

### Suitable

Use HappyCodex for public contracts, cross-system changes, migrations,
persistence, concurrency, destructive or production work, exhaustive claims,
long research, and work likely to cross compaction.

### Not suitable

Clearly local, low-risk edits should stay on the native Plan, tests, and diff
flow. If scope or risk grows, establish an ExecPlan before the next product
write.

<a id="install"></a>
## Install

Marketplace support is required.

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation so it discovers the installed Skill.

## Invoke

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## Four-phase workflow

1. `working`: freeze the request, Outcome, preservation boundaries, roles,
   exact grants, obligations, checks, effects, and stop conditions in the
   repository ExecPlan; implement one granted repair wave and run real-path
   checks.
2. `candidate_frozen`: account for all owned changes, evidence the obligations,
   preserve accepted baseline failures, and bind source, product, and
   configuration identities.
3. `exact_final`: give one fresh isolated read-only reviewer the frozen source,
   checks, obligations, and exclusions. Any product change returns to
   `working` and requires a new review.
4. `closed`: close only after obligations, checks, review, effects, receipts,
   ownership, and any explicitly requested Goal are all reconciled. Root makes
   the completion decision.

Goal is created or changed only when the user explicitly requests it. It never
expands authority and never replaces the ExecPlan or verification.

## What ships—and what does not

The package ships the core Runtime guidance and the resource-claim helper.
HappyCodex is not a controller, daemon, scheduler, MCP server, automatic
authority system, or automatic retry system.

HappyCodex bundles no model matrix or custom-agent profiles. User and Codex
configuration select available model and effort settings; the effective model,
effort, and permissions are recorded for each participant.

## 0.6.6 highlights

Version 0.6.6 focuses on material risks reachable through supported workflows.
It treats users, maintainers, local state, and selected configuration as
trusted but fallible; verifies state and identity rather than motive; prefers
the smallest sufficient control; and requires explicit user authority before
widening scope or trust boundaries.

[See GitHub Releases for full release history and validation status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
