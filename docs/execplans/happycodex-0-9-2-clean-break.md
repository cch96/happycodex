# HappyCodex 0.9.2 proactive read-only delegation

## Verbatim request

> 我举得一些情况下自动启动subagent挺好的你觉得呢
> 好的，你看看claude code是怎么做的，你搜一下，必要时候也可以通过claude code cli 询问或者看claude code session的日志
> 好的你改一下
> 发布吧
> 好了继续

## Outcome

Publish HappyCodex 0.9.2 so substantial read-heavy exploration proactively
uses two or three native read-only agents only when independent bounded lanes
make parallelism materially useful. Preserve a primary writer, one-level
delegation, primary evidence verification, and a single-agent fallback.

## Envelope

- Workspace: `/home/caichenghang/projects/happycodex`; only the owned Skill,
  bilingual READMEs, manifest, contract test, and this 0.9.2 plan may change.
- External resources and effects: one release commit; one non-force update of
  `origin/main`; annotated `v0.9.2`; one public GitHub Release; local `main`
  fast-forward; one rollback snapshot; one personal source/cache reinstall and
  activation through the supported cachebuster flow.
- Preservation: published tags and historical plans; exact
  `v0.6.5:skills/happycodex` tree; evaluator behavior and constraints; external
  role configuration; secrets and raw events; current install until rollback
  state is captured.
- Exclusions: no force push, tag rewrite, evaluator redesign, migration,
  compatibility layer, paid model call, universal submission, or unrelated
  cleanup.

## Baseline and allowed breaks

Source is `codex/happycodex-0.9-clean-break` at
`6a753960f8f18712a21335c6f65f8ecf096c483c`, also `main`, `origin/main`, and
annotated `v0.9.1`, with four intended unstaged paths and an empty index. The
published clean-source suite had 165 tests with exactly two accepted historical
evaluator failures: old-source `ProviderError` is not raised, and an old-source
dirty `EvalSpec` authority is accepted. The new contract test makes 166 tests.
Dirty-source identity errors and the 0.9.1 version collision are pre-freeze
only; closure allows no candidate-new failure or error.

## Design decision

Automatic delegation is conditional, native, read-only, and one level deep.
It starts only for at least two independent bounded evidence lanes when the
parallel benefit is material. The primary agent freezes non-overlapping
questions, owns writes and effects, waits for required results, and verifies
load-bearing evidence. Bounded serial work and unavailable native agents remain
single-agent. No custom role, model, effort, handle, or telemetry is required.

## Checks, done, and stops

Run focused contracts, the cumulative offline suite on the clean commit, Skill
and plugin validators, size budgets, `git diff --check`, exact path/index checks,
and one fresh blocker-only final review. Done requires remote `main`, annotated
`v0.9.2`, and the public Release to resolve to the frozen commit; the personal
plugin must be enabled as `0.9.2+codex.<cachebuster>` with source/cache bytes
verified against the release and a verified 0.9.1 rollback snapshot.

Attempt push, tag publication, Release creation, and activation once each. Stop
without retry on source/index/remote drift, a new test failure or review blocker,
protected-state drift, or a partial or ambiguous external effect. After
compaction, reread this plan and reconstruct live state from Git and tools.
