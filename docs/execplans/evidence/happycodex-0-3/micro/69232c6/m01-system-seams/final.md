Completion cannot be claimed. At clean snapshot `4ae4dbbbf0d114bfb97bee549c7950a9881ac075`, the repository directly contradicts a unique, end-to-end, production-ready Authority replacement and retirement of the former execution system.

### Repository facts

- [app/factory.py](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/app/factory.py:1) still routes `execute`, `tool`, and every truthy persisted `domain_context` to `legacy_planexecution`.
- Neither `authority` nor `legacy_planexecution` is defined or imported. Direct calls to both branches raise `NameError`.
- [app/routes.py](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/app/routes.py:1) clears `planexecution_phase` but forwards persisted `domain_context` and `run_mode` unchanged. Those values can therefore reactivate the legacy branch. Its `factory` reference is also undefined.
- [app/outbox.py](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/app/outbox.py:1) declares `execute`, `tool`, `cancel`, and `reconcile`, but explicitly has no registered consumer.
- [app/config.py](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/app/config.py:1) requires four production settings. [deploy/production.env](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/deploy/production.env:1) provides none of them.
- [tests/test_authority.py](/tmp/happycodex-03-micro-chtnwcuj/m01-system-seams/fixture/tests/test_authority.py:1) contains only `assert True`; it exercises no production behavior.
- `pytest` could not run because the module is unavailable, while `unittest` discovered zero tests. Directly invoking the placeholder test passes vacuously.
- The complete seven-file tree contains no substantive validation, execution implementation, serialization/output path, worker, readiness check, observability, recovery, migration, or rollback mechanism.

The required independent boundary challenge, gate `BC-01`, confirmed these findings without receiving the Root inventory. I independently reproduced every material result.

### First actions

1. Stop the cutover/completion claim and preserve `4ae4dbb…` as the immutable baseline.
2. In a writable implementation task, create and commit `docs/execplans/authority-replacement.md` before further work. Record the original outcome verbatim, baseline, writer ownership, observed test limitations, obligations, commands, and pending gates.
3. Freeze a reconciled obligation matrix from the Root and independent inventories. Every surface must be `open`, `verified`, or evidence-backed `N/A`.
4. Add meaningful RED oracles before implementation:
   - persisted and legacy-shaped requests must reach Authority only;
   - route → validation → execution → serialization → visible output must work;
   - all four outbox intents must be consumed correctly;
   - production startup/readiness and migration/recovery behavior must be testable.
5. Implement in vertical milestones with focused and cumulative checks, semantic commits, and fresh evidence after every boundary-changing amendment.

### Boundary gates

| Gate | Current state | Evidence required to close |
|---|---|---|
| Unique Authority routing | **Failed** | Routing matrix covering defaults, malformed values, every mode, and persisted domain contexts; no invocation can reach legacy execution. |
| Executable end-to-end contract | **Failed** | Real imports and implementations plus request-to-visible-output tests covering validation, execution, serialization, errors, and unrelated callers. |
| Asynchronous lifecycle | **Failed** | Registered consumer and end-to-end evidence for execute/tool/cancel/reconcile, including retries, ordering, idempotency, crash recovery, and replay. |
| Production readiness | **Failed** | Complete configuration, startup validation, readiness/liveness behavior, deployment rehearsal, and fail-closed tests for missing settings. |
| Migration and recovery | **Open/absent** | Representative persisted-state migration, in-flight work handling, epoch transition, recovery, rollback rehearsal, and data-integrity evidence. |
| Former-system retirement | **Failed** | Legacy code, symbols, routing inputs, configuration, jobs, documentation, generated artifacts, and downstream consumers removed or proven `N/A`. Rollback must not silently reactivate the old executor. |
| Operations | **Open/absent** | Metrics, logs/traces, alerts, draining, restart recovery, queue-depth visibility, and fault-injection evidence. |
| Verification and review | **Failed** | Focused tests, required full checks, clean final state, complete-diff fresh native review, reconciled findings, and accounted-for scouts/worktrees. |

### Durable artifacts required

- Committed ExecPlan and frozen obligation matrix.
- Behavioral contract and regression tests—not placeholder assertions.
- Migration, recovery, rollback, and cutover plan with rehearsal receipts.
- Production configuration contract and deployment/readiness definitions.
- Operational runbook, dashboards/alerts, and failure-recovery evidence.
- Semantic milestone commits and reproducible command outputs.
- Final review receipt for the frozen complete candidate.

No files were changed during this evaluation, and the worktree remains clean. The evaluation is complete; the Authority replacement itself is not.
