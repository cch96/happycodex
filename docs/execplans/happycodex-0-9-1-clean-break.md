# HappyCodex 0.9.1 native-permissions refinement

## Verbatim request

> codex://threads/019fd6ac-60e6-7871-88ac-f1b6842ada6f
> 用了happycodex，现在好像每次扩范围会询问你觉得合理吗
> 所以你觉得还是需要询问的是吗
> 但是ai native时代，感觉文件我都不熟悉了，是不是限制在沙盒中的当前项目下的就不问了
> 可以的，另外codex本身就有不同的批准等级，我们还需要做吗。
> 好的，有些话是不是不写比写好
> 好的执行
> 发布吧

## Outcome

Publish HappyCodex 0.9.1 so native Codex sandboxing and approvals own technical
permissions. Reversible work needed for the requested Outcome proceeds inside
the active workspace without per-file approval. A materially different Outcome
or an unrequested external, destructive, or costly effect still returns to the
user.

## Envelope

- Workspace: `/home/caichenghang/projects/happycodex`; only the owned product,
  bilingual README, contract-test, manifest, and this 0.9.1 plan changes.
- External resources and effects: one commit; non-force update of `origin/main`;
  annotated `v0.9.1`; public GitHub Release; rollback snapshot; personal
  marketplace source/cache reinstall and activation.
- Preservation: published `v0.9.0` and historical plans; the exact
  `v0.6.5:skills/happycodex` tree; evaluator behavior and constraints; external
  role configuration; secrets, raw events, and the current install until its
  rollback state is captured.
- Exclusions: no force push, old-tag rewrite, evaluator redesign, compatibility
  layer, universal-directory submission, paid model call, or unrelated cleanup.

## Baseline and allowed breaks

Source is `codex/happycodex-0.9-clean-break` at
`ab0077fba589e36311b6acb6061e6950f9764456`, also `main`, `origin/main`, and
annotated `v0.9.0`. The pre-commit dirty-source suite has 165 tests; exactly two
historical evaluator failures remain accepted: old-source `ProviderError` is
not raised, and old-source dirty `EvalSpec` authority is accepted. Dirty source
identity errors and the 0.9.0 version collision are pre-freeze only; closure
allows no new failure or error.

## Design decision

HappyCodex describes intent and effect boundaries, not a second permission
system. The host decides whether a technical operation is permitted. Within the
active workspace, Git discovers the concrete changed paths. User authority is
required only for a different Outcome or an unrequested external, destructive,
or costly effect. This removes redundant approval prose while preserving scope
discipline and one-shot external-effect stops.

## Checks, done, and stops

Run focused contract tests, the cumulative offline suite on the clean commit,
Skill and plugin validators, size budgets, `git diff --check`, exact path/index
checks, and one fresh blocker-only final review. Done requires remote `main`,
annotated `v0.9.1`, and the public Release to resolve to the frozen commit; the
personal plugin must be enabled as `0.9.1+codex.<cachebuster>` with verified
source/cache bytes and a verified rollback snapshot of 0.9.0.

Attempt push, tag publication, Release creation, and activation once each.
Stop without retry on source/index/remote drift, a new test failure or review
blocker, protected-state drift, or a partial or ambiguous external effect.
