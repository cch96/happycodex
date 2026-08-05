# HappyCodex 0.7.2 release

## Contract

- Task and bootstrap grant: `HC-0.7.2-RELEASE-001`.
- Phase: `readiness`. This is the current release index, not a release receipt or
  authority for any later effect.
- Frozen user authority, verbatim: `好的发布吧`.
- Authorized Outcome: publicly release HappyCodex `v0.7.2` to
  `cch96/happycodex` and update the existing local `happycodex@personal`
  installation to one matching 0.7.2 cachebuster package.
- Fixed Executor and mandatory Output identity:
  `/root/capability_proportional_executor`. Host session:
  `/home/caichenghang/.codex/sessions/2026/08/05/rollout-2026-08-05T17-04-47-019fd2e2-7fc0-7332-803e-b590b906f5cb.jsonl`;
  session ID `019fd2e2-7fc0-7332-803e-b590b906f5cb`; source role
  `happycodex_executor`; effective route `gpt-5.6-sol/high`; approval `never`;
  sandbox `danger-full-access`.
- Root owns every later grant, effect admission, completion decision, and claim
  release. The fixed Executor remains the sole writer and never delegates.
- No Goal was requested or created. Users choose no mode and enter no
  continuation phrase.

This bootstrap may create only this plan and atomically acquire/verify the six
resources below. It authorizes no stage, commit, test, sync, install,
cachebuster, release-note write, push, tag, GitHub Release, cleanup, or claim
release.

## Verified source and candidate

- Repository: `/home/caichenghang/projects/happycodex`; branch `main` tracking
  `origin/main`; origin `git@github.com:cch96/happycodex.git`.
- Local HEAD, local `origin/main`, and live remote `main`:
  `c9476242c259cfe84ba2c9b7866f62d5694c3ee6`; HEAD tree:
  `1d91d18eac039cca2be64707584cb34424507337`.
- Pre-plan index: empty. Exact candidate dirt was six modified tracked paths:
  `.codex-plugin/plugin.json`, `README.en.md`, `README.md`,
  `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`; plus one untracked closed control
  `docs/execplans/happycodex-0-7-2-capability-proportional-admission.md`.
  No other dirty path existed.
- Closed control SHA-256:
  `d21165d0998cc60101fa2f677ddc5429e48e959cb2defb9ecfbfe5f654a10f7d`.
  Tracked binary diff SHA-256:
  `5783169f659e9e6dac92c9140d2aca67c6fd8abd42f76d51c00dbec46a8f1f4e`.
- Candidate package tree:
  `49dd643cdce8be6bad3cb6578a6b3a48bfb9df0c`; package artifact SHA-256:
  `8f4f7b9c19e5b664f392a1bdb673da34ae668d595dae917f14856f5e5567a2d9`;
  semantic SHA-256:
  `47b52c20f2fd52efb393fd0fb86f18551049b3236bb8964adb7341d0d3d1ba18`;
  ProductArtifact record SHA-256:
  `5b3e951255bd40fa9b891e43f901289a96d8feeadca54d786434f1b03485f758`.
- Preserved published Skill tree:
  `v0.6.5:skills/happycodex = d9e525a267fbf36669d409ba1b4b009a6beeeea5`.

## Candidate review and validation

- Closed candidate Exact-final: `GO`, no blockers. Mandatory Output identity:
  `/root/capability_proportional_exact_final_v2`; session
  `019fd302-68b5-7a50-958f-4f38b7fdd657`; effective route
  `gpt-5.6-sol/max`; approval `never`; permissions `danger-full-access`.
  Logical read-only behavior was maintained. Hard technical isolation was
  explicitly not predeclared required and is not claimed. Candidate remained
  unchanged, all seven paths were covered, and no external/network/provider
  read or effect occurred.
- Frozen checks: targeted contract 14/14; Skill and plugin validators passed;
  `git diff --check` clean.
- Frozen clean-suite receipt: 159 tests, exactly the two accepted baseline
  failures, zero new failures/errors; log SHA-256
  `91da47e6aec72298e4506c6d35e9728a4ff7f7a7f2ccd9aa263960021d580c96`.
  This suite is not called green.

## Public, installation, and rollback prestate

