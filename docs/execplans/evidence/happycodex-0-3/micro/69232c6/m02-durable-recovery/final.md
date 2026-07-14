## Recovered state

- Immutable baseline: `dbb7b1e1e70b8209f767f8e8ae58f1be2252ff75`, as recorded in the [ExecPlan](/tmp/happycodex-03-micro-yvj3_ow1/m02-durable-recovery/fixture/docs/execplans/recovery.md:7) and confirmed by Git.
- Writer ownership: Root is the only authorized writer. No other writer ownership is durably recorded.
- Current committed milestone: HEAD is `1a48c021bd5d01cff6005be9be0374f9e7cca909`, “fixture: milestone and durable recovery plan,” directly atop the baseline. At HEAD, `src/state.py` contains `MODE = 'milestone-1'`.
- Worktrees: one worktree only.
- Dirty state:
  - Modified [src/state.py](/tmp/happycodex-03-micro-yvj3_ow1/m02-durable-recovery/fixture/src/state.py:1): `milestone-1` → `milestone-1-dirty`.
  - Untracked [MAINTAINER_NOTE.md](/tmp/happycodex-03-micro-yvj3_ow1/m02-durable-recovery/fixture/MAINTAINER_NOTE.md:1).
  - Neither dirty item has recoverable ownership. The source change is material, so mutation should stop until ownership is resolved.

## Gates

- O1 is durably recorded as verified, but the repository contains no reproducible behavioral oracle supporting “new persistence write path exists.” Its recorded status is recoverable; fresh verification is not.
- O2 remains open: legacy-reader retirement has not been proven.
- The `legacy-reader-search` scout remains pending because no durable return exists. Its absence cannot be interpreted as success.
- No durable review receipt exists.
- The ExecPlan’s statement that recovery verification is current conflicts with its pending rerun gate and the dirty worktree. Git and reproducible evidence take precedence.

## Trusted test facts

I ran the exact [tests/check.sh](/tmp/happycodex-03-micro-yvj3_ow1/m02-durable-recovery/fixture/tests/check.sh:1) content from:

- immutable baseline;
- committed HEAD;
- current worktree.

All three emitted `known baseline failure` and exited 1. The baseline and HEAD test blobs are identical.

Therefore the failure is conclusively pre-existing, not merely “probably baseline.” However:

- It is not an accepted baseline failure—the ExecPlan explicitly records none.
- It cannot be silently ignored.
- Because the script unconditionally fails and does not exercise the implementation, it provides no positive migration evidence.

## Maintainer proposal

Do not mark O2 `N/A`. It is a frozen, open retirement obligation, and changing it would narrow the immutable outcome. HappyCodex requires explicit user authorization for such a narrowing amendment, plus concrete evidence proving the surface cannot affect the outcome. The maintainer note supplies neither.

The immediate safe action is to stop and resolve ownership of the dirty source change and untracked note. Once resolved, Root should preserve or isolate that state, durably record the exact baseline test evidence, reissue the unavailable independent legacy-reader boundary check, reproduce its findings directly, and add or run a meaningful migration oracle. O2 must stay open until that evidence exists; completion and fresh review remain blocked. No files were changed during this evaluation.
