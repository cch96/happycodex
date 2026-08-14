# HappyCodex 1.3.0 proportionality implementation ExecPlan

Keep this contract static. Reconstruct live state from Git and tools.

## Request and Outcome

- Verbatim request/amendments: `好的，可以实现的可以实现一下，实验可以并行做（fork一个？，或者你是否有更好方案）`; this authorizes the previously proposed Increment A implementation and a parallel isolated Increment B experiment.
- Outcome: implement the proportional blocker-admission contract in the repository's public Skill, ExecPlan guidance, deterministic evaluator, closed fixtures/oracles/schemas, and offline tests while preserving material safety, immutable candidate identity, and one-shot effect rules; concurrently measure a read-only payload-ablation hypothesis without mixing it into the implementation candidate.
- Done evidence: Increment A acceptance cases and safety counter-cases are encoded and green; all offline repository tests pass; the exact candidate is frozen with a consumer-native immutable Git identity and receives one fresh blocker-only Exact-final verdict; Increment B reports current/projected bytes, exclusions, readability risks, and whether the 60% promotion threshold is met.

## Boundary

- Workspace/source identity: `/home/caichenghang/projects/happycodex` at `main == origin/main == v1.2.1^{}` commit `ccd14fef55d0bdf3060f4d31d72fb4cf64d35a76`, with the byte-identical installed `happycodex/1.2.1+codex.20260813163226` Skill used only as current guidance.
- Authorization boundary: reversible repository implementation and tests for Increment A; task-owned plans/reports; read-only local computation for Increment B. A local immutable Git object may be created for candidate review without moving refs or the user index.
- Planned primary surfaces: `skills/happycodex/SKILL.md`, `skills/happycodex/references/execplan.md`, `evaluation/policy.py`, `evaluation/provider-fixtures-v1.json`, `evaluation/hidden-oracles-v1.json`, `evaluation/report-schemas-v1.json`, `tests/test_attestation_contract.py`, `tests/test_stage_profiles.py`, `tests/test_attestation_flow.py`, and shared test fixtures only if required.
- Incidental footprint: this static ExecPlan; bounded Python/test caches and temporary index/worktree objects that are reconstructible, non-authoritative, non-consumer inputs, and contain no secrets. Account for them; do not delete pre-existing user artifacts.
- Preservation: existing ordinary-local behavior, material Outcome/preservation blockers, consumer-readable product inputs, stateless deterministic evaluator, fixed finding taxonomy/topology, authority boundaries, candidate/effect identities, one-shot external effects, truthful closure, published tags/trees, refs/index, installed plugin/config, and all pre-existing untracked files.
- Exclusions: no Increment B product edit; no `hooks/session_firewall.py`, record/schema version, topology, holdout pairing, canonicalization, authority, effect history, Git/tag behavior, historical ExecPlan rewrite, compatibility reader, migration, alias, dual write, mutable ledger/controller, severity scorer, review counter, dynamic impact engine, `evidence_paths` registry, version bump, commit/ref move, push, release, install, activation, provider/model call, or destructive cleanup.
- Supported workflows: ordinary reversible local work; substantial local implementation; public/high-risk exact-final review; external-effect preflight/observation; partial or ambiguous effect reconciliation; direct amendments `不用 review`, `自己解决`, and `直接发`; robustness tests only when the Outcome/preservation boundary requires them.
- Writer overlap: one `happycodex_executor` owns every Increment A product/test write and any task-owned implementation report. One parallel read-only explorer owns Increment B measurement and may not edit repository bytes. Root remains read-only after handoff and requests any candidate correction through the Executor.

## Handoff

- Stable Outcome/boundary/Done: implement only Increment A from `docs/execplans/happycodex-1-3-0-proportionality.md`; keep Increment B experimental and outside the candidate; no publication or activation.
- Fixed writer/current blockers: the fixed Executor receives the sole write lock after a clean Git/index recheck. Existing untracked ponytail/experiment/audit files are user-owned and excluded. Stop if an intended Increment A path already has pre-existing changes.
- Authorized increments/exclusions: one coherent Increment A edit, required fixture/test adjustments, one in-boundary repair change-set if Exact-final is adverse, and one read-only Increment B measurement; all exclusions above remain fixed.
- Revision admission: only a reproduced failure against the acceptance matrix, a current contract/test incompatibility, or a fresh Exact-final material blocker may revise the candidate.

## Baseline and breaks

- Baseline: `main`, `origin/main`, and `v1.2.1^{}` at `ccd14fef55d0bdf3060f4d31d72fb4cf64d35a76`; index empty; the listed pre-existing untracked files/directories remain untouched; repository and installed Skill SHA-256 both `3b7b750be0c273c2eea7cfae6861f14a1e170dbaf6a22fd1099d6aeecba8b41d`.
- Allowed compatibility breaks: closed candidate-review fixture/oracle/schema answers may change in lockstep to encode proportional admission. No public data migration, compatibility reader, published-tree mutation, or external consumer cutover is authorized.

## Consumer and candidate

- Consumer: future Codex sessions using the installed HappyCodex Skill and maintainers running the deterministic evaluator/tests; installation itself is not part of this task.
- Input closure: exact bytes/modes/deletions of every modified planned surface, any required shared fixture, this governing implementation ExecPlan, and transitive evaluator/schema/test dependencies. The separate design/audit/ponytail/experiment artifacts are not candidate inputs unless the Executor must modify them, which requires stopping first.
- Native immutable freeze: create a detached Git tree/commit object from `HEAD` plus only authorized candidate paths using a temporary index; do not stage the user index or move a ref. Record the exact commit/tree and full path list.
- Terminal admission: because installed public guidance and evaluator policy change, use one fresh no-history `happycodex_exact_final` over immutable baseline `ccd14fef...`, candidate identity, and this plan; require `GO` or `NOT_YET` plus exact identity echo.
- Repair/replacement budget: after `NOT_YET`, at most one already-authorized coherent repair by the same Executor, one new immutable freeze, and one fresh replacement Exact-final. Any later adverse result returns to the user.

## External effects

- Effects: none. Local tests and detached Git object creation are reversible repository operations. Do not publish, push, tag, release, install, activate, invoke a provider/model, or mutate external state.

## Checks and stops

- Required checks: recheck Git/index/refs before handoff and freeze; encode both must-block and must-not-block acceptance cases for GPU2, StockAI, Calcifer, Workflow, ordinary local, high-risk safety, one-shot effect, and robustness-required paths; run focused contract/stage/flow tests, repository validators discovered from source, `git diff --check`, and the complete offline standard-library suite once; verify no excluded path changed; measure Increment B against the current full-readable two-tree projection and the proposed deterministic projection.
- Stop conditions: baseline/ref/index drift; overlap with pre-existing changes on a planned path; changed Outcome/consumer/effect target; secret or raw unrelated-session exposure; schema/topology/identity/effect change outside Increment A; any Increment B repository mutation; inability to preserve material blockers or one-shot semantics; test/environment ambiguity that prevents classifying candidate correctness; Exact-final identity mismatch; or an adverse result beyond the repair budget.
- Recovery evidence: baseline commit/tag remain reachable; user index/refs/installed plugin stay unchanged; authorized diffs and detached candidate object remain inspectable; pre-existing untracked files remain present; no external effect exists to recover.