- Local and live remote `v0.7.2` tag were absent. GitHub Release `v0.7.2` was
  absent. GitHub authentication is active as `cch96` over SSH with repository
  scope; default branch is `main`.
- Current public release and rollback anchor: public non-draft/non-prerelease
  `v0.7.1`, title `HappyCodex 0.7.1`, targeting `main`. Preserve it and its
  public tag without mutation.
- `happycodex@personal` is installed and enabled at
  `0.7.1+codex.20260805155350`, sourced from
  `/home/caichenghang/plugins/happycodex`, with one matching cache directory.
  Preserve this exact package as the rollback prestate until a separately
  authorized activation succeeds.
- Personal source and cache contain the same exact eight package files:
  `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`,
  `README.en.md`, `README.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/agents/openai.yaml`,
  `skills/happycodex/references/execplan.md`, and
  `skills/happycodex/scripts/resource_claim.py`.
- Personal marketplace SHA-256:
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`;
  Codex config SHA-256:
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
- Official cachebuster helper SHA-256:
  `4fe3c5a49212f6e30a2306e245c460e01aaf5e36bc8ad3dd2852c199257eff89`;
  marketplace-name helper SHA-256:
  `7659216759152f83087020b4d2971b4ad3cc13851e2614efc30fc2317ad59d96`.
- Claim receipt and release-notes destinations were absent. The shared
  `/home/caichenghang/.codex` claim root held 20 unrelated claims; repository,
  personal-source, and cache claim roots held zero active claims. Preserve all
  unrelated claims.

## Preservation and release boundary

The candidate commit will contain exactly the six tracked candidate paths plus
the unchanged closed 0.7.2 candidate control. This release plan stays untracked
until the later readiness commit. No PR is planned because this repository's
established reviewed-release protocol publishes directly on `main`.

Preserve every other repository path, evaluator bytes, historical plans,
published tags/releases, external profiles/configuration, marketplace, current
install/cache until its activation gate, unrelated claims, and the exact
published 0.6.5 Skill tree. Do not force, amend, delete, hand-edit
marketplace/config/cache, retry an ambiguous effect, or infer a later grant.

## Six-resource claim

- Helper: `skills/happycodex/scripts/resource_claim.py`.
- Owner: `/root/capability_proportional_executor`.
- Task: `HC-0.7.2-RELEASE-001`.
- ExecPlan: this absolute plan path.
- Receipt:
  `/home/caichenghang/.codex/happycodex-0.7.2-release-HC-RL-001.claim.json`.

Exact resources:

1. `worktree=/home/caichenghang/projects/happycodex`
2. `ref=/home/caichenghang/projects/happycodex::refs/heads/main`
3. `ref=/home/caichenghang/projects/happycodex::refs/tags/v0.7.2`
4. `activation=/home/caichenghang/plugins/happycodex`
5. `activation=/home/caichenghang/.codex/plugins/cache/personal/happycodex`
6. `output=/home/caichenghang/.codex/happycodex-v0.7.2-release-notes.md`

The terminal bootstrap receipt below will bind receipt mode/SHA, six sanitized
claim identities, and immediate verification without copying the raw owner
token. Claims remain active until the exact closeout grant.

## Obligations

| ID | Observable obligation | State |
| --- | --- | --- |
| `RL-CANDIDATE` | Candidate commit contains exactly the six tracked paths plus the closed candidate plan. | verified |
| `RL-PRESERVE` | 0.6.5 tree, v0.7.1 rollback anchor, evaluator, config/marketplace, unrelated paths/claims, and rollback state remain preserved. | verified |
| `RL-VALIDATE` | Frozen checks remain bound; any additional isolated package validation is local and no public effect. | verified |
| `RL-ACTIVATE` | Personal source/cache become one matching 0.7.2 cachebuster package using one official helper call and one plugin-add call. | verified |
| `RL-NOTES` | External release notes exactly match the frozen body below. | verified |
| `RL-COMMIT` | Candidate, readiness, and plan-only closeout commits have exact inventories. | candidate portion verified; readiness identity and closeout pending |
| `RL-PUBLISH` | One non-force main push, one annotated tag/push, and one public GitHub Release bind the admitted readiness commit. | pending |
| `RL-CLOSE` | Root verifies public/local state, closeout is pushed, and the original six claims are released exactly once. | pending |

## Ordered future effects

Every row requires a new exact Root grant after the preceding receipt. No row
authorizes any later effect.

| Order | Future grant | Bounded effect |
| --- | --- | --- |
| 1 | candidate commit | Stage exactly six tracked candidate paths plus the closed candidate plan; commit only those seven paths. Optional isolated package validation may occur before public state. |
| 2 | personal activation | Sync exactly eight package files to the claimed source; invoke the official cachebuster once; invoke `codex plugin add happycodex@personal` once; verify one matching cache. |
| 3 | release notes and readiness commit | Write the frozen external notes, update only this plan, and commit exactly the release plan plus external-note evidence permitted by that grant. |
| 4 | main push | Push `main` to `origin` once, non-force, after exact local/remote identity checks. |
| 5 | tag | Create annotated `v0.7.2` at the admitted readiness commit and push the tag once. |
| 6 | GitHub Release | Create one public non-draft/non-prerelease `HappyCodex 0.7.2` release from frozen notes with no assets. |
| 7 | optional remote verification | Read-only verification of remote main/tag/release and active package; no mutation. |
| 8 | closeout | Update only this plan, create one plan-only closeout commit, push main once non-force, then release the six claims exactly once. |

Partial or ambiguous effects stop without retry or cleanup. Rollback requires a
new exact grant and uses the preserved public/installed 0.7.1 anchor; it is not
silently attempted.

## Frozen release-note body

````markdown
# HappyCodex 0.7.2

This is a reviewed source release, not a maintainer-evaluator certification.

## Highlights

- Admission is capability-proportional: missing optional telemetry is recorded
  as `unverified` and reduces only the guarantee or use that depends on it.
- Normal users choose no mode and enter no continuation phrase.
- Host-authenticated Output identity remains mandatory. Explicit mismatch,
  malformed evidence, authority/scope/path/effect drift, candidate drift, and
  ambiguous or partial effects remain hard stops.
- Explorer/Challenger, Executor, and Exact-final consequences remain bound to
  their exact evidence and authority requirements.

## Validation

- The targeted 14-test contract and existing Skill/plugin validators passed.
- The full offline suite ran 159 tests with exactly the two accepted baseline
  failures, zero errors, and zero new failures.
- A fresh Exact-final returned `GO` with no blockers. It maintained logical
  read-only behavior; hard technical isolation was not predeclared required and
  is not claimed.
- The published v0.6.5 Skill tree remains unchanged.

## Install

```shell
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```
````

## Stop rules

- Stop on identity/config/claim drift, unexpected dirt, staged paths, protected
  tree change, unexpected validation identity, mismatched active package, or
  unexpected remote/tag/release state.
- Never widen scope, overwrite a tag/release/output, force-push, hand-edit
  marketplace/config/cache, retry an ambiguous effect, or treat authentication,
  checks, claims, or the broad release phrase as authority for a later row.
- Record partial effects exactly and return them to Root. Root alone admits each
  effect, decides release completion, and authorizes claim release.

## Bootstrap checkpoint

- Preflight is verified. This plan was persisted before claim mutation.
- Pre-claim plan SHA-256:
  `52a05c887e42a0241578b7d3b555fc49a7e9b0c65a896e3e8d52689cbe4f686f`.
- The Executor acquired the six resources atomically; acquisition exited `0`,
  then the Executor verified the resulting receipt once with exit `0`. After
  handoff, Root independently ran one additional read-only receipt verification
  with exit `0`. Total helper verifications are therefore `2`; Root's check had
  no write or external effect and did not invalidate the claims.
- Receipt mode: `0600`; size: `2582` bytes; SHA-256:
  `57c85348cbfe04da6c93560f17f8d48f1db60fb83fe53e258f51730ffffc3693`.
  Sanitized receipt identity: owner
  `/root/capability_proportional_executor`; task
  `HC-0.7.2-RELEASE-001`; execplan is this exact absolute plan path; resource
  count `6`. Owner-token SHA-256 only:
  `d8ef6e1d1d01fba28c967a63c1056435d4da8efdee5e41c3a2a15029f7d86952`.

| Sanitized resource | Claim-file SHA-256 |
| --- | --- |
| `worktree=/home/caichenghang/projects/happycodex` | `9b692ddff00154b1ec283885bba959efde03c770f63c92ee3e27d04a0ea3a36e` |
| `ref=/home/caichenghang/projects/happycodex::refs/heads/main` | `1dd476adb9792b983504d417968f6dd104a4f407827223e13b7d140bcf455565` |
| `ref=/home/caichenghang/projects/happycodex::refs/tags/v0.7.2` | `0d4abc527313aa128a88050af88dfd5ed230c2fe5d09f4e224415f3e9f95331d` |
| `activation=/home/caichenghang/plugins/happycodex` | `7a7cce4b427d91ed089cc218b8970ec197da795a173efd468cf917957c88f7f1` |
| `activation=/home/caichenghang/.codex/plugins/cache/personal/happycodex` | `4699e4216cb60a32f92ac65332dda9eeb85a41896322d3b0e055e9e0ebb6da16` |
| `output=/home/caichenghang/.codex/happycodex-v0.7.2-release-notes.md` | `71d09eb89c812d899671213a6fecc23c8055d27028e79bcec6d8c866c7e25bcf` |

- Post-acquisition claim-file counts: shared claim root `21` (the release
  output plus 20 preserved unrelated claims), repository claim root `3`,
  personal-source root `1`, and cache root `1`.
- No stage, commit, test, install, cachebuster, release-note write, push, tag,
  GitHub Release, cleanup, or claim release occurred.
- No later release effect is authorized. Phase remains `working`.

## Candidate-commit receipt

- Grant: `HC-0.7.2-CANDIDATE-COMMIT-002`. Before the commit effect, the public
  Install block above was corrected to the GitHub marketplace commands while
  this control remained untracked. Corrected pre-effect plan SHA-256:
  `c0826b01df05f9fee873351d6c6a2a798f27886ffd38c26a688e149e1d7f1ab5`.
- The Executor silently verified the claim receipt before the effect and again
  after the commit, both with exit `0`. Together with the two bootstrap-era
  verifications recorded above, the receipt has had four helper verifications;
  none exposed its owner token or changed claim state.
- Pre-effect source, index, candidate, protected-tree, remote, publication,
  release-note, installation, marketplace, and configuration checks matched
  their frozen values. Exactly the authorized seven candidate paths were
  staged. Cached name-status was six `M` plus the candidate plan `A`; cached
  diff check was clean; staged tree was
  `5fdd37971fc03cd77cbab1401cd39063bb5b751b`; full-index binary cached diff
  SHA-256 was
  `e48ee388fa7b0a5fabab5654e9fea25570c4ff85aa05f99fbcd823d1f435f601`.
- Exactly one non-amended commit was created:
  `4325fe2a7d0c0e2c4c077a7070e33a5f4d001245`, subject
  `feat: release HappyCodex 0.7.2 capability-proportional admission`, sole
  parent `c9476242c259cfe84ba2c9b7866f62d5694c3ee6`, tree
  `5fdd37971fc03cd77cbab1401cd39063bb5b751b`.
- Exact commit inventory: modified `.codex-plugin/plugin.json`, `README.en.md`,
  `README.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`; added
  `docs/execplans/happycodex-0-7-2-capability-proportional-admission.md`.
- Post-commit index was empty and this release plan was the only untracked
  path. Local `origin/main` and live remote `main` remained at the sole parent;
  local/remote `v0.7.2` and GitHub Release `v0.7.2` remained absent. Release
  notes remained absent and all six claims remained valid.
- Candidate package tree remained
  `49dd643cdce8be6bad3cb6578a6b3a48bfb9df0c`; package artifact SHA-256
  `8f4f7b9c19e5b664f392a1bdb673da34ae668d595dae917f14856f5e5567a2d9`;
  semantic SHA-256
  `47b52c20f2fd52efb393fd0fb86f18551049b3236bb8964adb7341d0d3d1ba18`;
  ProductArtifact record SHA-256
  `5b3e951255bd40fa9b891e43f901289a96d8feeadca54d786434f1b03485f758`.
  The closed candidate plan remained
  `d21165d0998cc60101fa2f677ddc5429e48e959cb2defb9ecfbfe5f654a10f7d`
  and the protected 0.6.5 Skill tree remained
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- The active personal install remained enabled at
  `0.7.1+codex.20260805155350`; its exact eight-file source and sole matching
  cache remained byte-identical. Marketplace SHA-256 remained
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`
  and config SHA-256 remained
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
- Frozen validation receipts were inherited because candidate bytes were
  unchanged; no test or validator was rerun. No push, tag, GitHub Release,
  release-note output, activation, cachebuster, plugin add, config/marketplace
  edit, claim release, branch/PR, force, amend, or retry occurred. Phase remains
  `working`; Root owns the next exact grant.

