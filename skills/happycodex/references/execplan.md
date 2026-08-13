# `<task>` ExecPlan

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome
- Verbatim request: `<request and authorized amendments>`
- Outcome: `<one observable end state>`
- Done evidence: `<facts that prove completion>`

## Workspace and authorization boundary
- Workspace: `<root and source identity>`
- Authorization/change boundary: `<selected workspace/project, task-owned
  resources, and granted primary effects; never an exact realized-path list>`
- Planned primary surfaces: `<anticipated mutable paths/resources for ownership
  coordination; additions or relocations inside the unchanged boundary do not
  need per-path reauthorization, and do not imply old/shared deletion>`
- Incidental footprint: `<bounded additive reconstructible non-authoritative
  cache/tmp/log/compiled output; exclusions and unknown-classification stop>`
- Preservation: `<behavior, data, identity, and state to keep>`
- Exclusions: `<non-goals and forbidden effects>`
- Supported workflows: `<consumer-reachable paths that must remain valid>`
- Writer overlap: `<semantic mutable contracts and effect resources, including
  cross-repository surfaces, that share one writer>`

## Stability handoff
- Outcome/change boundary/Done: `<stable values or unresolved items>`
- Writer/current blockers: `<fixed Executor; current blockers or none>`
- Increments/exclusions: `<authorized increments; exclusions>`
- Revision admission: `<new decision-changing evidence or concrete current blocker>`

## Baseline and allowed breaks
- Baseline: `<command and exact accepted failures>`
- Allowed breaks: `<intentional incompatibilities or none>`

Never call an accepted failing baseline green or accept a new failure silently.

## Consumer and candidate
- Consumer: `<who or what consumes the result>`
- Input closure: `<exact complete direct, generated, and transitive consumer
  inputs at freeze, including modes, deletions, and byte identities>`
- Native freeze: `<commit/tree, package, image, revision, or snapshot>`
- Convergence review: `<advisory reviewers may be reused or followed up without
  a round cap; their output has no terminal authority>`
- Plan review identity: `<tracked immutable plan identity; GO validates the plan only>`
- Terminal admission identity: `<one fresh no-history Exact-final; one immutable
  consumer-native identity; strict GO/NOT_YET with identity echo>`
- Exact-final reuse: `<follow-up/message makes later output convergence-only;
  one fresh reviewer remains required>`
- Composite envelope: `<one immutable envelope binding every component identity>`

## External effects

For each effect record: `<effect; target; identity source; attempt/size/cost
cap; observation predicate; recovery cap or none>`. If none, write `none`.

## Checks

- Required checks: `<focused real paths during iteration; required cumulative
  or full suite after candidate scope is stable and before native freeze;
  diff/state checks; task-created temporary resources cleaned up or explicitly
  retained when applicable>`
- Terminal review trigger/brief: `<risk trigger; Done, preservation, supported workflows; or none>`
- Hook posture: `<optional, trust-dependent, bypassable guardrails or none>`

## Stops and recovery

Missing or unconfirmed native Goal identity, or a pending user decision, stops
autonomous mutation; never recreate or widen the Goal for continuity.

Stop on scope, identity, index, trust, or source drift; a new failure; a
required unknown; or a partial/ambiguous effect. Retry only after authentic
proof of no effect and only within the recorded recovery cap.

After a continuity break, confirm the old writer cannot resume, reread this
plan, inspect Git/index/candidate/effect state, and rederive current facts.
