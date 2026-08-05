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
3. `exact_final`: give one fresh logically read-only reviewer the frozen source,
   checks, obligations, and exclusions. Technical read-only isolation applies
   only when predeclared required. Missing optional route or permission telemetry
   alone does not block review and is disclosed. Any product change returns to
   `working` and requires a new review.
4. `closed`: close only after obligations, checks, review, effects, receipts,
   ownership, and any explicitly requested Goal are all reconciled. Root makes
   the completion decision.

Goal is created or changed only when the user explicitly requests it. It never
expands authority and never replaces the ExecPlan or verification.

## 0.7.2 capability-proportional admission

Version 0.7.2 uses capability-proportional admission with this requested routing
matrix:

| Logical role | Model | Effort |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| Unique Executor | `gpt-5.6-sol` | `high` |
| Unique fresh Exact-final | `gpt-5.6-sol` | `max` |

Normal users choose no mode and enter no continuation phrase. Before dispatch
and before substantive output is read, Root records the role, intended
consequence, requested route/config/fork, input identities and prompt digest,
and any guarantee required by the task, source, or user. Platform acceptance of
the exact request and a host-authenticated child/run/result handle are always
required. Missing output identity is never optional.

Missing optional telemetry records `unverified` and reduces only the guarantee
or use that depends on it. A missing effective name is record-only. Missing
model/effort permits continued use unless exact routing was predeclared
required; missing sandbox/approval permits continued use unless technical
isolation was predeclared required and cannot be independently established. An
exposed mismatch or a missing predeclared guarantee stops. Prompt/profile
read-only remains non-proof, and full access mismatches only a predeclared
read-only technical-isolation guarantee. Unverified exact routing or technical
isolation is never claimed.

Root first decomposes the problem into independent, decision-changing axes.
Multiple Explorers run concurrently only when multiple such axes exist.
For two or more qualifying independent decision-changing axes, Root
concurrently dispatches one native Explorer per axis through the host's builtin
`explorer` selector or an admitted namespaced custom Explorer selector.
Ordinary parallel tool calls are not Explorer dispatches. Each Explorer answers
one bounded question. Unverified Explorer or Challenger output supplies
advisory leads only; Root reproduces every material fact from source before it
affects a plan, grant, or phase. Challenger works before the behavior-plan
freeze. Executor writes remain governed by its fixed identity, exact grant,
source/prestate, paths/resources, and allowed effects; Root trusts Git, tests,
and receipts rather than prose. Exact-final can count under unverified optional
telemetry only for a fresh empty-history neutral review of an unchanged
candidate, when exact routing and hard isolation were not predeclared required,
output identity is bound, Root reproduces material findings, and unverified
guarantees are disclosed. Required but unproven hard isolation leaves review
open. Any repair returns to `working`, refreezes the candidate, and requires a
new review.

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
parent environment before dispatch, then verify effective permissions or bind
an independently established no-effect boundary. Otherwise stop. When hard
isolation was not required, record missing permission telemetry as `unverified`
and continue without claiming isolation.

## 0.7.2 highlights

Version 0.7.2 replaces blanket runtime-metadata admission with proportional use
while preserving strict output identity, mismatch, authority, drift, required
guarantee, and effect boundaries. It preserves native Explorer dispatch for
multiple qualifying axes, the four phases, and the smallest-sufficient-control
boundary. This describes a source candidate; it does not claim that 0.7.2 has
been released or activated.

[See GitHub Releases for full release history and validation status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
