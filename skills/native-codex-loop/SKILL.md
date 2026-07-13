---
name: native-codex-loop
description: Use when executing a long, multi-phase, repository-wide, high-risk, or compaction-prone implementation where omitted requirements, unsafe delegation, stale plans, or premature completion are plausible.
---

# Native Codex Loop

## Invariants

Keep the root thread as the only writer. Use Goal, native plan state, Git, tests,
bounded non-writing delegation, and an isolated review as separate controls. A plan or
an agent saying “done” is not completion evidence.

## Start contract

1. Read applicable `AGENTS.md`, the task/spec, repository state, baseline failures, and
   exact verification commands.
2. Use Goal only when the user explicitly requested Goal-backed execution. Call
   `get_goal` before creating or binding one. If an active Goal belongs to
   another objective, do not create, update, or complete it; report the conflict. Make a
   new Goal objective measurable.
3. Read the Task Contract shape in `references/packets.md`. Before edits, create it with
   mode `0600` outside the candidate repository. Freeze the objective, acceptance
   criteria, exclusions, exact task-baseline commit, repository/worktree, stop
   conditions, criterion-to-verification map, matching Goal thread ID, and SHA256 of the
   exact UTF-8 Goal objective bytes (`none` values when Goal was not requested). Record
   its absolute path and SHA256 in native plan. Never rewrite frozen text; append a
   versioned, user-authorized scope addendum and update the hash when scope truly changes.
4. If user changes already exist, preserve them. Work in a root-owned isolated worktree
   when that is safe; otherwise stop rather than manufacture an ambiguous base/head.
5. Create a short native plan. Do not require an ExecPlan file. Treat the plan as a live
   decision record, not a script or a substitute for acceptance criteria.

## Evidence loop

Repeat until the completion gate passes:

1. Select the smallest step that can produce decisive evidence.
2. Test first when behavior changes, then let only the root edit.
3. Run focused verification, inspect the diff, and compare observed behavior with the
   frozen Task Contract and every affected criterion.
4. Update the plan when evidence changes the best next action. Never silently lower,
   remove, or reinterpret an acceptance criterion.
5. Commit coherent checkpoints when they materially improve recovery or review.

After compaction or resume, verify the Task Contract hash, call `get_goal` and compare the
bound Goal thread/objective, inspect the native plan, `git status`, recent commits, live
agents, and latest test/review receipts before acting. Do not repeat completed or in-flight
work. A mismatch stops execution; do not reconstruct missing criteria from memory.

## Delegation router

Read `references/packets.md` before delegation. Delegate only when all are true:

- the work is investigative and has no mutable deliverable;
- its result can change a named decision or verification gate;
- a complete packet fits the inputs and output contract;
- integration costs less than root execution.

Built-in children inherit runtime capabilities; never point one at the candidate worktree
or its shared Git common directory. This is a policy boundary, not read isolation: require
every child command to name the disposable clone as its workdir and prohibit source paths.
Before dispatch, fingerprint candidate `HEAD`, refs,
index/worktree binary diffs, local config/hooks/worktree registrations, untracked files,
and task-relevant ignored/external paths. Create a separate disposable head-only clone,
remove its remote, verify its clean HEAD, and give the child only that path. Use a direct
child with `fork_turns="none"`, send the complete packet, prohibit recursive delegation,
prohibit edits and recursive delegation, and never delegate implementation. If a child
or tool mutates its clone, discard the result as a boundary failure. The root does not
edit while a child is live. After return, discard
the clone and compare the source/common-dir fingerprint. On a change, stop and preserve
evidence. After resume, inspect live agents before redispatching work.

Parallelize only packets that cannot affect one another. Subagent findings are advisory:
the root verifies them before changing the plan or code.

## Independent review gate

Any run of this Skill that changes a task-owned repository artifact requires review
before completion. The only no-review outcome is a verified unchanged HEAD/worktree:

1. Run required checks, self-inspect the full task diff, create a clean candidate commit,
   and atomically create a mode-`0600` factual review packet outside the repository.
   Record the frozen task-baseline/head SHAs, inline the exact Task Contract and its
   SHA256, and keep every required top-level packet field unique. Never substitute a
   later checkpoint as `--base`.
