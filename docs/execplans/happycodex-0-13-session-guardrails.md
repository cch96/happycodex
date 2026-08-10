# HappyCodex 0.13.0 session-guardrails release

Keep this contract static. Reconstruct live state from Git, tests, and tools;
do not add mutable phase, digest, agent, or review history here.

## Request and Outcome

- Verbatim request chain: `好的你觉得是否有提升优化的地方` ->
  `好的你让fable5也看看` -> `好的执行吧` -> `发布吧`.
- Outcome: forward-port only the three still-useful session guardrails onto the
  released 0.12 line, publish HappyCodex 0.13.0 to `cch96/happycodex` default
  branch `main`, annotated tag `v0.13.0`, and one public GitHub Release with no
  assets, then activate the matching personal plugin locally.
- The three guardrails are: preserve durable candidate/cutover/effect/rollback
  evidence before branch or worktree cleanup; reject automatic continuation
  after the authorized repair and replacement review are exhausted; and reject
  an untracked mutable-worktree digest as durability when no immutable copy is
  reachable.

## Envelope and preservation

- Workspace: `/home/caichenghang/projects/happycodex-0.13-session-guardrails`.
- Branch: `codex/happycodex-0.13-session-guardrails`, based exactly on released
  `v0.12.0` / `407629d89fe27c2e8d8046b0c22dd3dcd1197fe7`.
- Mutable repository paths:
  - `docs/execplans/happycodex-0-13-session-guardrails.md`
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `skills/happycodex/SKILL.md`
  - `evaluation/provider-fixtures-v1.json`
  - `evaluation/hidden-oracles-v1.json`
  - `evaluation/report-schemas-v1.json`
  - `tests/attestation_fixtures.py`
  - `tests/test_attestation_contract.py`
- External mutable resources after a terminal Exact-final `GO`: real Git index
  for the exact candidate; one release commit; local annotated ref
  `refs/tags/v0.13.0`; `origin:refs/heads/main`; `origin:refs/tags/v0.13.0`;
  GitHub Release `cch96/happycodex:v0.13.0`; a content-addressed rollback copy
  of `/home/caichenghang/plugins/happycodex`; that exact personal source; and
  the `happycodex@personal` install/cache selected by Codex.
