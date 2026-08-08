# `<task>` ExecPlan

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome
- Verbatim request: `<request and authorized amendments>`
- Outcome: `<one observable end state>`
- Done evidence: `<facts that prove completion>`

## Workspace and change boundary
- Workspace: `<root and source identity>`
- Mutable paths/resources: `<exact paths, prefixes, or resource identities>`
- Preservation: `<behavior, data, identity, and state to keep>`
- Exclusions: `<non-goals and forbidden effects>`
- Supported workflows: `<consumer-reachable paths that must remain valid>`

## Baseline and allowed breaks
- Baseline: `<command and exact accepted failures>`
- Allowed breaks: `<intentional incompatibilities or none>`

Never call an accepted failing baseline green or accept a new failure silently.

## Consumer and candidate
- Consumer: `<who or what consumes the result>`
- Input closure: `<all direct, generated, and transitive inputs>`
- Native freeze: `<commit/tree, package, image, revision, or snapshot>`

## External effects

For each effect record: `<effect; target; identity source; attempt/size/cost
cap; observation predicate; recovery cap or none>`. If none, write `none`.

## Checks

- Required checks: `<focused real paths, cumulative suite, diff/state checks>`
- Terminal review trigger/brief: `<risk trigger; Done, preservation, supported workflows; or none>`

## Stops and recovery

Stop on scope, identity, index, trust, or source drift; a new failure; a
required unknown; or a partial/ambiguous effect. Retry only after authentic
proof of no effect and only within the recorded recovery cap.

After a continuity break, confirm the old writer cannot resume, reread this
plan, inspect Git/index/candidate/effect state, and rederive current facts.
