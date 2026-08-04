# HappyCodex 0.6.6 prompt proportionality

## Current checkpoint

- Phase: `working`
- Owner: the runtime-selected fixed HappyCodex Executor for this task
- Source: branch `main`, commit
  `1446031d107ef32d176ad3ed573cadd6bd20a3e7`, tree
  `eb726ad8ffb6c04cc02205cc05cbe9c5f12b527b`
- Prestate: clean; `main...origin/main`
- Published product: immutable tag `v0.6.5`; `skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`
- Candidate: reviewed local working-tree version `0.6.6`; not yet staged,
  committed, pushed, synced to the personal source, or installed
- Verification snapshot evidence: temporary commit
  `7c4204988129862733fcfca76c3ec707f212bfbd`, tree
  `bbb181df5c81bff4f2f123a543cb31f215943eeb`, Skill tree
  `c0fe3daba16699390b07eb80ed1d1023da236f6a`
- Frozen package identity: artifact SHA-256
  `455d394f23f074aa55abe1ca4398ec26c1a4456c18457b3c88e45e49e3f8872a`;
  semantic SHA-256
  `528c042483c5912cbe0a0128fa1a22b9b23921147a52ccd7a906bbc1f6aaf05b`
- Selected checkpoint: this file, the current authorized working-tree diff, and
  the bound temporary verification snapshot evidence; the temporary commit/tree
  is neither a shared commit nor a released identity
- Active installed cache: `0.6.5+codex.20260804105551`; installed Skill SHA-256
  equals the v0.6.5 Skill SHA-256
  `07421636583ddec11308bf235fe4b49b2d0b11598944303f5287574f631d4bb5`;
  active bytes remain unchanged
- Open gates: remote-prestate verification, exact candidate commit and checks,
  first push, personal-source sync and cachebuster, one install, activation
  verification, ExecPlan receipt commit and second push, final clean-state check

## Bound pre-effect state

- Repository branch: `main`; local `HEAD` and local `origin/main` are both
  `1446031d107ef32d176ad3ed573cadd6bd20a3e7`.
- Remote: `origin` is `git@github.com:cch96/happycodex.git`.
- Worktree: exactly the seven paths in the grant below; candidate source
  manifest version is `0.6.6`.
- Active plugin: `happycodex@personal` version
  `0.6.5+codex.20260804105551`.
- Marketplace file: `/home/caichenghang/.agents/plugins/marketplace.json`, name
  `personal`, entry source `./plugins/happycodex`.
- Resolved personal source: `/home/caichenghang/plugins/happycodex`, a separate
  non-Git directory on old 0.6.5 cachebuster bytes, not this repository. Its
  packaged marketplace file already matches the repo; its manifest, README, and
  Skill are the three expected old packaged files.

## Request and Outcome

The user authorized execution with `好的执行吧` after the completed
`claude-fable-5`/`max` advisory verdict `MINOR_REVISE` on HappyCodex prompt
proportionality.

The user then amended the Outcome verbatim: `commit 到主分支 push然后重新安装`.

Implement a local 0.6.6 source candidate whose public Skill:

- reasons only about material failures reachable through supported workflows,
  including compaction, concurrency, and partial effects;
- treats the user, maintainer, workspace, and selected configuration as
  non-adversarial but fallible unless the request or source establishes
  otherwise, verifying state and identity rather than motive;
- prefers the smallest sufficient control and requires explicit user authority
  before expanding scope or trust boundaries;
- neutralizes adversarial vocabulary and removes evaluator implementation
  mechanics from the public Skill without weakening reliability obligations;
- stops design comparison and challenge once remaining alternatives cannot
  change the Outcome inside the stated trust boundary.

The extended Outcome is to commit the already reviewed 0.6.6 candidate directly
to local `main`, verify it as a real commit, push that exact commit to
`origin/main`, reinstall locally from the existing `personal` marketplace, then
commit and push the control-only receipt. Completion requires the pushed source,
personal source, active install, receipts, and final Git state to match the
identities below.

## Preservation and exclusions

Preserve the fixed Executor/Root split, exact grants, durable recovery,
prestate and identity checks, one-shot and partial-effect stop rules, secret
handling, separate external effects, real RED, and fresh isolated exact-final
review. Do not add a reference, gate, durable record type, phase, reviewer,
controller, compatibility path, or evaluator mechanism. Do not link evaluator
maintenance files from `skills/happycodex/SKILL.md`.

Keep the published `v0.6.5` tag/tree, external role configuration, marketplace
file, and existing caches unchanged. This extension authorizes only the ordered
commit, push, personal-source sync, cachebuster, install, verification, and
receipt effects below. Exclude tags, GitHub Releases, PRs, branch creation,
marketplace/config hand edits, cache deletion, evaluator/Fable/model review, and
product redesign.

## Exact grants and resources

The fixed Executor may use `apply_patch` only on:

1. `docs/execplans/happycodex-0-6-6-prompt-proportionality.md`
2. `skills/happycodex/SKILL.md`
3. `.codex-plugin/plugin.json`
4. `README.md`
5. `AGENTS.md`
6. `tests/test_attestation_contract.py`
7. `tests/attestation_fixtures.py`

