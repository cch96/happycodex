# HappyCodex 0.14.1 ExecPlan-clarity release

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: audit whether the proposed workflow refinements are
  over-designed; keep only the minimal ExecPlan wording changes; `好的`;
  `发布吧`.
- Outcome: publish the validated ExecPlan-template clarification as HappyCodex
  `0.14.1` to `cch96/happycodex` default branch `main`, one annotated tag
  `v0.14.1`, and one public GitHub Release with no assets.
- Done evidence: one immutable release commit contains exactly the allowed
  closure over `v0.14.0`; required checks and one fresh blocker-only exact-final
  pass; remote main and the peeled annotated tag equal that commit; and GitHub
  reports the exact public, non-draft, non-prerelease, zero-asset Release.

## Workspace and change boundary

- Workspace: `/home/caichenghang/.codex/worktrees/e0bb/happycodex`; branch
  `codex/happycodex-execplan-clarity`; baseline `v0.14.0` commit
  `d8d3c7a6deb5528985e8831f64298bc779014075`.
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `docs/execplans/happycodex-0-14-1-execplan-clarity.md`
  - `skills/happycodex/references/execplan.md`
  - `tests/attestation_fixtures.py`
  - `tests/test_attestation_contract.py`
- Mutable resources before exact-final: the exact Git index and one release
  commit on the candidate branch. Mutable resources after exact-final `GO`:
  `origin:refs/heads/main`; local and remote `refs/tags/v0.14.1`; and GitHub
  Release `cch96/happycodex:v0.14.1`.
- Preserve every published tag and reachable tree; exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; non-target branches/worktrees;
  evaluator topology, schemas, and source behavior; marketplace/config and
  credentials; and all personal plugin source/install/cache state.
- Exclusions: a user-visible Session/Outcome protocol; controller, ledger,
  scheduler, resource receipt, cleanup state machine, recovery snapshot,
  compatibility path, migration, evaluator or provider/model change, local
  plugin activation, force push, history rewrite, asset upload, cleanup, or
  retry after an ambiguous effect.

## Supported workflows and candidate closure

- During iteration, record focused real-path checks; after candidate scope is
  stable and before native freeze, record the required cumulative or full suite.
- When applicable, name task-created or reused containers, temporary database
  roles, and reserved ports or sockets in mutable resources. Check that
  task-created temporary resources are cleaned up or explicitly retained.
- Keep user-visible task/session behavior native. A request that changes an
  earlier judgment remains an amendment to that judgment; do not add HappyCodex
  continuity state for it.
- Keep `SKILL.md`, READMEs, evaluator topology, schemas, and runtime behavior
  byte-identical to `v0.14.0`. Keep the ExecPlan template within 80 lines.
- Consumer-native candidate: one clean Git commit whose tree is the complete
  allowed closure over `v0.14.0`. Public Git and the GitHub Release consume that
  immutable commit.

## Checks and terminal review

- During iteration: inspect exact Git/path diff; run the public metadata/template
  contract, Skill validator, plugin validator, import check, and
  `git diff --check`.
- After candidate scope is stable and before freeze: run the full offline
  standard-library suite; verify JSON, line budgets, protected published trees,
  exact changed-path closure, remote-main identity, and tag/Release absence.
- Freeze one exact release commit, then repeat the required commit-bound full
  suite, import, Skill/plugin, diff, path, tree, and remote precondition checks.
- Run exactly one fresh native `happycodex_exact_final`, no inherited history,
  read-only and blocker-only, against readable immutable `v0.14.0`, the release
  commit, this Outcome, boundary, preservation rules, supported workflows, and
  check receipts. Cap one invocation and one terminal verdict. `NOT_YET`, lost
  terminal, or a required unknown stops; no automatic repair or rereview.

## External effects and one-shot observation

- Push main: after proving remote main still equals the baseline and the local
  candidate equals the reviewed commit, make one non-force `HEAD:main` push;
  read back the exact remote SHA with `git ls-remote`. No retry.
- Tag: create one annotated local `v0.14.1` peeling to the release commit, push
  that tag once, and read back local/remote object type and peeled SHA. No retry.
- GitHub Release: create one public, non-draft, non-prerelease, zero-asset
  Release for `v0.14.1` using the exact title/body below; read back tag, title,
  body, state, target, URL, and assets. No retry.
- Treat every mutation as a separate effect. Any partial, ambiguous, unknown,
  non-fast-forward, or not-visible result stops all later mutations without
  retry or cleanup.

## Exact GitHub Release

- Title: `HappyCodex v0.14.1`
- Notes:

  HappyCodex v0.14.1 clarifies ExecPlan testing order and temporary runtime
  resources without adding a new control plane.

  Highlights:
  - Keeps focused real-path checks during iteration and places the required
    cumulative or full suite after candidate scope is stable and before native
    freeze.
  - Makes task-created or reused containers, temporary database roles, and
    reserved ports or sockets explicit mutable-resource examples.
  - Checks that task-created temporary resources are cleaned up or explicitly
    retained when applicable.
  - Adds no Session/Outcome protocol, controller, ledger, scheduler, resource
    receipt, cleanup state machine, or recovery snapshot.

  Validation:
  - Full offline suite, import check, Skill/plugin validators, and Git diff
    checks pass.
  - Fresh blocker-only exact-final: GO.

  Install:
  `codex plugin marketplace add cch96/happycodex`
  `codex plugin add happycodex@happycodex`

  Start a new Codex task after installation.

## Done, stops, and recovery

- Done only when all required checks pass; exact-final is `GO`; remote main and
  the peeled annotated tag equal the reviewed release commit; GitHub reports the
  exact public zero-asset Release; preservation holds; and no required fact is
  unknown.
- Stop on source/version/target/ref/path/index drift, remote main movement, a
  new failure, protected-tree drift, adverse review, or any partial/ambiguous
  effect.
- Only a deterministic pre-effect local failure may be corrected inside the
  named repository paths and fully revalidated before freeze. After an external
  attempt, preserve evidence and do not retry. After compaction, reread this
  plan and rederive candidate, refs, Release, and effect facts.
