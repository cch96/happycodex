Implementation is complete and verified in the worktree, but the overall request is not fully complete because the environment blocked commits and native review.

Implemented:

- All requests now dispatch exclusively through Authority; failures cannot fall back: [factory.py](/tmp/hc-holdout-amber-71yrfdxp/repo/app/factory.py:1)
- Removed PlanExecution request state and deleted `app/legacy.py`: [types.py](/tmp/hc-holdout-amber-71yrfdxp/repo/app/types.py:4)
- Added the four-intent v2 command gateway: [gateway.py](/tmp/hc-holdout-amber-71yrfdxp/repo/workflow/gateway.py:4)
- Registered callable workers for every Authority intent: [worker.py](/tmp/hc-holdout-amber-71yrfdxp/repo/app/worker.py:4)
- Added fail-closed startup validation and readiness: [settings.py](/tmp/hc-holdout-amber-71yrfdxp/repo/deploy/settings.py:3), [readiness.py](/tmp/hc-holdout-amber-71yrfdxp/repo/ops/readiness.py:6)
- Completed production configuration with deployment-time secret injection.
- Added comprehensive regressions: [test_authority_cutover.py](/tmp/hc-holdout-amber-71yrfdxp/repo/tests/test_authority_cutover.py:17), [test_production.py](/tmp/hc-holdout-amber-71yrfdxp/repo/tests/test_production.py:13)

Verification evidence:

- Baseline: `0635866d4de3acf9e19a3251d549cba513536386`, initially clean.
- RED confirmed: missing `command_v2` caused the intended import failure.
- Final tests: 12/12 passed.
- All 17 Python sources compiled.
- All 13 runtime modules scanned with zero PlanExecution or legacy references.
- Production configuration rejects a missing worker secret and accepts an injected one.
- `git diff --check` passed.
- No accepted baseline failures; Fable was not used.

Blocked gates:

- `.git` is read-only, so Git cannot create `index.lock`; HEAD remains unchanged and no requested milestone commits could be created.
- Native review selected `gpt-5.6-sol` at `max`, but both WebSocket and HTTPS connections to the Codex backend were prohibited. The CLI exhausted retries and exited with “Review was interrupted.” No review findings were produced.

The worktree contains exactly 11 intentional tracked changes, including the legacy-module deletion, plus the two new regression files.
