# HappyCodex v1.3.0 proportionality release

Keep this contract static. Reconstruct live state from Git and tools.

## Request and Outcome

- Verbatim request/amendments: `好的你执行吧，发布，然后本地重装` following approval of the Increment A proportionality candidate and explicit confirmation that the target release is `v1.3.0`.
- Outcome: publish the exact HappyCodex proportional blocker-admission implementation as public `v1.3.0` on configured `cch96/happycodex` `origin/main`, an annotated `v1.3.0` tag, and a public non-draft/non-prerelease GitHub Release; then reinstall that exact release through the existing `happycodex@personal` local marketplace while preserving a recoverable `v1.2.1` source/cache snapshot.
- Done evidence: one immutable release commit receives all offline checks and a fresh no-history Exact-final `GO`; remote `main`, peeled annotated tag, and GitHub Release read back to that commit; the personal source and installed cache report `1.3.0+codex.<UTC cachebuster>` and match the release runtime projection modulo that single manifest cachebuster; previous source/cache/config identities remain recoverable.

## Boundary

- Workspace/source identity: `/home/caichenghang/projects/happycodex` local `main == origin/main == v1.2.1^{}` commit `ccd14fef55d0bdf3060f4d31d72fb4cf64d35a76`; reviewed Increment A tree `cd25d14dac6928ac52102797bfc3c0249692fd56` recomputes exactly and has fresh Exact-final `GO` but is not the release identity.
- Authorization boundary: prepare and commit one `v1.3.0` release candidate; publish it once to configured `origin/main`, matching annotated `v1.3.0`, and GitHub Release; then replace and reinstall the existing local personal-marketplace source from that exact commit after creating rollback evidence.
- Planned primary surfaces: `.codex-plugin/plugin.json`; `docs/execplans/happycodex-1-3-0-proportionality-implementation-20260814.md`; this Release ExecPlan; `evaluation/hidden-oracles-v1.json`; `evaluation/policy.py`; `evaluation/provider-fixtures-v1.json`; `evaluation/report-schemas-v1.json`; `skills/happycodex/SKILL.md`; `skills/happycodex/references/execplan.md`; `tests/test_attestation_contract.py`; `tests/test_attestation_flow.py`; `tests/test_stage_profiles.py`.
- Incidental footprint: one timestamped mode-private rollback directory below `/home/caichenghang/.codex/happycodex-rollbacks`; one staged release export; local Git commit/tag refs; supported cache/config effects from one `codex plugin add happycodex@personal --json`; reconstructible test/cache output.
- Preservation: immutable published tags/trees; A semantics and Exact-final safety result; deterministic stateless evaluator and fixed topology/taxonomy; authority and one-shot effects; repository history; default personal marketplace metadata; user-owned untracked plans/experiments/tests; prior installed source/cache and enabled state through rollback; truthful closure.
- Exclusions: Increment B payload implementation; design/audit/ponytail ExecPlans; `experiments/`; `tests/test_ponytail_ablation.py`; README, marketplace, hook, identity/provider/verify, schema-version, topology, record, authority, or release-contract edits; history rewrite, force push, branch/PR creation, release assets, marketplace/config hand edits, cleanup, provider/model calls beyond required native Exact-final, any second external-effect attempt, or activation in the current already-running thread.
- Supported workflows: public repository/tag/Release consumption; existing personal local marketplace source; supported cachebuster helper followed by one plugin add; new-thread pickup of the installed version.
- Writer overlap: the fixed HappyCodex Executor exclusively owns release-candidate repository bytes until commit. Root alone owns commit, terminal review dispatch, remote publication, rollback/source replacement, cachebuster, reinstall, and readbacks. No parallel mutable writer or effect actor.

## Handoff

- Stable Outcome/boundary/Done: A bytes plus truthful `1.3.0` metadata, one new release plan, immutable commit identity, standard publication, and verified personal reinstall are fixed.
- Fixed writer/current blockers: reuse `/root/increment_a_executor` for the only repository write increment. Existing unrelated untracked files are excluded and must remain untouched. Stop if any planned path, ref, index, remote, source, cache, or installed identity drifts from preflight.
- Authorized increments/exclusions: one version/test/plan wrapper; one candidate commit; one fresh Exact-final; at most one in-boundary repair and one replacement review after `NOT_YET`; each named publication/install effect once; all exclusions above remain fixed.
- Revision admission: only a reproduced candidate-new material blocker, deterministic validation failure, or exact release/install identity mismatch may revise the candidate or stop an effect.

