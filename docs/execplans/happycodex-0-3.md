# HappyCodex 0.3 ExecPlan

## Original Outcome

The following user outcome is frozen verbatim:

> PLEASE IMPLEMENT THIS PLAN:
>
> # HappyCodex 0.3：Codex 原生可靠执行协议
>
> ## Summary
>
> - 只重构 HappyCodex Skill，不增加 hooks、外部控制器或 Task State JSON。
> - Root 始终是唯一 writer；scout、boundary challenger 和 reviewer 全部只读。
> - 采用三层状态：ExecPlan 保存持久契约，Native Plan 保存当前执行游标，Git/测试保存事实；Goal 仅在用户明确启用时使用。
> - 解决本次核心缺陷：系统边界收缩、契约被静默弱化、compaction 丢失状态、review 被 writer 叙事锚定，以及单组实验无法证明改进。
>
> ## 公开契约与执行流程
>
> - 为高风险、跨系统、迁移、并发、持久化或生产切换任务创建人类可读的 ExecPlan；优先遵循仓库政策，否则使用 `docs/execplans/<task-slug>.md`。
> - baseline 冻结后立即提交最小 ExecPlan，包含：原始目标原文、baseline/工作树状态、唯一 writer、当前阶段、已知基线失败、pending gates；不得等到调查结束才持久化。
> - ExecPlan 后续维护：系统边界与 obligation matrix、验收 oracle、纵向里程碑、证据、未决 scout、契约 amendments、review receipt。Retrospective 只在最终完成后填写，review findings 不写入计划正文。
> - Native Plan 不限制步骤数量，只表达当前阶段的执行游标；compaction 后由 ExecPlan、Git、测试和 live-agent 状态重建。
> - Goal 不替代 ExecPlan；仅当用户明确创建 Goal 时用于长期目标和完成状态。
>
> ### 边界冻结
>
> - Root 先独立调查入口、持久化路由、生产者/消费者、worker、配置部署、监控恢复、迁移回滚和遗留路径。
> - 对“唯一、全部、端到端、生产可用、替换、退役”等穷举性声明，强制启动不知道 Root inventory 的只读 boundary challenger。
> - Root 取双方发现的并集并复现证据；不得投票、重复派遣相同问题或让 scout 递归委派。
> - obligation 只能为 `open`、`verified` 或 `N/A`；`N/A` 必须带具体路径、搜索或命令证据。
> - 调查完成后提交 contract-freeze。冻结后允许新增 obligation；删除、降级或改为 `N/A` 等缩小交付范围的变更必须获得用户明确授权。无人值守时只能新增或停止，不能缩小契约。
> - 契约变化使受影响的旧证据失效，并追加 amendment、原因和授权来源。
>
> ### 实现和里程碑
>
> - 按可独立验证的纵向能力形成语义 commit，不按代码层机械拆分。
> - 每个里程碑执行：失败 oracle/回归测试、实现、focused tests、累计测试、diff hygiene、ExecPlan 证据更新、语义 commit。
> - 每次提交前做 obligation 对照和兼容性反例检查：默认值、边界值、类型语义、畸形输入、无关行为及既有调用方。
> - 不在每个 commit 后运行昂贵的完整 reviewer；使用里程碑 gate，最终 candidate 再运行 dedicated review。
> - compaction 恢复时必须重新确认 baseline、writer ownership、当前里程碑、未决 gate、测试状态和工作树；丢失的 scout 不得被默认为完成。
>
> ## Fresh Review 与完成门
>
> - 默认使用 Codex 原生 dedicated `codex review`，精确审查 contract-freeze baseline 到 candidate HEAD；配置模型由 Codex 原生设置继承，高风险任务请求 `max` effort，任何降级必须披露。
> - review 前要求任务改动全部提交且工作树 clean；否则必须隔离或显式纳入任务拥有的 staged、unstaged 和 untracked 文件，不能静默遗漏。
> - 默认一次 fresh review invocation，串行执行两个阶段：
>   1. Reviewer 仅根据原始目标、baseline 和仓库独立建立 obligation inventory，并完成 correctness/adversarial 检查；此阶段禁止读取 ExecPlan。
>   2. 随后只读取 ExecPlan 的契约部分，将独立 inventory 与冻结 obligation 逐项映射，检查 completeness 和漏改。
> - Reviewer brief 不包含 Decision Log、writer 自评、历史 findings、Review State 或 Retrospective。
> - 如果 reviewer 报告 diff/context 截断或不能证明覆盖完整范围，completion gate 失败；拆分里程碑 correctness review，并保留一次全仓 completeness review。
> - material finding 修复后最多运行一次新的匿名 rereview，且不向其提供上一轮 finding；再次出现 completion-blocking finding 时停止并交还用户。
> - completion-blocking 指可能违反原始目标、冻结验收、安全/数据完整性、生产运行条件，或“唯一/全部/退役”声明的未决问题，不引入未定义的 P0/P1 标签。
> - 只有在 obligation 全部 verified/N/A、证据仍有效、累计测试通过、工作树 clean、review 无 completion blocker、生产和遗留退役要求均满足时，才能声明 system complete。
>
> ## 测试、实验与发布
>
> - 静态验证 Skill 结构、插件清单、链接、示例和现有约束未丢失。
> - 行为级 micro tests 覆盖：边界遗漏、旧入口仍可达、缺失 worker/部署配置、冻结契约被缩小、冻结前 compaction、丢失 scout、dirty/untracked 文件、baseline 已有失败、review 锚定及大 diff 截断。
> - 强制 compaction 场景必须证明能从 ExecPlan、Git 和测试重建状态，不能依赖对话摘要或 in-flight agent 句柄。
> - 当前版本与候选版本使用相同模型、effort、仓库快照、任务、预算和 oracle 做盲化 paired holdout；至少包含一个 diff 外系统边界和一个机械或行为 oracle。
> - 自适应运行 2–3 组：候选首次出现 completion-blocking 回归立即拒绝；首组成功后运行第二组；结果分裂或不确定时运行第三组。
> - 候选必须不劣于当前版本，并至少在 micro test 或 holdout 中阻止一次当前版本的 false completion。
> - 记录 wall time 与 uncached input/output tokens。质量相同时，任一累计成本超过当前版本 25% 则简化后重测；质量明显提升但超过 25% 时，不默认发布，提交用户确认取舍。
> - 验证通过后再更新 Skill 文档、插件版本和变更说明为 0.3；失败则保留 0.2 为默认版本。
>
> ## Assumptions
>
> - 现有仓库规则优先；若禁止跟踪 ExecPlan，必须由用户指定持久位置。
> - 保留现有 HappyCodex 的 fail-closed、证据复现、禁止弱化验收、scope 变化使证据失效等规则。
> - 不承诺 in-flight subagent 跨 compaction 存活；ExecPlan 中的 pending gate 才是恢复依据。
> - Desktop detached review 只有在能保证同样的精确范围和 neutral brief 时才可替代 `codex review`。

