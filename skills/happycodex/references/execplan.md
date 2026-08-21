# `<task>` ExecPlan

This raw ExecPlan is a task artifact with one Candidate Review Body (`Request and Outcome` through `Checks and stops`) and one `Next-effect Binding`. Keep both in one task-owned unversioned path, never stage them, and freeze their exact bytes as one complete envelope.
Record only stable authority and current binding facts. After candidate `GO`, Body or Candidate-review tuple drift/uncertainty invalidates review; refresh only effect fields. Never append command output, attempt logs, live inventories, hash/review receipts, execution narration, or progress records. Derive live state from Git and tools.
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
- Review premises: `<environment or external facts whose change could alter code-review validity>`
- Native immutable freeze: `<identity>`
- Repair/replacement budget: `<values>`

## Checks and stops

- Required checks: `<Outcome/preservation-required consumer-native checks and commands; unavailable required paths remain unverified; heuristic, regex, synthetic, or cross-language proxies are advisory only; optional checks omitted or advisory>`
- Stop conditions: `<identity, scope, trust, effect, or required-coverage drift/unknown>`
- Recovery evidence: `<durably reachable candidate/effect/rollback evidence>`

## Next-effect Binding

- Candidate review tuple: `<verbatim native Exact-final verdict plus exact Body/candidate identity; fixed across Binding refresh; unavailable/mismatched native result rereviews; grants no effect authority>`
- Next effect: `<only the immediate material effect and target; or none>`
- Current binding: `<source/current identity, cap or cost, observation, rollback, and direct user authority>`
- Derivation/provenance: `<proof that the proposed artifact derives from the reviewed candidate; or unavailable stop>`
- Admission: `<compose exact reviewed Body with this Binding; mismatch stops and binding-only drift does not rereview code>`
- Later effects: `<ordered outline only; bind each separately when it becomes next>`
