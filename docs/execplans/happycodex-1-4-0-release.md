# HappyCodex v1.4.0 context-efficiency release

Keep this contract static. Reconstruct live state from Git and tools.

## Request and Outcome

- Verbatim request/amendments: publish the approved context-efficiency candidate as the backward-compatible feature release `v1.4.0`, then reinstall it locally.
- Outcome: commit the exact bounded context-efficiency implementation once, publish that immutable commit to configured `cch96/happycodex` `origin/main`, an annotated `v1.4.0` tag, and a public non-draft/non-prerelease GitHub Release, then reinstall its exact runtime projection through the existing `happycodex@personal` marketplace.
- Done evidence: one immutable release commit passes the isolated 106-test suite, focused contracts, Skill/plugin validators, diff and secret checks, and one fresh no-history Exact-final `GO`; every publication and activation effect is attempted once and independently read back; active source/cache report `1.4.0+codex.<UTC cachebuster>` and match the release projection modulo that cachebuster; the prior `v1.3.0` source/cache/config state remains recoverable.

## Boundary

- Workspace/source identity: `/home/caichenghang/projects/happycodex` local `main == origin/main == v1.3.0^{}` commit `b04ca81800887a772425af0bb0986920aa888462`; the index is empty.
- Frozen implementation evidence: archive SHA-256 `7642a12106cad5816fbe0faee26d324eeb3dcbc34f0ba60724b782b64d934349`; canonical Git tree `249e435abe9b9d7ba1a319be40c7e7f43c1ecde2`; official Exact-final verdict `GO`. These establish the prior implementation candidate, not the release commit identity.
- Target preflight: remote `v1.4.0` tag and GitHub Release are absent; installed prestate is enabled `1.3.0+codex.20260814083348` from `happycodex@personal`. Recheck all of these immediately before their dependent effect.
- Exact release-commit path closure: `.codex-plugin/plugin.json`; `docs/execplans/happycodex-1-4-0-release.md`; `docs/execplans/happycodex-subagent-context-efficiency-20260816.md`; `hooks/session_firewall.py`; `skills/happycodex/SKILL.md`; `tests/test_attestation_contract.py`; `tests/test_session_firewall.py`. The test path contains both the prior implementation contract changes and the `1.4.0` public-metadata wrapper.
- Preservation: published tags and reachable trees; deterministic stateless evaluation; user, maintainer, workspace, and selected configuration authority boundaries; repository history; default personal marketplace metadata; unrelated untracked docs, experiments, and tests; prior local source/cache/config through rollback evidence; truthful one-shot-effect closure.
- Exclusions: every repository path outside the seven-path closure; functional implementation changes beyond the frozen four tracked modifications; edits to the existing context-efficiency ExecPlan; README, marketplace, evaluator, identity, authority, schema, or other-test changes; staging or commit by the Executor; history rewrite, force push, branch/PR creation, release assets, cleanup, marketplace/config hand edits, provider/model calls except the one terminal Exact-final, activation in the current thread, or retry of an ambiguous effect.
- Writer/effect ownership: the fixed HappyCodex Executor exclusively writes the manifest/test/release-plan wrapper. Root alone owns full validation, staging, the local release commit, Exact-final dispatch, every external effect, rollback/source/cache/config mutation, local activation, readback, and completion judgment.

## Handoff and Candidate