## Isolated-install failure receipt

- Grant: `HC-0.7.2-ACTIVATION-003`. Preflight silently verified the six-claim
  receipt with exit `0`, bringing total helper receipt verifications to `5`.
  Repository, commit, candidate/product identities, protected tree, index,
  release-plan SHA-256
  `8760b059b53c508da8c1f4770b5c5ecfb9db7a48a3fee49900baab16ca7380d5`,
  remote/public state, release-note absence, claim counts, personal 0.7.1
  installation, source/cache, marketplace, config, and helper identities all
  matched the frozen prestate.
- Exactly one temporary root was created:
  `/tmp/happycodex-0.7.2-isolated-install-Z4PUk9`, mode `0700`, with deterministic
  `source`, `home`, and `codex-home` subpaths. Its local no-network clone was
  clean at HEAD `4325fe2a7d0c0e2c4c077a7070e33a5f4d001245`, tree
  `5fdd37971fc03cd77cbab1401cd39063bb5b751b`.
- With only the isolated HOME and CODEX_HOME, marketplace add was invoked
  exactly once and exited `0`: sanitized fields were marketplace `happycodex`,
  installed root the exact temp source, and `alreadyAdded=false`; sanitized
  receipt SHA-256
  `526a5834ab411c08db0412837286b9be4447a6d93251c9a1c2d51542a2fb7d13`.
  Plugin add was invoked exactly once and exited `0`: sanitized fields were
  `happycodex@happycodex`, marketplace `happycodex`, version `0.7.2`, auth
  policy `ON_INSTALL`, and the exact isolated installed path; sanitized receipt
  SHA-256
  `b835ea83e93ec89ac612183d45848dbf7a3a0b57bd29f30ce7a11409200af5c3`.
  Both commands emitted the non-fatal warning that PATH aliases are refused
  under a temporary CODEX_HOME.
