# HappyCodex maintainer protocol

Root is the only writer. Repository-level evaluation files are maintenance support,
not Skill runtime and must never be linked from `skills/happycodex/SKILL.md`.

- Keep runtime Markdown at or below 262 lines. Target at most 2,200 words; 2,400
  words is the hard ceiling.
- Keep the public base version and active 0.2 installation unchanged until the unit
  suite, both validators, behavior corpus, neutral native review, required Fable 5
  max review, two blinded paired holdouts, cost gate, and pre-release isolated install
  pass.
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