No other path may change. Unexpected dirt, source drift, a required unlisted
path, a weakened retained invariant, a new cumulative failure, an external
effect, or uncertainty between prompt proportionality and evaluator
architecture stops execution and returns the decision to Root.

For the later exact effect grant, mutable resources are limited to:

- repository index/ref `main`, remote `origin/main`, and the seven repository
  paths above, followed by an ExecPlan-only receipt commit;
- `/home/caichenghang/plugins/happycodex/.codex-plugin/plugin.json`,
  `/home/caichenghang/plugins/happycodex/README.md`, and
  `/home/caichenghang/plugins/happycodex/skills/happycodex/SKILL.md`, with the
  manifest cachebuster changed only by the plugin-creator helper;
- Codex plugin cache/config effects caused only by exactly one
  `codex plugin add happycodex@personal` invocation.

Do not hand-edit the marketplace file or any Codex configuration/cache. This
turn authorizes only this ExecPlan amendment; Root must issue the exact effect
grant before any resource above is mutated.

## Obligations

- Set the candidate version to `0.6.6` and add a concise README entry.
- Keep `SKILL.md` concise, imperative, and limited to non-obvious procedural
  guidance; create no auxiliary Skill documentation.
- Narrow qualification to material uncertainty and supported-flow failures.
- Replace public adversarial or motive-oriented framing with positive state,
  identity, authority, and outcome checks; do not enumerate attacker behavior.
- Simplify resource-claim and cost/effect implementation details while
  retaining conflict detection, exact effect boundaries, separate authority,
  and stop-on-drift behavior.
- Record in `AGENTS.md` the immutable historical `v0.6.5` tree, this exact
  candidate-only authorization, and the non-adversarial-but-fallible maintainer
  boundary while leaving evaluator constraints otherwise unchanged.
- Update the attestation contract tests so the immutable tag/tree and the local
  0.6.6 working-tree candidate are both testable before and after a future
  commit, including proportionality vocabulary checks.
- Keep `BASELINE_REVISION` fixed while binding `CANDIDATE_REVISION` to `HEAD`,
  whose product identity already resolves the last package-changing commit.
  Assert that future-commit invariant in the focused repository contract.

## Baseline and acceptance

Accepted baseline:

- `python3 -B -m unittest -v tests.test_attestation_contract`: 13/13 green.
- Cumulative suite: 158 tests with exactly two accepted failures:
  `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
  with `mutation='old-source'`, and
  `test_old_source_components_cannot_back_a_new_dirty_evalspec`.

Verified acceptance:

- Root created a fresh temporary committed snapshot using the actual repository
  `CANDIDATE_REVISION = "HEAD"` with no process-local override.
- Focused contract passed 13/13; Skill and plugin validators passed.
- The full suite ran 158 tests with exactly the two accepted baseline failures,
  `failures=2`, `errors=0`; Root's classifier exited 0.
- `git diff --check HEAD^` passed and the temporary snapshot status was clean.

## Exact effect order

1. Verify remote `main` still equals
   `1446031d107ef32d176ad3ed573cadd6bd20a3e7`; stop on drift.
2. Stage only the seven granted candidate paths and commit directly on `main`
   with `feat: refine HappyCodex prompt proportionality for 0.6.6`.
3. On that real commit, run the focused contract, Skill validator, plugin
   validator, `git diff --check`, and the 158-test classifier. Accept only the
   exact two frozen baseline failures, with no new failure or error.
4. Push that exact candidate commit to `origin/main`.
5. After verifying every other packaged file already matches, mechanically copy
   only `.codex-plugin/plugin.json`, `README.md`, and
   `skills/happycodex/SKILL.md` from the pushed repository to the resolved
   personal source.
6. Run plugin-creator `update_plugin_cachebuster.py` exactly once on
   `/home/caichenghang/plugins/happycodex` with its default UTC cachebuster.
7. Validate that source, then invoke exactly once:
   `codex plugin add happycodex@personal`.
8. Verify plugin list, installed manifest/version, installed Skill hash equality
   with the pushed Skill, exactly one `+codex.` suffix in the source manifest,
   and continued availability of the old cache.
9. Update only this ExecPlan with exact receipts, commit it as
   `docs: record HappyCodex 0.6.6 local activation`, and push `origin/main`
   again. This docs-only commit does not change product identity because product
   resolution selects the last `PACKAGE_PATHS`-changing commit.
10. Verify the repository is clean and `HEAD` equals `origin/main`.

## Stops and rollback preservation

Stop on remote drift, changed worktree/prestate, an unexpected path, any new
test failure or error, source mismatch, invalid cachebuster, ambiguous or
partial install, or push/install failure. Never retry the same external effect
automatically.

Do not delete the existing 0.6.5 cache. If install success is not clear, stop
with the old active state and exact evidence rather than manufacturing success.

## Current receipt

- Frozen candidate and exact-final `GO` remain bound to the verification
  identities and acceptance results above.
- This pre-effect amendment changed only this ExecPlan. No network, stage,
  commit, push, personal-source write, marketplace/config write, cachebuster,
  install, cache mutation, evaluator/Fable/model review, release, or publication
  effect occurred in this turn.
- Effect receipt: pending Root's exact effect grant.
