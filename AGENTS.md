# HappyCodex maintainer protocol

Root is the only writer. Repository-level evaluation files are maintenance support,
not Skill runtime and must never be linked from `skills/happycodex/SKILL.md`.

- Keep runtime Markdown at or below 262 lines. Target at most 2,200 words; 2,400
  words is the hard ceiling.
- Keep the public 0.3 release, active installation, and every shipped-package byte
  unchanged during the 0.4 certification-engine phase. Product/version/release work
  requires its own frozen gates and explicit authority. The operative 0.4 Outcome
  excludes Fable; future tasks follow their own exact frozen review requirements.
- Use only `python3 -m evaluation.cli`. Every evaluator Python/schema input must be
  classified as semantic, harness, or artifact. Unknown inputs fail closed. The
  read-only impact receipt and exact historical cost must be persisted before any
  live corpus or holdout authorization. Its `impact_token` is only an identity
  binding and never grants permission by itself: live CLI execution also requires a
  current-task user authority persisted in `current.json`, bound to the exact token,
  package identities, model, effort, timeout, arm, and complete invocation scope.
- `evaluation/results/current.json` is the sole active evidence ledger. Never promote
  `refresh_required` to `certified` from offline checks, and do not add historical
  result readers, aliases, migrations, or dual writes. Certification additionally
  requires a Git-reachable successor source whose package content and engine manifest
  match the snapshot and whose `current.json` already persists the exact authority
  and pending-derived impact, plus descendant content-addressed corpus, holdout, and
  review evidence whose Git blobs, SHA-256 digests, impact token, and authority digest
  validate.
- Store raw model events outside the repository. Track only sanitized summaries,
  hashes, fixed fixtures, prompts, hidden oracles, and executable evaluation code.
- Maintainer evaluation must prove native same-task compaction plus a distinct
  no-summary/no-handle durable reconstruction; ordinary Skill runtime must not require
  this control for each user task.
- Behavior comparisons must use fresh isolated homes/tasks and identical model,
  effort, fixture, prompt, timeout, and oracle. Reveal arm identities only after the
  evaluator freezes its result.
- Reject on the candidate's first completion-blocking holdout regression. After a
  first success run a second distinct pair; use a third only for a split or uncertain
  result. At equal quality, uncached input plus output tokens and wall time must each
  stay within 25% of public 0.2.
- Before release, use the plugin-creator cachebuster helper rather than hand-editing
  marketplace state. Re-run exact final product-scope review after version/change-note
  edits, prove a fresh isolated install/invocation of that exact release, then update
  the active plugin with the prior cache ready for rollback.
