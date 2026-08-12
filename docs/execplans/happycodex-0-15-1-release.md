# HappyCodex 0.15.1 release

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: reduce process-induced Root/max overthinking without
  degrading hard-task quality; implement the approved six-rule convergence
  increment; publish it as a backward-compatible patch release.
- Outcome: create one reviewed release commit for HappyCodex `0.15.1`, publish
  it to `cch96/happycodex` default branch `main`, publish one matching annotated
  tag `v0.15.1`, and create one public GitHub Release with no assets.
- Done evidence: the immutable release commit contains exactly the six-path
  candidate closure over `0.15.0`; all required checks pass; one fresh
  no-history blocker-only Exact-final returns `GO` for that exact commit; remote
  main and the peeled annotated tag equal it; GitHub reports the exact public,
  non-draft, non-prerelease, zero-asset Release; preservation holds; and no
  required fact is unknown.

## Workspace and change boundary

- Workspace: `/home/caichenghang/projects/happycodex`; candidate branch
  `codex/happycodex-0.15-review-admission`; baseline `origin/main` commit
  `c74a15fca8201dd78e5eafdd41fed8a4b65f65cf` (`0.15.0`).
- Mutable repository paths and exact candidate closure:
  - `.codex-plugin/plugin.json`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `tests/test_attestation_contract.py`
  - `docs/execplans/happycodex-root-convergence-guardrails.md`
  - `docs/execplans/happycodex-0-15-1-release.md`
- Mutable release resources: the real Git index; one release commit on the
  candidate branch; `origin:refs/heads/main`; local and remote annotated
  `refs/tags/v0.15.1`; and GitHub Release `cch96/happycodex:v0.15.1`.
- Preservation: every published tag and reachable tree; exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; non-target branches/worktrees;
  Root Sol/max, Executor Sol/high, Explorer Terra/high, Exact-final Sol/max;
  one fixed writer; Fable optional/advisory; existing Goal, review, bounded
  repair, effect, and truthful-closure semantics; evaluator determinism and
  statelessness; marketplace/config/credentials; personal source/install/cache;
  and local `main`.
- Exclusions: controller, mutable ledger, runtime monitor, timer/action/token
  quota, hook enforcement, general evidence graph, model downgrade, provider or
  model call, compatibility mechanism, force push, history rewrite, asset
  upload, install, activation, cachebuster, cleanup, or retry after an ambiguous
  effect.
- Supported workflows: static planning; explicit Root-to-Executor stability
  handoff; evidence-gated implementation revision; plan-stage reasoning and
  implementation-stage reproduction; bounded verification; freeze and one
  exact-final admission; verdict-first status; one-shot truthful publication.
- Writer overlap: the same fixed Executor owns all six candidate paths through
  repair; Root is read-only over candidate bytes after freeze.

## Stability handoff

- Outcome/change boundary/Done: the patch-release Outcome, six-path closure,
  and Done evidence above are stable.
- Writer/current blockers: one fixed Executor; none at plan creation.
- Increments/exclusions: only the Root convergence guidance, static handoff
  template, focused contract, patch version, and release plan; exclusions above.
- Revision admission: after handoff, another candidate revision brief must cite
  new decision-changing evidence or a concrete current blocker.

## Baseline and allowed breaks

- Baseline: at exact `0.15.0` commit
  `c74a15fca8201dd78e5eafdd41fed8a4b65f65cf`,
  `python -m unittest discover -s tests -p 'test_*.py'` passes 99 tests with no
  failures or errors; Skill/plugin validators pass.
- Allowed breaks: none; `0.15.1` is backward compatible with `0.15.0`.

Never call an accepted failing baseline green or accept a new failure silently.

## Consumer and candidate

- Consumer: Codex plugin discovery/runtime, Skill and ExecPlan readers, public
  Git users, the tag consumer, and the GitHub Release reader.
- Input closure: the exact six repository paths above, their modes and deletion
  state, the baseline parent identity, commit metadata, tag annotation, and the
  exact GitHub Release title/body/state/asset contract below.
- Native freeze: one clean release commit on the candidate branch, parented by
  the baseline and created by staging exactly the six candidate paths. Public
  main, the annotated tag, and GitHub Release all consume this commit identity.
- Convergence review: advisory only; no convergence output has terminal authority.
- Plan review identity: none; this plan governs the release but plan review does
  not replace candidate review.
- Terminal admission identity: one fresh no-history blocker-only Exact-final
  over the readable immutable release commit; strict `GO` or `NOT_YET` with the
  commit identity echoed.
- Exact-final reuse: follow-up/message makes later output convergence-only; any
  replacement terminal verdict requires a fresh reviewer.
- Composite envelope: the release commit binds the complete repository
  candidate; the tag and Release must resolve back to that same identity.
