# HappyCodex 0.14.0 Goal-continuation release

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: inspect Goal self-continuation; obtain a Fable 5
  dialectical review; implement the minimal HappyCodex refinement; discard the
  obsolete 0.10 work and restart from the latest source; use a 200-line hard
  cap for the Skill; `好的发布吧`.
- Outcome: publish the validated Goal-continuation refinement as HappyCodex
  `0.14.0` to `cch96/happycodex` default branch `main`, one annotated tag
  `v0.14.0`, and one public GitHub Release with no assets, then activate the
  matching personal plugin locally.
- Done evidence: the released immutable commit contains only the allowed
  closure over `v0.13.0`; required checks and one fresh blocker-only exact-final
  pass; remote main, peeled tag, Release, personal source, and enabled cache all
  resolve to that release identity modulo one generated cachebuster.

## Workspace and change boundary

- Workspace: `/home/caichenghang/projects/happycodex`; branch
  `codex/happycodex-goal-continuation`; baseline `v0.13.0` commit
  `94eb4a54f554ede626059bb5770e3aefd3bda679`.
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `docs/execplans/happycodex-0-14-goal-continuation.md`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `evaluation/provider-fixtures-v1.json`
  - `evaluation/hidden-oracles-v1.json`
  - `evaluation/report-schemas-v1.json`
  - `tests/attestation_fixtures.py`
  - `tests/test_attestation_contract.py`
- Repository freeze resources before exact-final: the exact Git index and one
  release commit on the candidate branch. External mutable resources after
  exact-final `GO`: local `main`; local and remote `refs/tags/v0.14.0`; remote
  `main`; GitHub Release `cch96/happycodex:v0.14.0`; one new rollback snapshot;
  `/home/caichenghang/plugins/happycodex`; and `happycodex@personal` source/cache.
- Preserve every published tag and tree; exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; non-target branches/worktrees;
  0.10 archive refs and verified bundle; marketplace/config/credentials;
  external role configuration; and the enabled 0.13 source/cache until rollback
  evidence is durable.
- Exclusions: compatibility paths, migration, controller, ledger, state
  machine, new durable record type or evaluator unit, provider/model evaluation,
  force push, history rewrite, asset upload, branch/worktree/archive cleanup,
  retry after an ambiguous effect, or mutation outside the named resources.

## Supported workflows and candidate closure

- Distinguish a same-Goal in-boundary checkpoint from a new Goal, Outcome,
  change boundary, effect target/identity/cap, or pending user decision.
- A Goal, user reply, or review verdict grants no unrecorded authority. Missing
  Goal identity pauses mutation. `GO` validates only its reviewed candidate.
- Permit one already pre-authorized in-boundary `NOT_YET` repair only while its
  repair and replacement-review budget remains; otherwise return to the user.
- Keep four durable record types, five behavior units, three fixed holdout
  pairs, twelve provider units, one exact-final, and stateless verification.
- Keep `SKILL.md` at most 200 lines and both READMEs at most 80 lines with
  natural formatting.
- Consumer-native candidate: one clean Git commit whose tree is the complete
  allowed closure over `v0.13.0`. Public Git, Release, and local activation
  consume that commit. The personal copy may differ only by changing manifest
  `0.14.0` to one helper-generated `0.14.0+codex.<UTC-seconds>` version.

## Checks and terminal review

- Before freeze: exact branch/HEAD/status/index/path inventory; JSON parsing;
  focused public-contract/schema tests; full offline standard-library suite;
  Skill and plugin validators; `git diff --check`; product and evaluator line
  limits; topology/record inventory; protected-tree digest; two oracle-blind
  forward cases; remote/tag/Release absence; current install and rollback facts.
- Freeze one exact release commit, repeat the required commit-bound checks, and
  prove its tree equals the staged candidate tree.
- Run exactly one fresh native `happycodex_exact_final`, no inherited history,
  read-only and blocker-only, against readable immutable `v0.13.0`, the release
  commit, this Outcome, boundary, preservation rules, supported workflows, and
  check receipts. Cap one invocation and one terminal verdict. `NOT_YET`, lost
  terminal, or required unknown stops; no automatic repair or rereview.

## External effects and one-shot observation

- Rollback snapshot: create one uniquely named directory under
  `/home/caichenghang/.codex/happycodex-release-installs/` containing the exact
  pre-mutation personal source and enabled 0.13 cache; verify inventories and
  checksums; never delete it in this task.
- Push main: after proving remote main still equals the baseline, make one
  non-force `HEAD:main` push and read back the exact SHA; then fast-forward local
  `main` once to the same commit. No retry.
- Tag: create one annotated local `v0.14.0` peeling to the release commit, push
  it once, and read back local/remote object and peel. No retry.
- GitHub Release: create one public, non-draft, non-prerelease, zero-asset
  Release for `v0.14.0` using the exact title/body below; read back all fields
  and body. No retry.
- Personal source: materialize the seven-file runtime projection from the
  release commit in one isolated directory; invoke the official plugin-creator
  cachebuster helper once; validate it; prove the personal marketplace still
  points to `/home/caichenghang/plugins/happycodex`; copy that exact projection
  to the personal source once and verify byte equality. Do not edit marketplace
  or config files.
- Local install: invoke `codex plugin add happycodex@personal --json` once;
  read back enabled state, generated `0.14.0+codex.*` identity, source/cache
  equality, and cachebuster-normalized equality to the release. Command exit
  alone is not success.
- Treat every mutation as a separate effect. Any partial, ambiguous, unknown,
  non-fast-forward, or not-visible result stops all later mutations without
  retry or cleanup.

## Exact GitHub Release

- Title: `HappyCodex v0.14.0`
- Notes:

  HappyCodex v0.14.0 makes Goal continuation scope-safe without adding a second
  control plane.

  Highlights:
  - Creates or recreates a native Goal only on explicit user request; missing
    Goal identity pauses mutation instead of manufacturing continuity.
  - Continues autonomously through in-boundary candidate checkpoints only while
    Goal, Outcome, boundary, surface, effect identity/cap, and pending decisions
    remain unchanged.
  - Makes user replies and `GO` candidate-scoped rather than implicit authority
    for deployment, canary exceptions, backfills, or a new phase.
  - Adds seven independent, closed, oracle-blind continuation cases without a
    controller, ledger, state machine, record type, or evaluator unit.

  Validation:
  - Full offline suite and focused continuation contracts pass.
  - Skill/plugin validators, JSON validation, line budgets, protected-tree, and
    Git diff checks pass.
  - Fresh blocker-only exact-final: GO.

  Install:
  `codex plugin marketplace add cch96/happycodex`
  `codex plugin add happycodex@happycodex`

  Start a new Codex task after installation.

## Done, stops, and recovery

- Done only when all required checks pass; exact-final is `GO`; remote main and
  the peeled annotated tag equal the release commit; GitHub reports the exact
  public zero-asset Release; personal source/cache equal the released runtime
  modulo one cachebuster; preservation holds; and no required fact is unknown.
- Stop on source/version/target/ref/path/index drift, remote main movement,
  schema/topology/record expansion, answer leakage, test regression, line-limit
  breach, protected-tree drift, missing rollback evidence, adverse review, or
  any partial/ambiguous effect.
- Only a deterministic pre-effect local failure may be corrected inside the
  named repository paths and fully revalidated before freeze. After an external
  attempt, preserve evidence and do not retry. After compaction, reread this
  plan and rederive candidate, refs, Release, source, cache, and effect facts.