2. Locate this loaded Skill's plugin root (two directories above its Skill directory).
   Run `python3 <plugin-root>/scripts/review_runner.py` with `--repo`, `--base`, `--head`,
   `--packet`, `--task-contract`, and `--source-codex-home`. The runner derives one
   canonical series from the repository and frozen baseline. Record its absolute
   `series_file`, baseline, Task
   Contract hash, and source-packet hash in the native plan. Do not replace it with an
   in-thread self-review.
3. Count every started invocation, including failures, in that canonical series. After
   resume, recover the path from the plan and read `series.json` before review. Require
   the final attempt in `series.json` to be `succeeded`; never fall back to an older
   receipt after a failed attempt. Require that final attempt's `receipt.json` to report `ok`, the
   exact baseline/head, Task Contract SHA256, and task-packet hash, `gpt-5.6-sol`, `max`,
   `read-only`, approval `never`, network `restricted`, and unchanged source/review tree
   hashes. Also require the restricted-profile preflight and Linux PID-namespace
   containment fields. Read `review.md`; absence or mismatch fails the gate.
4. Have the root independently reproduce each finding and record the disposition format
   from `references/packets.md`. Fix only confirmed findings, add a regression test when
   applicable, and rerun focused plus full checks.
5. If any task-owned artifact, Task Contract/addendum, or source packet changes after the
   first review, recompute both hashes and run a second fresh invocation. Allow at most
   two review invocations in the default series. If the second review supports another
   material change, record dispositions, report the unreviewed residual state, and stop
   instead of claiming completion or manufacturing a new series identity.
6. A later, explicit user approval may authorize one post-fix series. Preserve the
   original Task Contract bytes and append the exact append-only addendum from
   `references/packets.md`; never infer approval from a request to continue. Bind the
   addendum to the exhausted canonical parent `series.json`, its final receipt, prior
   reviewed head, and all confirmed finding IDs. Invoke the runner once with
   `--escalate-from-series <parent-series.json>`. Require the returned escalation
   provenance to match those hashes. The runner allows one escalation generation, caps
   it at two attempts, and rejects recursive escalation. If that series is exhausted,
   stop with residual risk; no global or path-based bypass is permitted.

The final `HEAD` must exactly equal the head in the final succeeded attempt's receipt. If
the runner is unavailable, not fresh, not max/read-only, exposes forbidden capabilities,
cannot prove an unchanged tree, finds credential bytes anywhere reachable from `HEAD`,
or returns a finding outside a changed new-side hunk, stop and report the failed gate.

## Completion gate

Before any completion claim, require fresh evidence for all of:

- every acceptance criterion maps to code and/or a verification result;
- required full and task-specific checks have acceptable exit codes;
- if review ran, every finding is fixed or rejected with evidence and no material finding is unresolved;
- every deliverable is tracked and committed; V1 does not permit ignored or external
  files as task-owned deliverables;
- if this run changed review-gated artifacts, recompute the current Task Contract and
  source-packet hashes and require them, `HEAD`, and task-owned state to equal the final
  succeeded attempt's receipt;
- the candidate worktree is clean; a genuine no-change result has fresh inspection/check evidence and does not reuse an old receipt;
- no delegated task, worktree, known material risk, or baseline deviation is unaccounted for.

Immediately before `update_goal`, call `get_goal` again. Only when its Goal thread ID,
objective hash, and active status exactly match the Task Contract may you call
`update_goal(status="complete")`. Never complete an unrelated/replaced Goal, or complete
merely because tests are green, the clock is low, or an agent declared success.

## Red flags

| Thought | Required response |
| --- | --- |
| “The tests are green, so review adds nothing.” | Tests and semantic review catch different failures; run the gate. |
| “Multi-agent was enabled, so review happened.” | Require an actual fresh `receipt.json`. |
| “The plan says this is done.” | Reconcile it with code, tests, criteria, and receipts. |
| “The reviewer probably meant…” | Reproduce the exact claim before editing. |
| “A tiny post-review fix needs no re-review.” | Final `HEAD` must equal the reviewed head. |
| “One more loop cannot hurt.” | Stop after two review invocations and report residual risk. |
| “I can point at a new directory for another review.” | Only explicit user approval plus the bound addendum can create one non-recursive escalation. |
