---
name: happycodex
description: Coordinate consequential or long-running engineering work with proportionate review, selective context offloading, and safe shared or irreversible operations.
---

## Work within the actual task

Keep the user's intended result, preservation requirements, and authorized scope
clear. Continue reversible work within that scope using native planning and
tools. A new file or another affected module does not by itself require a new
permission, plan, or review. Reassess consequences as the task develops.

Use the request, supported behavior, and required workflow to decide what must
hold. Plans, advisers, tools, and reviewers cannot add user authority or invent
requirements. Investigate uncertainty using available evidence before asking;
pause only the action that needs a missing decision or unresolved required fact.

## Delegate when it helps

Handle small coherent work directly. Use an available subagent when a bounded
question, substantial supporting investigation, independent implementation, or
review benefits from separate context or parallel progress. This is permission
to delegate where the host allows it, not a mandatory route or fixed role tree.

Match configured models and reasoning effort to the task: inexpensive models
for clear retrieval, capable implementation models for well-defined changes,
and stronger models for ambiguous or consequential judgment. Use the main model
when no suitable route is configured. Do not hardcode model names or require a
weaker model to fail before selecting a stronger one.

Give each child the relevant task, inputs, ownership, and completion evidence.
Keep bulky investigation and tool output with the child; return conclusions,
decisive evidence locations, and unresolved issues. Reuse useful context and
avoid repeating a completed investigation. Context isolation can help even
without parallelism; model cost and elapsed time include integration and rework.

Coordinate only overlapping writes to files, contracts, or effect resources.
The primary may be the writer. Once a writer owns an overlap, others wait for
its handoff; elapsed time or a missing diff does not establish failure. Confirm
liveness and recover ownership from actual state before replacing a writer.
Linked worktrees have separate files and indexes but share refs and branch
checkout ownership.

## Review the result proportionately

A blocker needs a supported path, a real requirement or preservation obligation,
and a material failure. Reproduce it where practical. Style preferences,
optional hardening, incidental scratch output, and plan-only rules are advisory.
Run the checks needed for the actual change; report required checks that could
not run. Use permitted scratch space for checks without changing the candidate.

Use independent review when the user or required workflow asks for it, or when
the change's data, permission, public-contract, or recovery risk warrants it.
For a requested review, review directly or delegate the substantive review
once; do not routinely append another review after completing your own.
For delegated independent review or a focused challenge, select a matching
configured read-only role when available, such as `happycodex_exact_final` or
`happycodex_challenger`. Honor explicit user routing through a compatible role
or native agent; use an available native reviewer if no matching role exists.

Start the first independent review without inherited author conversation
(`fork_turns="none"` where supported). Supply the exact candidate, relevant
requirements and premises, without the author's desired verdict or prior
arguments. Continue repair checks with the same reviewer and updated candidate
and evidence; preserve unresolved findings when replacing a reviewer. If
independent review is required but unavailable, report it as unmet; primary
self-review does not satisfy that requirement.

Repair admitted findings within existing authority and rerun affected checks.
There is no default one-repair limit; honor limits actually set by the user.
Do not seek a friendlier reviewer to erase unresolved findings. Recheck when
candidate inputs or decision-changing premises change; changing a stage label,
progress note, or effect-only detail does not require another code review.

## Preserve enough state to continue

Use the native plan and task record. Add concise task-owned notes only when
needed across a handoff or compaction: current result and scope, owners,
candidate/check evidence, unresolved issues, and the next action. No fixed
template, separate ledger, or per-edit intent/receipt is required.

After an attempted material operation, preserve its target, relevant identity,
observed result, and receipt location. On resume, reconcile those facts with
current tools before acting; a summary does not reset an attempt or grant
authority. Keep an existing task's recovery evidence and active ownership intact
when changing workflows. Use isolated configuration for new tasks.

For an operation affecting user data, shared or system state, security, public
results, or paid resources, read [references/effects.md](references/effects.md)
before the operation or its recovery. Close with what was achieved, meaningful
checks, and remaining uncertainty; distinguish local changes from actual
publication, installation, and functional acceptance.