## Baseline and breaks

- Baseline: Increment A focused 53/53 and Git-tracked offline 103/103 tests passed; JSON production-input loading, imports/inventory, Skill validator, plugin validator, and `git diff --check` passed; A tree `cd25d14dac6928ac52102797bfc3c0249692fd56` received strict `GO`; user index is empty; installed plugin is enabled `1.2.1+codex.20260813163226` from `/home/caichenghang/plugins/happycodex` through marketplace `personal`.
- Allowed compatibility breaks: plugin version and its closed contract assertion advance from `1.2.1` to `1.3.0`; candidate-review closed fixture/oracle/schema implements the already-reviewed proportional blocker admission. No data migration, compatibility reader, public layout break, marketplace change, or external consumer cutover.

## Consumer and candidate

- Consumer: Codex loading HappyCodex from the public repository/plugin or the existing personal installed cache; maintainers running the deterministic evaluator/tests.
- Input closure: exact bytes/modes of all twelve planned repository paths; repository-wide tracked tests and validators; manifest/marketplace identity; the nine-file runtime export (`.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, both READMEs, `hooks/hooks.json`, `hooks/session_firewall.py`, `skills/happycodex/SKILL.md`, `skills/happycodex/agents/openai.yaml`, `skills/happycodex/references/execplan.md`); generated cachebuster manifest; installed cache projection.
- Native immutable freeze: one commit on local `main` containing exactly the twelve planned paths. Its full commit SHA is the release candidate identity and must remain byte-stable after review.
- Terminal admission: one fresh native read-only no-history blocker-only HappyCodex Exact-final over baseline `ccd14fef...`, the exact release commit, and this plan; require strict `GO` or `NOT_YET` and exact commit echo. The prior A-tree `GO` is supporting evidence only.
- Repair/replacement budget: after `NOT_YET`, at most one already-authorized coherent in-boundary repair, a new commit identity, and one fresh replacement Exact-final. Any later adverse result returns to the user before publication.

## External effects

- Effects: after authenticated zero-effect preflight, attempt once each in order: non-force push of the exact candidate to `origin/main`; annotated `v1.3.0` tag creation/push; public non-draft/non-prerelease GitHub Release with no assets; recoverable replacement of `/home/caichenghang/plugins/happycodex` by the exact nine-file release export; one official default UTC cachebuster; one `codex plugin add happycodex@personal --json`. Observe remote branch/tag through independent refs, Release metadata through GitHub, and installation through plugin list, manifest versions, and source/cache/runtime hashes. Any partial, ambiguous, or unknown result stops without retry.
- Recovery: before local replacement, preserve exact old source, installed cache, personal marketplace file, plugin list, and hashes under a new mode-private `/home/caichenghang/.codex/happycodex-rollbacks/pre-v1.3.0-*`; immutable public `v1.2.1` remains the release rollback target. Do not auto-rollback an ambiguous effect.

## Checks and stops

- Required checks: exact Git/index/path/version preflight; focused proportionality tests; all Git-tracked `tests/test_*.py`; Skill quick validation; plugin validation; JSON/Python production-input loading; `git diff --check`; secret-pattern scan; frozen-commit path/tree verification; fresh Exact-final; remote branch/tag/Release absence preflight; post-effect remote/tag/Release readback; exact runtime export inventory; official cachebuster; personal marketplace name/source verification; post-install plugin list and source/cache hash comparison modulo cachebuster.
- Stop conditions: repository, branch, baseline, origin repository, target version, index, candidate path/tree/commit, remote main, existing tag/Release, GitHub auth, marketplace name/source, installed prestate, rollback, review identity, runtime projection, cachebuster, install output, readback, or trust drift; any unexpected test/validator/secret result; any extra staged/committed path; any partial, failed, or ambiguous effect.
- Recovery evidence: immutable `v1.2.1`; committed and reviewed `v1.3.0`; local/remote branch and tag identities; GitHub Release metadata; timestamped rollback snapshot; exact release export; cachebuster receipt; final source/cache/plugin hashes and enabled state.
