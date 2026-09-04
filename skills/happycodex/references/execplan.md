# `<task>` ExecPlan

This raw ExecPlan is a task artifact with one Candidate Review Body (`Request and Outcome` through `Checks and stops`) and one `Next-effect Binding`. Keep both in one task-owned unversioned path, never stage them, and freeze their exact bytes as one complete envelope.
Record only stable authority and current binding facts in this fixed-shape plan; retain its headings and replace current values in place. After candidate `GO`, Body or Candidate-review tuple drift/uncertainty invalidates review; refresh only effect fields. Never append command output, dated/history/receipt sections, attempt or execution logs, live inventories, hash/review receipts, execution narration, or progress records. Derive live state from Git and tools.
Record each opaque identity once in its named native slot; other fields reference that slot. Plan literals are review evidence, not effect operands. Capture the identity once from its native tool into a machine carrier; effect commands use only that carrier. Later live derivations compare against the frozen value; mismatch stops without rebinding.
For Git, record each predicate status separately (`0=true/1=false/>1=error`); never infer it from a wrapper exit. Distinguish target ref, cached remote-tracking ref, live remote observation, and checkout owner.
Repository admission is separate: distill only a standalone maintained ADR/runbook/contract, release manifest, or incident record with a named post-task consumer, real-use breakage if removed, correctness without task history, and consumer-required provenance only.

## Request and Outcome

- Verbatim request/amendments: `<text>`
- Outcome: `<observable end state>`
- Done evidence: `<proof>`

## Boundary

- Workspace/source identity: `<root and references to named identity slots>`
- Authorization boundary: `<workspace/project or task-owned domain and effects>`
- Planned primary surfaces: `<ownership coordination>`
- Incidental footprint: `<allowed classes and classification stop>`
- Preservation: `<behavior, data, identity, state>`
- Exclusions: `<non-goals and forbidden effects>`
- Supported workflows: `<Outcome/preservation-derived consumer-reachable paths>`
- Concurrency and ordering: `<task-specific FANOUT/BACKGROUND/ORDERED assignments; same-snapshot groups; dependency/review/effect barriers; overlapping paths, contracts, effect resources, and sole writer; shared-Git-dir ref/tracking/checkout conflicts>`

## Handoff

- Stable Outcome/boundary/Done: `<facts or unresolved items; for relevant Git work, exact target ref and SHA, checkout owner or none, observed cached/live remote relation with provenance/time as applicable, validation surface, relevant runtime consumer if any, and final worktree disposition>`
- Lifecycle/process/cleanup prerequisites: `<process checks only when switch, move, removal, or suspected runtime use makes them relevant; cleanup only when requested and authorized with recovery reachability; neither implies termination or cleanup authority>`
- Fixed writer/current blockers: `<identity and blockers>`
- Authorized increments/exclusions: `<values>`
- Revision admission: `<decision-changing evidence or concrete blocker>`

## Baseline and breaks

- Baseline: `<command and accepted failures>`
- Allowed compatibility breaks: `<exact authorized breaks and effects, or none>`

## Consumer and candidate

- Consumer: `<consumer>`
- Input closure: `<direct, generated, transitive inputs; modes and deletions>`
- Review premises: `<environment or external facts whose change could alter code-review validity; consumer-sensitive branch, upstream, cwd, worktree-local configuration, environment, or runtime>`
- Native immutable freeze: `<one literal candidate identity as review evidence; native derivation and machine-carrier name>`
- Repair/replacement budget: `<values>`

## Checks and stops

- Required checks: `<Outcome/preservation-required consumer-native checks and commands; unavailable required paths remain unverified; heuristic, regex, synthetic, or cross-language proxies are advisory only; optional checks omitted or advisory>`
- Stop conditions: `<identity, scope, trust, effect, or required-coverage drift/unknown>`
- Recovery evidence: `<durably reachable candidate/effect/rollback evidence>`

## Next-effect Binding

- Candidate review tuple: `<verbatim native Exact-final verdict plus exact Body identity and candidate reference to Native immutable freeze; fixed across Binding refresh; unavailable/mismatched native result rereviews; grants no effect authority>`
- Next effect: `<smallest independently authorized, attempted, and authoritatively observable result; exact direct targets and configured automatic downstream writes; or none>`
- Effect binding: `<requested and resolved targets or conflicts; material basis; each source/current identity once as review evidence with native derivation and carrier name; direct authority; cap or cost; observation; rollback>`
- Derivation/provenance: `<proof that the proposed artifact derives from the reviewed candidate; or unavailable stop>`
- Admission: `<compose exact reviewed Body with this Binding; mismatch or unresolved target stops only this effect; binding-only drift does not rereview code>`
- Later effects: `<manual or otherwise untriggered outline only; classify and bind each only when it becomes next>`
