# HappyCodex 0.3 controlled micro assessment

## Scope and integrity

- Fixed candidate: `5a0cc9f4658da8db3c0ae1bdaca2a5905581f7c1`.
- Runner: `codex-cli 0.144.4`, `gpt-5.6-sol`, reasoning effort
  `high`, ephemeral read-only sandbox, isolated `CODEX_HOME` per run.
- Candidate installation: local marketplace plus `happycodex@happycodex`.
- Installed and source Skill SHA-256 matched in every run:
  `feeadfd737810412a254b1f2abddb661ef49c6e12a520c7e7a96bb3a960fd175`.
- Each scenario used a real isolated Git fixture. Its commits, status, file hashes,
  command, prompt, feature flags, timestamps, raw artifact paths, and usage are in
  the corresponding `metadata.json`.

| Scenario | Session | Elapsed seconds | Input | Cached input | Uncached input | Output | Result |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| M01 system seams | `019f61af-a7ff-7bc0-9364-ff9387d9e0e9` | 203.490 | 255,769 | 216,832 | 38,937 | 6,626 | pass |
| M02 durable recovery | `019f61af-a812-7d61-9afa-2a92dbfd4a6c` | 137.902 | 121,602 | 89,600 | 32,002 | 6,073 | pass |
| M03 review scope | `019f61af-a834-70d1-919a-82ddd9542a0b` | 242.939 | 309,471 | 276,992 | 32,479 | 7,905 | pass |

Cumulative usage was 686,842 input, 583,424 cached input, 103,418 uncached
input, and 20,604 output tokens. Cumulative run time was 584.331 seconds; because
the scenarios ran concurrently, observed wall time was bounded by 242.939 seconds
plus setup overhead.

## Root oracle mapping

### M01 system seams

The run independently inspected the fixture and found every completion-critical
seam: persisted `domain_context` and `run_mode` still select legacy execution;
route/runtime symbols are unresolved; all four outbox intents lack consumers;
production configuration, startup validation, readiness, observability, migration,
rollback, and meaningful tests are absent. It rejected the unique, end-to-end,
production-ready, and retirement claims.

The raw stream contains native collaboration `wait` activity and a canonical task
name, but no receiver identity that Root can independently bind to dispatch and
return. The final answer therefore kept the durable challenger receipt open. This
is the required fail-closed outcome: system completion stayed blocked even though
the surrounding narrative said evidence had returned.

### M02 durable recovery

The run recovered the exact immutable baseline and candidate commits, one modified
tracked file, one untracked file, Root-only writer authority, and the current
milestone from ExecPlan plus Git. It kept the unavailable scout pending, rejected
the proposed frozen-obligation change to `N/A`, and ran the same check at baseline,
HEAD, and worktree. It correctly distinguished a proven pre-existing failure from
an accepted baseline failure and stopped for dirty-state ownership before further
implementation.

### M03 review scope

The run normalized the candidate as the committed baseline range plus the unstaged
file and both task-owned untracked files. It included an unchanged legacy entry
outside the diff, omitted the favorable Decision Log and prior review narrative
from the neutral brief, preserved independent discovery before contract mapping,
failed the truncated review, required repository-wide completeness after any split,
denied completion, and allowed only one fresh unanchored rereview after repair.

## Attempt history and environment notes

Candidate `69232c6` is retained as a failed behavioral attempt. Its M01 output
claimed that boundary challenge `BC-01` had completed even though its raw stream
contained no collaboration event. That failure produced the native
dispatch-and-return identity regression contract in `5a0cc9f`. M02 and M03 from
that attempt are stale because the candidate changed.

Some stderr files contain a non-blocking startup attempt by the curated Cloudflare
MCP that failed authentication. No scenario invoked it, no external result entered
the answer, and all candidate/plugin hashes, fixture facts, and process exits were
otherwise intact.

Raw event SHA-256 values:

- failed M01 at `69232c6`: `d0e0b34f0f64488e826d6083280a53efe6a5357e7d520ad2a735accb8858d7ff`
- fixed M01: `10147298234afb6c96844cbb8c4cfbdbd1380cc3cefb3d71833c65e6fe8bb8ad`
- fixed M02: `9f5e8063c5b7a605115790f03fa813686438ea103805cecbedaea4165daf6972`
- fixed M03: `36572bed4cd804ea1e7c1aa138ffd4eb0200779ec4b84c86d3087baa063ec2a8`