## Baseline and Ownership

- **Immutable task baseline:** `3b9c11fac1f97df75263e0bfc6421c575e04e8b2`
- **Branch:** `main`, initially aligned with `origin/main`
- **Initial worktree:** clean
- **Writer:** Root only
- **Preserved external worktrees:** existing detached/feature/evaluation
  worktrees are not task-owned and must not be modified or removed
- **Goal:** not enabled; the user did not explicitly request Goal
- **Current phase:** independent system-boundary investigation

## Accepted Baseline Failures

None.

Baseline evidence on 2026-07-14:

- `python3 -m unittest discover -s tests -v`: 15 passed
- `quick_validate.py skills/happycodex`: passed
- `validate_plugin.py .`: passed

## Pending Gates

| Gate | Status | Evidence required |
| --- | --- | --- |
| Independent boundary challenge | pending | Read-only return plus Root reproduction |
| Completion-contract freeze | pending | Obligation matrix and contract-freeze commit |
| Skill implementation | pending | Vertical milestone commits with tests |
| Static and micro validation | pending | Validators and behavioral scenarios |
| Fresh native review | pending | Complete-diff review receipt and dispositions |
| Paired holdout | pending | Two or three blinded pairs and cost accounting |
| 0.3 release | pending | All completion gates satisfied |

## Purpose / Big Picture

After this change, invoking HappyCodex on a high-risk task must create a durable
completion contract before implementation, independently challenge exhaustive
system claims, survive context compaction from repository facts, and finish with
an unanchored complete-diff review. The distributed plugin remains instruction-
only; no runtime, hook, daemon, or hidden state is added.

## Progress

- [x] (2026-07-14T16:10Z) Froze clean baseline `3b9c11f` and reproduced all
  three baseline validation commands.
- [x] (2026-07-14T16:25Z) Added and committed the minimal tracked ExecPlan as
  `624cb8c`.
- [ ] Reconcile Root's boundary inventory with one independent read-only
  challenger and freeze the completion contract.
- [ ] Implement the durable state/boundary workflow milestone.
- [ ] Implement the review/completion workflow milestone.
- [ ] Implement evaluation, packaging, and 0.3 release milestone.
- [ ] Run static checks, behavioral micro tests, fresh native review, and
  adaptive paired holdouts.

## Surprises & Discoveries

- Observation: `codex review` accepts either a selector or a custom prompt; its
  custom prompt conflicts with `--base`, `--commit`, and `--uncommitted`.
  Evidence: the current Codex CLI manual's `codex review` command reference.
- Observation: official Codex guidance treats a repository ExecPlan as a living,
  self-contained design document that complements Plan mode rather than replacing
  it. Evidence: the OpenAI “Using PLANS.md for multi-hour problem solving”
  cookbook and current Codex best-practices manual.
- Observation: the existing paired run is directional only and attributes most
  measured quality gain to two max-effort fresh reviews, at roughly 6x wall time
  and 9x uncached-token proxy cost. Evidence:
  `/home/caichenghang/projects/happycodex-pair-20260714-duration/results/REPORT.md`.

