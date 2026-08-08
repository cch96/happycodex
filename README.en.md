# HappyCodex

[简体中文](README.md)

*Open-source guidance for reliable high-risk engineering work in OpenAI Codex.*

HappyCodex freezes the outcome, boundaries, and completion conditions of risky
work in one short repository ExecPlan, then relies on Codex's native Plan, Git,
tests, diffs, and agents. It is not a controller, authority system, scheduler,
or retry engine.

## When to use it

Use HappyCodex for cross-system changes, public contracts, migrations,
persistence, concurrency, destructive or production effects, exhaustive
claims, and long work likely to cross context compaction.

Keep bounded, reversible local changes on the native Plan, tests, and diff.
Create an ExecPlan before the next risky write only when scope or risk grows.

## Install and invoke

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation, then invoke:

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## Core contract

- Keep at most one static ExecPlan per task. HappyCodex requires no extra
  control PRD or `run.md`. A durable product-design deliverable for an
  independent consumer may be an explicitly scoped product artifact; link its
  selected boundary from the ExecPlan instead of copying it.
- Native Codex sandboxing and approvals own technical permissions; the user's
  request defines intent. HappyCodex does not model or repeat those permissions.
  Reversible work needed for the Outcome proceeds in the active workspace.
- Require one writer at a time only for overlapping mutable paths or resources.
  One agent may write directly; other agents participate read-only when useful.
- Default to no review for reversible local work. Use at most one pre-challenge
  for hard-to-reverse architecture and one blocker-only final review for a
  public, external, irreversible, or otherwise high-risk candidate.
- Attempt each external effect once. Retry only after proving no effect. Stop
  mutation on a partial or ambiguous outcome, reconcile read-only, and return
  the uncertainty to the user.
- Keep secrets and raw events out of product bytes. Report baseline failures,
  skipped checks, workspace dirt, and required facts that remain `unverified`.

The ExecPlan stores only the request, Outcome, workspace or project boundary,
external resources and effects, baseline and allowed breaks, an optional design
decision, checks, done and stop conditions, and recovery. After compaction,
reconstruct current facts from the plan, Git, tests, and tools—never from a
mutable snapshot, phase history, or a reconciliation latch.

HappyCodex is portable, zero-config, and model-agnostic. It requires no custom
agent, pinned model, or pinned reasoning effort.

[See GitHub Releases for published versions and verification status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
