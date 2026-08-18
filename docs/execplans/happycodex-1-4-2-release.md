# HappyCodex 1.4.2 release ExecPlan

Keep this contract static: record stable authority; never append command output, attempt logs, live inventories,
hash receipts, or progress records. Reconstruct live state from Git and tools; report current evidence in the task or handoff.

## Request and Outcome

- Verbatim request/amendments: Implement the agreed continuity and spawn-fallback correction as patch release 1.4.2, publish it, and reinstall it locally. Root owns remote and installation effects; the fixed Executor owns only the repository candidate and offline validation.
- Outcome: HappyCodex 1.4.2 prevents no file diff, elapsed reasoning, or waits from being treated as writer failure; recognizes continuity loss only from hard terminal or confirmed-unreachable state; and does not grant fallback for a caller-parameter rejection when a corrected spawn succeeds.
- Done evidence: The exact candidate passes the focused contract tests, tracked offline standard-library suite, Skill and plugin validation, JSON parsing, diff/scope checks, and size limits; Root separately freezes, reviews, publishes, reads back, and reinstalls the established release candidate.

## Boundary

- Workspace/source identity: `/home/caichenghang/projects/happycodex`, branch `main` at the published `v1.4.1` baseline.
- Authorization boundary: The seven listed repository candidate paths and the standard 1.4.2 release effects assigned to Root.
- Planned primary surfaces: `.codex-plugin/plugin.json`; `docs/execplans/happycodex-1-4-2-release.md`; `skills/happycodex/SKILL.md`; `tests/test_attestation_contract.py`; `evaluation/provider-fixtures-v1.json`; `evaluation/hidden-oracles-v1.json`; `evaluation/report-schemas-v1.json`.
- Incidental footprint: Offline test caches and other reconstructible, ignored local outputs only; stop if any incidental output is tracked, shared, secret-bearing, or consumer-visible.
- Preservation: Existing evaluator topology, manifest, policy, role identifiers, compatibility, one-writer invariant, summary-not-authority invariant, genuine spawn-failure fallback, genuine continuity-loss recovery, and all runtime package files outside the listed Skill path.
- Exclusions: No other tracked path; no cleanup or modification of user-owned untracked files; no new role, watchdog, timer state machine, ledger/controller, heartbeat, Root-takeover exception, compatibility reader, migration, alias, or dual write. The Executor does not stage, commit, push, tag, create a GitHub Release, modify installed/cache trees, invoke providers/models/network, or install/activate anything.
- Supported workflows: Proactive native spawning with corrected caller parameters; valid spawn-failure fallback; terminal or confirmed-unreachable writer recovery; active-writer continuation despite no diff/time/wait; live progress continuation; focused status query when liveness is uncertain; offline release validation.
- Writer overlap: The fixed Executor is the sole writer for the seven candidate paths and their shared evaluator semantics. Root stays read-only until candidate handoff and owns later Git/release/install effects.

## Handoff

- Stable Outcome/boundary/Done: Patch-only contract correction and version bump within the exact seven-path closure, with offline validation before any effect.
- Fixed writer/current blockers: Fixed HappyCodex Executor; no known blocker at plan creation.
- Authorized increments/exclusions: One repository candidate increment to 1.4.2; one standard release sequence and one local reinstall assigned to Root; all exclusions above remain fixed.
- Revision admission: Only new decision-changing evidence or a concrete current blocker reachable through a supported workflow; ambiguity, partial effects, or identity/configuration drift returns to Root.

## Baseline and breaks

- Baseline: Clean tracked/index state on `main` at published `v1.4.1`; pre-existing untracked user material is preserved and excluded from candidate scope.
- Allowed compatibility breaks: None.

## Consumer and candidate

- Consumer: Codex users installing the HappyCodex plugin and the deterministic repository evaluator validating its behavioral contract.
- Input closure: The seven planned candidate paths, including exact file modes and deletions; evaluator topology, manifest, policy, other tests, and other runtime package files are preserved baseline inputs.
- Native immutable freeze: Root will freeze the exact candidate as a Git commit after offline validation.
- Terminal admission: Root will obtain one fresh no-history blocker-only Exact-final verdict that echoes the immutable candidate identity before public effects.
- Repair/replacement budget: One already-authorized in-boundary repair change-set for admitted findings, followed by a new freeze and replacement terminal review; otherwise return to the user.

## External effects

- Effects: Executor performs none. After candidate identity and approval are established, Root may attempt once each: non-force push to configured `origin/main`, annotated `v1.4.2` tag publication, matching GitHub Release creation, and local reinstall using the established release identity. Read back each effect separately; stop on partial, ambiguous, or unknown state and retry only after proof of zero effect and renewed recovery authority.

## Checks and stops

- Required checks: Focused `tests.test_attestation_contract`; full tracked standard-library test suite isolated from unrelated untracked tests; Skill `quick_validate`; plugin validation; JSON parse of all changed JSON; read-only contradiction check of `skills/happycodex/agents/openai.yaml`; owned-path `git diff --check`; exact changed-path/index/status accounting; and line, word, byte measurement enforcing Skill at no more than 155 lines, 1200 words, and 9000 bytes.
- Stop conditions: Baseline, candidate identity, writer ownership, exact path closure, semantics, compatibility, trust, configuration, effect target, or required coverage drift/unknown; any necessary edit outside the seven owned paths; any provider/model/network requirement; any partial or ambiguous effect.
- Recovery evidence: The immutable Git candidate and published baseline remain durably reachable; Root preserves and verifies installation rollback before local activation.
