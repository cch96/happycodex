# HappyCodex 0.15.0 release

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: implement the reviewed HappyCodex 0.15 clean break;
  `发布吧`.
- Outcome: publish HappyCodex `0.15.0` to `cch96/happycodex` default branch
  `main`, one matching annotated tag `v0.15.0`, and one public GitHub Release
  with no assets.
- Done evidence: one immutable release commit contains the complete allowed
  closure over `0.14.1`; required checks and one fresh blocker-only Exact-final
  pass; remote main and the peeled annotated tag equal that reviewed commit;
  GitHub reports the exact public, non-draft, non-prerelease, zero-asset
  Release; and no required fact is unknown.

## Workspace and change boundary

- Workspace: `/home/caichenghang/projects/happycodex`; branch
  `codex/happycodex-0.15-review-admission`; baseline `origin/main` commit
  `568582a6388c91d54f1f3a482ed18760abeb67b8` (`0.14.1`).
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `docs/execplans/happycodex-0-15-review-admission.md`
  - `docs/execplans/happycodex-0-15-0-release.md`
  - `evaluation/identity.py`
  - `hooks/hooks.json`
  - `hooks/session_firewall.py`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `tests/test_attestation_contract.py`
  - `tests/test_session_firewall.py`
- Mutable release resources: the real Git index; one release commit on the
  candidate branch; `origin:refs/heads/main`; local and remote annotated
  `refs/tags/v0.15.0`; and GitHub Release `cch96/happycodex:v0.15.0`.
- Preserve every published tag and reachable tree; exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; all non-target branches and
  worktrees; evaluator schemas, topology, records, fixtures, hidden oracles,
  and statelessness; marketplace/config/credentials; personal plugin source,
  install, cache, and hook trust; and local `main`.
- Exclusions: compatibility reader, migration, alias, dual write, controller,
  ledger, session state, transcript parsing, custom-agent/config mutation,
  force push, history rewrite, asset upload, install, activation, cachebuster,
  branch/worktree cleanup, or retry after an ambiguous effect.

## Supported workflows and candidate closure

- Publish the clean-break semantics already described by the implementation
  ExecPlan: unlimited advisory convergence review; one fresh no-history
  Exact-final over one immutable identity; follow-up/message downgrade;
  plan-only `GO`; composite envelope; semantic one-writer overlap; optional,
  trust-dependent, bypassable hooks; and the bounded repair stop.
- Keep the plugin manifest field set accepted by the validator; default hooks
  remain at `hooks/hooks.json`. Include all hook bytes in source/runtime product
  identity and represent the hookless `0.14.1` baseline with explicit absent
  entries under the single `0.15` identity scheme.
- Candidate: one clean Git commit whose tree is the complete twelve-path
  closure over the baseline. Public Git, the tag, and GitHub Release consume
  that immutable commit.
- Precondition observation: remote main equals the baseline; local/remote
  `v0.15.0` and GitHub Release are absent; authenticated GitHub account is
  `cch96`. Recheck immediately before the first external mutation.

## Checks and terminal review

- Before freeze: exact status/index/path closure; focused hook and cross-version
  construction tests; full offline standard-library suite; JSON and Python
  compile/import checks; Skill and plugin validators; line budgets;
  `git diff --check`; evaluator topology/record invariants; protected published
  tree; and remote/tag/Release preconditions.
- Stage exactly the twelve paths and create one release commit with message
  `feat(happycodex): add review admission guardrails`. Repeat the required
  commit-bound checks and prove the clean commit tree equals the staged tree.
- Run one fresh native `happycodex_exact_final`, no inherited history,
  read-only and blocker-only, against the readable baseline and release commit,
  this Outcome, boundary, preservation rules, supported workflows, checks, and
  exact Release contract. Require `GO` or `NOT_YET` with commit identity echo.
- A `NOT_YET` permits at most one already authorized in-boundary repair and one
  fresh replacement review. Any adverse replacement, lost terminal, or
  required unknown returns to the user before external mutation.

## External effects and one-shot observation

- Push main: after proving remote main still equals the baseline and the local
  candidate equals the reviewed commit, make one non-force `HEAD:main` push;
  read back the exact remote SHA with `git ls-remote`. No retry.
- Tag: create one annotated local `v0.15.0` with message
  `HappyCodex v0.15.0`, peeling to the reviewed release commit; push that tag
  once and read back local/remote object type and peeled SHA. No retry.
- GitHub Release: create one public, non-draft, non-prerelease, zero-asset
  Release for `v0.15.0` using the exact title/body below; read back tag, title,
  body, state, target, URL, and assets. No retry.
- Treat each mutation as a separate effect. Any partial, ambiguous, unknown,
  non-fast-forward, or not-visible result stops all later mutation without
  retry or cleanup.

## Exact GitHub Release

- Title: `HappyCodex v0.15.0`
- Notes:

  HappyCodex v0.15.0 separates iterative convergence from terminal Exact-final
  admission without adding a controller or mutable review ledger.

  Highlights:
  - Keeps iterative convergence review advisory and uncapped while requiring a
    fresh no-history reviewer over one immutable identity for terminal evidence.
  - Allows follow-up and messaging, but downgrades later Exact-final-handle
    output to convergence-only instead of enforcing a round limit.
  - Adds optional, stateless, trust-dependent hook guardrails using the default
    plugin hook path; hooks are explicitly bypassable and not an enforcement
    boundary.
  - Includes hook bytes in consumer identity and represents a hookless previous
    release with explicit absent entries under one identity scheme.
  - Clarifies plan-only review, composite candidate envelopes, and one writer
    across overlapping semantic contracts and effect resources.

  Validation:
  - Full offline suite, focused hook/cross-version tests, Skill/plugin
    validators, JSON/Python validation, line budgets, and Git diff checks pass.
  - Fresh blocker-only Exact-final: GO.

  Install:
  `codex plugin marketplace add cch96/happycodex`
  `codex plugin add happycodex@happycodex`

  Start a new Codex task after installation and review/trust optional hooks
  before expecting them to run.

## Done, stops, and recovery

- Done only when checks pass; Exact-final is `GO`; remote main and the peeled
  tag equal the reviewed commit; GitHub reports the exact public zero-asset
  Release; preservation holds; and no required state is unknown.
- Stop on source/version/target/ref/path/index drift, remote main movement, a
  new failure, protected-tree drift, adverse review, or any partial/ambiguous
  effect. After compaction, reread this plan and rederive Git, candidate, refs,
  Release, and effect facts before continuing.