- Stable Outcome/boundary/Done: the seven exact paths, backward-compatible `1.4.0` metadata, immutable release identity, standard public release, recoverable local activation, and no provider/model calls beyond terminal Exact-final are fixed.
- Candidate freeze: Root stages exactly the seven paths and creates one local release commit containing exactly the four prior tracked modifications, the context-efficiency ExecPlan, and this manifest/test/release-plan wrapper. Any extra path, mode, byte, or index entry stops the sequence.
- Validation before freeze: run the focused `tests.test_attestation_contract` and `tests.test_session_firewall` modules, the isolated 106-test suite, the Skill quick validator, plugin validator, JSON parse, owned `git diff --check`, and secret scan. All must pass without network access.
- Terminal admission: after the commit exists, one fresh native read-only no-history blocker-only HappyCodex Exact-final inspects and echoes that exact full commit SHA and returns strict `GO` or `NOT_YET`. The earlier tree-level `GO` is supporting evidence only and cannot admit publication.
- Revision admission: a reproduced candidate-new material blocker, deterministic validation failure, or exact identity mismatch stops and returns to the user. No wrapper or functional repair is implicit in this release authorization.

## Publication Effects

After authenticated read-only preflight, Root attempts each effect separately and once, and reads it back before continuing:

1. Push the exact release commit non-force to configured `origin/main`; independently read back remote `main` and require the exact commit.
2. Create and push the matching annotated `v1.4.0` tag; independently peel local and remote tags and require the exact commit.
3. Create the public non-draft/non-prerelease GitHub Release `v1.4.0` with no assets; independently read back tag, target, visibility, draft/prerelease flags, and asset count.

Any failed, partial, ambiguous, or unknown effect stops the sequence. Inspect state read-only; never retry until the prior attempt is proven to have had no effect.

## Local Activation Effects

- Before replacement, create one new mode-private recoverable snapshot below `/home/caichenghang/.codex/happycodex-rollbacks/pre-v1.4.0-*` containing the exact active `v1.3.0` source, installed cache, personal marketplace/config state, plugin-list receipt, identities, modes, and hashes. Read the snapshot back before continuing.
- Export exactly these nine runtime files from the reviewed release commit: `.agents/plugins/marketplace.json`; `.codex-plugin/plugin.json`; `README.md`; `README.en.md`; `hooks/hooks.json`; `hooks/session_firewall.py`; `skills/happycodex/SKILL.md`; `skills/happycodex/agents/openai.yaml`; `skills/happycodex/references/execplan.md`. Reject extras, omissions, links, mode drift, or bytes not sourced from that commit.
- Recoverably replace `/home/caichenghang/plugins/happycodex` with that exact nine-file export and read back its inventory, modes, and hashes before continuing.
- Run the official helper `/home/caichenghang/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py` once with its default UTC cachebuster against the exported source. Read back that only `.codex-plugin/plugin.json` changed and that `1.4.0` became exactly `1.4.0+codex.<cachebuster>`.
- Run exactly one `codex plugin add happycodex@personal --json`. Read back command JSON, `codex plugin list`, enabled marketplace/version, source and cache manifests, exact runtime inventories, and source/cache hashes modulo the single cachebuster.
- Do not invoke a provider/model during activation. A new thread is required to consume the newly installed Skill.

## Checks, Stops, and Recovery

- Required checks: exact repository/origin/branch/baseline/index/path/version identities; remote tag/Release absence; installed marketplace/prestate; focused RED then GREEN wrapper proof; isolated 106/106; Skill/plugin validators; JSON parse; owned diff check; secret scan; seven-path staged and committed closure; commit/tree identity; fresh Exact-final; per-effect remote/tag/Release readbacks; rollback snapshot; exact nine-file export; official cachebuster; one plugin add; final source/cache/plugin equality and enabled state.
- Stop conditions: any repository, origin, branch, baseline, target version, index, path, archive/tree, candidate commit, review, remote ref, tag/Release, authentication, marketplace, source/cache/config, rollback, runtime export, cachebuster, install output, readback, or trust drift; any unexpected check result; any extra staged/committed/exported path; or any partial, failed, ambiguous, or unknown effect.
- Recovery evidence: immutable public `v1.3.0`; the reviewed `v1.4.0` commit and public identities if created; the mode-private pre-`v1.4.0` source/cache/config snapshot; exact export inventory; cachebuster receipt; install JSON; and final source/cache/plugin identities. Never auto-rollback an ambiguous effect.
