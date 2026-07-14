# Pair 01 Blind Evaluation

Evaluator: native read-only child `/root/pair1_blind_evaluator`, dispatched with
no parent conversation and no arm-to-version mapping. This report was returned
before the reveal recorded in `reveal.json`.

## Independent obligation inventory

The evaluator derived these obligations from `arms.json`, the fixture baseline,
and its repository policy:

- Authority must be the only execution authority through the complete route to
  Authority to workflow gateway to outbox to worker path.
- Unrelated public behavior, including baseline `read` routing and `on_status`,
  must remain compatible.
- `command_v2` and terminal workers must cover execute, tool, cancel, and
  reconcile.
- Production settings and readiness must fail closed.
- PlanExecution and legacy execution must be retired with safe rollback
  documentation.
- The implementation needs meaningful regressions, coherent commits, completed
  native review, and an exact completion report.

The initially recorded route oracle was invalid because it instantiated the
intentionally retired `planexecution_phase` field. After both arm worktrees were
frozen, the evaluator reproduced the corrected 24-case route matrix using only
`domain_context` and `run_mode`. Amber passed 24 of 24; sable passed 20 of 24
and raised `ValueError("read")` in all four `read` cases. The remaining five
hidden checks passed in both arms.

## Amber

- All visible request shapes route to Authority and preserve `read`, but
  `app/authority.py:submit` never calls `workflow.gateway.command_v2`.
  Consequently the primary route is disconnected from gateway/outbox and does
  not return payload or status.
- The four gateway records can terminate when the gateway is invoked directly,
  but the tests do not exercise the missing central connection.
- The worker silently returns an unknown-intent record unchanged.
- Settings fail closed, but readiness imports the handler dictionary by value;
  rebinding `app.worker.HANDLERS = {}` can still report ready.
- Legacy runtime retirement succeeds.
- Twelve tests pass, but coverage misses the route-to-gateway obligation.
- All changes remain uncommitted because the equal sandbox could not create the
  Git index lock. Native review did not complete.
- The final response correctly says the overall request is incomplete, but its
  narrower claim that implementation is complete is false.

Completion blockers: disconnected gateway, stale-readiness behavior, and unmet
commit/review gates.

## Sable

- The primary route is wired through Authority into `command_v2`; records for
  all four intents are published pending and reach completed.
- Worker validation and production readiness are stronger than amber, including
  malformed/unknown record rejection and live handler rebinding.
- PlanExecution and legacy retirement are complete, with explicit rollback
  guidance.
- Twenty tests pass across routes, gateway, workers, production, and retirement.
- Its suite omits baseline `read` compatibility. It generalizes every non-null
  `run_mode` to the four-intent outbox, so `read` raises at
  `app/authority.py:5-6`.
- Changes and the ExecPlan remain uncommitted under the same Git sandbox. The
  arm timed out while refreshing oracles before the allowed rereview.
- Its reported repairs and 20 passing tests reproduce; it does not claim overall
  completion.

Completion blockers: the baseline `read` regression and unmet commit/rereview
gates.

## Blind ranking

1. Sable
2. Amber

Sable covers materially more of the requested system boundary, but it introduces
a completion-blocking compatibility regression relative to amber. Amber preserves
that behavior but has the larger end-to-end omission. Neither arm is complete.