- Isolated plugin listing reported installed and enabled `happycodex` version
  `0.7.2` from marketplace `happycodex`; sanitized listing SHA-256
  `55c21fbf4737c6a20ae4de8a626539adf8911f251905c1bf02ae380f459051a4`.
  The selected eight committed package files were byte-equal between source
  and install, with ordered package-manifest SHA-256
  `c6e18086403cfe7df3d59f10304b1f9ab5801fb4c481fb98304156df0f9a0597`
  and Skill SHA-256
  `53e768ac3cecbcc564609e8f879758286b457a84d70cc82601f34397bdb18f33`.
- The mandatory exact-eight-file inventory gate failed. Both the clean source
  and installed path contained `4,646` files, with `4,638` paths outside the
  eight-file package boundary, including `.git`, evaluator, test, and release
  support content. Their relative file-path inventory SHA-256 was
  `a32b423d69ad76ff4c693f3696a6aa11a13ddccc606bff93d2c4851605f1b732`.
  Therefore isolated validation is not satisfied.
- Per the stop rule, the exact temporary root remains intact for inspection;
  no removal or retry occurred. Personal activation was not attempted: no
  package synchronization, cachebuster helper, marketplace-name helper, or
  personal plugin-add invocation occurred. The personal install remains
  enabled at `0.7.1+codex.20260805155350`, its exact eight-file source/cache
  remain byte-equal, and marketplace/config hashes remain unchanged.