## Decision Log

- Decision: Keep the plugin instruction-only and use progressive disclosure:
  core invariants in `SKILL.md`, detailed ExecPlan/review/evaluation contracts in
  one-level references.
  Rationale: preserves the approved scope and keeps Skill context bounded.
  Date/Author: 2026-07-14 / Root.
- Decision: Use a neutral custom `codex review` prompt that instructs the
  reviewer to inspect the immutable baseline range itself.
  Rationale: the CLI cannot combine custom instructions with a target selector.
  Date/Author: 2026-07-14 / Root.
- Decision: Do not enable Goal for this implementation.
  Rationale: the user requested implementation but did not explicitly opt into
  Goal; Native Plan and this ExecPlan carry the execution state.
  Date/Author: 2026-07-14 / Root.

## Context and Orientation

The published artifact is a small Codex plugin. `skills/happycodex/SKILL.md`
contains the core workflow. Its direct references define investigation packets
and optional Fable review. `tests/test_contracts.py` guards the instruction and
package contracts. `README.md`, `.codex-plugin/plugin.json`,
`.agents/plugins/marketplace.json`, and `skills/happycodex/agents/openai.yaml`
form the install and discovery boundary. External historical experiment
directories are evidence inputs only and must not be modified.

## Draft System Boundary

Root's independent inventory currently includes:

1. activation and user-facing metadata;
2. baseline, ExecPlan, Native Plan, Goal, and Git/test state semantics;
3. read-only scout packets and exhaustive-claim challenger routing;
4. contract amendment and evidence invalidation rules;
5. vertical milestone implementation and compaction recovery;
6. native and optional Fable review scope, neutrality, and rerun policy;
7. completion-blocker classification and fail-closed completion;
8. static tests, behavioral forward tests, paired holdout protocol, and cost;
9. plugin validation, cachebuster/version, local reinstall, and release handoff;
10. preservation of all existing compatibility, reproduction, and ownership
    safeguards.

## Pending Investigation

- **Decision:** whether the draft boundary is complete enough to freeze.
- **Question:** without reading this ExecPlan, inspect snapshot `624cb8c` and
  identify implementation, validation, installation, or release surfaces that a
  `SKILL.md`-only redesign would miss.
- **Scope:** the HappyCodex repository excluding `docs/execplans/`; the prior
  HappyCodex paired report/protocol; the QC and Storyboard experiment reports and
  runbooks.
- **Boundary:** read-only; no edits, commits, stateful side effects, external
  models, or child delegation.
- **Status:** pending dispatch.
- **Gate:** contract freeze cannot pass until Root reproduces the return and
  reconciles the union.

## Plan of Work

First freeze the union of Root and challenger obligations. Then implement three
vertical milestones: durable contract and boundary discovery; review and
completion; evaluation, packaging, and 0.3 release. Each milestone begins with
contract-test failures where practical, reaches green, updates this plan, and
ends in a semantic commit. Finally validate the complete candidate, run fresh
native review, run the paired holdout gate, and update the local plugin cache only
after acceptance.

## Concrete Steps

All commands run from `/home/caichenghang/projects/happycodex`. The required
local validation commands are:

    python3 -m unittest discover -s tests -v
    python3 /home/caichenghang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/happycodex
    python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
    git diff --check

## Validation and Acceptance

Acceptance requires every frozen obligation to be `verified` or evidence-backed
`N/A`; all static and behavioral checks to pass without reclassifying new
failures; the complete committed task diff to pass staged fresh native review;
paired holdouts to satisfy the quality-first and 25 percent equal-quality cost
rules; plugin version/cache installation to represent the accepted candidate;
and the final worktree to be clean.

## Idempotence and Recovery

After resume or compaction, read this file, inspect `git status`, `git log`, the
baseline-to-HEAD diff, native-plan state, live agents, and recorded tests. Treat
source and reproducible evidence as authoritative. A missing live scout remains
pending and must not be inferred complete. Do not modify the preserved external
worktrees.

## Interfaces and Dependencies

The redesign introduces Markdown instruction contracts only. It adds no runtime
API, hook, MCP server, app, scheduler, Task State JSON, or external controller.
The exact reference filenames and package changes will be frozen after the
boundary challenge.

## Evidence Ledger

| UTC | Gate | Evidence | Status |
| --- | --- | --- | --- |
| 2026-07-14T16:10Z | Baseline | 15 unit tests and both validators passed | verified |
| 2026-07-14T16:25Z | Durable bootstrap | Commit `624cb8c` contains the initial ExecPlan | verified |

## Contract Amendments

None. After contract freeze, additions are allowed; any deletion, downgrade, or
new `N/A` that narrows the outcome requires explicit user authorization and
invalidates affected evidence.

## Review Receipt

Not run. This section will record scope, model/effort, result, and evidence only;
it will not contain findings, writer defense, or repair narrative.

## Outcomes & Retrospective

Intentionally empty until a milestone or the full task is complete.
