# HappyCodex 0.9.0 A-prime clean break

## Verbatim request

> 过度优化的可以删了，然后你看看有没有更好更优雅的方案， 考虑重构不兼容，然后和opus5辩证讨论一下
> 重写到不超过 120 行、900 词。会太严格吗
> 好的你继续执行吧

## Outcome

Produce a local, unreleased, incompatible HappyCodex 0.9.0 source candidate.
Replace control-plane-like guidance with one small static ExecPlan and native
Git, tests, diffs, plans, and agents. Keep the product portable, zero-config,
model-agnostic, and proportionate to risk.

## Envelope

Only these paths may change:

- `AGENTS.md`
- `docs/execplans/happycodex-0-9-0-clean-break.md`
- `.codex-plugin/plugin.json`
- `README.md`
- `README.en.md`
- `skills/happycodex/SKILL.md`
- `skills/happycodex/references/execplan.md`
- `skills/happycodex/agents/openai.yaml`
- `skills/happycodex/scripts/resource_claim.py` (delete)
- `tests/test_attestation_contract.py`

Allowed effects are reversible local edits, deletion of the named helper and
empty directory, and offline standard-library validation. Do not commit,
stage, push, tag, publish, install, activate, use the network, modify caches or
marketplaces, or write outside the listed paths.

Preserve `v0.6.5:skills/happycodex` tree
`d9e525a267fbf36669d409ba1b4b009a6beeeea5`; evaluator bytes and constraints;
external role configuration; active install, cache, and rollback
state; historical plans; secrets and raw events. The index must remain
untouched. No compatibility reader, migration, alias, dual write, replacement
claim helper, separate PRD, or `run.md` is allowed.

## Baseline and allowed breaks

Source is `codex/happycodex-0.9-clean-break` at commit `751f81dfc8994fa1dedcf4100612d0bdf1877d58`,
tree `5eec0e292390ccb740de0dab63fe5cdaed724aae`, tag `v0.8.1`, with clean worktree
and index. The full offline suite runs 164 tests with exactly two
accepted existing failures: old-source `ProviderError` is not raised, and an
old-source dirty `EvalSpec` authority is accepted. No new failure is allowed.
Compatibility with the 0.8 product protocol and prose contracts may break.

## Design decision

Use one ExecPlan only for high-risk, cross-system, or compaction-prone work.
Local reversible work stays on native Plan, tests, and diff. An optional design
section belongs in that plan only for a durable external contract with an
independent consumer. Live state is reconstructed from Git, tests, tools, and
the native plan; it is never duplicated as a mutable protocol snapshot.

One approval covers the frozen Outcome, scope, and effect envelope. Reversible
in-envelope local corrections do not re-ask. Re-ask only when an outcome,
path/resource, baseline/allowed break, trust/dependency/credential, external
destination/effect, destructive/irreversible action, or cost/model cap expands.
Only one writer may mutate overlapping resources at a time. Reviews are
risk-triggered and blocker-only, with the bounded repair/replacement rule in
the product guidance.

## Checks, done, and stops

Validate product size budgets, focused contract tests, the full offline suite,
skill `quick_validate`, plugin `validate_plugin`, `git diff --check`, exact
changed paths, and an untouched index. Done means the candidate meets the
Outcome, the two baseline failures are unchanged and reported exactly, every
other check passes, and no unverified required gate remains.

Stop before writing on source/index/path drift, evaluator or protected-tree
drift, a new test failure, a required unknown, scope expansion, or any partial
or ambiguous external effect. Retry an effect only after proving no effect.
After compaction, reread this plan, inspect live Git and tool state, and rerun
needed checks. Never infer live state from this static record.