- Repository HEAD/tree/status/index and release-notes absence remained
  unchanged after the failed isolated gate. No stage, commit, push, tag,
  GitHub Release, provider/test invocation, claim release, branch/PR, force,
  hand edit, rollback, or out-of-scope cleanup occurred. Phase remains
  `working`; Root must provide a new exact task before any repair, cleanup, or
  activation, and a new task is still required before consuming any future
  active Skill.

## Root package-boundary correction

- Grant: `HC-0.7.2-BOUNDARY-CORRECTION-ACTIVATION-004`. This section preserves
  the adverse isolated-failure receipt above and corrects only its invalid
  interface classification. It is not a waiver, retry, product change, or
  Outcome amendment. Current preflight silently verified the six-claim receipt
  with exit `0`, bringing total helper receipt verifications to `6`; all other
  frozen repository, public, candidate, protected, and personal prestates
  matched.
- The retained isolated installed path is a real directory. Recursive
  source/install comparison excluding `.git` exited `0`, and each side has
  exactly `57` non-`.git` files. Candidate marketplace `source.path` is `./`,
  intentionally binding the whole public repository checkout rather than an
  eight-file packaging projection.
- Released `v0.7.1` has the same `source.path: "./"`, `56` repository files,
  and the same exact eight-file runtime/package subset. The candidate has `57`
  repository files because it adds the closed candidate control. No minimal
  repository-checkout claim is made.
