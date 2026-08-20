# `<task>` ExecPlan

This raw ExecPlan is a task artifact: keep it in a task-owned unversioned path, never stage it, and freeze its exact bytes for final review.
Record only stable authority. Amend affected statements in place only when a decision-changing fact changes Outcome, boundary, authority, effect, or stop; never append command output, attempt logs, live inventories, hash/review receipts, execution narration, or progress records. Derive live state from Git and tools.
Repository admission is separate: distill only a standalone maintained ADR/runbook/contract, release manifest, or incident record with a named post-task consumer, real-use breakage if removed, correctness without task history, and consumer-required provenance only.

## Request and Outcome

- Verbatim request/amendments: `<text>`
- Outcome: `<observable end state>`
- Done evidence: `<proof>`

## Boundary

- Workspace/source identity: `<root and baseline>`
- Authorization boundary: `<workspace/project or task-owned domain and effects>`
- Planned primary surfaces: `<ownership coordination>`
- Incidental footprint: `<allowed classes and classification stop>`
- Preservation: `<behavior, data, identity, state>`
- Exclusions: `<non-goals and forbidden effects>`
- Supported workflows: `<Outcome/preservation-derived consumer-reachable paths>`
- Writer overlap: `<overlapping paths, contracts, and effect resources>`

## Handoff

- Stable Outcome/boundary/Done: `<facts or unresolved items>`
- Fixed writer/current blockers: `<identity and blockers>`
- Authorized increments/exclusions: `<values>`
- Revision admission: `<decision-changing evidence or concrete blocker>`

## Baseline and breaks

- Baseline: `<command and accepted failures>`
- Allowed compatibility breaks: `<exact authorized breaks and effects, or none>`

## Consumer and candidate

- Consumer: `<consumer>`
- Input closure: `<direct, generated, transitive inputs; modes and deletions>`
- Native immutable freeze: `<identity>`
- Terminal admission: `<fresh no-history Exact-final and identity echo>`
- Repair/replacement budget: `<values>`

## External effects

- Effects: `<target, identity source, cap, observation, recovery; or none>`

## Checks and stops

- Required checks: `<Outcome/preservation-required consumer-native checks and commands; unavailable required paths remain unverified; heuristic, regex, synthetic, or cross-language proxies are advisory only; optional checks omitted or advisory>`
- Stop conditions: `<identity, scope, trust, effect, or required-coverage drift/unknown>`
- Recovery evidence: `<durably reachable candidate/effect/rollback evidence>`
