# HappyCodex v1.4.1 required-validation clarity release

Keep this contract static: record stable authority; never append command output, attempt logs, live inventories,
hash receipts, or progress records. Reconstruct live state from Git and tools; report current evidence in the task or handoff.

## Request and Outcome

- Verbatim request/amendments: implement the agreed minimal HappyCodex wording-and-test hardening; then `发布吧，然后本地重装一下`.
- Outcome: publish the backward-compatible patch release `v1.4.1` once to configured `origin/main`, an annotated `v1.4.1` tag, and a public non-draft/non-prerelease GitHub Release, then reinstall its exact runtime projection through the existing `happycodex@personal` marketplace.
- Done evidence: the exact immutable release commit passes required offline checks and fresh Exact-final admission; each publication effect is attempted once and independently read back; installed source and cache match the release runtime projection modulo one official cachebuster; the prior installation remains recoverable.

## Boundary

- Workspace/source identity: `/home/caichenghang/projects/happycodex`, published baseline `v1.4.0`, branch `main`, configured GitHub `origin`.
- Authorization boundary: the six release-candidate paths below; standard publication to `origin/main`, annotated `v1.4.1`, and its GitHub Release; recoverable local replacement and reinstall of `happycodex@personal`.
- Planned primary surfaces: `.codex-plugin/plugin.json`; `docs/execplans/happycodex-1-4-1-release.md`; `skills/happycodex/SKILL.md`; `skills/happycodex/references/execplan.md`; `tests/test_attestation_contract.py`; `tests/test_attestation_flow.py`.
- Incidental footprint: pre-existing untracked docs, experiments, and tests remain unstaged and unchanged; the untracked Ponytail experiment's exact-old-source assertion is advisory and outside the versioned product suite.
- Preservation: every published tag and reachable tree; repository history; evaluator schemas and topology; default marketplace metadata; unrelated tracked and untracked files; prior local plugin source, installed cache, and configuration through a private rollback snapshot.
- Exclusions: force push, history rewrite, branch or pull-request creation, release assets, evaluator/schema/hook/README/marketplace edits, hand-editing local marketplace configuration, provider/model calls except one terminal Exact-final, retries after an ambiguous effect, or cleanup of prior/user-owned state.
- Supported workflows: Git-tracked offline tests; Skill and plugin validation; Codex loading the published runtime projection from the personal marketplace; rollback to the prior local installation.
- Writer overlap: Root alone writes, stages, commits, publishes, snapshots, exports, and installs these overlapping paths and effects.

## Handoff

- Stable Outcome/boundary/Done: patch-only validation clarity, six candidate paths, `v1.4.1`, standard public release, exact local runtime activation, and recoverable prior installation.
- Fixed writer/current blockers: Root is the only writer; any unexpected candidate path, failed required check, Exact-final result other than exact-identity `GO`, effect ambiguity, or installation mismatch blocks continuation.
- Authorized increments/exclusions: one version wrapper and release plan around the already implemented four-file patch; no functional expansion or compatibility break.
- Revision admission: only a reproduced candidate-new material blocker or deterministic required-check failure may reopen the candidate; otherwise stop after closure.

## Baseline and breaks

- Baseline: published `v1.4.0`; the Git-tracked offline suite is authoritative. Full filesystem discovery may include the excluded untracked Ponytail experiment that freezes older source bytes.
- Allowed compatibility breaks: none.

## Consumer and candidate

- Consumer: Codex plugin discovery/loading through the published repository and existing `happycodex@personal` local marketplace.
- Input closure: the six candidate paths above, their modes and deletions, and the runtime export consisting of `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, `README.md`, `README.en.md`, `hooks/hooks.json`, `hooks/session_firewall.py`, `skills/happycodex/SKILL.md`, `skills/happycodex/agents/openai.yaml`, and `skills/happycodex/references/execplan.md` from the release commit.
- Native immutable freeze: one local release commit containing exactly the six candidate paths, later matched by `origin/main`, peeled annotated tag, GitHub Release, runtime export, and installed cache.
- Terminal admission: one fresh native read-only no-history blocker-only Exact-final must echo the exact full commit identity and return strict `GO` before publication.
- Repair/replacement budget: no implicit repair; a blocker or identity mismatch returns to the user.

## External effects

- Effects: one non-force push of the exact commit to `origin/main`; one annotated `v1.4.1` tag push; one public GitHub Release without assets; one recoverable local source replacement; one official cachebuster update; one `codex plugin add happycodex@personal --json`. Read back each effect before the next; never retry an ambiguous result.

## Checks and stops

- Required checks: exact branch/baseline/index/path/version and absent-target preflight; `git diff --check`; JSON parse; Git-tracked offline unittest suite; focused contract/flow/session tests; Skill quick validation; plugin validation; bounded secret scan; exact six-path commit closure; fresh Exact-final; remote main/tag/Release readbacks; private rollback snapshot; exact nine-file runtime export; cachebuster-only source mutation; one plugin add; final enabled version, inventory, mode, and byte equality modulo the cachebuster.
- Stop conditions: identity, scope, index, version, authentication, check, candidate, review, remote ref, tag/Release, effect, rollback, marketplace, runtime export, cachebuster, install, or readback drift/unknown; any extra staged/committed/exported path; any failed, partial, ambiguous, or unknown effect.
- Recovery evidence: immutable `v1.4.0`; the `v1.4.1` release identities if published; private pre-install source/cache/config snapshot; exact runtime export inventory; cachebuster and install readbacks. Never auto-rollback an ambiguous effect.