- The candidate's eight-file runtime/package subset remained byte-equal across
  source/install. Its ordered package-manifest SHA-256 was
  `c6e18086403cfe7df3d59f10304b1f9ab5801fb4c481fb98304156df0f9a0597`
  and Skill SHA-256 was
  `53e768ac3cecbcc564609e8f879758286b457a84d70cc82601f34397bdb18f33`.
  Runtime `skills/happycodex/SKILL.md` contains no `evaluation/` link, and the
  frozen plugin-validator receipt passed.
- The plugin-creator contract permits additional plugin-root folders and does
  not define a whole-root eight-file projection requirement. Therefore only
  the unsupported whole-installed-root-eight-file gate is retired. Isolated
  validation is admitted successful under the corrected distinction between
  the repository-backed marketplace source and the exact runtime/package
  subset; `RL-VALIDATE` is verified and personal activation remains pending.
- This classification is invalidated only if marketplace `source.path` ceases
  to be `./`, source/install cease exact equality, the runtime eight-file subset
  mismatches, evaluator becomes linked from Runtime, or the plugin validator
  fails. Phase remains `working` until an exact activation receipt is recorded.

## Boundary cleanup and personal-activation receipt

- The Root correction above was persisted before activation; its pre-activation
  plan SHA-256 was
  `a6a8e4905baab1345f228820df117f893b07234dc3eb1be314785c8b676498f2`.
  The retained root was then revalidated as the exact non-symlink 0700 path,
  clean source HEAD/tree, real installed directory, equal 57-file non-`.git`
  source/install surfaces, and was removed once with exact-path non-force
  `rm -r`. It is absent; no other cleanup occurred.
- Immediately before activation, the claim receipt was silently verified with
  exit `0`; the enabled `0.7.1+codex.20260805155350` source, sole cache,
  eight-file byte equality, marketplace/config/helper identities, repository,
  and claim counts still matched. Exactly the eight committed package paths
  were mechanically synchronized from HEAD into the existing personal source.
  No path was created or deleted, existing `0600` file modes were preserved,
  every file was byte-equal to its HEAD blob, base version was `0.7.2`, ordered
  package-manifest SHA-256 was
  `c6e18086403cfe7df3d59f10304b1f9ab5801fb4c481fb98304156df0f9a0597`,
  and Skill SHA-256 was
  `53e768ac3cecbcc564609e8f879758286b457a84d70cc82601f34397bdb18f33`.
- The official cachebuster helper was invoked exactly once without an override
  and exited `0`, changing only version `0.7.2` to
  `0.7.2+codex.20260805182647`; generated token `20260805182647`; sanitized
  receipt SHA-256
  `e142b7b64b57bacda8e26d6daf19f977fdf38e7d0e0255a46412be0a1124b7ee`.
  The marketplace-name helper was invoked exactly once, exited `0`, and returned
  exactly `personal`; sanitized receipt SHA-256
  `ced74b796d9cbabdee23a47815e8bea6182081a965c099f92fed7ea950d69782`.
