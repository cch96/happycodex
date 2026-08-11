# HappyCodex 0.15 review-admission clean break

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: inspect the latest HappyCodex session and agent
  routing; find why `/root/plan_exact_final` repeatedly issued terminal
  conclusions for at least five candidates; prefer optimization over a hard
  round limit; obtain a Fable 5 dialectical review; permit an incompatible
  refactor; `好的执行吧`.
- Outcome: implement a local HappyCodex `0.15.0` clean break that permits
  iterative reviewer dialogue but admits terminal Exact-final evidence only
  for one immutable candidate reviewed by one fresh no-history reviewer, with
  optional non-blocking native hooks that expose misuse without adding state.
- Done evidence: the allowed closure over baseline passes focused and full
  offline checks; one Git tree freezes all consumer inputs; one fresh
  blocker-only Exact-final returns `GO` for that exact tree; no install,
  activation, publication, commit, or remote mutation occurs.

## Workspace and change boundary

- Workspace: `/home/caichenghang/projects/happycodex`; branch
  `codex/happycodex-0.15-review-admission`; baseline `origin/main` commit
  `568582a6388c91d54f1f3a482ed18760abeb67b8` (`0.14.1`).
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `docs/execplans/happycodex-0-15-review-admission.md`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `hooks/hooks.json`
  - `hooks/session_firewall.py`
  - `evaluation/identity.py`
  - `tests/test_attestation_contract.py`
  - `tests/test_session_firewall.py`
- Preserve every published tag and reachable tree; exact
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; evaluator schemas, topology,
  records, provider fixtures, hidden oracles, and stateless verification;
  non-target branches/worktrees; marketplace/config/credentials; personal
  plugin source/install/cache; and user/global agent configuration.
- Exclusions: controller, ledger, registry, transcript parser, session marker,
  counter, mutable evidence graph, compatibility reader, migration, alias,
  dual write, automatic agent rewrite, custom agent installation, provider or
  model call, network access, commit, publish, tag, release, install, activate,
  cleanup, or external effect.

## Supported workflows and allowed breaks

- Convergence review may be reused, messaged, interrupted, or followed up any
  number of times; it remains advisory and has no terminal authority.
- Exact-final admission requires one consumer-native immutable identity, a
  fresh no-history reviewer, strict `GO` or `NOT_YET`, and the identity echoed
  in the verdict. Any candidate-byte change invalidates that verdict.
- A tracked immutable plan may be reviewed separately, but plan `GO` validates
  only that plan. Implementation requires its own frozen candidate review.
- A multi-repository or otherwise composite candidate uses one immutable
  envelope binding every component identity, not several moving identities.
- Follow-up or message to an Exact-final handle is allowed but semantically
  downgrades later output to convergence evidence. Interrupt remains allowed.
- The optional hook denies only a deterministically unsupported explicit
  custom-agent/full-history spawn. Other review misuse receives context or a
  warning and remains allowed. Missing, untrusted, or bypassed hooks fall back
  to Skill guidance; no complete enforcement claim is allowed.
- Hook logic is fail-open, standard-library-only, stateless, transcript-blind,
  and workspace-blind. Compaction receives only a re-grounding reminder.
- Clean break: the plugin is no longer described as wholly zero-config; its
  product/runtime projection now includes default-discovered hook bytes; no
  compatibility wording or legacy review-certification alias is retained.

## Baseline, consumer, and candidate

- Accepted baseline: 85 offline unit tests pass; current Skill and plugin
  validators pass; branch and worktree are clean at the baseline commit.
- Consumers: Codex plugin discovery/runtime, Skill and README readers, and the
  repository's product-identity/evaluation path.
- Input closure: manifest, marketplace locator, public docs, Skill/template,
  default hook configuration and script, product projection logic, all tracked
  repository bytes in the review projection, and test evidence.
- Native freeze: a Git tree created through a temporary index over the exact
  worktree closure. The real index and branch ref remain unchanged.

## Checks and terminal review

- Focused checks: hook unit/subprocess cases; default hook JSON shape and
  commands; fail-open behavior; hard-deny and warning boundaries; consumer
  projection includes every hook byte; public review/admission wording; JSON
  parse; Python compile/import; line budgets; Skill and plugin validators.
- Stable-candidate checks: full offline standard-library suite,
  `git diff --check`, exact changed-path closure, clean real index, protected
  published tree, and Git-tree/readback identity.
- Run one fresh native `happycodex_exact_final` with `fork_turns=none`,
  read-only and blocker-only, against the readable baseline, frozen Git tree,
  this Outcome, boundary, preservation rules, supported workflows, and check
  receipts. It must return one `GO` or `NOT_YET` and echo the tree identity.
- A `NOT_YET` authorizes at most one in-boundary repair by the same fixed
  Executor and one fresh replacement Exact-final against a new tree. Any
  adverse replacement, lost terminal, or required unknown returns to the user.

## External effects, stops, and recovery

- External effects: none.
- Stop on source/branch/path/index/trust drift, out-of-boundary bytes, a new
  failure, incomplete hook/product closure, protected-tree drift, or a required
  unknown. Do not infer hook trust, activation, or installation from validation.
- After interruption or compaction, confirm the prior writer cannot resume,
  reread this plan, inspect Git/index/candidate state, and rederive checks.
