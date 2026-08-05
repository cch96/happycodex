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

## 0.7.0 role routing

Version 0.7.0 defines this protocol-level routing matrix:

| Logical role | Model | Effort |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| Unique Executor | `gpt-5.6-sol` | `high` |
| Unique fresh Exact-final | `gpt-5.6-sol` | `max` |

Complete routing applies only when the host supports exact selectors and
runtime-issued metadata. Before dispatch, Root verifies itself as
`gpt-5.6-sol/max` and confirms the selector can request the target role, model,
effort, and `fork_turns = none` or a bounded positive integer. Root's
authenticated dispatch/tool receipt binds logical role, selected agent request,
requested model/effort or custom config SHA, fork, input baseline/candidate
identities, and prompt/brief digest; platform acceptance of the spawn completes
the dispatch receipt. The portable builtin/default path explicitly pins model
and effort. For a namespaced custom agent, its file's model and effort take
precedence; omit conflicting or redundant explicit arguments.

Spawn may start immediately. Runtime-issued session/turn metadata supplies the
actual platform/custom role or name when visible, effective model and effort,
effective sandbox/approval, and child/run/session identity; it need not echo
Root-owned logical role, fork, input identities, or prompt digest. Root admits
output only after cross-binding the dispatch receipt and runtime metadata.
Before admission, output cannot enter the behavior plan, trigger a write grant,
advance phase, or count as a final verdict. If either required source is missing
or the cross-bind mismatches, Root interrupts a still-running child, discards
the output, and fails closed.

Root first decomposes the problem into independent, decision-changing axes.
Multiple Explorers run concurrently only when multiple such axes exist, and
each Explorer answers one bounded question. Root reproduces and merges the
evidence; it never votes. Challenger works before the behavior-plan freeze;
only after that freeze does the unique Executor write. After candidate freeze,
start exactly one fresh Exact-final with empty history and a neutral brief. Any
repair returns to `working`, refreezes the candidate, and requires a new review.

## What ships—and what does not

The package ships the core Runtime guidance and the resource-claim helper.
HappyCodex is not a controller, daemon, scheduler, MCP server, automatic
authority system, or automatic retry system.

Plugin installation does not bundle, install, activate, or require custom
agents. Optional machine-local `happycodex_explorer`,
`happycodex_challenger`, and `happycodex_exact_final` profiles are only strict
or convenience profiles, do not replace built-ins, and are not a plugin
guarantee. Record logical role separately from platform agent type or
custom-agent name; a name, profile, or agent self-report is not routing
evidence.

Under a full-access parent task, a custom agent's
`sandbox_mode = "read-only"` may be overridden by the live parent. Profile
defaults and prompt instructions are therefore not hard technical isolation.
When hard read-only isolation is required, launch from a read-only top-level or
parent environment before dispatch, then verify the effective sandbox and
approval policy after the receipt arrives. Unverified output is inadmissible.

## 0.7.0 highlights

Version 0.7.0 adds host-capability-gated, receipt-admitted role routing while
preserving the four phases and smallest-sufficient-control boundary. This
describes a source candidate; it does not claim that 0.7.0 has been released or
activated.

[See GitHub Releases for full release history and validation status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