- Preserve every published tag and reachable tree, the exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`, all other worktrees and branches,
  the dirty `/home/caichenghang/projects/happycodex` 0.10 candidate, the
  untracked 0.12 release plan, external role configuration, credentials, and
  the enabled 0.12.0 cache as rollback evidence.
- Exclude old 0.10 evaluator architecture, compatibility paths, migrations,
  aliases, dual writes, ledgers, controllers, new durable record types, new
  behavior/holdout units, provider evaluation calls, asset upload, force push,
  history rewrite, branch/worktree cleanup, and deletion of rollback state.

## Supported workflows and candidate closure

- Keep exactly four durable record types, five behavior units, three fixed
  concurrent holdout pairs, twelve provider units, and one exact-final.
- Extend the existing `candidate-review` contract with the two review/freeze
  hard stops and the existing `effect-closure` contract with cleanup evidence;
  keep schemas closed and provider input mapping-blind.
- Keep the public Skill within 120 lines and both READMEs within their existing
  80-line contract. Update public summaries only enough to describe the new
  cleanup guardrail and 0.13 identity.
- Consumer-native candidate: one clean Git commit whose tree contains exactly
  the allowed repository paths over v0.12.0. GitHub and local source/install
  consume that immutable commit. The local cachebuster may change only the
  manifest version from `0.13.0` to one helper-generated
  `0.13.0+codex.<UTC-seconds>` identity; normalized runtime bytes must equal the
  released product projection.
- Overlapping dirt or an out-of-scope path is a stop. The old dirty 0.10 tree is
  evidence only and is never a source for the 0.13 candidate.

## Checks and review

- Before freeze: exact branch/HEAD/status/index/path diff; JSON parse and closed
  schema consistency; focused public-contract tests; full offline
  standard-library suite; Python compile/import checks; Skill quick validator;
  plugin validator; `git diff --check`; line budgets; protected-tree digest;
  and unchanged old 0.10/0.12 worktree state.
- Freeze one release commit, then repeat required checks against the commit and
  verify its tree is the staged candidate tree.
- Run exactly one fresh native `happycodex_exact_final` review using
  `gpt-5.6-sol` at `max`, with no inherited task history, against readable
  immutable `v0.12.0` and the candidate commit plus this Outcome, Envelope,
  checks, preservation rules, supported workflows, and accepted baselines.
  Cap: one invocation and one terminal result. No Fable rerun and no repair or
  replacement-review loop. `NOT_YET`, lost terminal, or required unknown stops.
- Admit only a reproduced Done/preservation failure or reachable candidate-new
  material safety/correctness regression. Style, alternatives, speculative
  hardening, and unrelated baseline issues are non-blocking.

## External effects and one-shot observation

- Push main: target `origin:refs/heads/main`; identity is the frozen release
  commit after proving remote main still equals v0.12.0; cap one non-force
  push; read back exact SHA with `git ls-remote`; no recovery attempt.
- Tag: target local and remote `refs/tags/v0.13.0`; identity is one annotated tag
  peeling to the release commit; cap one local creation and one push; read back
  object type and peeled SHA locally/remotely; no recovery attempt.
- GitHub Release: target `cch96/happycodex:v0.13.0`; cap one public,
  non-draft, non-prerelease release creation with the exact title/body below and
  zero assets; read back title, body, state, target tag, URL, and assets; no
  recovery attempt.
- Rollback snapshot: target a new uniquely named directory below
  `/home/caichenghang/.codex/happycodex-release-installs/`; identity is the
  complete pre-mutation personal source plus current enabled 0.12 cache
  identity; cap one copy and checksum readback; never delete it in this task.
- Personal source: target `/home/caichenghang/plugins/happycodex`; prepare an
  isolated exact runtime projection from the release commit, run the
  plugin-creator cachebuster helper once there, validate it, prove the existing
  marketplace locator still points at this source, then apply that prepared
  projection once and read it back byte-for-byte; no marketplace JSON edit.
- Local install: target `happycodex@personal`; cap one
  `codex plugin add happycodex@personal --json`; read back enabled state, exact
  generated 0.13 cachebuster, source/cache equality, and cachebuster-normalized
  release-runtime equality. Do not infer activation from command exit alone.
- Each external mutation is separate. Partial, ambiguous, not-visible, or
  unknown terminal evidence stops all later mutations without retry or cleanup.

## Exact GitHub Release

- Title: `HappyCodex v0.13.0`
- Notes:

  HappyCodex v0.13.0 adds mechanically tested session guardrails without
  expanding the evaluator topology.

  Highlights:
  - Preserves candidate, cutover, effect, and rollback evidence before branch
    or worktree cleanup.
  - Stops automatic continuation after the authorized repair and replacement
    review are exhausted.
  - Rejects an untracked mutable-worktree digest as durable when no immutable
    copy is reachable.
  - Keeps four durable record types, five behavior units, three fixed holdout
    pairs, and twelve provider calls.

  Validation:
  - Full offline test suite and focused session-guardrail contracts pass.
  - Skill validator, plugin validator, JSON validation, and Git diff checks
    pass.
  - Fresh blocker-only Exact-final: GO.

  Install:
  `codex plugin marketplace add cch96/happycodex`
  `codex plugin add happycodex@happycodex`

  Start a new Codex task after installation.

## Done, stops, and recovery

- Done: candidate checks pass; exact-final is `GO`; release commit tree equals
  the reviewed tree; remote main and peeled annotated tag equal that commit;
  GitHub reports the exact public Release with zero assets; personal source and
  enabled cache match the released runtime modulo the single cachebuster; all
  preservation checks hold; and no required state is unknown.
- Stop on source/version/target/ref/cap/schema/topology/path/index drift, remote
  main movement, a non-fast-forward, test regression, protected-tree drift,
  missing rollback evidence, adverse review, or any ambiguous/partial effect.
- A deterministic pre-effect local failure may be corrected only inside the
  listed repository paths and revalidated before freeze. After any external
  attempt, preserve evidence and do not retry. After compaction, reread this
  entire plan and rederive candidate, refs, Release, source, cache, and effect
  facts before continuing.