- Precondition observation: Root established remote main at the baseline;
  local/remote `v0.15.1` and GitHub Release `v0.15.1` absent; authenticated
  GitHub account `cch96`. Recheck all four facts immediately before the first
  release mutation.

## External effects

- Release commit: stage exactly the six named paths and make one commit on the
  candidate branch with subject
  `fix(happycodex): bound Root convergence on evidence`; require baseline parent,
  exact tree/path closure, clean index/worktree, and subject readback. No retry
  after an ambiguous or partial result.
- Push main: after rechecking remote main equals the baseline and local HEAD is
  the reviewed commit, make one non-force `HEAD:main` push; read back exact SHA
  with `git ls-remote`. No retry.
- Annotated tag: create local `v0.15.1` once with annotation
  `HappyCodex v0.15.1`, peeling to the reviewed commit; read back type,
  annotation, and peeled SHA. Push the tag once and read back remote object and
  peeled SHA. No retry after either ambiguous result.
- GitHub Release: create one public, non-draft, non-prerelease, zero-asset
  Release for `v0.15.1` using the exact title/body below; read back tag, title,
  body, state, target, URL, and assets. No retry.

Treat each mutation as a separate one-shot effect. Any partial, ambiguous,
unknown, non-fast-forward, or not-visible result stops all later mutation
without retry or cleanup.

## Checks

- Required checks before commit: exact six-path worktree and index closure;
  focused convergence contract and public version tests; full offline
  standard-library suite; manifest JSON parse; Python compile/import; Skill and
  plugin validators; Skill/template line budgets; `git diff --check`; all
  preexisting published tag objects and reachable trees unchanged, including
  the protected `v0.6.5` Skill tree; and remote main/tag/Release preconditions.
- Commit-bound recheck: prove parent, subject, exact changed-path closure, tree,
  clean real index/worktree, manifest version, focused/full tests, JSON/import,
  Skill/plugin validators, line budgets, diff hygiene, published-tree
  immutability, and remote preconditions against the immutable release commit.
- Terminal review trigger/brief: this installed public-guidance release requires
  one fresh no-history blocker-only Exact-final over the readable baseline and
  immutable release commit. Brief Outcome, Done, preservation, supported
  workflows, exact boundary, exclusions, check receipts, and release contract;
  require `GO` or `NOT_YET` with commit identity echo.
- Hook posture: existing optional, trust-dependent, bypassable behavior only;
  this patch adds no hook enforcement.

A `NOT_YET` permits at most one already authorized in-boundary repair wave by
the same fixed Executor and one fresh replacement review over a new release
commit identity. Any adverse replacement, lost terminal, required unknown, or
exhausted budget returns to the user before publication.

## Exact GitHub Release

- Title: `HappyCodex v0.15.1`
- Notes:

  HappyCodex v0.15.1 bounds Root convergence on decision-changing evidence
  while preserving hard-task blockers, required unknowns, and existing release
  safety.

  Highlights:
  - Adds an explicit stability handoff covering Outcome, change boundary, Done,
    writer, blockers, increments, and exclusions.
  - Gives the fixed Executor the candidate write lock and admits later revision
    briefs only with new decision-changing evidence or a concrete blocker.
  - Admits new obligations through a concrete Outcome, preservation, required-
    workflow, or candidate-new safety/correctness failure path; plan-stage
    reasoning remains allowed and implementation reproduces where feasible.
  - Preserves current blockers and required unknowns instead of treating the
    convergence gate as a reason to escape or close them.
  - Allows Root at most one focused verification after delegated evidence,
    requires naming the verdict it could flip, and answers status/conclusion
    requests with the current verdict and unknowns first.
  - Makes Root read-only after freeze and returns any candidate change to the
    fixed Executor before checks, refreeze, and existing review semantics.
  - Adds no controller, mutable ledger, runtime monitor, model downgrade, token
    quota, or other runtime enforcement mechanism.

  Validation:
  - Full offline suite, focused convergence/version tests, manifest JSON and
    Python import validation, Skill/plugin validators, line budgets, published-
    tree immutability, commit-bound readback, and Git diff checks pass.
  - Fresh no-history blocker-only Exact-final: GO.

  Install:
  `codex plugin marketplace add cch96/happycodex`
  `codex plugin add happycodex@happycodex`

  Installation and activation are separate from this release. Start a new
  Codex task after any separately authorized installation or activation.

## Stops and recovery

Stop on source/version/target/ref/path/index/config drift; any path outside the
six-path closure; remote main movement; a new failure; protected-tree drift;
adverse review; a required unknown; or any partial/ambiguous effect. Retry only
after authentic proof that an earlier attempt had no effect, and only when this
plan grants recovery; this release grants no ambiguous-effect retry.

After a continuity break, confirm the fixed writer can resume, reread this plan,
inspect Git/index/candidate/ref/Release state, and rederive all checks and effect
observations before any mutation.