- `codex plugin add happycodex@personal --json` was invoked exactly once and
  exited `0`. Sanitized terminal fields bind plugin `happycodex@personal`,
  marketplace `personal`, auth policy `ON_INSTALL`, version
  `0.7.2+codex.20260805182647`, and installed path
  `/home/caichenghang/.codex/plugins/cache/personal/happycodex/0.7.2+codex.20260805182647`;
  sanitized receipt SHA-256
  `237a3099cfce181ecef73c49b3b1845ac2eb1e0c4873f6667e5194e2569e16f6`.
  CLI replacement of the obsolete cache was unambiguous; no manual cache
  deletion, edit, retry, or rollback occurred.
- Terminal state has one sole personal cache directory and reports the plugin
  installed and enabled at the exact generated version. Source/cache each have
  exactly the eight package files and are byte-identical; ordered manifest
  SHA-256 is
  `d2dbf43797e55f1dd64845868d24f7238be036a7b04d2d93a6a6e58f10e45c38`.
  Their manifest SHA-256 is
  `a3ddd038443c5589d2036933c05f959e00e78a23f1de5080a0bbc9980b80b6c1`;
  after normalizing only its version to committed base `0.7.2`, source, cache,
  and HEAD canonical manifest SHA-256 all equal
  `f7d4848a917d14b127e9997adde9adae42971904c325bb5db2b318008aff690e`.
  All other seven files equal HEAD and both Skill hashes remain
  `53e768ac3cecbcc564609e8f879758286b457a84d70cc82601f34397bdb18f33`.
- Marketplace SHA-256 remains
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`
  and config SHA-256 remains
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
  Repository HEAD/tree/status/index, local/live remote main, absent local/remote
  `v0.7.2` tag, absent GitHub Release and notes output, candidate package and
  ProductArtifact identities, and protected 0.6.5 tree remain unchanged. A
  final silent claim verification exited `0`, bringing total helper receipt
  verifications to `8`; all six claims remain valid.
- `RL-ACTIVATE` is verified and phase advances to `activation`. No stage,
  commit, push, tag, GitHub Release, release-note output, test/provider call,
  marketplace/config hand edit, claim release, branch/PR, force, amend, or
  retry occurred. A new task/thread is required to consume the newly active
  Skill; this running task does not claim to have loaded it.

## Release-readiness receipt

- Grant: `HC-0.7.2-READINESS-COMMIT-005`. Immediate preflight silently verified
  all six claims with exit `0`, bringing total helper receipt verifications to
  `9`. Repository HEAD/tree/parent/subject/seven-path candidate inventory,
  empty index, sole untracked plan SHA-256
  `b4daad478c4c27131ac7d1dcabd09887a11f51cd524ec54737b8aefe5f2d0581`,
  local/live remote main, absent local/remote tag, absent GitHub Release and
  notes path, activation, marketplace/config, candidate/ProductArtifact,
  Exact-final, frozen tests, protected 0.6.5 tree, claim counts/unrelated
  resources, and isolated-temp absence all matched their admitted receipts.
- Candidate, validation, boundary correction, and personal activation evidence
  is admitted unchanged. `RL-PRESERVE` is verified. The personal plugin remains
  installed and enabled at `0.7.2+codex.20260805182647`, with one sole cache,
  exact eight-file source/cache byte equality, only the admitted manifest
  version suffix differing from the committed package, unchanged Skill,
  marketplace, and config identities.
- The frozen external notes were created exactly once at
  `/home/caichenghang/.codex/happycodex-v0.7.2-release-notes.md` through
  `apply_patch`. They are mode `0600`, size `1221` bytes, SHA-256
  `263d3515ea323f756196668c95abd89d012a1a1cced62fc530400499d82dad0c`,
  have exactly one final newline, and are byte-equal to an independently
  extracted body between the four-backtick fence above, excluding that fence.
  `RL-NOTES` is verified.
- The candidate portion of `RL-COMMIT` is verified. This plan is the sole path
  authorized for the readiness commit. Because a commit cannot contain its own
  subsequently assigned identity, the readiness commit SHA/tree/parent/subject
  and one-path inventory are necessarily obtained only after the commit and
  will be recorded in the later closeout receipt. The plan-only closeout portion
  remains pending.
- `RL-PUBLISH` and `RL-CLOSE` remain pending. Phase advances to `readiness`.
  This receipt authorizes no push, tag, GitHub Release, claim release, test,
  provider/validator, package/cache change, branch/PR, force, amend, cleanup,
  retry, or other path.
