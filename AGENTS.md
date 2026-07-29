# HappyCodex maintainer protocol

The current 0.4-to-0.5 source-construction task remains a Root-only writer task through
closure under its frozen ExecPlan. Do not recursively apply candidate 0.5 ownership to
this migration. After an authorized 0.5 activation, fresh HappyCodex/0.5 tasks use one
fixed Executor as the sole authorized writer; Root reads, decides, grants, and verifies.
Repository-level evaluation files are maintenance support, not Skill Runtime, and must
never be linked from `skills/happycodex/SKILL.md`.

- Keep Runtime Markdown at or below 262 lines. Target at most 2,200 words; 2,400 words
  is the hard ceiling.
- The active 0.4 installation, public package bytes, and rollback cache remain unchanged
  until cutover is separately authorized. The operative 0.5 Outcome excludes Fable.
  Existing 0.4 tasks finish under 0.4 or are abandoned; never migrate them into 0.5.
- Use only `python3 -m evaluation.cli`. Every evaluator Python/schema input is
  classified as semantic, harness, or artifact; unknown inputs fail closed.
- `evaluation/results/current.json` is the sole active evidence ledger. 0.5 uses a
  fresh full-refresh 0.5 genesis: add no 0.4 evidence reader, alias, migration, dual
  write, prior-coverage reuse, or parser fallback. Offline checks never promote
  `refresh_required` to `certified`.
- Before any live corpus or holdout authorization, persist the read-only impact receipt
  and exact source-derived historical-cost envelope. `impact_token` binds identity but
  grants no permission. Live CLI execution additionally requires current-task user
  authority in `current.json`, bound to the exact token, package/config identities,
  model, effort, timeout, arm, and complete invocation. Only the canonical affirmative
  line derived from the exact approval-request digest is authority; prose is not.
- The new Executor pilot has no prior cost. First persist a conservative source-derived
  envelope and complete exact invocation, then request separate exact authority for one
  bounded calibration. Its sanitized successful actual cost becomes historical basis.
  Executor pilot, corpus, and adaptive holdout are three separate authority gates.
- The validator mints one immutable process-local capability. Every model-reaching
  Executor/corpus/holdout helper requires and rebinds it before fixture, mapping,
  workspace mutation, or subprocess work. Candidate Executor fixtures run only in fresh
  temporary repos/homes and never touch the source or active plugin.
- Certification requires a Git-reachable successor source whose normalized Git package
  artifact and engine manifest match the snapshot. Its retained Executor authority and
  calibration bind the exact external role-config digest; its ledger already persists
  three gate-scoped authorities bound to the pending phase. Every evidence commit
  strictly postdates that source. Shared schema validates inputs during both impact
  planning and execution.
- A zero-live `receipt` or `isolated_install` gate still requires strictly post-source,
  content-addressed `offline_summary` evidence. Receipt evidence binds current artifact
  identity; install evidence binds the existing exact source/installed-package/config
  receipt.
- Store raw model events outside the repository. Track only sanitized summaries, hashes,
  fixed fixtures, prompts, hidden oracles, and executable evaluation code.
- Maintainer evaluation proves native same-task compaction and a distinct
  no-summary/no-handle reconstruction. It also proves writer identity cannot be replaced;
  ordinary Runtime does not rerun that control for every user task.
- Read-only behavior comparisons use fresh isolated homes/tasks and identical model,
  effort, fixture, prompt, timeout, and oracle. Reveal arms only after results freeze.
  Reject the first completion-blocking holdout regression; after first success run a
  second distinct pair, using a third only for split/uncertain results. At equal quality,
  uncached input plus output tokens and wall time each stay within 25% of public 0.2.
- Before release, use the plugin-creator cachebuster helper instead of hand-editing
  marketplace state. Prove a fresh isolated install/invocation of that exact release and
  external role config, then update the active plugin atomically with the prior cache
  ready for paired package/config rollback.
