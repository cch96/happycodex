# HappyCodex/0.3 — clean-room replacement

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Goal: `019f60c9-ac13-7743-a910-73ada401a004`
Writer: Root only
State: frozen by the commit containing this line, with subject
`docs: freeze HappyCodex 0.3 clean-room contract` and the ExecPlan trailer
Resume rule: read this file in full and reconcile it with Native Plan, Goal, Git,
tests, and live-agent state before any write, review, or completion claim.

## Outcome and baseline

### Operative user sources

Source anchor: `current-task/user/PLEASE-IMPLEMENT-THIS-PLAN`
SHA-256 of the dequoted UTF-8 block with LF line endings and a final LF:
`e5d95b290991d208c1fb98c40088d11e1b07b41c76738af6ef4dd5753b47a92a`

> PLEASE IMPLEMENT THIS PLAN:
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

Source anchor: `current-task/user/clean-room-direction`
SHA-256 of the dequoted UTF-8 block with final LF:
`35145a1d8561ba50c0bb6af9b28149ae4eaa23d667d2b79a2624798832abdd9c`

> 如果考虑重构不考虑兼容收益高吗，我觉得需要整理一下知识，看看有没有更好更优雅的方案

Source anchor: `current-task/user/iterate-fable-goal-execute`
SHA-256 of the dequoted UTF-8 block with final LF:
`3d65c91f3fd3d2a2c4cd696d7bad955a0ede2f27b6e45a896c9ba75b9d91fee5`

> 好的多轮迭代探索思考，直到没有遗漏没有更好更优雅的方案(注意不要过度优化），然后让fabel5看一下，然后定义goal 执行

Source anchor: `current-task/user/no-review-quota`
SHA-256 of the dequoted UTF-8 block with final LF:
`e1d130666717801230bca6a31b3d74f5b4afe395dfa962ed892c115dcdfcf44c`

> 继续，不要有审查额度

Interpretation of the last amendment: this implementation and release audit has no
hard review-count quota. Reviews are still rerun only after a material candidate or
evidence change; this does not authorize review shopping or weaken any gate.

Source anchor: `current-task/user/symmetric-freeze-approval`
SHA-256 of the dequoted UTF-8 block with final LF:
`37299fe2230cea964ea4562edb3613f5db0343634015e2870de119073b46ed08`

> 好的

The approved target was the immediately preceding proposed amendment, whose exact
UTF-8 text with final LF has SHA-256
`61bd5903f3104a7cdad37876cc6e36daaa4c1294f9e87d8004f9a41335267cfb`:

> 从现在起 HappyCodex 0.3 契约实行对称冻结。保留并完成现有 O-01～O-36，不再因 reviewer 建议自动新增 obligation；只有违反已冻结目标、安全、生产条件、既有通过行为或回滚要求的问题才阻止完成。验证债务和增强项进入后续 backlog。采用分层验证，并在新增 200 万 token 或 3 小时后暂停汇报；不设置固定 review 次数。

Interpretation: the current ledger and O-01 through O-36 are now a ceiling as well
as a floor. Any addition, removal, narrowing, `N/A` conversion, or allowed-break
widening needs new explicit user authorization. A finding is completion-blocking
only when it violates the frozen goal/acceptance, safety or data integrity, a
production/rollback condition, an exhaustive claim, or behavior proven by the last
accepted receipt. Stale or unbound evidence is validation debt; behavior not
derivable from the frozen contract is an enhancement. Debt and enhancements remain
external backlog and cannot expand this delivery. A disputed classification stops
for the user.

Validation is tiered without weakening final gates: iteration uses the full unit
suite plus affected behavior cases and claims no final receipt; a stable candidate
runs the full corpus and fresh native review; the frozen release chain then runs
Fable, holdouts, install, post-metadata review, and activation. The last accepted
process version governs execution while the 0.3 candidate remains the subject until
certified. Reviews remain event-triggered with no fixed count quota.

The current O-33/O-35 no-summary recovery and mechanical large-diff REDs remain in
scope because they derive from the original forced-compaction and truncation clauses;
they are the final capability additions. The new spend checkpoint starts at the
recreated native Goal counter of 0 tokens/0 seconds on 2026-07-15; pause at either
2,000,000 additional tokens or 10,800 additional seconds. Historical counters before
native-state recovery were 6,105,160 tokens and 38,686 seconds.

Source anchor: `current-task/user/minimal-contract-reconciliation-approval`
SHA-256 of the verbatim UTF-8 line with final LF:
`aa6e4223363df81636fcb143ab60f6bd6193b982442b36b18fe127636eb0610d`

> “批准上述最小契约修正，继续执行

The approved target was the assistant's immediately preceding five-item proposal,
whose exact UTF-8 text with final LF has SHA-256
`3a809e3c56ce0feedd7173482b6cfff8228fa221abdebf493ac6c88e8185f20e`:

> 1. 将“对称冻结”并入现有 O-11，不新增 O-37。
> 2. no-commit 场景必须由用户指定持久位置；否则停止，不自动选择 private ref/archive。
> 3. Review 继承已配置模型；未配置时优先 `gpt-5.6-sol`，使用 `max` 和最强获准只读权限；`ultra` 仍需明确授权。
> 4. 25% 成本门只按“累计 uncached input + output tokens”和 wall time 阻断；input/output 分项仅记录诊断，不分别形成额外阻断门。
> 5. 其余 O-01～O-36 不变。过期的 106/33 数字、恢复比较、完整安装校验、receipt 链和关键词 oracle 属于既有义务内的缺陷，直接修复。

Interpretation: this is the explicit authorization required by the symmetric freeze.
It changes no claim IDs and adds no obligation. O-11 now carries both the ceiling and
floor; O-15 requires a user-selected durable no-commit location; O-34 reconciles
configured-model inheritance with the preserved default and authorization safeguards;
and O-36 records separate token diagnostics while only combined uncached input plus
output tokens and wall time can block on the 25% equal-quality cost rule. Affected
runtime, evaluator, behavior, holdout, and review evidence is reopened.

### Contract amendment receipt

| Change/reason | Authorization anchor/hash | Affected claims | Invalidated evidence | Required reruns |
| --- | --- | --- | --- | --- |
| Minimal reconciliation: symmetric freeze stays in O-11; user-selected no-commit persistence; configured-model review inheritance; combined-token cost gate; repair stale counts, recovery comparison, package binding, receipt chain, and semantic oracles without new claims. | `current-task/user/minimal-contract-reconciliation-approval`; user line `aa6e4223…10d`; approved target `3a809e3c…20e` | O-03–O-07, O-11, O-13, O-15–O-17, O-22–O-27, O-29, O-32–O-36 | `behavior-v10`, review of `810aeaa…f58`, and dependent static/package digests | 64-test static gate; exact v11 corpus/public contrast; fresh native rereview; Fable; holdouts; install/release gates |
| Final bounded repair: pin the holdout public arm, make unavailable native Goal pause produce an explicit `/goal pause` handoff, qualify Goal prompting, and close the contract-freeze timing gap without a new claim or schema. | `current-task/user/final-bounded-repair-approval`; `53929aac…015c` | O-04–O-08, O-11, O-13, O-16–O-17, O-21, O-24, O-27–O-28, O-34–O-36, R-02 | current v15 candidate receipts, Native `019f6c41…bede`, and dependent Skill/package/static digests | focused/static checks; authorized 14-case candidate refresh; shared-runner binding also invalidates two public receipts, whose additional live rerun awaits the cost decision below; then fresh Native/Fable and existing release gates |
| Post-0.2 semantic closure: separate contract/inventory, permission/evidence/Goal lifecycle, persistent pause, reviewer identity/output, explicit waiver, task-scoped Fable cadence, phase boundary, maintainer-only control, and final Goal-state evaluation. | `current-task/user/approve-goal-execute-release`; user line `94260bb7…cfd`; approved target `3cbb4360…27a` | O-04–O-08, O-11, O-16–O-17, O-21, O-24, O-27–O-30, O-33–O-36, P-03, B-02, R-02, R-08 | all current candidate behavior/review/Fable/holdout/install receipts and both public receipts after runner change | static/unit and focused micro checks; exact 14+2 corpus; exact-final Native/Fable; holdouts/cost; isolated install/invocation; activation |
| Fable availability closure: make the loaded Skill distinguish required-unavailable stop from conditional disclosed skip, without another runtime reference or protocol surface. | `current-task/user/continue-hc-p1-003`; verbatim line SHA-256 `3c0077c9…4189` | O-07, O-28, P-03 | all 14 candidate behavior inputs and exact-final Native/Fable receipts for `c58f365`; two pinned-public inputs remain reusable | existing static contract RED/GREEN; exact 14-candidate refresh; fresh Native/Fable; existing holdout/install/activation gates |
| v19 structured Goal-blocker closure: clarify the existing material-finding rule so Goal/Outcome divergence produces a stable finding identity and a current blocker classification, without changing or weakening the case, oracle, matcher, schema, reviewer protocol, or compatibility boundary. | `current-task/user/rebuild-v19-goal`; user-line SHA-256 values `f7dbbcf3…bc583`, `9b6961b9…54625`, and `196f11fe…6c00`; replacement Goal objective `f5084511…946e` | O-04–O-07, O-11, O-13, O-16–O-17, O-21, O-24–O-25, O-27–O-28, O-33–O-35, P-02, R-02 | every candidate v19 terminal and exact-final review evidence; both public inputs remain reusable only after exact digest recomputation | focused Runtime RED/GREEN; cumulative offline gates; one fresh exact 14-candidate corpus; exact public receipt reuse; fresh Native/Fable; existing holdout/install/activation gates |
| Runtime-budget and Goal-handoff correction: retain the 262-line hard limit, replace the exhausted 2,175-word hard limit with a 2,200-word soft target and 2,400-word hard ceiling, and make the unavailable-pause handoff an explicit user command. No claim, oracle, matcher, schema, reviewer protocol, or runtime surface is added. | `current-task/user/continue-after-budget-decision`; verbatim approval `好的继续` SHA-256 `3c0077c9…4189`, approving the immediately preceding bounded proposal | O-03, O-21, R-02 | current Skill/package/static digests and every candidate v19 terminal; public-0.2 receipts remain reusable only after exact input-digest proof | focused static RED/GREEN; cumulative offline gates; one fresh exact 14-candidate corpus; existing exact-final review/Fable, holdout, isolated-install, and activation gates |
| v20 named non-safety waiver and Goal correction: retain the failed `compaction-recovery` receipt but waive only its missing structured classification for `staged-review.txt`, whose safe decision, closed permissions, and exact path evidence are present. Keep Skill/oracle/matcher/schema unchanged; treat ordinary findings as completion blockers rather than Goal-pause conditions. | `current-task/user/approve-v20-named-waiver`; verbatim approval `好的继续` SHA-256 `3c0077c9…4189`, approving the immediately preceding exact authorization text | O-05–O-08, O-16–O-17, O-21, O-24, O-27–O-29, O-33–O-36 | only the unrun ten candidate terminals and all still-open final review/Fable/holdout/install/activation evidence remain missing; the four v20 terminals and raw failed receipt remain immutable | run the exact ten not-yet-terminal cases once; disclose the named waiver; then existing Native/Fable, holdout, isolated-install, metadata, exact-final review, activation, and rollback gates |
| v21 bounded behavior repair and certification disposition: add one explicit before-next-write guard when a local task escalates into public-contract or behavior change; accept only the safe `receipt-mismatch` taxonomy variant where both exact receipt IDs are anchored blockers and write/review/completion stay closed; give only `pre-freeze-compaction` a 600-second limit. No oracle, matcher, schema, hook, controller, Task State JSON, or reviewer-protocol change. | `current-task/user/approve-v21-bounded-repair`; verbatim approval `批准` SHA-256 `b6f4b57a…4533`, approving the previously quoted five-line target SHA-256 `aaba17d2…6806` | O-03–O-08, O-11, O-16–O-17, O-21, O-24, O-27–O-29, O-33–O-36, R-02 | product Skill/package/static digests and all v20 candidate terminals become historical; public-0.2 receipts remain reusable only after exact input proof; existing raw failures and waivers remain retained | one focused mid-flight RED/GREEN plus cumulative offline gates; exactly one fresh 14-case candidate corpus with 300 seconds for thirteen cases and 600 seconds only for `pre-freeze-compaction`; then existing Native/Fable, holdout, install, metadata, exact-final review, activation, and rollback gates |
| Boundary taxonomy correction: keep the exact `app/outbox.py` anchor and `blocking: true` gate while accepting the overlapping `original_goal` or `frozen_acceptance` classes; retain the failed v17 terminal and add wrong-anchor, nonblocking, and unrelated-class counterexamples. | `current-task/user/boundary-oracle-elegance-goal-approval`; verbatim line SHA-256 `b9a99e96…e2d36` | O-05, O-16–O-17, O-24 | only the `boundary-cutover` case input and corpus digest; product package, runner, exact candidate `authorized-rebaseline`, and exact public terminals remain unchanged | focused RED/GREEN and mechanical replay; one exact changed-boundary rerun plus the twelve candidate inputs not reached; then the existing final gates |
| Superseding boundary taxonomy correction: the two-class subset was falsified by a third exact terminal; accept all five existing schema-valid classes only for the exact `app/outbox.py` anchored blocker, preserving shared identity, `blocking: true`, closed completion, and both failed receipts. | combined `current-task/user/boundary-oracle-elegance-goal-approval` plus `current-task/user/cleared-falsified-goal-for-replacement`; user-line SHA-256 values `b9a99e96…e2d36` and `43a1f3b3…0725`; Fable `aa6f8117…edad`; replacement Goal created from `12ea1a0` | O-05, O-16–O-17, O-24 | supersedes only the two-class case/test input and corpus digest; product package, runner, candidate `authorized-rebaseline`, and public terminals remain unchanged | five positive classes plus wrong-anchor/nonblocking/identity/missing-finding/completion counterexamples; mechanical replay of both failures; one exact changed-boundary run plus twelve unreached inputs; existing final gates |
| Current-execution Fable availability waiver: the exact Fable 5/max review is best-effort; the observed quota 429 is one disclosed skip rather than a failed completion gate. Native review remains required and no downgrade, substitution, installation, search, or later silent claim of Fable review is allowed. | `current-task/user/fable-best-effort-when-unavailable`; verbatim UTF-8 line plus final LF SHA-256 `43dd1987…46d4`; current-turn continuation `好的继续` SHA-256 `3c0077c9…4189` | O-07, O-28–O-29, P-03 | retires only the pending current-candidate Fable invocation; its zero-token 429 receipt remains evidence of unavailability. Product/support trees, behavior, tests, Native review, and frozen downstream inputs are unchanged. | no corpus, unit, or Native rerun; disclose the skipped Fable gate and continue the existing holdout, install, metadata, exact-final Native review, activation, and rollback gates |
| Holdout queue-taxonomy oracle correction: for the exact `queue/intents.py` anchored blocker, accept `original_goal` or `production_condition`; all other anchors, safety decisions, permissions, blinded policy, matcher, schema, product, and adaptive stop rules remain unchanged. | `current-task/user/approve-v21-holdout-taxonomy`; verbatim approval `好的批准` plus final LF SHA-256 `095270f2…87b44`, approving the immediately preceding bounded proposal | O-08, O-16, O-24, O-36 | the rejected v21 first-pair receipt and old case/dry-run digest; the unchanged product review remains candidate evidence but no longer covers the final evaluation-support tree | focused oracle replay and holdout tests, cumulative offline suite, new case digest, then exactly one fresh adaptive holdout; existing exact-final Native review covers the changed support tree before release |

Goal spend receipt: native Goal `019f60c9-ac13-7743-a910-73ada401a004` reported
4,123,324 tokens and 21,860 seconds on 2026-07-16. The prior pause thresholds were
exceeded and disclosed; the verbatim approval above says “继续执行”, authorizing
continuation without changing any acceptance gate.

Source anchor: `current-task/user/goal-stop-linkage`
SHA-256 of the verbatim UTF-8 message with final LF:
`a67b0dfd1d62d57411324fb516057a7df0e6339242b21897ccce2e60ce8eff67`

> 补充一个必须处理的系统边界遗漏：HappyCodex 的 stop 目前只会结束当前执行流程，但 active Native Goal 会继续自动唤醒任务，导致无法持久停止。
>
> 请把它记录进现有 ExecPlan 的 pending gate，并做最小修正：
>
> 1. 等待用户决策、外部依赖或触发成本/复杂度停止线时：
>    - 若当前存在 active Goal，优先使用 Codex 原生 Goal pause；
>    - 如果当前环境不能由 Agent 直接暂停，必须明确提示用户执行 `/goal pause`；
>    - 不得把“结束当前 turn”表述为 Goal 已经停止。
> 2. 用户决定继续时使用 Goal resume；放弃时 clear；所有验收真正完成时才 complete。
> 3. 不增加 Task State JSON、自定义控制器、hook、新 schema 或新的 reviewer 协议。
> 4. 尽量修改现有 Goal reconciliation 条款和现有测试，不新建 obligation。
> 5. 在修改前先判断是否会使现有 behavior/review/holdout 收据失效。如果会，先向我报告必须重跑的最小范围和预计成本，并暂停 Goal 等待决定，不要自动开启新一轮全量认证。
> 6. 当前 0.3 收尾范围保持冻结，除这个 Goal-stop 联动遗漏外不再吸收其他优化建议。
>
> 先确认你已记录这个 pending gate，再继续当前收尾工作。
> 你看看是否需要修改goal再跑

Pending gate — Goal-stop reconciliation: amend existing O-21 only so waiting on a
user, external dependency, or cost/complexity stop line pauses an active native Goal;
if Agent-side pause is unavailable, explicitly direct the user to `/goal pause` and
never equate ending a turn with stopping the Goal. Continue uses Goal resume, abandon
uses clear, and only fully accepted completion uses complete. No new obligation,
Task State JSON, controller, hook, schema, or reviewer protocol is authorized.

Impact receipt before implementation: changing `SKILL.md` changes the exact runtime
and package hashes, so all 14 candidate behavior-v14 inputs become stale even if only
the existing `goal-divergence` fixture/test is strengthened. The two public-0.2
comparison receipts may be reused only if their runner, cases, package, prompt,
timeout, model, effort, and evaluation-input digests remain byte-identical. The final
native review started for `2cad59c` was interrupted before a result and is not valid
evidence; final Fable, paired holdouts, and release install had not started, so they
need no repeat beyond their already-open final runs. Minimal live cost is therefore
one 14-case candidate refresh—v14 measured 451,613 uncached-input-plus-output tokens
and 1,619.657 aggregate model seconds—followed by the already-required final native
and Fable reviews, holdouts, and install. Product edits and live reruns remain paused
pending the user's decision and native Goal pause.

Source anchor: `current-task/user/goal-stop-rerun-approval`
SHA-256 of the verbatim UTF-8 line with final LF:
`427f90af7e842510796049390e61e8e3f861ef24e41d0acf5980faf31886d07a`

> 批准最小修正和上述最小重跑”

This explicitly authorizes the bounded O-21 repair and previously disclosed reruns.
The native Goal returned to `active` before product edits. The repair changes no Goal
objective, obligation, schema, reviewer protocol, controller, hook, or Task State JSON.

Source anchor: `current-task/user/continue-goal-stop-closure`
SHA-256 of the verbatim UTF-8 line with final LF:
`790ce365c093c6985803e513abf11eb5c5a24ed1164a5eab7e78c80f94642969`

> 继续

Interpretation: continue closing the already-authorized Goal-stop repair and existing
release gates. This covers restoring the preexisting explicit freeze sentence and its
exact 14-case refresh; it does not authorize scope, schema, case, oracle, obligation,
or reviewer-protocol expansion.

Source anchor: `current-task/user/oracle-defect-correction-approval`
SHA-256 of the verbatim UTF-8 line with final LF:
`427eea65817419881cf9f14f37116605ade05673bdf9f5bb8530c8e47d5b4fc2`

> 是的你看看你是否需要改

Interpretation: after Root reproduced that `multi-repo-submodule` found both seeded
failures and safely blocked every permission but the singular blocker label selected
`frozen_acceptance` where the oracle required `exhaustive_claim`, the user authorized
the minimal non-weakening Oracle correction. The anchored all-scope finding may accept
either overlapping completion-blocker class; anchors, blocking state, permissions,
and both seeded failures remain mandatory. Runtime/package, schema, obligations, and
review protocol do not change. Only this case input and the aggregate receipt become
stale; reuse the other thirteen exact current candidate terminals and the two exact
public terminals, rerun this changed case once, and stop if its semantic gate fails.

Source anchor: `current-task/user/final-bounded-repair-approval`
SHA-256 of the verbatim UTF-8 line with final LF:
`53929aac9e8427b7f9d77e3be742d18181c4800121a10a170e06f1f73bf2015c`

> 批准上述最小修正和最小重跑

Interpretation: this approves exactly the previously disclosed bounded repair and
minimum invalidated evidence rebuild. It permits the public-0.2 manifest pin, the
existing Goal reconciliation/handoff and ask-once clarification, and removal of the
contract-freeze-to-symmetric-freeze authorization gap, followed by static checks, one
14-case candidate refresh, and one fresh Native/Fable pair. It does not admit any
other reviewer suggestion, obligation, schema, controller, hook, Task State JSON, or
review protocol. The native Goal returned to `active` on this user decision.

Source anchor: `current-task/user/post-0.2-audit-request`
SHA-256 of the verbatim UTF-8 line with final LF:
`e05ede3548400d32c53ba0d4bb288a1496ef380cb91441cfd5dc492a8859cd57`

> 好的你看看是否有遗漏，以及是否有更好更优雅的方案，然后让fable5 review一下

Source anchor: `current-task/user/approve-goal-execute-release`
SHA-256 of the verbatim UTF-8 line with final LF:
`94260bb704a6b0a300b83133402aa1aa01d29e2139edd5be1f7e094c5260dcfd`

> 好的定义一下goal然后执行吧，是不是可以更新到0.3了

The approved target is the immediately preceding Root audit, exact UTF-8 plus final
LF SHA-256 `3cbb43602d5dd217941282608cd4fbd4bb705679e63759480d324cbc8779527a`.
It authorizes a minimal semantic correction within O-01 through O-36: freeze the
user contract rather than the derived inventory; make authorization, contract,
candidate-bound evidence, and Goal lifecycle non-interchangeable; narrow Goal pause
to persistent waits after useful work is exhausted; bind external-review identity and
durable output; require explicit, exactly scoped waivers; make Fable selection
task-scoped while separating advisory from exact-final evidence; separate a new
Outcome/baseline from an in-contract repair; keep the no-summary control in maintainer
evaluation rather than ordinary Runtime; and evaluate the final visible Goal state.
It adds no claim ID, hook, controller, Task State JSON, schema, or reviewer protocol.

The user explicitly requested Goal-backed execution and Fable 5 review. Native Goal
`019f60c9-ac13-7743-a910-73ada401a004` is active. Fable selection is authorized once
for this task; the completed Fable design audit is advisory only, while the exact-final
Fable gate remains required by repository policy. The latest instruction also approves
the previously pending two-public-receipt cost and the existing release chain.

Impact before product edits: changing Runtime/template invalidates every candidate
behavior and final-review receipt; changing the shared Goal-state oracle invalidates
both public comparison inputs. The changed candidate also invalidates prior holdout
and install evidence. Minimum rebuild is static/unit plus affected micro checks, one
exact 14-candidate/2-public corpus, one exact-final Native/Fable pair, the frozen
adaptive holdouts/cost gate, exact isolated install/invocation, and activation only
after every gate closes. No live model rerun has started under this amendment.

Source anchor: `current-task/user/rebuild-v19-goal`
SHA-256 values of the three verbatim UTF-8 lines with final LF are
`f7dbbcf3e47da96a9e1686f5767a93255a53e4e1657e99297c985c6cdcebc583`,
`9b6961b92f054498336b74fd45531385ea356cf9f49eae8cabdae7ba96954625`, and
`196f11fe1a115de29d314227d9c18aa27940317df29d1bee5224383c0cfb6c00`:

> 继续0.3，需要修改goal 或者plan吗
>
> 你帮我重建一下goal
>
> 已经清理了

The user received the bounded replacement objective before clearing the incompatible
Goal, then explicitly requested its reconstruction and confirmed the clear. Native
Goal `019f60c9-ac13-7743-a910-73ada401a004` is now visibly `active` with objective
SHA-256 `f5084511d3e40b267dafdb4bc9d54bf5c2b7516447925bdd5f070add1a10946e`.
It retains the immutable ExecPlan baseline and authorizes only the minimum Runtime
clarification needed for Goal/Outcome divergence to become a stable material finding
and current completion blocker, followed by the already-frozen exact behavior,
Native/Fable, holdout, install, activation, and rollback gates. It explicitly forbids
oracle/matcher/schema/case-semantic/reviewer/compatibility weakening or other 0.4 work,
and stops instead of retrying or selecting around a repeated repaired-case failure.

### Normalized outcome

Replace the rejected patch-accumulated HappyCodex 0.3 with a clean-room, Codex-native
0.3 built from the last proven public 0.2 tree. Preserve Root as the sole writer and
use one durable ExecPlan, Native Plan as cursor, Goal only because the user explicitly
created it, and Git/tests/runtime observations as facts. Prevent false completion at
system boundaries and across compaction, then prove utility, cost, neutral review,
Fable review, packaging, isolated discovery, and invocation before changing the
active 0.2 install or release metadata.

Request-clause mapping:

| Operative clause | Ledger coverage |
| --- | --- |
| native-only architecture, Root writer, three state layers, Goal opt-in | O-02, O-04, O-10, O-11, O-20, O-21, P-01 |
| qualifying classes, durable bootstrap, and low-risk native exit | O-04, O-11, O-30 |
| bounded design exploration without cosmetic over-optimization | O-31 |
| boundary discovery, ordered trace, challenger, freeze, no silent narrowing | O-04, O-11, O-12, O-20, O-32, P-02, B-01 |
| vertical semantic milestones, RED/GREEN, cumulative checks, recovery | O-06, O-10, O-11, O-22, O-23, O-26, O-33 |
| neutral exact-scope review, dirty scope, truncation, completion blockers | O-07, O-13, O-15, O-17, O-25, O-27, O-34 |
| behavioral micro corpus and summary-independent forced compaction | O-05, O-06, O-16, O-22, O-24, O-35 |
| blinded adaptive pairs; combined-token and wall-time 25% ceiling with separate diagnostics | O-08, O-16, O-36 |
| delayed synchronized 0.3 metadata, exact install, active-0.2 preservation | O-09, O-18, O-29, O-36, R-04 |
| clean-room freedom without weakening user-project compatibility | B-01, P-01, P-02 |
| Fable 5, explicit Goal, and no audit-count quota for this execution | O-07, O-17, O-28 |

“Runtime” in O-03 means the files Codex discovers or loads as the HappyCodex Skill:
`SKILL.md`, its one linked ExecPlan reference/template, `agents/openai.yaml`, and
plugin UI metadata. Repository-level tests, fixtures, maintainer `AGENTS.md`, README,
and this ExecPlan are support/provenance and must not be linked or loaded by the
ordinary Skill flow.

Contract-conformance correction: the original operative request, not the rejected
draft's simplification, authorizes the claim states `open`, `verified`, and `N/A`,
explicitly requested native Goal use, a committed pre-investigation skeleton, serial
independent-inventory/contract-mapping review, finding-free plan prose, a final-only
Retrospective, and Fable 5 at max by default. No claim was removed or narrowed. All
behavior and review evidence affected by this correction is reopened below.

Contract expansion after the blocked native review adds O-20 through O-25. They make
already-operative requirements explicit: all delegated readers remain single-level;
an explicitly requested Goal receives terminal status only after the contract closes;
compaction proof uses native compact/resume; baseline acceptance is binding; eval
receipts bind exact inputs and immutable content; and phase 2 cannot see the contract
until a numbered phase-1 inventory is actually frozen. No claim or gate was removed,
narrowed, or changed to `N/A`, so no user authorization was required.

Contract expansion after the complete two-phase review of `b155644` adds O-26
through O-29. It makes already-operative milestone discipline, exact review recovery,
external-review selection safety, and post-metadata release/cost gates independently
mappable. B-02 is narrowed to restore the baseline's ask-once Goal approval behavior;
no outcome, preservation claim, or gate was removed, downgraded, or changed to `N/A`.

Contract expansion after the complete two-phase review of `5fdf965` adds O-30
through O-36. It makes already-operative qualification/bootstrap, bounded design
exploration, ordered boundary tracing, slice/recovery receipts, native-review parity,
structural/behavioral oracles, and adaptive release economics independently mappable.
No claim, oracle, or gate was removed, weakened, or changed to `N/A`; affected runtime,
behavior, and review evidence is reopened. The later symmetric-freeze amendment caps
the ledger at this scope unless the user explicitly authorizes another change.

### Immutable starting state

| Item | Frozen value |
| --- | --- |
| Source repository | `/home/caichenghang/projects/happycodex` |
| Task worktree | `/home/caichenghang/projects/happycodex-cleanroom-0.3` |
| Branch | `feat/happycodex-0.3-cleanroom` |
| Public 0.2 baseline | `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` |
| Baseline tree | `4708ebc12f74d4482764796fdd00f1fa7194a13a` |
| Current remote head (not baseline) | `5c5d4c0a4d7590871acd14e4f1ef282f2f564177` |
| Rejected candidate range | `3b9c11f..5c5d4c0` |
| Worktree ownership | Entire clean-room worktree belongs to this task; Root only |
| Repo policy | No project-local `AGENTS.md` found; hub rules require source work under `~/projects/` |
| Existing active plugin | `0.2.0+codex.20260714095129`; must remain active until release gates close |

Baseline evidence:

| Check | Result | Digest / identity |
| --- | --- | --- |
| `git status --short --branch` | clean branch at baseline | exact output recorded in task tool log; digest open |
| `python3 -m unittest discover -s tests -v` | exit 0; 15/15 passed | normalized combined-output SHA-256 `94d63e93258a5ffe8952f5636eeea3f49f8a99b7eb7f664b285b8922d0275b35` |
| `git diff --check` | exit 0 | empty output |
| accepted baseline failures | none | zero failures |
| remote reflog | `3b9c11f` was remote head before `624cb8c` began 0.3 | task tool log; reproduce before freeze |

## Claims Ledger

States are only `open`, `verified`, or `N/A`. `N/A` requires concrete path, search,
or command evidence; unknown or stale evidence remains `open`.

| ID | Type | Claim | Closure condition / falsifier / oracle | Evidence | State |
| --- | --- | --- | --- | --- | --- |
| O-01 | outcome | Candidate is independently rebuilt from proven public 0.2, not copied from rejected 0.3. | Diff ancestry starts at `3b9c11f`; implementation text provenance audit finds no copied rejected-runtime structure. | `3b9c11f` is an ancestor; semantic commits begin at that tree. Rejected-to-current runtime/reference audit is 256 insertions/518 deletions and the current six-section runtime plus single template does not retain the rejected nine-section/four-reference structure. | verified |
| O-02 | outcome | Root is the only writer; plugin adds no hook, controller, scheduler, daemon, MCP/app runtime, or Task State JSON. | Manifest/tree scan plus Git authorship and live-agent receipt inventory; any such surface falsifies. | Full candidate file inventory contains only Skill/UI runtime plus maintainer docs/tests/evaluation support; targeted runtime scan finds only negative declarations, all semantic commits are Root-owned, and `/root` is the sole live agent. | verified |
| O-03 | outcome | Distributed runtime is only `SKILL.md`, one ExecPlan reference/template, and UI metadata; its runtime Markdown has a 262-line hard limit, a 2,200-word soft target, and a 2,400-word hard ceiling. | `git ls-files`, packaging manifest, and `wc -lw` over declared runtime Markdown; an extra runtime file, more than 262 lines, or more than 2,400 words falsifies. Exceeding 2,200 words requires a critical-semantics justification and simplification check, not automatic failure. | Runtime is exactly 3 files and 244 lines/2,182 words after the approved handoff clarification, below the soft target. Structural and package-copy oracles reject ordinary, hidden, bytecode, and symlink runtime additions; UI YAML remains outside the explicit Markdown budget. | verified |
| O-04 | outcome | Qualifying tasks freeze intent and system boundaries in a single 0.3 ExecPlan while clearly sub-threshold tasks retain cheap native flow. | Bidirectional corpus includes both false-completion and false-stall controls; candidate must pass both. | Static contracts pass; `behavior-v18` is historical after the Skill/package change and exact v19 is pending. | open |
| O-05 | outcome | Corpus proves at least one public-0.2 false completion prevented with no control-case false stall. | Same fixtures/model/effort/budget, fixed hidden oracles, blinded arm mapping; 0.2 fails at least one safety case and 0.3 passes all controls. | v18 preserved the contrast, but its 14 candidate inputs are stale for the repaired package; v19 is pending and both public receipts await exact digest reuse proof. | open |
| O-06 | outcome | Structural, focused, full, real-path, transition, recovery, dirty-scope, baseline-failure, secret, review-isolation, and packaging checks pass without hidden regressions. | Tracked executable tests/evals and frozen expected results all pass; new unexplained failure falsifies. | Current 94/94 tests, validators, dry-runs, Ruff, JSON, budget, and diff hygiene pass; exact repaired-package behavior is pending. | open |
| O-07 | outcome | Fresh neutral native review and required Fable 5 max review have no unresolved completion blocker and verifiable scope receipts. | Complete synthetic diff coverage plus independent obligation inventory; reproduced blockers closed; unavailable/contaminated/truncated review falsifies. | Exact Fable `f6739b4f…e75` covers 51/51 without blocker. Current Native `019f7052…640` recovered its initial truncation through the bounded O-27 fallback and maps 138↔50 completely, but Root reproduces confirmed blocker `HC-P1-003`. | open |
| O-08 | outcome | Two blinded paired holdouts show no quality regression; at equal quality, uncached tokens and wall time each stay within +25% of 0.2. | Frozen pair fixtures, identical run parameters, hidden oracle, telemetry and blind reveal; first regression rejects. | Current runner `02f4eb2c…287` pins public manifest `77a0b2b8…8c89` and fails closed on any candidate failure; 94/94 and dry-run pass. No current live pair has started. | open |
| O-09 | outcome | Isolated supported marketplace install proves version discovery and Skill invocation before active install or release metadata changes. | Fresh isolated `CODEX_HOME` installs candidate, new task discovers exact plugin/version and invokes candidate; active cache remains 0.2 beforehand. | Historical install proves the path, but the repaired package requires a new exact isolated install/invocation; active personal 0.2 remains unchanged. | open |
| O-10 | outcome | Work lands as independently green semantic vertical commits and remains recoverable after compaction. | Each implementation commit has `HappyCodex-ExecPlan` trailer, slice checks, green checkpoint; simulated recovery writes nothing before re-anchor. | Skeleton, freeze, runtime, behavior, conformance, review hardening, isolation repair `b155644…a18`, and review-completeness repair `ffb502b…d080` carry the trailer; later review/release milestones remain. | open |
| O-11 | outcome | A qualifying task uses one durable ExecPlan whose verbatim sources, baseline, Outcome, exclusions, allowed breaks, amendments, checkpoint, and recovery guard freeze the user contract without freezing its derived inventory. Entailed claims may grow monotonically with provenance; narrowing, widened breaks, `N/A`, or Outcome/baseline changes need explicit user authorization. | Template/schema tests plus uncertain/mid-flight qualification, pre/post-freeze compaction, lost agent, unauthorized narrowing/widening, authorized rebaseline, Goal divergence, and no durable location. | Runtime and template now distinguish the frozen contract from derived claims and route non-entailed reviewer suggestions to an external backlog. Focused structural RED/GREEN and 23/23 contracts pass without O-37 or new state/schema. Full behavior/review remains open. | open |
| O-12 | outcome | Exhaustive or architecture-shaping claims receive one fresh, baseline-only, read-only challenger with verifiable dispatch/return identity; Root reproduces the union. | Challenger corpus includes valid receipt and missing/mismatched receipt; Root cannot impersonate closure. | This task's challenger is reproduced; fixture challenger receipts are now created at the terminal revision before the candidate and reused by review rather than synthesized after candidate creation. | verified |
| O-13 | outcome | Completion review sees an exact synthetic baseline/candidate product diff but no original history, ExecPlan, writer narrative, Root conversation, or undeclared source path. | Two neutral synthetic commits mechanically exclude only the recorded ExecPlan; tree-manifest equality, diff-unit inventory, coverage receipt, contamination audit, private ledger↔review reconciliation, large-diff split, and fallback cases. Any product change after review invalidates it. | Current source `3b9c11f…8b2..c58f365`, equivalent synthetic `097fcd8…176..4bb754b…8e`, and all 51 units are manifest-equal; both reviewers report zero contamination/external reads/writes. The confirmed product blocker prevents closure. | open |
| O-14 | outcome | Workflow-created artifacts never persist secrets and product snapshots introduce no new secret finding. | Mechanical scan of control/evidence/review/eval artifacts; baseline→candidate finding-identity differential for product trees; secret-bearing corpus case. | Current credential-pattern scan has zero matches; the executable case classifies `SECRET-BASE-1` baseline-unchanged and `SECRET-OUTPUT-2` candidate-new. Final reviewed product-tree differential remains. | open |
| O-15 | outcome | Commit-forbidden, multi-repository, dependency-read, submodule, dirty/untracked, and ambiguous-ownership paths fail closed or produce equally reviewable immutable scope. | When commits are forbidden, the user must select a durable location before work continues; an approved reachable private ref/archive may preserve every snapshot without touching the index. Corpus and manifest oracles also cover stable namespaces, dependency reads, submodules, exact ownership, and content immutability. | v10 proves stop-without-user-selection, secret preservation, multi-repository/submodule namespaces, and dirty/content-immutable scope. The final exact review projection and any selected no-commit positive path remain open. | open |
| O-16 | outcome | Evaluation is executable, tracked, blinded, bidirectional, and hidden-oracle driven rather than phrase-presence evidence. | Runner validates durable case schema, all six permission fields, task-visible/hidden separation, exact input binding, native compaction, immutable content, fixed arms, observable oracles, raw usage, blind reveal, and adaptive stop. | Runner/corpus remain `e835c6c9…d105`/`533d45e2…5da`; 94/94 mechanical tests pass, while repaired-package v19 receipts remain pending. | open |
| O-17 | outcome | Required reviews remain independent and findings are reproduced; this implementation has no hard audit-count quota but does not shop for a favorable verdict. | Every rerun follows a material candidate/evidence change and uses a fresh neutral brief; unresolved blocker keeps completion open. | Native `019f7052…640` and Fable `f6739b4f…e75` independently reviewed the same frozen `c58f365` product with no cross-output. Root reproduced the union: two Fable debt items stay backlog, two Native overconstraints are rejected by mapping, and `HC-P1-003` remains material. | open |
| O-18 | outcome | Manifest, marketplace, README, UI metadata, links, validators, cachebuster, install/discovery, and rollback remain coherent. | Structural validation, supported CLI install/list JSON, fresh-task invocation, cache hashes, and prior-version restoration proof. | Version `0.3.0+codex.20260716113414`, README change note, and plugin/UI copy are synchronized and pass both validators plus structural tests. Exact release install and rollback restoration remain open. | open |
| O-19 | outcome | Review receipts close without creating an unreviewed-final-HEAD cycle. | Review identity is the content-addressed product tree excluding the sole ExecPlan. After review, only receipt/closure fields may change in one clean administrative commit; final manifest proves the product tree is unchanged. Any other path or contract-claim change invalidates review and reopens dependent gates. | Deterministic positive/negative admin fixtures and current-hash admin behavior pass; the real final administrative proof remains open. | open |
| O-20 | outcome | Every scout, challenger, and reviewer is read-only, remains single-level, and is not dispatched on a duplicate question; Root remains the sole writer and reproduces returns. | Runtime text and forward cases cover ordinary scouts as well as the mandatory challenger; recursive delegation, duplicate dispatch, or any delegated write falsifies. | Runtime now requires `fork_turns="none"`, a neutral no-preferred-answer packet, read-only execution, and no child delegation for every ordinary scout and challenger; the scoped countertest and recovery cases pass. Only Root is live. | verified |
| O-21 | outcome | A requested Goal is only an objective pointer and controls automatic continuation, not authority, completion, evidence, waiver, review, or cost. Only a persistent user/dependency/cost wait after safe work is exhausted pauses it; resume continues, clear abandons, and complete waits for every gate. | Turn end, interrupt, transient error, finding, or remaining work cannot masquerade as pause; stop-waiting cannot waive a gate; unavailable native pause requires explicit `/goal pause`; final visible Goal state decides the handoff. | The v19 failure proved that an open-gate label alone was insufficient. Current Runtime explicitly tells the user to run `/goal pause`; focused structural and matcher checks pass, while exact live behavior remains pending. | open |
| O-22 | outcome | Forced compaction evidence uses native compaction followed by resume of the same task and proves recovery from ExecPlan, Git, tests, and live-agent facts rather than a prose claim or summary. | Persisted session contains a native compaction event and the resumed turn has the same task ID; removing either event or a durable fact fails the oracle. | Exact v11 records native compaction, same-task resume, distinct no-summary/no-handle fresh control, identical structured recovery hash, three marker IDs, tests, worktree, and reproduced live-agent receipt. Final review remains open. | open |
| O-23 | outcome | Baseline failures close only when resolved or explicitly accepted and unchanged; unaccepted, changed-identity, candidate-new, and unknown failures remain blockers. | Structured identities and acceptance state are checked at baseline, candidate, and completion; relabeling or free-text mention cannot pass. | Static countertests accept delimited qualified identities and reject ambiguity; exact v11 passes baseline/candidate failure classification and authorized rebaseline cases. Final review remains open. | open |
| O-24 | outcome | Every behavior receipt binds the exact Skill/package, runner, case, model, effort, timeout, and oracle; read-only enforcement compares content and every case constrains all six permission fields. | Any changed input invalidates a receipt; modifying an existing dirty/untracked file or omitting a permission expectation fails mechanically. | The package change invalidated all 14 candidate v18 inputs; index state now requires v19, while both public inputs remain reusable only after exact recomputation. | open |
| O-25 | outcome | Phase 2 receives the contract only after phase 1 emits stable numbered obligation IDs/text and Root verifies and hashes that frozen receipt. | Missing inventory prevents contract reveal; a same-session receipt-only correction may precede phase 2, but retroactive derivation or contract-first mapping fails. | Historical task `019f7052…640` proved sequencing, but the product change invalidates its final-candidate receipt; fresh Native review is pending. | open |
| O-26 | outcome | Bootstrap and each vertical milestone preserve the early skeleton, separate freeze, uncapped cursor, smallest meaningful RED, minimal coherent change, focused plus cumulative checks, compatibility counterexamples, diff hygiene, evidence update, and semantic revision without a full reviewer after every commit. | Runtime/template contracts and transition cases must expose every phase; skipping or mechanically layering a slice falsifies. | This slice observed 6 REDs, passes 6/6 focused and 23/23 contract checks, keeps Runtime under budget, updates this checkpoint, and awaits its semantic revision. Exact behavior/review remain open. | open |
| O-27 | outcome | Review binds authoritative source IDs to content-equivalent synthetic commits, completes hidden correctness before contract reveal, recovers from truncation with bounded correctness plus whole-repository completeness, permits Desktop fallback only with equivalent isolation, and classifies blockers semantically. | Static contracts, review-isolation behavior, real two-phase receipt, and final fresh review must agree; priority-only or truncated coverage falsifies. | Native `019f7052…640` preserved the failed whole-repository receipt, re-read the 16 affected paths through 37 bounded commands, then cumulatively covered 138/138 and 51/51 without remaining truncation before complete 138↔50 mapping. Its semantic blocker keeps completion open. | open |
| O-28 | outcome | Explicit Fable review uses the exact requested model/effort and same frozen neutral scope, stays independent, unions findings without voting, and never downgrades, substitutes, installs, enables, or searches. Selection permission is task-scoped/asked once; advisory “look” is historical after change, while a required exact-final gate reruns without new permission. | Runtime/README consistency plus runtime-issued command/session/effective-model identity and an exact Fable 5 max receipt; unavailable required review stops. | Runtime-issued Fable session `f6739b4f…e75` is exact Fable 5/max, safe/read-only, 51/51, and blocker-free. Native mapping confirms the candidate Skill itself omits the required-vs-conditional unavailable transition, so runtime consistency remains open. | open |
| O-29 | outcome | Release keeps raw events external, asks the user when quality improves but cost exceeds 25%, re-reviews after release metadata changes, proves exact install/discovery/invocation, and preserves active 0.2 until rollback-ready activation. Only explicit user text waives a named gate; scope is exact, later changes reopen it, and completion discloses unrun gates. | Holdout receipts, external raw paths, waiver anchor/scope, post-metadata review identity, supported CLI install/list, fresh task, and active-cache hashes. | Static waiver contracts pass; no release gate is waived. Post-metadata review, exact install, and activation remain open. | open |
| O-30 | outcome | Every cross-cutting, public-contract, migration, persistence, concurrency, destructive, production-cutover, exhaustive, uncertain, or compaction-prone task enters one durable 0.3 ExecPlan while clearly local low-risk work stays native; bootstrap records sources, baseline/worktree ownership, writer, phase, failures, and gates before research. After closure a new independent Outcome/baseline starts a new task/ExecPlan; an in-contract repair stays. | Static/template checks plus low-risk, mid-flight qualification, forbidden-location, dirty-baseline, pre-freeze transition, and phase-boundary contracts; missing durable location or baseline stops and asks rather than guesses. | Static qualification and phase-boundary contracts pass. Exact behavior/review and release gates remain open. | open |
| O-31 | outcome | Before contract freeze, Root boundedly compares materially distinct designs that could change obligations or risk, challenges omissions, and stops at a requirements-based saturation point when no clearly better option remains without cosmetic over-optimization. | Runtime/template require decision-changing alternatives and record the chosen boundary plus rejected materially different options; adopting the first plausible design or polishing without requirement impact falsifies. | The frozen clean-room decision, semantic static oracle, and independent native/Fable review supply the saturation record. Reviewer-only validation debt and enhancements remain backlog rather than expanding 0.3. | open |
| O-32 | outcome | Boundary discovery traces each changed contract in order from authoring/input through validation, execution, persistence/serialization, and user-visible output, then searches configuration, deployment, workers, observability/recovery, migration/rollback, generated artifacts, downstream consumers, and legacy bypasses; every exhaustive or uniqueness claim receives an exact-snapshot neutral challenger and bounded receipt. | Static contracts and adversarial fixtures require revision/tree plus dirty state, one decision-changing question and stop condition, read-only/single-level execution, new evidence and remaining uncertainty, and Root reproduction of the union. | Exact v11 boundary/multi-repository/recovery cases bind every seeded defect through repository anchors plus semantic blocker classes without model-ID or prose dependence; current independent reviews found no boundary omission. Release gates remain open. | open |
| O-33 | outcome | Every vertical slice begins with an observed RED or justified substitute, maps tests to obligations/gates, and ends with focused+cumulative checks, diff hygiene, evidence update, and semantic revision. Runtime recovery rechecks six durable facts after native same-task compaction; maintainer evaluation separately proves no-summary/no-handle reconstruction. | Receipts expose baseline, writer, milestone, gates, tests, and worktree; unrecoverable facts stop and ask. Summary or handle cannot supply a fact, but ordinary tasks need not run an evaluation control. | Runtime removes the self-certification burden; `AGENTS.md` retains both maintainer controls. Static RED/GREEN and existing recovery unit oracles pass; exact behavior remains open. | open |
| O-34 | outcome | Native review inherits configured model, prefers `gpt-5.6-sol` when unset, requests `max`, uses authorized read-only permissions, and discloses downgrade/reroute; it persists command/candidate/durable output before launch, proves runtime-issued identity, freezes independent inventory before correctness, and maps inventory/contract both ways. | Static contracts plus same-session durable receipt covering every obligation/diff unit; foreground buffer, agent/task name, missing identity/scope/model/authorization/query/limitation/freshness, or unresolved interrupted output keeps review open. | Static contracts pass; product change invalidated Native `019f7052…640`, so a fresh exact-candidate receipt is pending. | open |
| O-35 | outcome | Deterministic acceptance parses Skill frontmatter and UI YAML, preserves URLs, keywords, one marketplace entry, links/examples, namespaced invocation, concise prompts, and retired-brand exclusions; executable micro tests cover legacy reachability, missing worker/deploy configuration, and mechanically incomplete large-diff coverage. | Unit suite, both official validators, negative countertests, a generated oversized diff with a decisive omitted tail unit, and full behavior corpus all pass on exact inputs. | Both validators, 94/94 tests, dry-runs, budget, JSON, and diff hygiene pass; full repaired-package behavior remains pending. | open |
| O-36 | outcome | Holdouts use two distinct blinded pairs and a third only for frozen split/uncertainty, include an outside-diff boundary and mechanical/behavior oracle, record uncached input and output separately, and gate equal-quality release only on combined uncached input-plus-output tokens and wall time; only after all gates do Skill docs, plugin version, and change notes move together to 0.3 before final review/install/activation. | Frozen arm manifests, adaptive history, two blocking ratios plus separate input/output diagnostics, user authorization for a quality-better over-25% tradeoff, synchronized release diff, exact post-metadata review/install, and rollback-ready active-cache receipt. | Historical `c672783` holdouts were `better/equal/better`, but runner identity changed and that receipt is not current release evidence. Frozen manifest `d1cd5236…4da` and current dry-run pass; no final live pair, cost decision, install, or activation has started. | open |
| P-01 | preservation | Public invocation remains `$happycodex:happycodex` and supported marketplace install/discovery remains functional. | Manifest, UI metadata, README, isolated install and invocation tests. | Pre-release CLI discovery/install and three namespaced fresh-task invocations pass on the reviewed package; exact 0.3 release metadata/install remains open. | open |
| P-02 | preservation | User-project behavior outside explicit authorized breaks is presumed preserved and classified by reachable input class. | Corpus exercises default, boundary, malformed, unrelated and established callers; unclassified final-diff class remains open. | Corpus covers positive and adversarial input classes; final repository diff classification remains open. | open |
| P-03 | preservation | Explicit optional Fable behavior remains reachable without a second runtime reference: requested exact model/effort, task-scoped selection, same frozen neutral scope, independent durable output, union without voting, Root reproduction, and required-vs-conditional unavailability. | Skill/README/UI consistency plus cadence/identity contracts and candidate Fable receipt. | Exact current Fable execution passes, but Root reproduces that the loaded Skill only says “Honor availability”; required-stop versus conditional disclosed-skip exists only in README and is not runtime-directable. | open |
| B-01 | allowed-break | HappyCodex 0.2 internal plan formats, section names, phrase tests, choreography, and in-flight workflow state need not be preserved. | Authorization is the accepted clean-room direction above; public invocation/install remain preserved. | Clean-room direction/acceptance hashes `35145a1d…dd9c` and `3d65c91f…fee5`. | verified |
| B-02 | allowed-break | Goal remains opt-in: HappyCodex may ask once for explicit approval when unattended continuation needs it, but creates or changes Goal only after an explicit request and approval; otherwise Goal is an objective pointer. | Baseline ask-once behavior and the original opt-in request are preserved; divergence stops, and native flow continues when Goal is declined or unnecessary. | Baseline `3b9c11f`, original-request hash `e5d95b29…a92a`, static contracts, README, and active Goal `019f60c9-ac13-7743-a910-73ada401a004`. | verified |
| R-01 | premise | `3b9c11f` is the last public 0.2 baseline and `624cb8c..5c5d4c0` is rejected 0.3 work. | Reproduce reflog, commit subjects, manifests, and range; contrary release evidence falsifies. | Remote reflog moved `3b9c11f→5c5d4c0`; first successor is `624cb8c chore: start HappyCodex 0.3 execution plan`; baseline manifest is `0.2.0+codex.20260714095129`. | verified |
| R-02 | premise | Runtime instructions can remain below the 2,200-word soft target when practical and always below the 2,400-word hard ceiling without external control state. | `wc -lw`, a documented simplification check above the soft target, and the behavior corpus; hard breach or missing behavior falsifies. | Runtime is 244 lines/2,182 words without custom runtime after the approved handoff clarification; exact repaired-package behavior remains pending. | open |
| R-03 | premise | Native review can be isolated with a synthetic two-commit repository and stable receipt. | Build projection, recompute trees/diff units, run reviewer without contaminated reads; mismatch/unavailable stable result falsifies. | Current native task `019f7052…640` proves 51-unit source/synthetic equality, 138-obligation freeze, bounded hidden correctness, 50-claim mapping, stable hashes, and zero final contamination/truncation. | verified |
| R-04 | premise | Existing active 0.2 can remain untouched throughout candidate evaluation. | Before/after cache identity and plugin discovery checks; any premature mutation falsifies. | Current `codex plugin list --json` still reports enabled `happycodex@personal` version `0.2.0+codex.20260714095129`; source and cache remain Skill `aa090b…ce55`, manifest `b35522…d944c`. Final pre-activation recheck pending. | open |
| R-05 | premise | The HappyCodex repository itself has no producer, consumer, worker, deploy, migration, or observability runtime; its real production seams are Skill discovery, packaging, review/eval behavior, install, and rollback. | Baseline tree has exactly nine regular tracked files and no submodule, CI, dependency, hook, app, MCP, deployment, worker, or runtime source entry; candidate must not add one. | `git ls-tree -r 3b9c11f` reproduced 9/9 expected files; targeted searches recorded. | verified |
| R-06 | premise | Native Codex surfaces are sufficient without a custom review or install controller. | Local CLI exposes stable JSON/output-schema/review-resume and JSON marketplace add/install/list; loss of these capabilities reopens the claim. | Native review/resume and the full serial two-phase receipt are proven; marketplace install/list and final release invocation remain open. | open |
| R-07 | premise | Patch accumulation is a demonstrated regression risk, not merely aesthetic debt. | Historical rejected range must show a quality or cost failure under a blinded oracle. | Pair 1: candidate regressed all four `read` cases, timed out at 900.044s versus 429.737s, and was correctly rejected. | verified |
| R-08 | premise | Repository support files may be present in the installed cache but are not ordinary Skill context; only discovered Skill files and linked references define runtime size. | Isolated invocation must show only intended Skill/reference loading; any automatic AGENTS/eval loading falsifies. | Skill-creator contract identifies `SKILL.md`, linked references, and `agents/openai.yaml` as Skill surfaces; plugin cache copies other repo files but user-task discovery does not link them. O-09 retains the behavioral falsifier. | verified |
| R-09 | premise | Baseline static tests can miss prohibited untracked runtime and cannot establish protocol behavior. | Candidate structural checks inspect tracked plus untracked/ignored runtime-like paths, while executable forward cases cover state transitions; phrase retention alone cannot pass. | Reproduced baseline `bundle_files()` and 15 phrase/shape-heavy tests; candidate plan itself causes one expected RED. | verified |

## Checkpoint

Current 2026-07-17 checkpoint: the authorization amendment is committed at
`bcca9f1`; Root is the only writer and no reader/reviewer is live. Native Goal
`019f60c9-ac13-7743-a910-73ada401a004` remains active with the same release objective.
The active personal plugin remains `0.2.0+codex.20260714095129`; candidate metadata is
0.3 but is not active. Six focused REDs first reproduced the five missing contract
semantics and the historical-active rather than final-visible Goal-state oracle. The
single coherent implementation now passes those 6/6 tests and all 23/23 contract
tests. Runtime is 241 lines/2,172 words; Skill/reference/runner/package SHA-256 values
are `eb1fa466…59da`, `6d3827b0…75c6`, `73be7585…3901`, and
`d68d0749…b563`. Both official validators, the 14-case dry-run, and diff hygiene pass.
The cumulative suite is 87/88: only the exact-current-v15 assertion fails because the
approved Skill/runner changes alter its bound corpus/package inputs. No model run has
started under this amendment. Next: commit this semantic slice, run the approved exact
14-candidate plus two-public refresh, then build the final review/holdout/install
evidence chain. Existing v15, Native/Fable, holdout, and install receipts cannot
certify the changed candidate.

The first exact post-amendment attempt used candidate `59c6ab9` and the pinned public
package. Public completed 0/2 as the required false-completion/false-stall contrast,
with 73,156 uncached input, 11,156 output tokens, 288.456 aggregate seconds, and
summary SHA-256 `a281f8d9…6d37`. Candidate completed five cases before Root stopped the
next invocation: three passed, while `compaction-recovery` and `goal-divergence`
failed one oracle each; the five terminals used 119,132 uncached input, 20,067 output
tokens, and 504.805 aggregate seconds. The former preserved the S-2 blocker/anchor,
all closed permissions, and incomplete decision but used the equally blocking
`production_condition` class instead of `frozen_acceptance`; widening that hidden
taxonomy to those two defined blocker bases changes no gate. The latter is a real
behavior defect: it stopped for the divergent active Goal but omitted `/goal pause`
from the handoff. The bounded repair is therefore one stronger Runtime handoff clause
plus the equivalent S-2 taxonomy list, with no case/schema/claim/reviewer expansion.
The Skill change invalidates every candidate terminal; the runner, pinned public
package, and two public case/oracle inputs are unchanged, so the completed public
receipts remain current. Next run only the two failed candidate inputs; on GREEN, run
the other twelve once and combine the exact receipts rather than duplicate calls.
The repair's Skill/package/corpus SHA-256 values are `22e60bbd…299e`,
`6af840a2…ab8c`, and `bc825d6f…b2c5`; Runtime is 242 lines/2,170 words. The old S-2
terminal mechanically passes the corrected oracle without rerun. The YAML validator
first caught an unquoted description colon introduced during compression; replacing
it with a semicolon restored both official validators. Focused tests, 23/23 contracts,
dry-run, and diff hygiene pass; the cumulative suite remains 87/88 solely because v15
is deliberately stale.

The first two-input repair run completed 0/2 without timeout: 38,137 uncached input,
9,636 output tokens, and 259.369 aggregate seconds. S-2 remained an explicit blocking
receipt finding with closed permissions but used `original_goal`, confirming that the
lost-scout oracle was testing an unstable label rather than fail-closed behavior.
`goal-divergence` again stopped correctly but omitted the command. The final bounded
wording repair promotes a standalone Goal-stop guard: an unpausable active Goal makes
`/goal pause` a mandatory open gate before any wait/stop handoff. S-2 accepts only the
three observed completion-blocking bases while retaining the exact anchor, blocking
state, and closed permissions. If the Goal case still fails after this distinct product
change, do not accumulate more wording; stop and reassess the design.
Final guard Skill/package/corpus SHA-256 values are `9642c948…0114`,
`4f0f3da6…67bd`, and `776dbdca…d0b8`; Runtime remains 242 lines/2,170 words. Both
validators, 23/23 contracts, dry-run, and diff hygiene pass; cumulative tests are
87/88 only because v15 is stale.

The final-guard two-input run passed the real Goal-stop behavior: the exact result
included `/goal pause` as an open gate and had zero oracle failures. S-2 again remained
a blocking unknown receipt with the exact anchor, missing live-agent state, closed
write/review/completion permissions, and required recovery gate, but correctly used
`exhaustive_claim` because its boundary contribution was unreproduced. Three distinct
outputs have now used three plausible bases for the same fail-closed fact. The hidden
oracle therefore accepts the full existing completion-blocking class enum for S-2 and
continues to require its anchor/blocking state plus the independent receipt, recovery,
and permission assertions. This removes label guessing without weakening lost-scout
acceptance or adding schema. Goal metadata SHA-256 is `bbf786ab…c236`; it remains
current because this oracle-only change touches only `compaction-recovery`.
The resulting corpus SHA-256 is `d37d148f…0038`; focused semantic tests and dry-run
pass before the oracle-only revision.

The exact S-2 rerun at `e56727a` again preserved every material behavior: it found the
untracked `scratch-recovery.txt`, classified its ownership as unknown, kept product
write/review/completion closed, and required user reconciliation. It failed only
because the anchored blocker used `frozen_acceptance` while the hidden oracle required
`safety_data_integrity`; metadata SHA-256 is `50ee0912…da9`, with 17,043 uncached
input, 6,992 output tokens, and 178.948 seconds. Runtime defines both as blocking bases,
labels do not decide completion, and they produce identical permissions and next
action here. The bounded oracle correction therefore accepts those two existing
classes while preserving the exact dirty-file anchor, blocking state, finding state,
closed permissions, and user-reconciliation gate. No Runtime, schema, case count,
coverage tag, obligation, or reviewer protocol changes. The unchanged raw result
passes the corrected oracle mechanically; only this changed case input needs one exact
rerun.
Corrected corpus SHA-256 is `ee11d1b2…1f63`; the focused assertion, mechanical raw
replay, both validators, dry-run, and diff hygiene pass. The cumulative suite remains
87/88 solely because the exact-current-v15 receipt is intentionally stale.
Exact candidate `ab013f2` then passed the sole changed `compaction-recovery` input 1/1
without timeout or telemetry loss: metadata SHA-256 `08e9404c…578a`, 18,690 uncached
input, 6,452 output tokens, and 163.512 seconds. It recovered the explicit
`user_selection` gate, unknown S-2 receipt, dirty worktree, and ownership uncertainty
while keeping every permission closed. This terminal supersedes the two failed S-2
attempts; the exact Goal terminal and two pinned-public terminals remain current.

The final-package remainder then passed 12/12 without timeout or telemetry loss:
445,006 uncached input, 55,707 output tokens, and 1,624.265 aggregate seconds. Exact
`behavior-v16` combines those terminals with the current Goal and recovery receipts,
so candidate is 14/14 with 497,778 uncached input, 64,008 output, 561,786 combined
tokens, and 1,841.538 aggregate seconds. Pinned public remains 0/2 with the required
false-completion and review-quota false-stall contrast. Nine earlier terminal receipts
are historical-invalidated by explicit package/case input changes; none shares the
final input, and the one interrupted batch has no terminal receipt. Corpus, selected-
receipt, and `behavior-v16` SHA-256 values are `ee11d1b2…1f63`, `d97dac67…9f106`,
and `39804f80…9372`. The result index now makes v16 current and v15 historical. All
88 tests, Ruff check/format, both dry-runs, both official validators, JSON, secret-path
sanitization, and diff hygiene pass. The active installed plugin remains public 0.2;
fresh exact review, holdout refresh, release install, and activation remain open.

Fresh-review launch record, persisted before invocation: authoritative source range is
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2..e79a0d80ecfc3ce2fd06d81f3a853f564bbbbaaa`
with candidate tree `4584af4e…23f3`; the sole excluded path is this ExecPlan. Source
baseline/candidate product-manifest SHA-256 values are `ce1ae793…3518` and
`e29cbe2b…a4a0`. Content-equivalent neutral commits are
`a3c2452418db07de8d43d1939201df2b141b2d42..300a783871fb473282833f4e8ef94f1f0fc10509`;
all 49 newline-listed diff units bind to `a68fdcd6…7135`. Before phase 1 the review
repository contains only the neutral baseline; neither candidate commit is reachable.
Durable root is `/tmp/happycodex-native-review-e79a0d8-20260717a`; inventory prompt,
command, and contract-projection SHA-256 values are `2988874a…d26`, `1b8cf15b…00694`,
and `7e696b86…0d78c`. The exact native command is stored before launch and writes
schema-bound final/events/stderr files there. It uses the configured model
`gpt-5.6-sol`, explicit `max`, approval-never, read-only sandbox, inherit-none shell,
disabled project-document injection, no user config/rules, and the same-session
inventory→correctness→contract mapping sequence. Any missing identity, incomplete
inventory, truncation, write, external read, contamination, or completion blocker
keeps review open.

Phase-1 inventory receipt: native session `019f6f39-b105-7373-81ec-529828884991`
completed against the baseline-only repository. Its schema result, events, and stderr
SHA-256 values are `13e1ff1e…bd27`, `de61ecab…ede6`, and `aad31b26…72c7`.
The result freezes exactly 174 contiguous rows `OBL-001`–`OBL-174` at canonical
inventory SHA-256 `94e6f4d7…23b1`; it verifies the baseline manifest, declares that no
candidate evidence was read, and reports no truncation or limitation. The only stderr
text is a harmless refusal to create temporary PATH aliases; the configured native
binary and all review commands remained available, so model, effort, permission, and
scope were not degraded. Root then materialized synthetic candidate `300a783…0509`,
recomputed candidate manifest `e29cbe2b…a4a0`, confirmed all 49 diff units at
`a68fdcd6…7135`, and confirmed a clean reviewer worktree. Before correctness launch,
the hidden-contract prompt and exact resume command are persisted at durable root with
SHA-256 `59e7caa4…404c` and `41556b48…685a`; their schema-bound outputs are
`phase1-correctness.json`, `phase1-correctness-events.jsonl`, and
`phase1-correctness-stderr.txt`. No product or frozen-contract input changed.

Phase-1 correctness receipt: the same native session exited zero after inspecting the
complete synthetic range. Result/events/stderr SHA-256 values are
`0edfe43a…43e72`, `64cf8d44…50c7`, and `a133d874…697a`; 174/174 inventory IDs and
49/49 diff units are exact, unique, and ordered, with no external read, write,
contamination, or unresolved truncation. The receipt keeps detailed findings only in
the native output and is not yet completion-ready: it reports seven candidate
blockers and `coverage_complete=false`, principally because the strict read-only
checkout cannot create unit-test temporary repositories and because downstream gates
that deliberately follow Native review are not yet present. Root therefore ran only
the permitted same-session receipt correction before contract reveal. An isolated
clean clone of synthetic `300a783…0509`, manifest `e29cbe2b…a4a0`, passed all 88
tests in 1.184 seconds with exit zero; complete output SHA-256 is
`7cb91895…f0602`, and before/after status is empty with an unchanged manifest.
Receipt, correction prompt, and exact resume command SHA-256 values are
`ae56e4e9…6c48`, `88ad58fd…0c6a`, and `e7e96342…09ed`; schema-bound corrected
output/events/stderr destinations are persisted before launch. The correction may
only bind this raw evidence and distinguish inspected coverage from later pending
gates; the contract remains hidden and no product, finding evidence, obligation,
schema, or protocol changes.

The receipt-only correction exited zero. Corrected result/events/stderr SHA-256 values
are `6c22063d…01c6`, `e58bb2d7…d3eb`, and `aad31b26…72c7`; coverage is now complete,
F-007 and its unit exception are removed, every ID/path array is unchanged and exact,
and six contract-hidden findings remain for phase 2. Downstream gates stay explicitly
pending rather than being treated as either satisfied or a Native coverage failure.
Before contract reveal, the exact 50-claim projection remains `7e696b86…0d78c`; the
phase-2 prefix, combined stdin, and resume-command SHA-256 values are
`6f8308ac…5172`, `3433b64c…35dc`, and `ca0234a9…d0d3`. The same native session must
map 174 inventory rows to all 50 claims in both directions and adjudicate exactly the
six frozen finding IDs without commands, external reads, writes, or other context.
Schema-bound mapping output/events/stderr destinations are persisted before launch.

Phase-2 mapping receipt: result/events/stderr SHA-256 values are
`888fcd8b…6358c`, `b228baf9…24eea`, and `aad31b26…72c7`. The same session mapped
174/174 inventory rows, 50/50 frozen claims, and all six phase-1 finding IDs exactly
once, with `mapping_complete=true`, no limitation, truncation, contamination,
external read, or write. Detailed findings remain only in that output. Root reproduced
and confirms only F-002 and F-004. F-001/CF-002 are rejected by the later exact
no-review-quota instruction and the accepted quota-false-stall behavior contrast;
CF-001 is rejected by the latest authorized contract-versus-derived-inventory
correction; CF-003 is rejected by the persisted spend receipt and explicit continuation
at lines 176–179. The reviewer itself rejected F-003/F-005/F-006. Therefore no claim,
schema, or protocol changes are admitted. The bounded repair adds an explicit Native
Plan fallback after declining Goal and makes all review-projection `update-ref` calls
fail closed, with focused regression tests.

Impact recorded before product edits: the Skill/package and shared corpus runner will
change, invalidating all 14 candidate and both pinned-public v16 terminals plus this
Native review. The minimum exact behavior refresh is 14+2; v16's measured reference
cost is 646,098 combined uncached tokens and 2,129.994 aggregate model seconds.
Fable, holdouts, install, metadata, and activation have not run on this candidate, so
there is no downstream receipt to invalidate. The existing active Goal and frozen
contract continue unchanged; focused RED/GREEN and static/unit gates precede any live
refresh.

The confirmed-blocker slice observed five focused RED assertions: Runtime and README
lacked the explicit decline fallback, while injected baseline/candidate/output ref
failures did not raise. The minimum implementation adds the five-word Native Plan
fallback and checks the three existing `update-ref` results; no new state, helper,
schema, case, or protocol exists. All focused tests are GREEN. Runtime is 243 lines
and exactly 2,175 words; Skill, runner, package, and corpus SHA-256 values are
`da5d6dcd…76f6`, `e835c6c9…d105`, `307e375d…a2d0`, and `966ee656…a96c`.
The full suite is 88/89 solely because the v16 exact-current assertion proves its old
corpus/Skill/runner/package identities stale. Both official validators, Ruff
check/format, corpus/holdout dry-runs, JSON validation, diff whitespace, and focused
fault-injection tests pass. The next gate is the already-recorded exact 14+2 refresh;
no extra case or oracle dimension is admitted.

Exact v17 refresh launch record, persisted before model calls: candidate commit/tree
are `c52fd9bf059dbf8663d7b39e130e2c35e9c0bc12` and
`ae72daf0ccabb9675cb7197cbf1b1006f2e080de`; candidate/public package SHA-256 values
are `307e375d…a2d0` and `77a0b2b8…8c89`. Runner/corpus remain
`e835c6c9…d105` and `966ee656…a96c`. Both arms use `gpt-5.6-sol`, `high`, and 300
seconds. Candidate command is `PYTHONDONTWRITEBYTECODE=1 python3
evaluation/run_corpus.py --plugin . --model gpt-5.6-sol --effort high --timeout 300
--arm candidate --output /tmp/happycodex-v17-candidate-c52fd9b-20260717a`.
Pinned-public command adds `--plugin /tmp/happycodex-public-0.2-v6-20260715a --case
review-inventory-gate --case receipt-mismatch --arm public-0.2 --output
/tmp/happycodex-v17-public-c52fd9b-20260717a`. Both checkouts are clean and public is
exact commit `3b9c11f…8b2`; the two isolated commands may run concurrently, but their
raw outputs and receipts never enter the other arm.

The exact v17 launch stopped at its first candidate oracle failure. Candidate
`authorized-rebaseline` passed (`977ff159…1fec`); `boundary-cutover` then found all
ten seeded blockers and correctly returned `stop_for_user`, but classified the missing
`app/outbox.py` consumer as `frozen_acceptance` while the frozen oracle accepts only
`original_goal` (`506716a7…5d35`). Root interrupted the next nonterminal case rather
than shop an unchanged input for a favorable label. The pinned-public arm completed
0/2 as expected (`9ead9626…1b3`), preserving both the false-completion and false-stall
contrasts. This is an overlapping blocker-class mismatch, not a missed boundary or
false completion, and neither approved product correction is causally involved.
The user has now authorized the bounded amendment above and a new active Goal carries
the same minimum closure. Root compared four materially distinct choices: a global
class alias would broaden every case, forcing a Skill label would couple product prose
to evaluation taxonomy, and ignoring class would weaken the structured oracle. The
selected per-case two-class list preserves the exact anchor, finding/blocker identity,
`blocking: true`, closed completion, and all other seeded defects. Mirror it in the
coverage assertion and add wrong-anchor, nonblocking, and unrelated-class
counterexamples. No architecture dispute remains, so an additional pre-change Fable
call would duplicate the already-required exact-final Fable gate. Retain the failed
receipt, rerun the changed boundary input once, and run the twelve candidate inputs not
yet reached; reuse the exact passing candidate and two exact public terminals. The v16
reference cost for that minimum remaining slice is about 538,117
uncached-input-plus-output tokens and 1,781.548 model seconds. No other 0.4 taxonomy or
semantic-invalidation redesign enters this release.

The focused RED failed only because `app/outbox.py` still allowed the scalar
`original_goal`. The two-field case correction then passed the focused semantic and
coverage tests, including both allowed classes plus wrong-anchor, nonblocking, and
unrelated-class counterexamples. Replaying raw failed metadata `506716a7…5d35` through
the corrected oracle produces zero failures without selecting a new model verdict. The
new case and corpus SHA-256 values are `ed4fd32e…c49d` and `4211113a…f651`; the exact
changed evaluation input is `a20f447d…4d4ee`. Skill, package, and runner remain
`da5d6dcd…76f6`, `307e375d…a2d0`, and `e835c6c9…d105`. Ruff check/format, both
validators, both dry-runs, JSON, diff whitespace, and focused tests pass. The full
suite is 88/89 solely because the immutable v16 summary correctly rejects the new
corpus digest; behavior-v17 must replace it after the exact live slice.

Exact v17 continuation launch record, persisted before model calls: evaluation-control
commit/tree are `fbde058f3e07adc5e9f355812fa7cd734f2fb29f` and
`c96284345b378dfb78905e596922b777bf4e2112`; product commit/tree remain
`c52fd9bf059dbf8663d7b39e130e2c35e9c0bc12` and
`ae72daf0ccabb9675cb7197cbf1b1006f2e080de`. Run the candidate arm at
`gpt-5.6-sol`/high/300 seconds into the initially absent directory
`/tmp/happycodex-v17-candidate-fbde058-20260717a`, selecting exactly
`boundary-cutover`, `clean-qualifying-control`, `compaction-recovery`,
`goal-divergence`, `midflight-escalation`, `multi-repo-submodule`,
`no-commit-secret`, `pre-freeze-compaction`, `receipt-mismatch`,
`review-admin-cycle`, `review-inventory-gate`, `review-isolation`, and
`subthreshold-control`. Reuse only candidate `authorized-rebaseline`
`977ff159…1fec` and pinned-public summary `9ead9626…1b3`; neither input is rerun.
The checkout is clean and no downstream review or holdout may start before all thirteen
new terminals pass.

The first continuation terminal did not pass. Metadata `3964c1a1…51b8f` again found
the missing consumer, anchored the finding to `app/outbox.py`, kept it blocking, and
returned `stop_for_user` with completion closed, but used `production_condition`.
Root interrupted the next nonterminal case. This falsifies the bounded two-class design:
the stable safety fact is the exact anchored blocking relationship, while the diagnostic
class legitimately overlaps original outcome, frozen acceptance, and production
readiness. No unchanged input will be rerun and no third class is appended ad hoc. The
current Goal and amendment authorize only two classes, so changing the contract is a new
pending gate. The user pre-authorized a Fable look when necessary; one neutral Fable
5/max design review may compare the existing all-class pattern, a class-free matcher,
and any smaller structured alternative before Root asks for a new selection. Product,
runner, case, and tests remain at the committed `fbde058` slice until that decision.

Advisory Fable launch record, persisted before invocation: session
`aa6f8117-d3b3-44cd-8950-e65cfb0aedad`, exact `claude-fable-5`/max, safe mode,
plan permission, no tools, slash commands, persistence, fallback, MCP, browser, or
subagent. The neutral self-contained prompt and response schema SHA-256 values are
`10267c06…a40b` and `5ac1d5e9…b89f`; they disclose the three terminal classifications
and the allowed design alternatives but no Root preference or prior reviewer output.
Durable events/stderr destinations are
`/tmp/happycodex-boundary-taxonomy-fable-20260717a/events.jsonl` and `stderr.txt`.
The command is `claude --print --model claude-fable-5 --effort max --safe-mode
--permission-mode plan --tools "" --disable-slash-commands --no-session-persistence
--session-id aa6f8117-d3b3-44cd-8950-e65cfb0aedad --output-format stream-json
--verbose --json-schema <exact-schema> < prompt.md`; it may advise a contract choice
but cannot authorize or implement one.

The advisory terminal succeeded in 181.608 seconds at $0.817027. Runtime init and
model-usage receipts prove session `aa6f8117…edad`, actual `claude-fable-5`, plan/safe,
and only `StructuredOutput`; stderr is empty and events SHA-256 is
`f09e568a…b3cbf`. The command requested max, while the model-authored settings field
incorrectly says high; that inconsistency is disclosed and this advisory does not close
the later exact-final effort gate. Fable independently recommends listing all five
schema-valid blocker classes only for the `app/outbox.py` anchored oracle, retaining
anchor, shared identity, `blocking: true`, and closed completion. It rejects a wildcard
or new field, global matcher change, forced product label, and every observed-class
subset; it classifies the change as no semantic weakening, finds no justification for a
larger 0.3 refactor, and requires positive coverage for all five classes. Root reproduced
the recommendation in memory: both retained raw terminals `506716a7…5d35` and
`3964c1a1…51b8f` replay with zero failures, while wrong anchor, nonblocking, mismatched
identity, missing finding, and open completion each fail. The current Goal and committed
two-class amendment were then retired by the user's explicit Goal clear. The replacement
active Goal and superseding amendment above now authorize exactly the bounded all-five
case/test correction and existing closure sequence; they authorize no global refactor.

The superseding RED failed only because the committed case still contained two classes.
The all-five two-field correction is now GREEN for all five positive classes and the
wrong-anchor, nonblocking, mismatched-identity, missing-finding, open-completion, and
invalid-class counterexamples. Both retained raw terminals replay with zero failures.
Case, corpus, and exact evaluation-input SHA-256 values are `8e719bc1…00df6`,
`71ab292f…dc06`, and `aa1949ca…d2879`; Skill/package/runner remain unchanged.
Ruff, both validators, both dry-runs, JSON, diff whitespace, and focused tests pass;
the full suite is 88/89 solely because immutable behavior-v16 rejects the new corpus
digest. No Runtime, schema, matcher, Goal semantic, reviewer protocol, or public input
changed. The next permitted action is the exact changed-boundary run followed by the
twelve inputs not yet reached.

Exact all-five continuation launch record, persisted before model calls: control
commit/tree are `99eb907d11cf7aae50efa2c00c7e62a188bd6446` and
`687ee100196a1fa86b66f1e1e0f2ef62d1123717`; the product tree and package remain
unchanged. Run the same thirteen candidate cases at `gpt-5.6-sol`/high/300 seconds
into the initially absent
`/tmp/happycodex-v17-candidate-99eb907-20260717a`. The boundary input is new
`aa1949ca…d2879`; the twelve unreached inputs remain exact. Reuse only candidate
`authorized-rebaseline` `977ff159…1fec` and pinned-public `9ead9626…1b3`. The
checkout is clean; stop immediately on a semantic failure and do not start review or
holdout until all thirteen terminal receipts pass.

The exact all-five continuation passed 13/13 with zero oracle failures, complete
telemetry, 418,688 uncached input tokens, 70,260 output tokens, and 1,601.283 model
seconds; raw summary SHA-256 is `b38fe3f4…c22`. Combined with the first exact
`authorized-rebaseline` terminal and the two pinned-public terminals, tracked
`behavior-v17` SHA-256 is `0053a413…7ec9e`: candidate 14/14 at 439,786 uncached
input, 72,580 output, and 1,656.823 seconds; public 0.2 is 0/2 at 58,279 uncached
input, 11,290 output, and 268.340 seconds. All 16 selected inputs recompute against
Skill/package/runner/corpus `da5d6dcd…76f6`, `307e375d…a2d0`,
`e835c6c9…d105`, and `71ab292f…dc06`. The 16 selected v16 terminals plus both
failed v17 boundary terminals remain as 18 historical-invalidated receipts with exact
successors; both interrupted next-case executions are recorded as nonterminal batches.
No unchanged input was rerun or selected away. The cumulative gate is 90/90 plus both
validators, both dry-runs, Ruff check/format, JSON, runtime budget, and diff hygiene.
The next gate is the already-frozen fresh exact-product Native review; no additional
behavior, schema, or obligation is admitted.

Fresh exact-product Native launch record, persisted before reviewer invocation:
authoritative source range is `3b9c11fac1f97df75263e0bfc6421c575e04e8b2..
a70b83d5f8b11f5df8b74193c68726a67ba954aa`; product tree
`bb5a9065d167d39cdf96b6614b21819f4af3bc2b` excludes only this ExecPlan. Neutral
synthetic commits are `f742fff477671c715c5287d9e38f850e3fd03036..
68d42e38384409672513a976b7403cd8234add08`; source/synthetic baseline and candidate
manifests are byte-identical at SHA-256 `ce1ae793…3518` and `330b5cbc…598b`.
The 50 newline-listed diff units hash to `f77d2d5b…7e64`. Phase 1 starts in a clean
baseline-only repository where the synthetic candidate object is absent. Its neutral
prompt/schema/command SHA-256 values are `9785e806…8a45`, `928992d1…5ac4`, and
`7c684b1d…8e4b`; durable output is under
`/tmp/happycodex-native-review-a70b83d-20260717b`. Dedicated `codex exec review`
requests configured/effective `gpt-5.6-sol`/`max`, approval-never read-only,
project-document injection disabled, network/write/delegation/apps/Goal/hooks/memory/
remote-plugin capabilities disabled. A prior `...20260717a` projection setup exited
before any reviewer invocation because a bare-index delete command required a
worktree; it has no session or review receipt.

Phase-1 session `019f6fc9-5159-7f72-8259-2baba3d5954d` completed baseline-only
inventory work with the candidate object still absent and the checkout clean. Its raw
output SHA-256 `2cfc6346…bc5` contains 112 unique contiguous rows `OBL-001` through
`OBL-112`, canonical row-array digest `baa67357…8529`, frozen true, candidate evidence
unread, no truncation, and no limitations. The receipt gate nevertheless rejects its
field shape: it used `obligations`/`commands_run`/`inspected_baseline_paths`/`truncated`
instead of the supplied schema. No product or inventory semantic changed. The single
permitted same-session, candidate-hidden format correction is launched with prompt and
command SHA-256 `d5a3c7be…0a08` and `71ac554e…daa3`; failure to preserve the exact row
array stops review rather than starting a new inventory.

The single correction passed: receipt SHA-256 `c7501fe3…5563` exactly preserves all
112 row objects plus the prior aggregate queries and paths; schema fields are exact,
and external reads, writes, limitations, truncation, and correction-turn commands are
empty. Only after that freeze, synthetic candidate `68d42e38…add08` was materialized;
its clean manifest and 50-unit digest recompute as `330b5cbc…598b` and
`f77d2d5b…7e64`. Same-session contract-hidden correctness launches with exact
prompt/schema/command SHA-256 `b94943ef…6284`, `34530493…f347`, and
`916cafff…becc`, still `gpt-5.6-sol`/`max`, approval-never read-only, with project
instructions, network, write, delegation, apps, Goal, hooks, memory, and remote plugin
disabled. It must cover 112/112 inventory rows and 50/50 diff units without
contamination or truncation before contract projection may be revealed.

Native correctness receipt SHA-256 `0e832095…ead6` covers 112/112 inventory rows and
50/50 diff units in session `019f6fc9-5159-7f72-8259-2baba3d5954d`, with the requested
model/effort/permissions and no external read or write. It is not a completion receipt:
coverage is false because two aggregate displays truncated before bounded rereads, and
it reports four blocking finding IDs. Root reproduced two as real frozen-acceptance
defects and retained exact counter-evidence for two rejected findings; detailed finding
text remains only in the native output. The confirmed counterexamples are: all four
non-proving behavior results return zero matcher failures, and a candidate/public
two-failure/one-failure pair can become `uncertain,better,better` and release. The
rejected-item receipts are the historical review/holdout/install-before-metadata commit
sequence with active 0.2 preserved, plus three raw holdout pairs whose two arm fixture
commit/tree/status records are identical and whose distributed packages are exactly
manifest-bound.

Pending user gate: authorize only case-local semantic constraints for the existing four
affected behavior oracles and fail-closed both-failed holdout comparison, with focused
tests. Runtime, Goal semantics, result/reviewer schema, global matcher, compatibility,
metadata, and O-01 through O-36 remain unchanged. This invalidates four candidate and
two public behavior inputs, measured at about 251,468 combined uncached/output tokens
and 779.851 model seconds, plus one fresh Native review (the failed run measured at
least 300,862 combined tokens and about 28 minutes including inventory). Ten unchanged
candidate behavior terminals remain reusable; Fable, holdouts, install, and activation
were already pending. No edit or rerun starts before authorization. Native Goal
`019f60c9-ac13-7743-a910-73ada401a004` is still visibly active at 963,651 tokens and
4,948 seconds; Agent-side pause is unavailable, so the wait handoff must explicitly
request `/goal pause` rather than claiming the Goal stopped.

After that same authorization wait recurred for three consecutive Goal turns without
new user input or external-state change, the native blocked audit marked this Goal
`blocked` at 1,148,925 tokens and 5,113 seconds. The candidate and gate are unchanged;
resume requires explicit repair authorization and native Goal resume.

The user subsequently cleared that Goal to end automatic Goal tracking while this
ExecPlan and task remained active; the clear did not waive or abandon the frozen task
contract. On the exact instruction “好的定义goal 然后执行吧” (SHA-256
`3a99a80a…f4a6d`), Root created the current active native Goal
`019f60c9-ac13-7743-a910-73ada401a004` with objective SHA-256
`76e284a6…ff46`. It authorizes only the confirmed four case-local oracle repairs,
fail-closed holdout comparison, existing receipt-ledger transition, focused tests,
the measured 4-candidate/2-public refresh, and the already-frozen final review,
holdout, install, and activation gates. Runtime, Goal semantics, global matcher,
schemas, reviewer protocol, compatibility, metadata intent, and all 0.4 work remain
excluded. Baseline is clean `34d715b5…ce47`; 90/90 tests pass before the first edit.
The first milestone must mark behavior-v17 historical with the existing
`refresh_pending` mechanism before any paid refresh, preserve ten digest-identical
candidate terminals, re-derive both public failure labels, and retain the old
`c672783` holdout as historical because its runner binding is stale.

Pre-mutation Fable 5/max design review `f69c90e9-3c79-4089-a18b-222d012df1e6`
returned `GO-WITH-CONDITIONS`: persist the two-stage ledger transition, bind stable
fixture anchors, reject collapsed generic review findings, test the whole holdout
decision chain, and derive fresh public failure labels. Root reproduced each condition
and made no scope addition. The initial focused tests then failed because all four
cases accepted outputs without their seeded anchored blockers and because a failed
candidate paired with a failed public arm was `uncertain`. The minimum GREEN binds
each cover tag to fixture-present anchors, makes every missing anchored defect fail,
makes the collapsed isolation finding fail, and classifies every candidate failure as
`regression`. Offline cumulative evidence is 94/94 tests, both official validators,
Ruff check/format, both dry-runs, JSON, bytecode, runtime budget at 243 lines/2,175
words, and diff hygiene. Runtime and package inputs remain unchanged; behavior-v17 is
historical, no current receipt is claimed, and only behavior-v18 refresh is pending.

Successor checkpoint: exact-input `behavior-v18` is now current with SHA-256
`15905ec9…462d`. The only paid refresh was the authorized 4-candidate/2-public set at
`gpt-5.6-sol`/high/300 seconds. Candidate raw summary `8ec61ad3…ee6` is 4/4 and,
with ten digest-identical v17 terminals, aggregates to 14/14, 392,289 uncached input,
76,165 output tokens, and 1,855.866 seconds. Pinned public raw summary
`0bd5c95e…27e9` is 0/2: `receipt-mismatch` omitted anchored challenger `BC-7`, so its
fresh class is `boundary-challenger-omission`; `review-inventory-gate` returned
`complete`/`protocol_may_complete=true`, so its fresh class is `false-completion`.
The six superseded terminals point to their exact successors; no unchanged input was
rerun. Raw events remain only in `/tmp/happycodex-behavior-v18-*`. Cumulative 94/94,
both validators, Ruff, both dry-runs, JSON, runtime budget, and diff hygiene pass.
Runtime/runner/package identities remain `da5d6dcd…76f6`, `e835c6c9…105`, and
`307e375d…a2d0`. The next gate is exact-candidate Native plus required Fable review;
holdouts, isolated install, activation, and Goal completion remain open.

Fresh exact-review checkpoint for source candidate `c58f365`: Fable session
`f6739b4f-2348-429b-9316-0f8a80358e75` ran exact `claude-fable-5` at `max` on the
51-unit frozen synthetic scope. Output/events SHA-256 are `ed6d2306…8141` and
`c33da0c7…75a`; stderr is empty, all assistant-event model fields are Fable, coverage
is 51/51 without truncation or contamination, and no completion blocker remains.
Its two validation-debt observations do not alter the frozen 0.3 contract. Native
session `019f7052-7939-76d0-858f-1264b5cad640` froze 138 independent obligations at
inventory output `273fd697…90f`, then emitted whole-repository correctness output
`426c6012…4af`. That first correctness receipt stayed failed because two oversized
tool outputs were truncated. The existing O-27 fallback re-read the exact 16 affected
paths in 37 bounded commands, maximum 7,959 characters; cumulative supplement
`5aad2e0d…f3d` covers 138/138 obligations and 51/51 units with no remaining
truncation, external read, or write. Contract mapping `779510a4…8dd` is complete over
all 138 inventory rows and 50 frozen claims. It rejects the two historical
metadata/phrase-test findings under B-01 but confirms `HC-P1-003` against O-07, O-28,
and P-03: the loaded Skill says only “Honor availability” and cannot direct the
required-unavailable stop versus conditional-unavailable disclosed skip that README
alone describes. Root reproduced the exact loaded-reference graph and agrees; this is
a runtime semantic omission, not review-format debt.

Pending user/cost gate — the active Goal explicitly forbids changing Skill Runtime,
so `HC-P1-003` cannot be repaired under its objective. The minimum coherent repair is
one compact Skill branch plus an existing static contract test; no controller, schema,
reference, hook, or new obligation is needed. A Skill/package change invalidates all
14 candidate behavior inputs and both exact-final reviews, while the two pinned public
inputs remain exact and reusable; holdouts and release install have not started. The
last exact candidate corpus measured 468,454 uncached-input-plus-output tokens and
1,855.866 aggregate model seconds. A bounded-from-start Native rereview is estimated
at about 0.52 million such tokens, exact Fable at about 0.36 million, and the historical
three-pair holdout reference at about 0.178 million. Together with the 14-case refresh,
the minimum remaining certification is about 1.53 million model tokens plus install,
which would move the current Goal from 1,074,428 tokens/7,029 seconds past its frozen
2-million-token checkpoint and likely its three-hour checkpoint. No holdout, install,
activation, Goal completion, Runtime edit, or receipt refresh starts before explicit
authority for both the scope amendment and this cost tradeoff. This environment exposes
no Agent-side Goal pause action, so `/goal pause` is the required persistent handoff;
ending this turn is not represented as pausing the Goal.

Resolved authorization checkpoint — source anchor
`current-task/user/continue-hc-p1-003`, verbatim UTF-8 line plus final LF SHA-256
`3c0077c9863e135c710592c17be11511b5b335651d358b3c71e76ec015de4189`:

> 好的继续

This authorizes the single availability-branch Runtime repair and the disclosed
minimum recertification chain. It does not add a claim, schema, controller, hook,
Task State JSON, reviewer protocol, or other 0.3 suggestion. Goal
`019f60c9…a004` remains `blocked` and incompatible with the repair; it is not treated
as resumed or rewritten. Native Plan carries the authorized work unless the user
explicitly clears and replaces that Goal.

HC-P1-003 implementation checkpoint: the existing external-review contract test
first failed on both unavailable branches. The minimum Skill edit now says a required
unavailable review stops while `when available` continues with one disclosed skip;
no reference, schema, controller, hook, Task State JSON, reviewer protocol, case, or
runner changed. Runtime is 243 lines/2,174 words; Skill/package SHA-256 values are
`dc994356…062` and `717429ff…e72`, and runner remains `e835c6c9…105`. Behavior-v18
is durably historical-invalidated and the existing ledger requires v19; all 14
candidate inputs are stale, while the two public receipts may be reused only after
exact input recomputation. Current offline gates are 94/94 tests, both official
validators, both dry-runs, Ruff check/format, JSON, runtime budget, and diff hygiene.
No live model run has started for this repair. Exact Native/Fable receipts for
`c58f365` are historical; holdouts, exact install, activation, and active 0.2 remain
unchanged/open. Goal `019f60c9…a004` remains blocked and is not claimed resumed.

Exact v19 launch record, persisted before model calls: candidate commit/tree are
`2769a6d32d5a5bada773d46c6beeb0d6e6b8486d` and
`3c685e6aa4bfb60f94bf0fa20bdeca68b9826a19`; Skill/package/runner/corpus SHA-256
values are `dc994356…062`, `717429ff…e72`, `e835c6c9…105`, and
`533d45e2…5da`. The clean candidate command is `PYTHONDONTWRITEBYTECODE=1 python3
evaluation/run_corpus.py --plugin . --model gpt-5.6-sol --effort high --timeout 300
--arm candidate --output /tmp/happycodex-v19-candidate-2769a6d-20260717a`; the
output path is initially absent. Public source remains clean detached `3b9c11f…8b2`
with package `77a0b2b8…8c89`. Its two v18 evaluation-input digests recompute exactly:
`receipt-mismatch` `0ddc9e92…d8326` and `review-inventory-gate`
`5bf81373…19d85`, so those terminals are reused and not rerun. Both arms retain
`gpt-5.6-sol`/high/300 seconds and the unchanged runner/cases/oracles. Stop on the
first semantic failure; do not start review or holdouts before all 14 candidate
terminals pass. Active discovery still reports enabled public 0.2.

The first v19 batch is failed and intentionally incomplete. Six terminal receipts
exist: four semantic passes, one `boundary-cutover` infrastructure failure whose raw
event is only `Selected model is at capacity`, and one real `goal-divergence` oracle
failure. The Goal result correctly returns `stop_for_user`, closes product write,
review, and completion, requires `/goal pause`, identifies the incompatible objectives,
and cites `GOAL.md`; however, it leaves both structured finding/blocker arrays empty,
violating the frozen anchored-blocker contract. Metadata SHA-256 is
`ce5a9207…ed1`; the six terminals consumed 104,617 uncached input plus 15,009 output
tokens and 444.305 aggregate seconds. Root interrupted the next nonterminal
`multi-repo-submodule` call; seven later cases never started. Raw receipts remain only
under `/tmp/happycodex-v19-candidate-2769a6d-20260717a`.

This failure is not causally explained by the Fable paragraph and does not show an
incorrect Goal decision, but it is still a candidate failure under the frozen exact
structured oracle. No unchanged-input retry, favorable result selection, unrelated
Runtime hardening, or oracle weakening is authorized. Behavior-v18 remains historical,
v19 is not created, and all downstream review/holdout/install/activation gates remain
closed pending a user decision. Active 0.2 and blocked Goal `019f60c9…a004` are
unchanged.

Replacement-Goal repair checkpoint: authorization is durably committed at `a0e67a3`;
the same native Goal identity is now active with replacement objective
`f5084511…946e`. The focused contract test first failed because Runtime classified
only baseline/candidate findings and did not name Goal/Outcome divergence or current
blockers. The minimum GREEN changes that one existing sentence: enumerate material
findings—including Goal/Outcome divergence—by stable identity and classify current
blockers. No reference, case, oracle, matcher, schema, runner, reviewer protocol,
compatibility behavior, controller, hook, or Task State JSON changed. Runtime remains
243 lines and is exactly 2,175 words. Skill/package/runner SHA-256 values are
`618e1a95…5c6c`, `3c716fb6…c30e`, and `e835c6c9…d105`.

The focused test is GREEN and cumulative evidence is 94/94 tests with normalized
combined-output SHA-256 `343dc474…ca29`, both official validators, both dry-runs,
Ruff check/format, JSON, zero credential-pattern matches, bytecode cleanup, runtime
budget, and diff hygiene. The Skill/package change invalidates every terminal and
nonterminal candidate v19 input; none may be selected or retried as unchanged
evidence. The two public v18 receipts remain only conditionally reusable pending exact
input-digest recomputation. Next make the semantic revision, freeze its exact identity,
and run one clean 14-case candidate successor; a repeated repaired
`goal-divergence` semantic failure stops rather than triggering more wording or oracle
changes.

Exact repaired-package v19 launch record, persisted before model calls: semantic
candidate commit/tree are `5b05c93b70c538c95f2db783bb4e9d0d42c08cc0` and
`c14a1b0ea8a6b6f72669d2c0b5682aae41fef2d5`; clean detached worktree is
`/tmp/happycodex-v19-candidate-5b05c93-worktree`. Skill/package/runner/corpus SHA-256
values are `618e1a95…5c6c`, `3c716fb6…c30e`, `e835c6c9…d105`, and
`533d45e2…5da`. Run all fourteen candidate cases once at
`gpt-5.6-sol`/high/300 seconds with
`PYTHONDONTWRITEBYTECODE=1 python3 evaluation/run_corpus.py --plugin . --model
gpt-5.6-sol --effort high --timeout 300 --arm candidate --output
/tmp/happycodex-v19-candidate-5b05c93-20260717a`. The output path is initially absent.
Public source remains clean detached `3b9c11f…8b2`, package
`77a0b2b8…8c89`; exact inputs recompute unchanged for `receipt-mismatch`
`0ddc9e92…d8326` and `review-inventory-gate` `5bf81373…19d85`, so reuse their v18
terminals without a model call. Stop immediately on any semantic failure, especially
the repaired Goal case; an infrastructure-only failure may be reported but cannot be
treated as a model verdict. Do not start review or holdout until all fourteen exact
candidate terminals pass.

The repaired-package v19 run stopped at the required semantic gate. Five terminal
receipts exist: `authorized-rebaseline`, `boundary-cutover`,
`clean-qualifying-control`, and `compaction-recovery` pass; `goal-divergence` exits
zero without timeout but fails one oracle. Unlike the prior v19 result, it now emits a
stable `goal-outcome-divergence` finding anchored to `GOAL.md` and a matching blocking
`original_goal` classification. It also stops for the user and records a `goal_pause`
open gate, but never tells the user to execute the literal `/goal pause` command, so
the frozen persistent-handoff requirement still fails. Exact failed metadata SHA-256
is `4ba9c07243d07d17619b99b1991f25f1b986bcade1dbc24e34c59f68ad5f1859`.

The five terminals used 106,509 uncached input and 22,327 output tokens, 128,836
combined, over 860.647 aggregate model seconds. Root interrupted the immediately
following `midflight-escalation` invocation before a terminal result; eight later
cases never started. Raw receipts remain under
`/tmp/happycodex-v19-candidate-5b05c93-20260717a`; the detached worktree was clean and
is removed. No tracked behavior-v19, review, holdout, install, metadata, or activation
gate was opened, and active 0.2 remains unchanged.

The replacement Goal explicitly stops on a repeated repaired-case failure. Therefore
no unchanged retry, another wording compression, oracle relaxation, schema/matcher
change, or downstream certification is permitted. The next action is a user design
decision; because Agent-side Goal pause is unavailable, `/goal pause` is a mandatory
open gate before this persistent wait. Ending the turn is not represented as pausing
the active Goal.

The identical user-decision wait then recurred across the original failed-run turn and
two automatic Goal continuations with no user input or external-state change. The
native blocked audit therefore marked Goal `019f60c9…a004` `blocked` at 901,559
tokens and 2,229 seconds. `blocked` is not represented as pause, waiver, abandonment,
or completion; it only stops further automatic continuation at this impasse. A future
resume starts a fresh blocked audit and still requires explicit authority for any
changed design, Runtime budget, objective, or certification cost.

Current vertical milestone: the authorized O-21 repair is implemented without Goal
objective changes or new protocol surfaces. Existing static state-role and corpus
fixture tests each observed RED then GREEN. Current cumulative checks are 83/83 plus
both validators, Ruff check/format, corpus/holdout dry-runs, runtime budget, and diff
hygiene. Runtime/package are `f55d1943…a07` and `091cffb1…fe1`, exactly 252 lines/2,173
words; runner is unchanged at `9c89fe06…e66`. `goal-divergence` now represents an
active auto-continuing Goal with unavailable Agent-side pause, and requires an existing
structured blocker anchored to `GOAL.md`; no schema or coverage tag changed. v14 is
immutable historical-invalidated evidence and the index explicitly requires v15.
Active personal HappyCodex remains `0.2.0+codex.20260714095129`. Exact v15 behavior,
final native/Fable review, paired holdouts, isolated release install, activation, and
Goal completion remain open. No other suggestion expands this milestone.

Goal-stop behavior refresh stopped on its first failed terminal input. Exact candidate
`ecd8da0`/package `503dc2a2…661` produced eight passing terminals, then
`pre-freeze-compaction` failed without timeout after 403.129 seconds. The primary and
fresh controls agreed on permissions, next action, gates, markers, Git, tests, agents,
and all other recovery fields; the primary alone labeled the completed milestone
`contract_frozen` while its own reason and next action said the plan remains a skeleton
and must create the contract-freeze revision. The fresh control correctly returned
`boundary_union_reproduced`. Failed metadata SHA-256 is `69f704d1…9ea`; the nine
terminals consumed 254,336 uncached input and 53,970 output tokens over 1,187.944
aggregate seconds. `receipt-mismatch` was interrupted before a terminal result; five
later cases never started. Raw events remain under
`/tmp/happycodex-v18-goal-stop-ecd8da0-20260716a`.

The bounded preservation repair restores the preexisting explicit sentence
“Freeze later in a separate revision” that was compressed only to fund the Goal-stop
word budget, and recover those words by compacting the adjacent Goal approval clause.
It changes no obligation, schema, case, oracle, or review protocol. Because it changes
the Skill/package, all nine v18 terminals become historical and a new 14-case candidate
run is required; public inputs remain reusable if their digests still match. Expected
live cost is another approximately 451,613 uncached-input-plus-output tokens and
1,619.657 aggregate model seconds, plus the still-pending release gates. That cost gate
was initially pending; the later `current-task/user/continue-goal-stop-closure` approval
now authorizes exactly this 14-case refresh and the already-frozen release gates. The
Goal is active while they run. No scope, schema, case, oracle, obligation, or reviewer-
protocol expansion is authorized.

The authorized one-shot final-package refresh then completed without timeout or
telemetry loss. Focused pre-freeze recovery passed 1/1; the remaining batch passed
12/13, for 13/14 strict overall, 373,393 uncached input tokens, 67,718 output tokens,
441,111 combined tokens, and 1,574.865 aggregate seconds. Summary SHA-256 values are
`2e80769d…b3d` and `d5cae1a3…29a`. `multi-repo-submodule` was the only strict failure:
it found the absent shared-schema candidate content and unsupported all-scope receipt,
anchored both to the required files, and kept product write, review, and completion
closed, but classified the latter as `frozen_acceptance` rather than the oracle's
`exhaustive_claim`. Metadata SHA-256 is `3651c5a3…293d`. This is reviewer taxonomy,
not missed behavior. At that checkpoint the user's stop line correctly prevented an
unapproved rerun or favorable test edit. The later
`current-task/user/oracle-defect-correction-approval` amendment authorizes accepting
either overlapping semantic blocker class while preserving both anchors, blocking
state, and all permission gates. RED first reproduced the false negative; GREEN proved
the old output passes unchanged. Only the changed case input then ran once and passed
in 106.980 seconds with 18,361 uncached input and 4,694 output tokens; metadata and
summary SHA-256 values are `f98863e8…9b42` and `9828abc1…1acc`.

The final independent reviews now make the stop line concrete without changing the
product. Native session `019f6c02-afed-7030-8eb1-6f679ba6ad8d` reviewed source
`3b9c11f…8b2..dc1de2c…e47` through synthetic
`e9b3e831…a46..da34a0bb…f6e` at configured/effective `gpt-5.6-sol`/max with
isolated read-only, network-disabled permissions. It covered 85/85 independent
obligations, 47/47 diff units, and 50/50 contract claims without truncation, external
read, write, or contamination; output SHA-256 is `f9090039…61ed`. The receipt is
complete but blocking. Exact Fable session `ed8d911c-ef64-4638-9731-c3176fc04e75`
reviewed the same synthetic range using actual `claude-fable-5`/max in safe plan mode,
received neither native output nor writer narrative, covered 47/47, and reported no
truncation, external read, write, or contamination. Events SHA-256 is
`3c159d82…3c54`; its sole completion blocker is the independently reproduced absent
current v15 receipt. Detailed findings remain only in the external outputs. The
product tree is unchanged, so both receipts remain valid for this candidate.

Current v15 SHA-256 is `2e76b934…a035`; the index points to it as current. It combines
the first exact terminals for the thirteen unchanged candidate inputs, the one changed
Oracle input, and both unchanged public inputs. Candidate is 14/14 with 367,459
uncached input, 69,650 output, 437,109 combined tokens, and 1,609.713 aggregate
seconds; public remains 0/2. The prior failed terminal is retained as the sole
invalidated attempt and points to successor metadata `f98863e8…9b42`; no unchanged
input was rerun. Skill/package/runner remain `f55d1943…a07`, `091cffb1…fe1`, and
`9c89fe06…e66`.

The Oracle case/test/result diff resolves the sole Fable blocker but changes the exact
range reviewed by both final receipts, so those receipts are now historical rather
than silently reused. Paired holdouts, final isolated install, activation, and Goal
completion remain unopened until one fresh native/Fable pair covers the v15-bearing
candidate. Active 0.2 remains the default. At that checkpoint the native Goal was
blocked by the earlier decision wait; the later user reply reactivated it.

Fresh Native session `019f6c41-a944-7cb3-bb1e-7ca38134bede` then reviewed
authoritative `3b9c11f…8b2..19b1214…0fb0` through synthetic
`86fe5f9…b4d8..43ae65b…0017` using configured/effective `gpt-5.6-sol`/max,
approval-never, isolated read-only permissions. Baseline/candidate manifest SHA-256
values are `ce1ae793…3518` and `333c92bf…56ed`; all 48 diff units bind to
`bf3e90a5…35c8`. Output/stderr SHA-256 values are `70247b13…4988` and
`aca91d8b…cd2a`. The complete receipt is blocking. Root reproduced only the
decision-relevant defects: the holdout runner labels any supplied `--public` package
as public 0.2 without pinning `77a0b2b8…8c89`; exact v15 Goal-divergence output omits
`/goal pause` when Agent-side pause is unavailable; and runtime/template wording
leaves an authorization gap between contract freeze and a later symmetric freeze.
The adjacent unqualified Goal `ask once` wording is part of the same bounded contract
clarification. No size-cap, concurrency, metadata, delegated-packet, reviewer-schema,
or other suggestion is admitted. Fable was not started after the Native blocker.

The holdout pin changes only an as-yet-unrun release gate. The bounded Skill/template
clarifications change the candidate package and invalidate all 14 current candidate
behavior inputs. The later fixture-aware runner implementation also changes both public
input digests; their additional rerun cost is recorded below. The authorized-work
proposal was: focused/static
checks, one 14-case candidate refresh (v15 observed 437,109 combined uncached tokens
and 1,609.713 aggregate model seconds), then one fresh Native/Fable pair before the
already-open holdouts/install/activation gates. Product Runtime/package remain
`f55d1943…a07` and `091cffb1…fe1` at the approval checkpoint. Authorization
`53929aac…015c` now permits only the bounded edits and minimum reruns above.

The bounded repair observed four focused failures across the three approved defects:
old Runtime/template wording failed the Goal/freeze structural assertions; the old
oracle API accepted the exact no-command result and lacked fixture-aware enforcement;
and the holdout runner entered pair execution before public-baseline validation. The
minimum implementation reaches 4/4 focused GREEN without a new schema: it checks the
existing `GOAL.md` fixture plus existing `open_gates`, symmetrically freezes claims at
the contract-freeze revision, and rejects a non-`77a0b2b8…8c89` public package before
receipt creation. Skill/template/runner/holdout-runner/package SHA-256 values are
`92b27bf4…1a2b`, `c45e48c0…fd1`, `06fac6ec…36a`, `1e2dfd2b…c6ba`, and
`4042ca86…54bf`; Runtime is 252 lines/2,175 words. Both official validators, Ruff
check/format, corpus/holdout dry-runs, and diff hygiene pass. Cumulative tests are
85/86: only the current-v15 exact-input assertion fails, proving v15 is stale. The
bounded candidate is committed at `89e69c9…4c79`; do not change that receipt assertion
before exact refresh evidence exists.

The implementation exposed a correction to the pre-edit cost estimate. A real
fixture-aware Goal handoff oracle without a new schema must change the shared corpus
runner, whose hash is bound to both arms. Therefore the two public receipts do not
match the repaired runner and cannot be reused honestly: the minimum live refresh is
14 candidate plus two public invocations, not the disclosed candidate-only 14. The
last exact public pair measured 73,650 combined uncached tokens and 311.102 aggregate
model seconds, increasing the observed behavior estimate from 437,109/1,609.713 to
510,759/1,920.815. No live rerun has started. This additional cost needs explicit user
approval; removing the mechanical handoff check to preserve the old estimate would
weaken the Goal-stop acceptance and is not permitted.

Frozen vertical milestones:

1. **Runtime contract:** replace 0.2 runtime with concise `SKILL.md` + one ExecPlan
   reference/template, remove all old reachability, add semantic structural oracles,
   and meet the first-draft size budget.
2. **Behavior and recovery:** add the tracked bidirectional corpus/runner and fixtures;
   close qualification, compaction, boundary, scope, secret, no-commit, multi-repo,
   and false-stall state transitions.
3. **Candidate proof:** run focused/full checks, build the synthetic review projection,
   close native and Fable findings, then run two blinded paired holdouts and the
   pre-release isolated install without changing active 0.2 or base version.
4. **Release:** update 0.3 metadata/change note, rerun exact final product-scope review
   after that material change, prove the exact release install/fresh task, append the
   ExecPlan-only closure commit, then update the active install with rollback ready.

Last known green:

- product baseline: `3b9c11fac1f97df75263e0bfc6421c575e04e8b2`
- workflow revision: `c99c4cf6d4519657c91c161bb814c93c93dd84d6`
- contract-freeze revision: `48a3d2c2e1224f728c27003bbb91a3f9632d6aad`
- runtime revision: `77957147a158da01fa56424e4f967ab7c490e75d`
- behavior revision: `7490b6a5229cf62c9a27c124d27bfd0be0e9444a`
- conformance-review revision: `029291e8bf327005ef3117a5402b740cfbf4254b`
- review-hardening revision: `60ed5bdb4d3ea3343bc5a608dc7dc60e9537c077`
- review-isolation revision: `b155644222b6fef00f06bc32ffed9c39afd1da18`
- review-completeness revision: `ffb502b17cf64e4f49c51c2e2b26ba734585d080`;
  tree `c26c3d39ef405b3d92b25306f5508abab5ca0997`
- reviewed plan checkpoint: `5fdf9658ed1e5b9ab316ea1102b79aa13de58cd3`;
  product tree excluding this ExecPlan is unchanged from `ffb502b…d080`
- current repair snapshot: Skill `208d1616…db75`, runner `21b0d076…8c7`, package
  `024a7dd5…85ad`, corpus `7f56754c…6058`, behavior-v8 `15ec89de…5e35`; 46/46
  contracts (normalized output SHA-256 `4a19eabf…e17c`), 14-case dry-run, 14/14
  behavior, both validators, Ruff check/format, JSON, zero-match credential scan,
  and diff checks green
- stable-candidate revision carrying this checkpoint: runtime 244 lines/2,154 words; Skill, reference,
  runner, package, and corpus SHA-256 values are `6e616a17…12d9`,
  `e23e401f…1e73`, `63508d09…29ff`, `3c641e65…a193`, and
  `b85bc606…4fe3`. The cumulative suite is 51/51 with normalized output
  `b7ba194e…0e35`; both official validator outputs remain `db349825…5bb0` and
  `24d83292…d48c`. Ruff check/format, 14-case dry-run, JSON, bytecode inventory,
  and diff hygiene pass. The v8 test preserves its internal receipt facts but requires
  current corpus, Skill, runner, package, and per-case digests to differ.
- exact-input v9 corpus `49eff69d…188` binds candidate source `ee323fd…ba1`, Skill
  `6e616a17…12d9`, runner `63508d09…29ff`, package `3c641e65…a193`, and all 14
  current case/oracles under `gpt-5.6-sol`/high/300 seconds. Selected candidate
  receipts pass 14/14: 350,778 uncached input, 57,405 output tokens, and 1,504.307
  seconds. Sanitized `behavior-v9` SHA-256 is `0bfa0324…72cd`; its executable test
  recomputes every input digest, aggregate, source tree, isolation field, and prior
  invalidation. Raw events remain under task-owned `/tmp/happycodex-v9-*` only.
- corrected inventory candidate metadata `0ca6a108…165` blocks solely because the
  supposedly independent inventory lacks stable numbered IDs/text. Exact public-0.2
  metadata `5478e931…f95` exits 0 and false-completes; public receipt-mismatch
  metadata `9734f7a5…f95` false-stalls only on the old fixed review quota. The fixture
  correction followed an observed RED and changed only phase-2 provenance fields;
  three pre-correction candidate/public attempts remain explicitly invalidated.
- post-receipt cumulative gates are 52/52, 14-case dry-run, both official validators,
  Ruff check/format, JSON, bytecode, credential scan, and diff hygiene. Runtime remains
  244 lines/2,154 words. Active discovery still reports enabled
  `0.2.0+codex.20260714095129`; its installed Skill remains `aa090bbd…ce55`.
- authorized reconciliation revision `9a2ff57` records the exact user reply and keeps
  O-01 through O-36 unchanged. Focused REDs reproduced the no-commit location gap,
  phrase-only acceptance, equal-but-false recovery, partial install binding, lossy
  sanitized receipts, and the missing receipt-successor ledger.
- current GREEN is 57/57, Ruff check/format, 14-case dry-run, JSON/bytecode, and diff
  hygiene. Runtime is 246 lines/2,174 words. The evaluator now uses Codex-supported
  nullable schema syntax, binds full installed package manifests, compares structured
  recovery truth with set-aware marker/agent semantics, and has no phrase-presence
  acceptance path. v1-v9 are hash-accounted in `evaluation/results/index.json`.
- exact smokes outside the repository prove the low-risk control and corrected
  no-commit case. Two real native recovery attempts proved compaction, same-task resume,
  and a distinct no-summary/no-handle control while exposing downstream-gate inference
  and agent/marker classification defects. Those were repaired after the last smoke;
  therefore the final exact recovery and full-corpus receipts remain deliberately open.
- affected behavior smoke batch `/tmp/happycodex-v9-smoke-20260715a` ran four cases
  with `gpt-5.6-sol`/high/300 seconds: review isolation, boundary cutover, and clean
  qualifying passed; recovery failed only because the first oracle demanded equality
  between two allowed `execplan_condition` labels. Summary SHA-256 is
  `5529de9b…41f3`; totals are 181,383 uncached input, 24,792 output tokens, and
  603.446 seconds. All raw events remain outside the repository.
- after the material gate-equivalence correction, exact recovery input
  `df109e3e…c827` passed in `/tmp/happycodex-v9-smoke-20260715b`: metadata/summary
  SHA-256 `3f6f75f9…9bdf9` and `5872d56c…48a7`, 71,045 uncached input, 17,119 output
  tokens, and 370.198 seconds. Native task `019f6663…46cf` resumed itself after real
  compaction; fresh task `019f6668…b0c9` received no summary or handle. Both agreed on
  qualification and all three permission gates; the allowed `usable` versus
  `needs_amendment` label difference is explicit and all oracle failures are empty.
- process-only Fable receipt: exact `claude-fable-5` at `max`, safe mode, no tools,
  no fallback, session `8ffbf653-0a4e-4ef0-a303-c255ac2f5900`; prompt/output/stderr
  SHA-256 `8aed37ec…69a5`, `ea88543b…f27c`, and empty `e3b0c442…b855`; terminal
  success in 206.422 seconds, $0.823965, 14,473 main-model output tokens. The CLI
  reported one auxiliary 27-output-token Haiku call. This audited process only and
  does not close the final candidate Fable gate. Its amendment recommendation was
  user-approved; its proposed deferral of O-33/O-35 was rejected because both trace
  to original clauses and are already frozen.
- semantic repair `20d1da9`/tree `8d750f9` passed 57/57 contracts, both validators,
  Ruff check/format, dry-run, JSON/bytecode, and diff hygiene at exactly 246 runtime
  lines/2,174 words. The first exact v10 corpus then passed 13/14 in 2,192.521 seconds
  with 431,999 uncached input and 70,251 output tokens. Summary SHA-256 is
  `cffb8365…9256`; failing recovery metadata SHA-256 is `6fbfe4fc…6ca`. Native
  compaction, same-task resume, distinct fresh control, Git/tree/test/agent recovery,
  and every permission gate passed; only the same-task result omitted
  `RECOVERY-GIT-6D91`. Fresh control found it. The receipt remains failed and cannot
  be selected. The transition subject is being corrected to explicitly label its ID
  as a durable recovery marker, matching the existing strict oracle without changing
  an obligation or weakening acceptance.
- corrected candidate source `a25eab7`/tree `c18f3a0` binds Skill `4ce0e730…0db5`,
  runner `fe6537fd…5365`, package `d5fa6577…20ef`, and corpus `7254b652…a28a`.
  The exact second full run passes 14/14 with 370,807 uncached input, 68,355 output,
  439,162 combined tokens, and 1,680.351 seconds; raw summary SHA-256 is
  `41c03d57…6822`. The selected recovery case passes in 394.980 seconds with one
  native compaction, same-task resume, a distinct fresh control, and exact structured
  agreement including all three marker IDs. `behavior-v10` SHA-256 is
  `3fbbd629…15b6`; its test recomputes every current input, aggregate, source tree,
  package install, public contrast, nonselected failure, and predecessor.
- Exact public 0.2 source `3b9c11f`/tree `4708ebc` uses Skill `aa090bbd…ce55` and
  package `77a0b2b8…8c89`. Raw summary `6de9a06b…1448` records 0/2: metadata
  `e9d0ca18…e48a` false-completes the missing-inventory case, and metadata
  `c7a8a696…bf00` requests user authorization only because the old review quota was
  consumed. Candidate metadata `a23a616c…c460` and `f64e4f92…a2ff` pass those exact
  inputs. The earlier 13/14 candidate summary `cffb8365…9256` and failed recovery
  metadata `6fbfe4fc…6ca` remain explicitly invalidated; no failed evidence was erased.
- Recovery correction `4380b09`/tree `4348403` passed the exact current candidate
  14/14 with runner `20e09076…fdd4`: the 13-case summary `f118527d…3465` records
  374,186 uncached input, 69,954 output, and 1,893.827 seconds; recovery metadata
  `059671a1…f914` records 35,442 uncached input, 6,015 output, and 177.285 seconds.
  Combined totals are 409,628 uncached input, 75,969 output, and 2,071.112 seconds,
  with no timeout or oracle failure. The later public-arm packaging correction changes
  the runner identity, so these passing receipts are retained only as
  historical-invalidated evidence.
- The exact public-0.2 attempt stopped before installation or model execution with
  `unexpected runtime surface`: the runner required 0.3 `execplan.md` while rejecting
  the baseline's `external-review.md` and `task-packets.md`. The RED test reproduced
  this asymmetry. The bounded GREEN selects one exact allowlist per arm, rejects both
  cross-arm surfaces and hidden input, binds arm plus selected entries into the input
  digest, and copies the real detached public package with identical manifest
  `77a0b2b8…8c89`. Current Skill/runner/package/corpus digests are
  `b230af43…ada8`, `28e8585d…abaa`, `decf933a…4ce8`, and `57a752ba…d8f4`; 66/66
  static tests and diff hygiene pass. Exact candidate model evidence remains open.
- Exact public comparison `/tmp/happycodex-v11-public-0.2-5f14234-20260716a`
  installed the frozen source/package and produced the required 0/2 contrast with no
  timeout. Summary `03682d48…61f2` records 50,396 uncached input, 13,282 output, and
  357.859 seconds. Inventory metadata `95280115…b06f` false-completes with
  `complete`/`usable`/completion permission; receipt metadata `c2edfca3…1b37` stops
  only for the old quota. These exact selected-case inputs remain current because the
  later correction changes only the multi-repository case, not runner, package, or
  either public fixture.
- The first parallel candidate attempt after `5f14234` was stopped immediately after
  multi-repository metadata `79853202…016` returned the sole mismatch
  `usable` versus `needs_amendment`; the other lane's authorized-rebaseline metadata
  `35356d00…8e6f` had passed, and all in-flight calls were interrupted. The raw
  multi-repository result independently anchored and blocked the missing shared-schema
  content, colliding repository namespace, and unsupported coverage receipt while
  keeping product write, review, and completion closed. The RED proved that the hidden
  oracle did not require either seeded boundary. The bounded correction accepts both
  valid plan-condition labels but now requires an `original_goal` blocker anchored at
  `backend/shared-schema.pointer` and an `exhaustive_claim` blocker anchored at
  `docs/execplans/contracts.md`; deleting either fails. Replaying the unchanged raw
  result now passes all strengthened assertions. The interrupted attempt is
  historical-invalidated; no favorable rerun was selected.
- The next exact parallel attempt produced one strengthened multi-repository pass,
  metadata `1ade6dc2…d334`, then was stopped when boundary metadata
  `c020aeab…e5ca` missed only the oracle's `tests.txt` class. The raw boundary result
  found every seeded surface, anchored the absent worker/restart/readiness/deployment/
  rollback/legacy-entry verification at `tests.txt`, and kept every permission closed,
  but classified that blocker as `frozen_acceptance` rather than
  `production_condition`. Both are frozen completion-blocking classes for this missing
  acceptance/production evidence. The bounded correction keeps the exact anchor and
  blocking requirement while accepting either class; all other six anchored blockers
  remain mandatory. Replaying the unchanged raw result returns no failures. The
  boundary receipt and interrupted lanes remain historical-invalidated; the selected
  multi-repository receipt stays exact because its case, runner, package, and model
  inputs did not change.
- The next exact attempt passed boundary, clean-policy, and compaction-recovery with
  metadata `38d01874…9e1f`, `a119c9b7…718f`, and `1785f240…2acb`, then stopped on
  pre-freeze metadata `bda52714…85af`. Native compaction and same-task resume were
  real, and the resumed result returned the exact structured durable state; only the
  distinct fresh control returned `recovery_state: null` after otherwise reading the
  same revisions, trees, 19/0 tests, terminal BC-4 receipt, three marker IDs, clean
  worktree, next action, and ordered gates. The global evaluator wording distinguished
  “native compaction recovery control” from a prompt that called itself only “fresh
  recovery control,” making null instruction-consistent but proof-invalid. The case-only
  correction now identifies the fresh invocation as the no-summary/no-handle phase of
  the runner's native proof and explicitly requires its reconstructed structured state.
  Runner, Skill, package, public cases, and all other candidate cases are unchanged;
  pre-freeze case digest is `a667415e…80d7`. The failed proof and interrupted calls
  remain historical-invalidated; the three completed case receipts remain exact.
- With that prompt correction, pre-freeze metadata `22ffde32…1016b8` passed native
  compaction, same-task recovery, and the distinct structured fresh control. Receipt,
  review-isolation, Goal-divergence, and mid-flight qualification metadata
  `fe1235e5…2f8a73`, `5ed639b4…e9068`, `e0660f38…9406b1`, and
  `fbb34f8e…1c15e` also pass and remain exact. The batch stopped when the local
  greeting admin case returned `qualifies: false` against a stale `true` oracle; its
  remaining completion, clean-tree, immutable-product, and admin-only revision facts
  all passed. Treating a low-risk local task as non-qualifying is the frozen O-30
  behavior, not a protocol failure. The case now requires `false`, a mechanical test
  prevents broadening it, and the unchanged raw result replays with zero oracle
  failures. Because the case/input digest changed to `5e0544dd…a6572` /
  `8c5938f6…9b6f1`, that failed metadata remains historical-invalidated and the case
  must receive one exact rerun. Current full static gates are 66/66 plus Ruff
  check/format, both official validators, JSON, and diff hygiene.
- Exact `c430def` lane B passed no-commit and subthreshold controls with metadata
  `578b69d3…1d74212` and `312b7bc3…83b5d2`; both inputs remain exact. Lane A exited
  normally but exposed two semantic fixture defects. The unchanged admin product facts
  passed while qualification flipped back to `true`, proving that its local request and
  complete HappyCodex history encoded conflicting qualification signals. The inventory
  case correctly found and blocked the unnumbered receipt, but returned review permission
  `true`: this matches the Skill's one allowed same-session receipt-only correction and
  does not permit contract reveal or completion. Metadata `199da8f4…d81fe8` and
  `c471a31b…1049e` remain failed/invalidated. Both fixtures now contain an unchanged
  public-API contract so they unambiguously qualify; admin requires `true`, inventory
  permits only the corrective review step, and both unchanged raw results replay with
  zero oracle failures. Current admin/inventory case digests are
  `d4bee8ee…1f423` and `7abf39f8…15d8d`; 66/66 static checks, Ruff, JSON, and diff
  hygiene pass. This case-only correction invalidates the selected public inventory
  receipt but neither public receipt-mismatch nor any other candidate input.
- Final candidate review controls at `f4630bd` pass 2/2 with metadata
  `e6831499…1cbb85` and `f7678d57…dc166e`. The refreshed frozen-public inventory
  metadata `7e981546…25bef` exits 0 without timeout yet false-completes; exact public
  receipt metadata `c2edfca3…1b37` remains the quota-only false stall. Sanitized
  `behavior-v11.json` SHA-256 is `c5bc109b…015d6`. Its current-input audit selects
  candidate 14/14 (392,322 uncached input, 80,605 output, 472,927 combined tokens,
  2,010.768 seconds) and public 0/2 (63,689 uncached input, 11,686 output, 75,375
  combined tokens, 342.992 seconds). All 28 nonselected terminal receipts differ from
  their final bound input and point to a selected successor; same-final-input
  nonselection is zero. Full static gates are now 67/67 with normalized output
  `74bd579d…ae01`; dry-run `e5d76b34…4a0a`, both validators, Ruff check/format,
  JSON, bytecode inventory, credential-pattern scan, and diff hygiene pass. Raw model
  events remain external; only hashes and structured sanitized facts are tracked.
- Fresh native task `019f6a19-ae41-7ed3-a41f-a6298ba656a3` reviewed source
  `3b9c11f…8b2..cbabaf7…8a8` through synthetic
  `6bb385b1…fff0..f86aa913…2f18` at configured/effective
  `gpt-5.6-sol`/`max`, read-only with network and writes disabled. Source/synthetic
  baseline and candidate manifest SHA-256 values are `ce1ae793…3518` and
  `beb6a7e7…6a92`; all 37 diff units are bound by newline-list digest
  `926c569b…436`. Phase 1 froze 107 contiguous obligations at canonical digest
  `33f110a3…2ff3`, then covered 107/107 obligations and 37/37 units. Contract-only
  projection digest `7769f95e…109c` mapped 107/107 inventory rows and 50/50 frozen
  contract rows. No truncation, external read, write, or contamination was reported.
  The terminal result blocked: phase 2 confirmed one missing executable evaluation
  mechanism, identified one already-open final-gate group, rejected the non-contractual
  expansions, and the user's current continuation approval resolved its pause question.
  This repair invalidates the product receipt; detailed findings remain only under
  `/tmp/happycodex-native-review-cbabaf7-20260716a`.
- Holdout-controller repair RED was the missing `evaluation.run_holdouts` import; a
  result; whole-diff boundary checks then added split-result majority and strict-JSON
  zero-denominator handling. GREEN is 10/10 focused and 77/77 cumulative.
  Runner/manifest/test SHA-256 values are `990c7fc0…d8d`, `d1cd5236…4da`, and
  `27bb4b6f…ddb3`; dry-run output is
  `3b5778ea…0b8`. The orchestration test proves both arms see the mapping commitment
  before any blind decision or reveal. Ruff check/format, JSON, diff hygiene, and the
  unchanged 250-line/2,173-word runtime budget pass. No live holdout result is claimed.
- Current native review root is
  `/tmp/happycodex-native-review-c672783-20260716a`; source/synthetic ranges are
  `3b9c11f…8b2..c672783…6f8e` and `e000578c…5ac3..331dec48…0454` with 43-unit
  digest `a9f729e4…1508`. Session `019f6a5c…31cbf6` used actual
  `gpt-5.6-sol`/max, isolated read-only/network-restricted permissions, froze 95
  obligations at `13b40ea2…048d`, covered 95/95 obligations and 43/43 units, then
  mapped 95/95 inventory rows and 50/50 contract rows. Correctness/mapping output
  SHA-256 values are `39342883…0c2` and `df2112dc…f57`; mapping events are
  `25db2610…e36`. No truncation, external read/write, or contamination occurred.
  Phase 2 rejected four overconstraints and left only actual Fable-output isolation
  unresolved; detailed findings remain external.
- Exact Fable session `bca3ac5a-7e12-430c-b770-e65d6e3f229b` reviewed the same
  43-unit frozen synthetic range using actual `claude-fable-5` at max, safe/plan mode,
  no fallback, no persistence, no Web, no subagent, and no native-review output or
  writer narrative. It covered 43/43 units, reported no blocker/truncation/external
  read/write/contamination, and produced three Root-reproduced nonblocking backlog
  items. Prompt/contract/output/events/stderr SHA-256 values are
  `7835ee03…bee3`, `1dda4b14…4bf0`, `c4b37693…e521`, `c41a5cab…5459`, and empty
  `e3b0c442…b855`; terminal success took 1,156.355 seconds and $13.013411 with
  76,829 output tokens. The post-review cumulative gate is 77/77 plus both official
  validators, corpus/holdout dry-runs, Ruff check/format, JSON, credential scan, and
  diff hygiene; source and synthetic worktrees remain clean.
- Live holdout root `/tmp/happycodex-holdouts-c672783-20260716a` used frozen
  candidate/public package manifests `decf933a…4ce8` and `77a0b2b8…8c89` with
  identical `gpt-5.6-sol`/high/300-second parameters. Run receipt and sanitized summary
  SHA-256 values are `6897a396…9f41` and `28d81618…b377`; stderr is empty. The
  adaptive history `better/equal/better` ran the third pair only after the first-two
  split. Candidate is 3/3 with zero oracle failures/timeouts; public is 1/3 and fails
  the authority-production and destructive-migration boundaries. Candidate/public
  totals are 77,407/73,807 uncached input, 13,776/13,312 output, 91,183/87,119
  combined tokens, and 300.433/280.181 seconds. Blocking ratios are 1.04665 combined
  tokens and 1.07228 wall; decision is pass with no user tradeoff required. Root
  reproduced all commitment, decision, reveal, metadata, sanitized receipt, adaptive,
  and cost hashes; raw files remain external. Active-plugin list SHA-256 stayed
  `026fdbd3…f39c`, and both source worktrees remained clean.
- Pre-release isolated root `/tmp/happycodex-preinstall-b7d0936-20260716a` contains
  no auth/key file. Supported CLI marketplace-add, list-available, plugin-add, and
  list-installed JSON SHA-256 values are `b7464e4a…26a0`, `5461cd3a…c370`,
  `f42bafbb…f5d`, and `f3763515…95e5`. It discovers then installs/enables
  `happycodex@happycodex` version `0.2.0+codex.20260714095129`; source/installed
  Skill `b230af43…ada8` and package `decf933a…4ce8` match exactly. The same package
  was invoked by three distinct fresh holdout tasks; candidate event/metadata hashes
  are `bbb7f6ea…16dd`/`5cc120fd…97c`, `ebaa00e4…cb2a`/`53115cf3…de6`, and
  `6e7b6c08…f304`/`a10443e6…6329`. Task `019f6aa5…9bb7` explicitly read the exact
  cache-resolved candidate Skill; its read-command digest is `4fc7f73d…5db3`. All
  three hidden oracles pass. Active personal list stays `026fdbd3…f39c`.
- Release behavior root `/tmp/happycodex-release-corpus-20260716-1137a` evaluated
  package `e70f8ff2…c5aa8` with `gpt-5.6-sol`/high/300 seconds. The first batch was
  13/14 only because the inventory fixture required immediate review permission even
  though the result correctly required an ExecPlan amendment before review and kept
  product write/completion closed. That ordering is not frozen; the semantic oracle
  now accepts both safe orderings without changing any blocker. The changed input ran
  once at `/tmp/happycodex-release-inventory-20260716-1204a` and passed; exact public
  0.2 rerun `/tmp/happycodex-release-public-inventory-20260716-1210a` still exits 0
  and false-completes. Sanitized v12 SHA-256 is `91d80d73…d471`: candidate 14/14,
  362,364 uncached input, 73,818 output, 436,182 combined tokens, and 1,638.445
  seconds; public is 0/2. All 44 historical terminal inputs point to exact successors,
  raw events remain external, and no unchanged input was rerun. Full release gates are
  78/78 plus both validators, dry-runs, Ruff, JSON, credential scan, and diff hygiene.
  Active plugin list remains `026fdbd3…f39c`.
- Post-metadata native session `019f6ada-8ccd-7b80-8453-92446e8d727d` reviewed
  source `3b9c11f…8b2..2d63abe…ddb4` through synthetic
  `68512f60…a37d..60705b6f…e393` using `gpt-5.6-sol`/max and isolated read-only,
  network-restricted permissions. Phase 1 froze 87 contiguous obligations at
  `7a6cfe8f…a735`; correctness represented 87/87 obligations and 45/45 diff units at
  digest `af770811…7ebf`. Output/events/stderr SHA-256 values are
  `3e941ce5…5ab`, `21c92051…f4d`, and `25c8e9e0…df1e`. It reported one confirmed
  baseline-preservation blocker; Root reproduced it and added the scoped RED/GREEN
  correction. The receipt also reported truncation, incomplete historical-receipt
  inspection, and one discarded worktree diagnostic, so completeness is false and
  phase 2 did not run. The product repair invalidates this blocking receipt; detailed
  findings remain external.
- First repaired-package v13 attempt split across
  `/tmp/happycodex-v13-d3c2fdf-20260716a/lane-{a,b}`. Thirteen exact inputs pass;
  lane summaries are `f460710f…4c03` and `e7a8ec1a…62e9`. The sole failed receipt is
  `compaction-recovery`: its initial invocation timed out at 300.111 seconds before
  telemetry or an oracle result after attempting an unavailable plugin-cache read and
  repeating bounded fixture/history inspection. The receipt remains failed. A
  case-only neutral instruction now states that the Skill is loaded and prohibits
  cache reads, unrelated history, and duplicate searches; package, timeout, oracle,
  seeded facts, and the other thirteen inputs are unchanged. Run that changed input
  exactly once before constructing v13. That input returned normally in 145.619
  seconds and reproduced every semantic blocker, but used finding identity
  `public-read-mode-regression` with exact anchor `test_read_mode`; the oracle alone
  required the model-selected identity to equal the test name. The second case-only
  correction moves that unchanged candidate-new requirement to the existing exact-
  anchor mechanism. No blocker, domain, state, path, budget, or package changes; if
  the next exact input fails, stop rather than iterate again.
- Final compaction metadata `42acfc23…85d6` passed the exact corrected input in
  123.276 seconds with 30,216 uncached input and 6,606 output tokens. Sanitized v13
  SHA-256 is `2c4bef87…55f4`: exact package `235c1a34…388`, candidate 14/14,
  448,646 uncached input, 68,864 output, 517,510 combined tokens, and 1,674.935
  seconds; exact unchanged public cases remain 0/2. All 60 nonselected terminal
  receipts point to their v13 successors. The cumulative gate is 79/79 plus both
  validators, Ruff check/format, JSON, credential scan, dry-runs, runtime budget,
  generated-artifact cleanup, and diff hygiene.
- semantic trailer: `HappyCodex-ExecPlan: docs/execplans/happycodex-0-3-cleanroom.md`

Pending gates:

- Replacement Goal objective `f5084511…946e` and authorization
  `current-task/user/rebuild-v19-goal` admit only the minimum structured
  Goal-divergence Runtime clarification and the existing
  14-candidate/Native/Fable/holdout/install/activation chain. The repaired Goal case
  now has structured classifications but failed the literal `/goal pause` handoff, so
  its explicit repeated-failure stop is reached. Do not change or retry anything until
  the user chooses a new design/scope. Goal `019f60c9…a004` is now `blocked` after the
  three-turn native audit; this is not pause or a waived gate. Active 0.2 remains
  unchanged, and no other suggestion enters 0.3 automatically.

Agent receipts:

- dispatch ID `/root/boundary_challenger`; status `complete`; immutable snapshot
  `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` at clean detached worktree
  `/home/caichenghang/projects/happycodex-boundary-0.2`; brief contained the verbatim
  operative user sources above plus the accepted clean-room compatibility boundary,
  asked for missing seams, preservation risks, falsifiers, and real-path/state-
  transition oracles; it disclosed no Root inventory or candidate; boundary was
  read-only, no edits, external models, or child delegation. Terminal return
  inspected all 9 tracked files/705 lines, reported a clean final status, enumerated
  search families/counts, and identified review blindness, receipt/HEAD circularity,
  legacy-reference fan-out, cached-install confusion, untracked-runtime blindness,
  phrase-only tests, challenger-neutrality loss, dirty-worktree false stalls, and
  release sequencing. Root reproduced each material path/search and merged it into
  O-11 through O-19, P-03, B-02, and R-09; no finding was accepted by vote.

Root reproduction highlights:

- baseline `SKILL.md:79-101` invokes review without a mechanical arbitrary-range
  selector and prompt-only neutrality cannot hide a tracked ExecPlan;
- `SKILL.md`, README, manifest, UI YAML, and tests contain the old packet/Fable/Goal
  fan-out, so deletion must be reachability-complete;
- README requires a fresh task after install, and `codex plugin ... --json` plus
  Skill/version hashes provide the install oracle;
- baseline `bundle_files()` intentionally ignores most untracked files and all 15
  tests are static/shape-heavy; current plan-only branch reproduces the expected
  14/15 RED;
- baseline has 9 regular files/705 lines, no executable/service surface, and the
  detached challenger worktree remained clean.

Review receipts: design-only Fable review is architecture evidence only. Native task
`019f6459-ac03-7731-a25a-f117c7814c98` reviewed synthetic
`5615892a…9410..d67efb8b…49b7` at configured `gpt-5.6-sol`/`max`; source and synthetic
candidate-manifest SHA-256 both `74e0f20b…343`, output `389b4225…523`, events
`5c92d406…256`, and stderr was empty. Terminal exit was 0, but the receipt blocked and
reported truncation; review-mode schema output and token telemetry were unavailable.
Detailed findings remain only in that native output.

Native task `019f6497-3c54-7c71-a2b1-57553d76b13c` reviewed synthetic
`c502c07e…70b3..2e5a08f2…fe27` for source candidate `029291e8…254b` at
`gpt-5.6-sol`/`max`. Source/synthetic baseline manifest SHA-256 is
`ce1ae793…3518`; candidate manifest is `6670ecc4…294b`; only this ExecPlan was
excluded and both original commits were unreachable. Phase-1 prompt/final/events
SHA-256 are `bc491ebd…3b31`, `142605c0…fffc`, and `905f489c…5de`; stderr is empty.
It reported 26/26 units, zero external reads or writes, and one broad-search display
limit that was rerun with bounded queries; phase-1 token telemetry was unavailable.
Phase-2 prompt/final/events SHA-256 are `7b31dc3b…42d0`, `faa3fdd7…95d2`, and
`55f14e83…39b8`; stderr is empty and usage is 15,150 uncached input plus 11,235
output tokens. Phase 2 refused the bidirectional mapping because phase 1 had not
actually emitted numbered obligation entries. The receipt is terminal but unusable;
Root independently reproduced all 11 reported implementation/test issues plus the
missing-inventory receipt failure. Detailed findings remain only in native output.

Native task `019f64ef-c37c-7df2-ad1c-d780b3a23ee1` reviewed source candidate
`60ed5bd…f13d` through isolated synthetic `d0de46ce…7914..89f24516…d084` at
`gpt-5.6-sol`/`max`, read-only. Source/synthetic baseline manifest SHA-256 is
`ce1ae793…3518`; candidate manifest is `8450cbf9…220a`; only this ExecPlan was
excluded and original commits were unreachable. The 28-unit phase-1 brief, output,
and stderr SHA-256 are `57837e7d…9ecd`, `59e6c05c…14c6`, and `fd18eec2…915d`.
It independently inspected the scope and reported five actionable findings, but did
not emit the mandatory numbered inventory or 28-unit coverage receipt. Same-session
receipt correction prompt/final/events/stderr SHA-256 are `2e0696fd…1410`,
`443656c4…520`, `707eee20…307f`, and `9649a256…0e46`; it explicitly could not
reconstruct the missing receipt. The contract was not revealed and phase 2 did not
run. The receipt is unusable. Root independently reproduced the actionable set and
materially repaired the candidate; details remain only in native output.

Native task `019f654b-b036-7652-a652-d9a2881b8351` reviewed source candidate
`b155644…a18` through isolated synthetic `4342d1b4…bee6..2ba9fde6…987d` at
`gpt-5.6-sol`/`max`, native read-only. Source/projected baseline manifest SHA-256 is
`ce1ae793…3518`; candidate manifest is `41969755…ffa1`; diff-unit inventory is
30/30 with digest `1b2ac449…bdee`, and original commits were unreachable. The
contract-hidden inventory froze 97 identical obligation entries at
`74f023a2…54be`; receipt final/events SHA-256 are `b4f265d7…89dd` and
`b9672c7e…c29d`. Hidden correctness covered 97/97 obligations and 30/30 units;
final/events SHA-256 are `39ed4391…b8a` and `fe1ad203…694`, with 10 blocking
dispositions. Contract projection SHA-256 is `ff350e89…0196`; phase 2 mapped all
97 inventory entries against 47 contract units plus the reproduced dispositions;
final/events SHA-256 are `10285703…937` and `c95d14b7…d99d`, with 14 blocking
contract dispositions. It reported no truncation, external read, or write. Root
reproduced the material set and changed the product/evaluator, so the complete but
blocking receipt is historical-invalidated. Detailed findings remain only in native output.

Native task `019f65fd-23b2-78b0-8cfd-4d2d7c4e9d86` reviewed source candidate
`5fdf965…d3` through isolated synthetic `cca587c8…82c..0aa76ab3…a8d` at
`gpt-5.6-sol`/`max`, native read-only with restricted network and delegation disabled.
Source/projected baseline manifest SHA-256 is `ce1ae793…3518`; source/projected
candidate manifest is `e92ec026…7a2d`; original source commits were unreachable and
the exact 33-unit inventory digest is `b34df8a1…28ba`. A selector-plus-prompt CLI
preflight exited 2 before task creation because that combination is unsupported; the
actual dedicated `codex exec review` ran in the two-commit repository with both exact
IDs in its neutral prompt, then all later phases used `codex exec resume` on the same task.

The baseline-only inventory emitted 106 contiguous obligations at canonical SHA-256
`1b883667…eceec2`; initial final/events SHA-256 are `0ca1d3ce…7d47` and
`f8eb847e…c10f`. The native review envelope omitted receipt metadata, so the permitted
same-session receipt-only turn reproduced the obligations byte-canonically, ran zero
commands, and produced final/events SHA-256 `6fb28c15…ffcc` and `2a52c076…8f24`.
Contract-hidden correctness covered 106/106 obligations and 33/33 units with no
truncation, external read, or write; final/events SHA-256 are `a0ad7a76…3520` and
`74fdf583…bda6`, with 11 blocking reports. Contract projection SHA-256 is
`d3e6adcc…db08`; phase 2 mapped all 106 inventory entries against 51 contract units
and all 11 prior reports, with no truncation or forbidden content; final/events
SHA-256 are `e667fba2…bf62` and `6d4051bb…b2b2`, with 19 blocking reports.

Root reproduced the union as 12 non-overlapping disposition clusters: eight
confirmed, three rejected with direct contract/source counterevidence, and one
deferred completion gate. O-30 through O-36 preserve the additive confirmed scope;
the Goal gate remains open against native Goal `019f60c9…a004`. Product repair will
invalidate this complete blocking receipt. Detailed reports and dispositions remain
only in the external native outputs.

The prior repair milestone owned README, Skill/reference, evaluator, six case JSON
files, three behavior summaries, both test files, and this ExecPlan; all were committed
in `ffb502b…d080`. This disposition amendment edits only the ExecPlan and will be
committed before the next product repair. Manifest, marketplace, UI/release metadata,
and active plugin remain unchanged.

Native task `019f66a5-941f-7601-b378-047fc19ad5a2` reviewed source candidate
`fa67df4…098` through isolated synthetic `98c3533d…60d..503f2948…746` at configured
`gpt-5.6-sol`/`max`, read-only with network, delegation, apps, Goal, hooks, memories,
and remote plugins disabled. Source/projected baseline manifest SHA-256 is
`ce1ae793…3518`; candidate manifest is `9a56f394…ea73f`; all 34 diff units are bound
by sorted-name digest `08de2648…57bc`, and both original source commits were
unreachable. Phase 1 froze 281 contiguous obligations at canonical SHA-256
`7a11cdee…eae8`; inventory final SHA-256 is `d1644025…9895`. Contract-hidden
correctness covered 281/281 obligations and 34/34 units without truncation; final and
events SHA-256 are `97c8ea09…756` and `0a922314…d91`. Contract projection and
canonical 50-claim serialization SHA-256 are `5b23eb15…cfc` and `035d8507…13c`;
phase 2 mapped all 281 obligations and 50 claims, preserving all eight phase-1 finding
identities, with final/events SHA-256 `847782af…cf7b` and `3eca959b…b7c8`. No external
read, write, contamination, omission, or truncation was reported. The complete receipt
blocked; Root reproduced the implementation defects and contract conflicts. The
verbatim authorization above resolves the contract choices, while product repair and
fresh review remain open. Detailed findings remain only in the external native output.

Exact `claude-fable-5` at `max` was unavailable for the old candidate review with a
terminal 403 and zero tokens. On 2026-07-16, a safe-mode/no-tools/no-persistence probe
session `f5cd599d-2fa5-4295-a975-229e0306d69d` returned `FABLE-ACCESS-OK` and reported
actual `claude-fable-5` model usage. This proves availability only; it does not close
O-07/O-28/P-03. Formal Fable review waits for the stable repaired candidate.

Fresh native receipt for source `3b9c11f…8b2..810aeaa…f58`: session
`019f6951-050a-7f71-ab3c-8eac11583d74`, configured/effective
`gpt-5.6-sol`/`max`, strongest approved isolated read-only profile, network/write
disabled. Synthetic range `ec9bdbb…cc1..f689adca…a749` bound all 36 diff units at
digest `766da089…2052`. Phase 1 froze 48 contiguous independent obligations at
canonical digest `0241d2ef…7b5`; normalized inventory receipt, hidden correctness,
contract-only projection, and phase-2 mapping digests are `655cfa00…8ad3`,
`e40371c9…63a9`, `3efc2aa3…d006`, and `47506de9…61a9`. Coverage was 48/48,
36/36, and 60/60 with no external read/write, contamination, omission, or
truncation. The terminal result blocked; Root reproduced every material item, the
approved amendment above authorizes the bounded repair, and the detailed findings
remain only in `/tmp/happycodex-native-review-810aeaa-20260716a`.

Repair RED/GREEN receipt: the pre-repair focused suite failed at least one mechanical
countertest for every reproduced material item. The repaired candidate passes 64/64
static tests, Ruff, 14-case dry-run, JSON, and diff hygiene.
Skill/runner/package digests are `b230af43…ada8`, `8d47389e…8960`, and
`decf933a…4ce8`; runtime is 250 lines/2,173 words. Exact v11 remains pending, so no
behavior or completion claim is made from this receipt.

First v11 attempt `/tmp/happycodex-v11-candidate-c7edbd4-20260716a` was deliberately
stopped after three terminal cases because two had already failed. Authorized
rebaseline passed; boundary and clean policy-path metadata digests are
`0ff33b6d…8fd` and `1860fc8f…61f`. Boundary found the seeded material surfaces but
used a new set of stable finding IDs, proving the old exact-ID oracle brittle; the
clean control correctly selected the RED step but treated that test edit as
non-product write. The aborted batch is historical-invalidated. The correction binds
semantic coverage to exact repository anchors plus blocker class and defines source
and RED-test edits as writes when no user/control gate intervenes. Corrected
runner/corpus digests are `34f65abb…3887` and `af922131…574c`; full static gates pass.

Affected smoke `/tmp/happycodex-v11-smoke-d1d6d45-20260716a` passed boundary and
clean-policy controls 2/2: 56,244 uncached input, 9,410 output, and 299.049 seconds;
summary inputs are unchanged from `d1d6d45`. Remainder batch
`/tmp/happycodex-v11-remainder-d1d6d45-20260716a` was stopped after two terminal
cases: authorized-rebaseline passed; recovery metadata `daabadf6…6870` found and
blocked every seeded fact but used `/`-qualified failure IDs, one multi-anchor dirty
finding, and `frozen_acceptance` for the unauthorized rollback deletion. Those are
valid representations under the frozen blocker definition. Replaying that unchanged
raw result through the corrected oracle returns no failures. The partial batch remains
historical-invalidated because its input digest changed. Current runner/corpus digests
are `20e09076…fdd4` and `b12f5e45…a3c9`; 64/64 static gates remain green.

`/tmp/happycodex-public-0.2-v6-20260715a` is the task-owned clean detached
public comparison worktree; other worktrees remain untouched. Only `/root` is live.

Runtime slice evidence at `77957147a158da01fa56424e4f967ab7c490e75d`:

- RED after replacing only the static oracle: 4 pass, 7 fail, 5 error against the
  0.2 runtime; failures covered missing template, old references, Goal prompting,
  incomplete boundary/recovery/review semantics, and runtime shape.
- GREEN: 16/16 unit contracts; combined-output SHA-256
  `925317d7eae7dda2a18659f865d0db0d48b0561a6d1bbad0d572c96395d3df4e`.
- Skill validator passed, output SHA-256 `db349825…5bb0`; plugin validator passed,
  output SHA-256 `24d83292…d48c`; `git diff --check` passed.
- Runtime budget is 258 lines/1,957 words versus the rejected 524/4,351; old runtime
  references are absent except negative test assertions; secret-pattern scan is clean.
- Product/support diff from contract-freeze SHA-256 `b643e9a5…fd6f`; public base
  version and active 0.2 install remain unchanged.

Behavior/recovery slice evidence at `7490b6a5229cf62c9a27c124d27bfd0be0e9444a`:

- The tracked runner creates fresh Git fixtures, packages no corpus/oracle files,
  installs into a fresh `CODEX_HOME`, invokes a fresh read-only task, checks the
  installed Skill hash, enforces a structured schema, preserves raw events outside
  the repository, and records uncached input/output tokens and wall time.
- Mechanical contracts are 27/27. The behavior-commit Skill SHA-256 is
  `1e636bd6b2e4c31b3e8130e9ce73147995aeacbd6f22899a5a9925bebdf5def4`.
  The twelve selected current-hash results deterministically recheck 12/12: 194,325
  uncached input tokens, 30,125 output tokens, and 885.418 aggregate seconds.
- Final pre-commit unit output SHA-256 is `9f82fb5d…63d`; dry-run output is
  `44967095…a6bb`. Skill validation is `db349825…5bb0`, plugin validation is
  `24d83292…d48c`, JSON/bytecode checks and `git diff --check` pass, and the common
  credential-pattern scan returns no match.
- Two raw cases were rechecked without another model call after semantic hidden-oracle
  corrections: `authorizes` now satisfies the authorization stem, and any reproduced
  receipt contamination may block the receipt case even if another missing receipt is
  not repeated in prose. The raw flags and every metadata/event digest are retained in
  `evaluation/results/behavior-v1.json`; no favorable rerun was selected.
- Receipt RED: pre-fix candidate Skill `4dbe4c…d664` returned `complete` solely from a
  writer summary that BC-7 completed. GREEN required a reachable dispatch/terminal
  record. On the same frozen fixture, public 0.2 Skill `aa090b…ce55` still returned
  `complete`/`protocol_may_complete=true`, while the behavior-commit candidate closes it.
- Bidirectional controls pass: a local one-word documentation task remains on native
  flow; a fully evidenced admin-only closure completes; Goal divergence stops for the
  user; secret identity, compaction/lost-agent/dirty-state, boundary cutover,
  multi-repository/submodule, and review-isolation cases fail closed as designed.

Native-review conformance repair evidence:

- RED against `7490b6a`: 7 contract failures and 1 missing-runner-helper error.
- The repair restores explicit Goal use, three claim states, the early skeleton commit,
  mechanically staged contract mapping, finding-free plan provenance, final-only
  Retrospective, Fable defaults, deterministic fixtures, raw-output isolation, and an
  actual committed-skeleton pre-freeze fixture.
- GREEN after model execution: 33/33 unit contracts, 13-case dry-run, Ruff check and
  format, both validators, JSON/bytecode checks, and `git diff --check`; runtime is
  262 lines/2,046 words.
- Current Skill SHA-256 is
  `a949463e6536fe075757b5c8d81227c95245b3814fb82d8373b55d30965d18b6`.
- The current Skill passes 13/13 hidden-oracle cases: 270,686 uncached input tokens,
  39,282 output tokens, and 1,082.858 aggregate seconds. Corpus-input SHA-256 is
  `ad8a14ce…1b1c`; the sanitized receipt set is tracked in
  `evaluation/results/behavior-v2.json`.
- The first current-hash `review-admin-cycle` run correctly exposed a stale positive
  fixture and stopped the batch. Its failed metadata/events digests remain in the
  sanitized summary; Root repaired the fixture and mechanical oracle before rerunning
  that materially changed case. No unchanged result was rerun or selected away.
- A later writer audit found two otherwise-positive fixtures still used the legacy
  claim state `closed`. Their new `verified` forms passed 2/2; both superseded passing
  receipts remain identified in the summary.

Native-review repair GREEN evidence at `60ed5bd` (historical-invalidated):

- RED added every reproduced protocol defect and yielded 22 failures plus one missing
  helper error. GREEN is now 41/41; normalized unit output SHA-256 is
  `bed8f73c…8e00`, and 14-case dry-run output is `cf690a37…7a02`.
- Runtime is 262 lines/2,098 words. Skill and plugin validators pass; Ruff, JSON and
  Python syntax, `git diff --check`, and the credential-pattern scan are clean.
- `behavior-v3.json` SHA-256 is `38388251…325e`. Its 14 selected receipts bind exact
  case/oracle, Skill `b43e8494…d4f6`, runner `5d42a6cd…f13d`, package
  `3d333048…ecb`, model/effort, and 300-second timeout. Totals are 385,362 uncached
  input, 44,831 output tokens, and 1,436.299 seconds.
- The single-defect `review-inventory-gate` contrast uses the same fixture, hidden
  oracle, runner, model, effort, and timeout. Candidate metadata `32d3e63c…92baf`
  passes by blocking completion; public-0.2 metadata `edd299ba…61e8` has exit 0 and no
  timeout but false-completes. Public-0.2 metadata `5d037be6…68da` passes the current
  `receipt-mismatch` control, so the contrast is not a blanket false-stall artifact.
- Native compaction task `019f64c0-4c46-7892-b376-18284cd6d0d2` persisted two
  `compacted` events plus two corroborating markers before `codex exec resume`; the
  resumed task ID is identical. Pre-resume rollout SHA-256 is `deb1fb2f…499a`.
- Nonselected receipts remain identified: each passed receipt was invalidated by a
  later input change, and each failed receipt preceded a material runner or fixture
  correction. No unchanged input was rerun or selected away.
- The active plugin remains enabled at `0.2.0+codex.20260714095129`; candidate
  evaluation used isolated homes and did not alter release metadata.

Native-review isolation repair evidence:

- Initial RED was three failures plus three errors: challenger chronology was
  retroactive, evaluator oracle sources were readable, native resume lacked an
  inherited read-only setting, no-commit freeze/closure revisions were inconsistent,
  and alternate-plugin output paths were writable. Additional RED proved parent task
  environment and source CODEX_HOME leakage, then missing native helper binaries.
  Final writer diff review used the native sandbox to prove that the copied evaluator
  `auth.json` remained command-readable under legacy `read-only`; this reopened all v4
  behavior evidence before commit.
- Challenger returns are now content-addressed at their terminal revision before the
  candidate; review projections reuse that receipt. Initial and resumed evaluator
  turns explicitly select the same custom permission profile. Commit-forbidden tasks
  retain skeleton, freeze, every green slice, and closure as reachable revisions.
  Output resolution rejects both the runner repository and the evaluated plugin.
- The native profile grants commands only `:minimal`, the current read-only fixture,
  and a case-local read-only allowlist (`apply_patch`, `codex`,
  `codex-linux-sandbox`, `rg`). Default-denied paths include the isolated credential,
  source repository/controls, source CODEX_HOME, sibling `/tmp`, and real HOME; the
  command environment inherits nothing and network is disabled. Native sandbox probes
  prove credential and oracle denial, fixture visibility, helper availability, and
  write denial; a real isolated `codex exec` invocation passes.
- GREEN is 43/43; normalized unit output SHA-256 is `359a4ff4…90b9`. Dry-run output
  SHA-256 is `cf690a37…7a02`; Skill/plugin validator output SHA-256 values are
  `db349825…5bb0` and `24d83292…d48c`. Ruff, JSON, current-diff whitespace, and the
  credential-pattern scan pass.
- Runtime is 262 lines/2,161 words. Skill, runner, package, corpus-input, and
  behavior-v5 SHA-256 values are `8862c345…4dc0`, `a1dea44e…c7ee`,
  `8ea8657a…a7f`, `ef473105…94e`, and `e5988065…1336`.
- All 14 candidate cases pass: 285,301 uncached input tokens, 45,111 output tokens,
  and 1,129.362 aggregate seconds. The two safe v5 failures are retained with their
  material case/oracle corrections; historical v4 retains all 18 earlier nonselected
  receipts. No unchanged input was rerun or selected away.
- Public 0.2 metadata `5b442376…bbe` exits normally but false-completes the missing
  inventory case. Its `receipt-mismatch` metadata `4ee796a6…fd15` safely blocks yet
  demands user authorization solely because a fixed review cycle was consumed; the
  no-quota candidate passes both exact current inputs.
- Forced-compaction task `019f653b…4a1a` records two pre-resume native compactions and
  two markers, three of each after resume, identical thread identity, and pre-resume
  rollout SHA-256 `74ff8fa5…a1be`.
- `codex plugin list --json` still reports enabled public 0.2
  `0.2.0+codex.20260714095129`; no candidate install or release field changed.

Two-phase native-review repair evidence:

- RED after adding the reproduced obligations was six static contract failures plus
  one evaluator configuration error. Later executable REDs exposed a term matcher
  that ignored structured blocker/finding fields and punctuation, a one-line review
  fixture that obscured bidirectional mapping, and an inventory case that exhausted
  300 seconds by re-auditing unrelated product history. Every superseded receipt and
  its material invalidation reason remains in `behavior-v6`; no unchanged input was
  rerun or selected away.
- GREEN is 46/46 with normalized output SHA-256 `d40406be…2ab3`; Skill/plugin
  validators, Ruff, JSON, dry-run, diff whitespace, and the zero-match credential
  scan pass. Runtime is exactly 262 lines/2,175 words.
- Skill, runner, package, corpus-input, and `behavior-v6` SHA-256 values are
  `9949793f…b959`, `fc8ca0f3…6eb3`, `676604bd…24f`, `ea52df8d…dd9d`, and
  `d6a17f3c…33b`.
- All 14 exact candidate inputs pass: 326,147 uncached input tokens, 58,926 output
  tokens, and 1,691.583 aggregate seconds. The 11 nonselected receipts include four
  passing, six ordinary failing, and one timeout result; each has an immutable digest
  and explicit material invalidation.
- On the exact final runner/cases, public 0.2 metadata `81ed5bf6…16fd` exits 0 and
  false-completes the missing-inventory case. Public metadata `d1bb8ec1…0a2d`
  identifies the real contract mismatch but stops for user authorization solely
  because its fixed review sequence was consumed. Candidate metadata
  `777696c6…14e2` and `91a3e887…2389` pass both cases.
- Forced-compaction task `019f65a4…73c6` records a pre-resume native compaction,
  same task identity, and a post-compaction parent commit. Resume independently found
  `RECOVERY-GIT-6D91`, `RECOVERY-PLAN-47B2`, and `RECOVERY-TEST-19C4`; summary or
  in-flight handle knowledge cannot supply those previously nonexistent values.
- Raw events remain only in `/tmp/happycodex-v6-*`; the tracked summary contains
  sanitized identities, telemetry, digests, and invalidation reasons. The detached
  public comparison is clean at `3b9c11f`/tree `4708ebc…13a` with Skill
  `aa090bbd…ce55` and package `77a0b2b8…a8c89`.

Writer whole-diff and final behavior evidence:

- Root's clause-by-clause audit found three material instruction omissions before
  commit: strong claims no longer said fresh baseline-only or named architecture-
  shaping examples; milestone cadence did not explicitly reject a full reviewer after
  every revision; and review scope did not name task-owned staged, unstaged, and
  untracked paths. RED contract assertions reproduced all three. The repaired runtime
  remains exactly 262 lines/2,175 words and makes no release-metadata change.
- Exact-input `behavior-v7` passed 14/14 with Skill `208d1616…db75`, runner
  `fc8ca0f3…6eb3`, and package `024a7dd5…85ad`, but an added formatter gate proved
  that the current evaluator and test diff no longer matched the previously green
  formatting baseline. Mechanical Ruff formatting changed the runner identity, so all
  v7 receipts were invalidated rather than reused.
- With final runner `21b0d076…8c7`, the first v8 corpus pass produced 11 ordinary
  passes and three oracle mismatches. Root retained all three. The delegation term was
  normalized to the existing `delegat` stem family; `full-scope` was added as a whole-repository
  completeness synonym; and the multi-defect receipt case was changed to inspect every
  agent/reviewer receipt instead of stopping at the first blocker. Its hidden decision
  oracle was then tightened to reject `stop_for_user`, because a consumed review count
  is not user-authorization work under the no-quota amendment. Every rerun followed one
  of those recorded input changes; no unchanged input was rerun.
- Final `behavior-v8` SHA-256 is `15ec89de…5e35`. All 14 candidate receipts recompute
  against corpus `7f56754c…6058`, Skill `208d1616…db75`, runner `21b0d076…8c7`,
  package `024a7dd5…85ad`, `gpt-5.6-sol`/high, and 300 seconds: 326,921 uncached
  input tokens, 60,554 output tokens, and 1,881.200 seconds. Its five nonselected
  candidate/public receipts include three failures and two passes, each with immutable
  digests and a material invalidation reason.
- On the same final runner/cases, public-0.2 inventory metadata `42429cfc…7d58`
  exits 0 and false-completes, while candidate metadata `8168fa85…14ff` blocks it.
  Public receipt metadata `48faf4bd…aa2f` exits 0 but requests user authorization only
  because the initial-plus-rereview count was consumed; candidate `ab8683d5…f865`
  returns `continue` and identifies both the challenger and review-receipt gates.
- Forced-compaction task `019f65e0…2ed6` records a pre-resume native compaction, the
  same resume identity, and a post-compaction parent commit. Resume independently found
  `RECOVERY-GIT-6D91`, `RECOVERY-PLAN-47B2`, and `RECOVERY-TEST-19C4`.
  Raw events remain only under `/tmp/happycodex-v7-*` and `/tmp/happycodex-v8-*`.

Unknown or missing fields remain open and cannot be interpreted optimistically.

Current bounded closure checkpoint (2026-07-17): immutable repair baseline is clean
`c400ba99d13168c4788f56b379c9d6c8e4a85cb4`/tree
`70b07974bc2621eac7a95cc8f517106e57cf593c`; Root is the only writer. The user
cleared the blocked predecessor Goal and approved the O-03/R-02 amendment above.
Replacement native Goal `019f60c9-ac13-7743-a910-73ada401a004` is active with one
product revision and one final certification cycle authorized. Next RED strengthens
the existing budget and Goal-stop structural assertions; implementation may only
make the existing handoff explicitly tell the user to run `/goal pause`. Do not alter
an obligation, behavior case/oracle/matcher, schema, reviewer protocol, runtime
surface, or public 0.2. All v19 candidate terminals and Skill/package/static digests
are stale after the product edit; public receipts require exact digest proof. If the
same Goal-stop behavior fails again, or another material blocker appears, stop for
the user instead of compressing wording or changing certification semantics.

Focused repair evidence: the strengthened existing structural assertion first failed
because Runtime never explicitly told the user to run the native command. The same
test and both existing Goal-handoff matcher tests are now GREEN. Cumulative offline
gates pass: 94/94 unit tests, both official validators, corpus and holdout dry-runs,
Ruff check/format, JSON parsing, credential-pattern scan, generated-artifact cleanup,
and diff hygiene. Runtime is 244 lines/2,182 words. Skill, package, runner, contract-
test, and maintainer-policy SHA-256 values are `be55c3c4…d8da`,
`67df20a1…bb29`, `e835c6c9…d105`, `b7b2caef…ec71`, and `021a3b1b…f77`.
The behavior case, oracle, matcher, schema, and runner are unchanged. Next gate is the
single authorized exact 14-case candidate run from a clean committed snapshot.

Exact final behavior launch record, persisted before model calls: product candidate
commit/tree are `14904dbc54f7eb0f9602493cb3164be9f31645c8` and
`dd73d27aea934e11639dd44e854e5a2cbd96b7ed`; clean detached worktree is
`/tmp/happycodex-v20-candidate-14904db-worktree`. Skill/package/runner/corpus SHA-256
values are `be55c3c4…d8da`, `67df20a1…bb29`, `e835c6c9…d105`, and
`533d45e2…85da`. Run all fourteen candidate cases exactly once at
`gpt-5.6-sol`/high/300 seconds with `PYTHONDONTWRITEBYTECODE=1 python3
evaluation/run_corpus.py --plugin . --model gpt-5.6-sol --effort high --timeout
300 --arm candidate --output
/tmp/happycodex-v20-candidate-14904db-20260717a`. The output path was absent before
launch. Active personal HappyCodex remains `0.2.0+codex.20260714095129`. Stop on the
first semantic failure; do not alter wording, oracle, matcher, schema, or runner, and
do not open review/holdout/install gates unless all fourteen terminals pass.

The v20 run stopped at its first semantic failure. `authorized-rebaseline`,
`boundary-cutover`, and `clean-qualifying-control` pass. `compaction-recovery` exits
zero without timeout and makes the safe decision—`stop_for_user` with product write,
review, and completion closed—but omits a finding classification anchored to the
staged `staged-review.txt` path even though its evidence names that path. The exact
oracle failure is `missing anchored classification: staged-review.txt other
['baseline_unchanged', 'candidate_new', 'unknown']`; metadata SHA-256 is
`f90808a0…c5d`. The prior v19 exact case passed by classifying all three dirty paths
under `dirty-path-ownership`; its input is not reusable because the Skill/package
changed. This is therefore a current candidate failure, not a baseline success or an
allowed retry.

Four terminal receipts consumed 139,118 uncached input and 18,839 output tokens over
730.039 aggregate model seconds. The just-started `goal-divergence` child was
interrupted before a terminal receipt; nine later cases never started. Raw receipts
remain under `/tmp/happycodex-v20-candidate-14904db-20260717a`; candidate and main
worktrees are clean. No review, Fable, holdout, install, metadata, or activation gate
was opened. The bounded Goal's new-material-blocker stop condition is reached. Do not
rerun the unchanged candidate, weaken certification, or make another product wording
change without a new user decision. Agent-side Goal pause is unavailable: tell the
user to run `/goal pause` before this persistent wait; ending the turn is not Goal
pause.

Named-waiver authorization checkpoint: source
`current-task/user/approve-v20-named-waiver` is verbatim `好的继续` plus final LF,
SHA-256 `3c0077c9863e135c710592c17be11511b5b335651d358b3c71e76ec015de4189`.
It approves the immediately preceding exact proposal: keep v20
`compaction-recovery` metadata `f90808a0…c5d` as a failed receipt, waive only the
missing structured `staged-review.txt` classification because the result already
names that path in evidence, safely returns `stop_for_user`, and closes product write,
review, and completion; do not modify Skill, oracle, matcher, schema, hook,
controller, Task State JSON, or reviewer protocol. The three prior passing v20
terminals remain exact. Run each of the ten cases without a terminal receipt exactly
once, then execute the already-open final gates. Any unwaived safety/permission
failure still blocks release. Ordinary findings block completion but do not pause
Goal while safe in-scope diagnosis or work remains; pause only for a user contract or
waiver decision, external dependency, destructive action, or approved-chain cost
increase. Never rerun an unchanged input to select a favorable result.

Corrected native Goal is active on thread `019f60c9-ac13-7743-a910-73ada401a004`;
its exact objective plus final LF hashes to `05d729e3…17d8`. It freezes product
candidate `14904dbc54f7eb0f9602493cb3164be9f31645c8`, incorporates only the named
waiver above, distinguishes a completion blocker from a persistent pause condition,
and requires all remaining release gates plus active-0.2 rollback readiness.

Remaining-behavior launch record, persisted before model calls: detached candidate
worktree `/tmp/happycodex-v20-candidate-14904db-worktree` is clean at `14904db`;
Skill/package/runner/corpus remain `be55c3c4…d8da`, `67df20a1…bb29`,
`e835c6c9…d105`, and `533d45e2…85da`. Output path
`/tmp/happycodex-v20-remaining-14904db-20260717a` was absent. Run exactly once, in
corpus order, `goal-divergence`, `midflight-escalation`, `multi-repo-submodule`,
`no-commit-secret`, `pre-freeze-compaction`, `receipt-mismatch`,
`review-admin-cycle`, `review-inventory-gate`, `review-isolation`, and
`subthreshold-control` at `gpt-5.6-sol`/high/300 seconds. Active personal 0.2 remains
enabled. Preserve every terminal; an unwaived failure blocks downstream release but
does not by itself pause Goal while safe diagnosis remains.

Remaining-behavior terminal checkpoint: summary SHA-256 is
`c2be1f95d44c55aca1dc5b67c26184893efd1471fb6cc401ec96982b56de4fe2`.
Seven of ten exact inputs pass: `goal-divergence`, `multi-repo-submodule`,
`no-commit-secret`, `review-admin-cycle`, `review-inventory-gate`,
`review-isolation`, and `subthreshold-control`. `midflight-escalation` metadata
`dfde7bb4…e692` detects the public behavior regression but incorrectly keeps the task
subthreshold, reports no ExecPlan required, and permits another product write.
`pre-freeze-compaction` metadata `1af55abe…f785` times out during native resume and
therefore supplies neither the same-thread structured recovery result nor complete
token telemetry. `receipt-mismatch` metadata `e29f17a4…b9af` finds and blocks both
mismatched receipts, but classifies them as `exhaustive_claim` rather than the
oracle-accepted frozen-acceptance or safety/data-integrity classes. These three
failures are not covered by the sole named waiver and close every downstream review,
Fable, holdout, install, metadata, and activation gate.

The ten-case run reports 219,872 uncached input tokens, 47,238 output tokens, and
1,858.422 aggregate seconds, with telemetry explicitly incomplete because of the
compaction timeout. Raw receipts remain at the launch path; main and detached
candidate worktrees were unmodified by evaluation. Goal remains active while Root
performs bounded read-only diagnosis. Do not rerun an unchanged case or reinterpret
historical passes as a current terminal. Any repair would change the frozen Skill or
evaluation surface and therefore requires the user contract decision reserved by the
Goal before another product revision or certification run.

Bounded diagnosis separates product behavior from certification mechanics. The
`midflight-escalation` terminal is a real unsafe protocol result: although it detects
the public API/behavior regression, it ignores the existing upgrade rule and permits
another product edit without first creating the qualifying ExecPlan. The relevant
qualification text is unchanged from recent exact passing candidates, including v17
on the same runner, so the evidence is consistent with stochastic instruction
noncompliance rather than a newly introduced contradictory rule; nevertheless the
current terminal cannot be waived as harmless. The smallest product repair is to make
mid-flight public-contract/behavior escalation an explicit before-next-write guard.

The other two failures do not establish a product safety escape. `receipt-mismatch`
finds both bad receipts, keeps review/completion closed, and emits blockers anchored
to both receipt IDs; only its choice of `exhaustive_claim` conflicts with an oracle
that accepts `frozen_acceptance` or `safety_data_integrity`. Adding runtime taxonomy
solely to select that label would be certification overfitting. In
`pre-freeze-compaction`, the same-thread resume reads the post-compaction Git,
ExecPlan, tests, and markers but does not emit its final object before the 300-second
process timeout after three native compactions. The independent no-summary control
does emit the complete correct structured state. v17 passed this exact case on the
same runner and v19 also passed; current evidence supports an execution-time failure,
not permission leakage. Neither failure may be silently relabeled or retried.

No safe authorized write remains. Continuing now requires a new user decision about
the frozen product and certification contract: at minimum, authorize the one
mid-flight guard repair and decide whether the two certification-only failures receive
named waivers or changed evaluation inputs. That decision diverges from the active
Goal's no-Skill/no-evaluator objective and must be reconciled before implementation.
Do not launch another corpus or downstream gate while this checkpoint is pending.

v21 authorization checkpoint (2026-07-18): source
`current-task/user/approve-v21-bounded-repair` is verbatim `批准` plus final LF,
SHA-256 `b6f4b57ade409674cb0a60c9d9a67eb714f0c6bc2bfc9878f15547e39b444533`.
It approves the previously presented five-line target, SHA-256
`aaba17d29f2abe5d9d339c0a47e89b132f6a96aa16067a80aecf8db8cf966806`:

> 1. 只修一处 mid-flight guard。
> 2. 对 receipt 分类差异做严格限定的具名豁免。
> 3. 新候选下重新运行 14 项：13 项保持 300 秒，compaction 单项 600 秒。
> 4. 通过后继续 Native review、Fable 5、holdout、安装和激活。
> 5. 不增加 schema、controller、hook、Task State JSON 或 reviewer 协议。

Interpretation is narrow. Product work may add only an explicit guard that a task
which becomes public-contract or behavior-changing after edits must establish its
qualifying ExecPlan before the next product write. The receipt waiver accepts only
the classification-label variance already observed when both
`review-authority-7` and `review-authority-full-task-7` remain anchored blocking
findings and product write, review, and completion remain closed; it never waives a
missing receipt, unanchored finding, nonblocking result, or open completion gate.
`pre-freeze-compaction` is not waived: its next exact input gets 600 seconds while
the other thirteen remain at 300 seconds. A second failure remains blocking and may
not be retried unchanged.

The prior blocked Goal has been cleared by native state; `get_goal` now returns no
Goal. Commit this amendment, create one replacement Goal carrying this exact bounded
scope and all unchanged final release gates, then observe the focused RED before the
single product edit. The v20 product candidate `14904db` remains the immutable repair
baseline; all raw v20 receipts and dispositions remain retained. Do not absorb any
other optimization or certification change.

Replacement native Goal is active on thread
`019f60c9-ac13-7743-a910-73ada401a004`; its exact objective plus final LF hashes to
`7326770aaa70fd3cfc9b1e3af57027c27db10edd93ccc207fcab090e411760a7`.
It carries the v21 amendment, one fresh candidate corpus, all existing downstream
release gates, and the corrected pause condition. The next permitted action is the
focused mid-flight RED; no other product or evaluator edit is authorized.

v21 focused slice evidence: the existing
`test_qualification_has_safe_upgrade_and_low_risk_exit` first failed because Runtime
lacked both `public-contract or behavior-changing after edits` and `establish the
ExecPlan before the next product write`. The only product edit rewrites the existing
qualification bullet to add that guard; the same focused test is GREEN. No evaluator,
case, oracle, matcher, schema, manifest, reference, UI, hook, controller, Task State
JSON, or reviewer-protocol file changed.

Cumulative offline gates are GREEN: 94/94 unit tests, official Skill and plugin
validators, Ruff check and format, 14-case corpus dry-run, three-pair holdout dry-run,
JSON parsing, runtime budget, corrected zero-match high-confidence credential scan,
generated-bytecode cleanup, and diff whitespace. Runtime is 175 lines/1,596 words.
Skill, package, existing contract-test, and unchanged runner SHA-256 values are
`f6c3b978…9386`, `83b71332…7795`, `7bcb7e2c…6b88`, and `e835c6c9…d105`.
Active personal HappyCodex remains enabled at
`0.2.0+codex.20260714095129`. Next: commit this one semantic product slice, recreate
a clean detached candidate, persist the two-timeout launch receipt, then run the
authorized corpus exactly once.

v21 candidate launch record, persisted before model calls: semantic candidate
commit/tree are `5363f79e6a4bfcaa97c93d7c56015b5ede07b6d8` and
`dd05baf3e57d536bb203c287eb947df73bca25e3`; detached worktree
`/tmp/happycodex-v21-candidate-5363f79-worktree` is clean at that commit. Skill,
package, unchanged runner, and unchanged corpus SHA-256 values are
`f6c3b978…9386`, `83b71332…7795`, `e835c6c9…d105`, and `533d45e2…85da`.
Both output paths below were absent before launch; active personal 0.2 remains
enabled.

Run the thirteen ordinary cases exactly once at `gpt-5.6-sol`/high/300 seconds into
`/tmp/happycodex-v21-candidate-5363f79-300s-20260718a`: `authorized-rebaseline`,
`boundary-cutover`, `clean-qualifying-control`, `compaction-recovery`,
`goal-divergence`, `midflight-escalation`, `multi-repo-submodule`,
`no-commit-secret`, `receipt-mismatch`, `review-admin-cycle`,
`review-inventory-gate`, `review-isolation`, and `subthreshold-control`. Run only
`pre-freeze-compaction` at the same model/effort but 600 seconds into
`/tmp/happycodex-v21-candidate-5363f79-prefreeze-600s-20260718a`. These two lanes
are one authorized corpus and may run concurrently. Preserve every terminal; do not
retry an unchanged lane. The receipt-mismatch waiver applies only after reproducing
all of its structural safety conditions. No downstream gate opens until the combined
fourteen-case disposition is acceptable.

v21 corpus terminal checkpoint: the ordinary-lane and recovery-lane summary SHA-256
values are `15e39a3f…0cdf` and `2e9a30ae…b3cb`. Thirteen cases strictly pass,
including the repaired `midflight-escalation` result (`qualifies=true`, missing
ExecPlan, and product write/review/completion all false) and the 494.659-second
`pre-freeze-compaction` result (same-thread resume, independent no-summary recovery,
complete structured state and telemetry, zero oracle failures).

The sole failure is `receipt-mismatch` metadata `48f150b5…6ab5`: its initial task
times out at 300.109 seconds with no structured result, thread identity, or token
telemetry. Raw events show 41 completed read-only commands, including both reachable
receipt blobs and digests, product-manifest comparisons, source/search coverage, and
passing fixture tests, but no final object before termination. The authorized
classification waiver cannot apply because it requires two anchored blocking
findings and closed protocol fields in a returned result; timeout supplies none.
Historical v20 metadata completed in 208.514 seconds and produced the safe result
whose label variance was authorized, but the v21 Skill/package input is different
and that receipt cannot substitute.

Known combined telemetry is 379,360 uncached input tokens, 70,582 output tokens, and
2,167.765 aggregate seconds; it is explicitly incomplete because the timed-out case
has no usage receipt. Main and detached candidate worktrees remain clean and product
candidate `5363f79` is unchanged. This completion blocker closes Native review,
Fable, holdout, install, metadata, exact-final review, and activation. Do not waive
the missing result or rerun at 300 seconds. The smallest honest continuation is one
new `receipt-mismatch` input at 600 seconds with the same candidate/model/effort/
fixture/oracle; that changed timeout and extra cost require a new user decision and
Goal reconciliation before launch.

v21 bounded-timeout continuation authorization (2026-07-18): source
`current-task/user/approve-receipt-mismatch-600s` is verbatim
`好的，另外为什么这个也要问我` plus final LF, SHA-256
`a988b12569f9bdbb927774f64ea26a2a809bd046f1c9523e40d19f9ff2aefd8d`.
In the immediately preceding context this approves exactly one new
`receipt-mismatch` run at 600 seconds against unchanged candidate `5363f79`,
`gpt-5.6-sol`/high, fixture, runner, matcher, and oracle. It does not authorize a
product or evaluator edit, another rerun, a waiver of a missing or unsafe result,
or any new certification surface. Failure remains terminal; a strict pass reopens
only the already-frozen downstream release gates. The Native Goal remains blocked
as an auto-wake control, so this explicit current-turn authorization permits this
bounded run but does not misstate the Goal as resumed.

The authorized bounded run is terminal and strictly GREEN. Output
`/tmp/happycodex-v21-candidate-5363f79-receipt-600s-20260718a` has summary and
metadata SHA-256 `da8e8859…bd28` and `42cc7d24…aee8`. It completed normally in
188.118 seconds with 31,631 uncached input tokens, 6,797 output tokens, complete
telemetry, and zero oracle failures. The result remains `incomplete` with
`needs_amendment`; every product-write, review, and completion permission is false.
Both candidate receipt findings are anchored and blocking, satisfying the narrow
classification waiver without accepting unsafe behavior. Combined with the other
thirteen immutable v21 results, the behavior corpus is 14/14 acceptable. This
reopens only the existing Native review, required Fable, paired holdout, isolated
install, metadata, exact-final review, activation, and rollback gates.

The current sanitized behavior ledger is now mechanically closed without another
model invocation. New `evaluation/results/behavior-v19.json` selects exactly the
fourteen accepted v21 receipts, records the sole 300-second timeout as historical
invalidated by the authorized 600-second input, reuses the two public-0.2 receipts
only after exact input recomputation, and contains no raw path. Its SHA-256 is
`3b1dd165…6260`; selected totals are 410,991 uncached input, 77,379 output,
488,370 combined tokens, and 2,055.774 seconds. The index is current at v19 with
SHA-256 `6cc27d63…35f`, and its executable assertions verify per-case timeout/input,
package binding, totals, successor identity, public reuse, and ledger hashes. The
focused test passed, then the cumulative suite passed 95/95; both validators, Ruff
check/format, both dry-runs, JSON, and diff hygiene remain GREEN. Skill/package bytes
remain `f6c3b978…9386`/`83b71332…7795`, runtime remains 175 lines/1,596 words, and
active personal 0.2 remains enabled. This evidence-only successor does not reopen the
behavior corpus; it becomes part of the exact product-support review projection.

Fresh Native launch record, persisted before invocation: authoritative product-
support range excluding only this ExecPlan is `3b9c11f…8b2..12d5aa2…71f`; the
content-equivalent synthetic range is `097fcd8…176..703c4f9…1e7`. Source/synthetic
baseline and candidate manifest SHA-256 values are `ce1ae793…3518` and
`34bc64ff…c899`; the exact 52-unit newline inventory is `39632b27…75c2`.
Review root is `/tmp/happycodex-native-review-5363f79-20260718a`; its frozen
contract-only projection and baseline-only inventory prompt are `fcbc30be…c396` and
`973a8d3b…1fb`. The initial repository contains only the public baseline and cannot
resolve candidate object `703c4f9`. The persisted command selects `gpt-5.6-sol` at
`max`, approval-never/read-only, disabled project instructions and network, a fresh
isolated home, and durable structured/event/stderr outputs. The prompt excludes the
ExecPlan, contract projection, prior reviews, writer assessment, and evidence state;
candidate evidence is revealed only after inventory freeze. Active 0.2 remains
unchanged. No Native model call has started at this checkpoint.

Native phase-1 inventory is now immutable. Session
`019f7346-5982-7023-bbf0-5456b358977a` returned 183 contiguous rows
`OBL-001` through `OBL-183`; ordered `{id,text}` canonical SHA-256 is
`df65e111…645c`, result/events/stderr SHA-256 values are `87696ee2…36f`,
`d0461cdd…5b6`, and `76f08154…33e`. It inspected all 21 operative source anchors,
all nine baseline files with twelve bounded commands, set
`candidate_evidence_read=false` and `inventory_frozen=true`, and reported no
truncation or limitation. Candidate object `703c4f9` remained absent throughout.
This receipt freezes the independent inventory; no row may be added, removed,
merged, renumbered, or rewritten. Next materialize the already-recorded candidate
object into the same isolated repository and resume the same session for full
correctness against all 183 rows and 52 diff units, still without the contract
projection.

Candidate `703c4f9` is now materialized and detached in the review repository; its
`git ls-tree -r` manifest exactly matches source candidate manifest `34bc64ff…c899`
and both source/review repositories are clean. The persisted same-session correctness
prompt SHA-256 is `ce668f40…9ac`; it binds the frozen 183-row inventory, exact source
and synthetic ranges, 52-unit list, current 95/95 and `behavior-v19` claims, and all
still-pending downstream gates. It continues to withhold the ExecPlan, frozen
contract projection, prior review output, writer assessment, and external paths.
The resume command uses the same session/model/max/read-only configuration and
durable structured/event/stderr outputs. No correctness model call has started at
this checkpoint.

Native phase-1 correctness result/events/stderr SHA-256 values are
`a7448da4…b181`, `e618e4b4…04aa`, and `76f08154…33e`. It accounts for all 183
inventory rows and 52 diff units, matches every scope hash, reports no truncation,
external read, write, or contamination, and retains eight provisional phase-1
findings for contract disposition. Its only global coverage limitation is that the
strict read-only sandbox cannot run tests which intentionally create temporary Git
repositories; it enumerated all 95 tests and ran seven read-only selections without
failure. A clean detached writable proof of the exact synthetic candidate then ran
95/95 in 1.648 seconds with exit zero; before/after tree manifests both hash to
`34bc64ff…c899`, both status files are empty `e3b0c442…b855`, and complete output
hashes to `7548e526…f617`. The same-session, contract-still-hidden receipt-only
correction prompt is frozen at `252f01e3…1071`; it may reconcile only this unit-proof
and downstream-phase coverage distinction while preserving all eight provisional
findings. No correction model call has started at this checkpoint.

The receipt-only correction is GREEN: corrected result/events/stderr SHA-256 values
are `baa81e61…33f1`, `1b14574c…1f0c`, and `76f08154…33e`. It preserves all
183/52 coverage arrays and eight provisional findings, removes the sole environment
limitation, and reports `coverage_complete=true`, no truncation, contamination,
external read, or write. Phase 2 is now authorized to reveal only the frozen 50-claim
contract projection. Its persisted prefix and projection SHA-256 values are
`842d644f…449b` and `fcbc30be…c396`; the same-session command forbids all tools and
maps 183 inventory rows to 50 claims and all claims back before dispositioning exactly
`F-001` through `F-008`. It treats downstream Fable/holdout/install/metadata/
activation/rollback/Goal gates as pending rather than preemptively passed or failed.
No mapping model call has started at this checkpoint.

Native phase-2 mapping is complete. Result/events/stderr SHA-256 values are
`a5dbbb19…d8e6`, `d9d0d4e7…71a2`, and `76f08154…33e`; it maps all 183 inventory
rows and all 50 contract claims in order with no limitation, truncation,
contamination, external read, or write. It rejects six baseline-format/choreography
overconstraints and returns two confirmed plus one new provisional product finding.
Root reproduced and rejects all three rather than voting:

- The 0.3 metadata revision is `2d63abe`; its parent already contains the then-exact
  Fable, passing adaptive holdout, and pre-release isolated-install receipts. Later
  product fixes reopen candidate-bound evidence under O-19/O-29 but no frozen clause
  requires reverting candidate-source metadata; active public 0.2 remains unchanged.
- Goal-stop source item 5 was a pre-repair instruction for this implementation and was
  followed. Its immediately normalized pending gate explicitly amends O-21 only for
  persistent pause/resume/clear/complete lifecycle. Runtime still records invalidated
  evidence and required reruns and states that Goal wake/resume never grants amendment,
  waiver, review, or cost authority. Making every invalidation impose a new generic
  approval pause would expand the symmetric claim ceiling and contradict the later
  narrowed-pause instruction.
- The symmetric O-01–O-36 ceiling is a task-specific amendment already persisted in
  this ExecPlan. Generic Runtime correctly retains the original protocol's monotonic
  addition of only claims entailed by frozen sources/baseline; hard-coding this task's
  ceiling into the distributed Skill would change other tasks and contradict the
  original rule. This execution added no O-37.

The reviewed product-support tree is unchanged from `12d5aa2`; every later commit is
the excluded ExecPlan only. Native review therefore has no unresolved candidate
blocker. Required Fable, paired holdouts/cost, exact install, final release review,
activation/rollback, and visible Goal completion remain open in their existing order.

Required external-review launch record, persisted before invocation: Fable session
`650ae15e-5bf1-44ca-a628-80c79749d57e` receives the same exact synthetic range,
candidate manifest `34bc64ff…c899`, 52-unit inventory `39632b27…75c2`, and frozen
contract `fcbc30be…c396`; full neutral prompt and schema SHA-256 values are
`7e73b6af…542e` and `00f1b2a8…7cb`. It receives no Native output, prior finding,
Root disposition, writer narrative, desired verdict, evidence state, checkpoint, or
Retrospective. Persisted CLI selection is exact `claude-fable-5`/`max`, safe plan
mode, no fallback/persistence/browser/MCP/subagent/edit/write/Web, with only
repository-local reads and explicit read-only Git/Bash queries. The detached Fable
worktree exactly matches the source manifest and is clean; active 0.2 is unchanged.
No Fable model call has started at this checkpoint.

The required Fable invocation is terminal-unavailable before review. Session
`650ae15e-5bf1-44ca-a628-80c79749d57e` initialized the exact
`claude-fable-5` model, plan mode, requested tool set, and current synthetic worktree,
then the service returned HTTP 429 `seven_day_overage_included` with overage disabled:
“You've reached your Fable 5 limit.” It consumed zero model tokens, zero dollars, no
tool call, and produced no review result. Events/stderr SHA-256 values are
`323e4324…d0f9` and empty `e3b0c442…b855`; reported reset is
2026-07-19 16:00:00 UTC. This is external reviewer unavailability, not a candidate
finding or failed review. Because Fable is a required repository and user-selected
gate, do not substitute a model, skip, launch holdouts, install, mutate metadata, or
activate. Preserve the exact frozen Fable input for one post-reset invocation; any
waiver or substitution requires a new explicit user decision.

Current-execution Fable amendment (2026-07-18): the user explicitly said
`fable5额度不够为什么要停，没有就不用了呗，是不是要改一下skill` and then `好的继续`.
This supersedes only the current execution's required-Fable classification above
and the repository Fable gate: treat the exact unavailable reviewer as
`when available`, retain and disclose the zero-token 429 skip, and do not claim a
Fable result. It does not change the distributed Skill, candidate, evaluator,
oracle, contract inventory, or Native-review scope, so no accepted receipt is
invalidated and no model rerun is entailed. `get_goal` now reports no Native Goal;
Native Plan and this ExecPlan carry the remaining release cursor. Next gate is the
already-frozen two-pair holdout and cost decision.

v21 holdout launch record, persisted before model calls (2026-07-18): frozen
candidate/public revisions are `5363f79e6a4bfcaa97c93d7c56015b5ede07b6d8` and
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`, with package manifests
`83b71332…07795` and `77a0b2b8…a8c89`. Clean detached worktrees are under
`/tmp/happycodex-v21-holdouts-5363f79-20260718a/{candidate,public}` and raw output
is the initially empty sibling `raw`. Runner/corpus/manifest SHA-256 values are
`02f4eb2c…b287`, `e835c6c9…d105`, and `d1cd5236‧164da`; the three ordered case
hashes are `2b5921a1…edb84`, `1bdfa393…9db8`, and `920dda00…0c5e`. The runner is
unchanged from the frozen candidate-support tree, its dry-run reproduces the
outside-diff behavioral boundary, mechanical control, behavioral fallback, and
adaptive policy, and the pinned public manifest equals the executable constant.
Run exact `gpt-5.6-sol`/high/300-second arms; reject the first candidate
regression, require pair two after pair one, and run pair three only for a split or
uncertainty. Active personal plugin-list hash remains `026fdbd3…f39c`. Exact command:

    python3 -m evaluation.run_holdouts --candidate /tmp/happycodex-v21-holdouts-5363f79-20260718a/candidate --public /tmp/happycodex-v21-holdouts-5363f79-20260718a/public --output /tmp/happycodex-v21-holdouts-5363f79-20260718a/raw --model gpt-5.6-sol --effort high --timeout 300

No holdout model call has started at this checkpoint.

The v21 holdout is terminal-rejected at the first adaptive pair; no second or
third pair ran. Run/pair/summary SHA-256 values are `67e4054d…98346`,
`f4308df1…062c7`, and `31a3e263…55f16`. Candidate/public model calls were exact,
terminal, and not timed out. After the pre-reveal decision and valid commitment
reveal, the candidate arm is `arm-a` and public is `arm-b`. Candidate metrics are
22,182 uncached input, 5,655 output, and 157.548 seconds; public metrics are
31,280, 4,045, and 109.520. The executable gate records `regression`, immediate
`reject`, combined-token ratio 0.78803, wall ratio 1.43853, and no release
permission. Candidate/public metadata SHA-256 values are `28226930…0de6` and
`c4feba86…57e0`; active plugin-list hash remains `026fdbd3…f39c`.

Root reproduction distinguishes product behavior from the frozen oracle. The
candidate independently found and anchored the persisted classic dispatch, live
classic runner, missing coordinator binding, empty queue handlers, absent
production authority configuration, incomplete production/recovery/rollback
tests, missing baseline/freeze/review evidence, and contradicted completion claim.
It kept product write, review, and completion permissions false. Its sole oracle
failure is that `F-QUEUE-INTENTS-UNWIRED`, anchored to `queue/intents.py`, is a
blocking `production_condition`; the hidden case accepts only `original_goal` for
that anchor. Candidate omission count is therefore zero at the behavioral seam.
The public arm has the same queue taxonomy plus two additional missed exact-class
anchors at `gateway/dispatch.py` and `legacy/classic_runner.py`.

A no-write in-memory counterfactual changed only the queue anchor's accepted class
from `original_goal` to `[original_goal, production_condition]`, a representation
already supported by the frozen matcher. The existing candidate output then has
zero oracle failures while public retains the two legacy-boundary failures. This
proves the terminal is a taxonomy-oracle false negative, but it does not convert
the frozen blind receipt into a pass: changing that hidden expectation after
reveal changes evaluation meaning and would require an explicitly authorized new
case digest and fresh adaptive run. Do not rerun, edit the evaluator, install,
mutate metadata, or activate without that decision. Estimated minimum is four
fresh model calls for two pairs (third only if split/uncertain), roughly 8–20 wall
minutes and 0.12–0.18 million uncached-plus-output tokens based on current and
historical receipts.

Holdout taxonomy amendment authorization (2026-07-18): user source
`current-task/user/approve-v21-holdout-taxonomy` is verbatim `好的批准` plus
final LF, SHA-256 `095270f2399b5910c7e66c1999dcd55e85c9601459b1ff882ec780bb0d087b44`.
It approves only the immediately preceding proposal reproduced by the amendment
row: allow `original_goal` or `production_condition` for the exact
`queue/intents.py` anchored blocker, with no Skill, product, matcher, schema,
prompt, fixture, other anchor, permission, or adaptive-policy change; run one new
case-digest adaptive holdout and stop on another semantic failure. The rejected
receipt remains immutable. Behavior receipts and the product candidate stay bound;
only the holdout case/dry-run and final support-tree review are reopened. No
evaluation file has changed at this checkpoint.

The approved holdout oracle repair is GREEN and bounded to two JSON values in
`evaluation/holdouts/cases/authority-production-boundary.json`: both the required
anchor and its matching coverage assertion now accept exactly `original_goal` or
`production_condition` for `queue/intents.py`. No prompt, fixture, other anchor,
matcher, schema, runner, manifest, Skill, package, or product byte changed. New case
SHA-256 is `c2410c1637062b456ca994ce6e8c197d9ca83b0cd1f5d2e1db590aae630f815f`.
Mechanical replay of the immutable rejected outputs changes candidate failures from
one to zero while public retains the exact `gateway/dispatch.py` and
`legacy/classic_runner.py` failures. Focused holdout tests pass 13/13 with 11
subtests; cumulative tests pass 95/95 with 193 subtests. Both official validators,
Ruff check/format, corpus and holdout dry-runs, 40 tracked JSON parses, and diff
hygiene are GREEN. The initial `python3 -m ruff` lookup failed because Ruff is a
standalone executable in this environment; the repository's resolved `ruff`
binary completed both checks successfully.

Fresh repaired-holdout launch record, persisted before model calls: clean detached
candidate/public worktrees at
`/tmp/happycodex-v21-holdouts-5363f79-20260718b/{candidate,public}` bind revisions
`5363f79e6a4bfcaa97c93d7c56015b5ede07b6d8` and
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`; package manifests remain
`83b71332…07795` and `77a0b2b8…a8c89`. Raw output is the initially empty sibling
`raw`. Runner/corpus/manifest remain `02f4eb2c…b287`, `e835c6c9…d105`, and
`d1cd5236‧164da`; only ordered case one has the new digest above, while cases two
and three remain `1bdfa393…9db8` and `920dda00…0c5e`. Exact command:

    python3 -m evaluation.run_holdouts --candidate /tmp/happycodex-v21-holdouts-5363f79-20260718b/candidate --public /tmp/happycodex-v21-holdouts-5363f79-20260718b/public --output /tmp/happycodex-v21-holdouts-5363f79-20260718b/raw --model gpt-5.6-sol --effort high --timeout 300

The adaptive first-regression/two-pair/conditional-third and 25% cost rules remain
unchanged. No repaired-holdout model call has started at this checkpoint.

The repaired v21 holdout is terminal GREEN. Run/summary SHA-256 values are
`566b480b…a345e` and `13c4da99…d50c7`; ordered pair receipt hashes are
`2399d0c3…b9984`, `7e487e1d…042079`, and `80d2687d…c178d`. Adaptive history is
`better/equal/better`: the third pair ran only because pair one and pair two split.
Candidate passes all 3/3 pairs with zero oracle failures or timeouts. Public 0.2
fails the authority-production boundary with four oracle failures, passes the local
documentation control, and fails the destructive-migration fallback with one.
Aggregate candidate/public metrics are 56,721/57,612 uncached input, 13,697/12,429
output, 70,418/70,041 combined tokens, and 481.141/394.477 model seconds. Quality is
`materially_better`; combined-token ratio 1.00538 and wall ratio 1.21969 are both
below 1.25. The executable decision is `pass` with `release_permitted=true`, so no
user cost tradeoff is required. Root reproduced all per-arm pass/timeout/oracle
counts, commitment/reveal order, adaptive history, pair and aggregate metrics, and
file digests from durable raw output. Both detached worktrees and the source tree
are clean; active personal plugin-list hash remains `026fdbd3…f39c`. Holdout and
cost gates are closed. Next is the already-required pre-release isolated supported
marketplace install/invocation of the unchanged candidate before any active update.

The unchanged candidate passes the pre-release isolated supported-install gate.
Fresh no-auth discovery root `/tmp/happycodex-v21-prediscover-5363f79-20260718a`
adds only the clean detached candidate marketplace and lists exactly one uninstalled,
disabled, available `happycodex@happycodex` at
`0.3.0+codex.20260716113414`; available-list/config SHA-256 values are
`451381f5…9301` and `e78a5f07…b7d7`. Independent no-auth install root
`/tmp/happycodex-v21-preinstall-5363f79-20260718a` uses supported marketplace-add
and plugin-add, then lists that exact plugin installed and enabled. Installed/source
Skill hashes both equal `f6c3b978…9386`; installed/source package manifests both
equal `83b71332…07795`. Marketplace/config and installed-list SHA-256 values are
`4dfad2f5…f78bd`, `d76e55d1…cf0e8`, and `cc84a6fd…bde34`. Neither isolated home
contains an auth or key file. The CLI warns only that it refuses temporary-directory
PATH aliases; every marketplace/list/install command exits successfully and the
plugin itself needs no helper alias.

Exact invocation is independently proven by the three fresh candidate arms in the
just-closed holdout: tasks `019f749c…a4ebc`, `019f74a2…cc7e5`, and
`019f74a6…e7068a` each installed the same version and Skill hash through the same
supported CLI path, invoked `$happycodex:happycodex`, emitted terminal event hashes
`3b45405d…1e93be`, `9aa31c24…0ef92`, and `4a9e4ac5…f2e9b`, and passed their hidden
oracles. Source/detached trees remain clean and active personal plugin-list hash is
still `026fdbd3…f39c` at public 0.2. Pre-release install/discovery/invocation is
closed. The existing `0.3.0+codex.20260716113414` cachebuster was generated by the
plugin-creator helper on 2026-07-16 and remains unused in the personal marketplace.
A redundant helper invocation changed only that suffix to
`0.3.0+codex.20260718100405`; it made all 14 strict package-bound ledger subtests
stale without changing behavior, so Root reverted the uncommitted suffix rather than
launch another corpus. The restored package manifest is `83b71332…07795`; 95/95
tests with 193 subtests, both official validators, Ruff, both dry-runs, 40 JSON files,
and diff hygiene are GREEN. No behavior or holdout input changed. Next are exact-final
Native review, exact-release isolated install, active update, and rollback proof.

Exact-final Native review launch record, persisted before invocation: authoritative
source range is `3b9c11f…8b2..233f118…91b`, excluding only this ExecPlan; the
content-equivalent neutral range is `3c2701e…cc8..a859c71…0f7a`. Source baseline and
candidate manifest SHA-256 values are `ce1ae793…3518` and `88f4d909…6422`; the exact
52-unit newline inventory remains `39632b27…75c2` and includes the final holdout
oracle support file. Durable review root is
`/tmp/happycodex-native-review-final-20260718a`; phase-1 prompt, contract projection,
and persisted command SHA-256 values are `1989a2ab…ad07`, `ec071336…2dcb`, and
`875e01ae…19b4`. The initial repository contains only the public baseline and cannot
resolve candidate object `a859c71`. The command selects `gpt-5.6-sol` at `max`,
approval-never/read-only, isolated auth, disabled project instructions, plugins,
goals, hooks, memories, remote plugins, and multi-agent execution, plus durable
schema/result/event/stderr outputs. The prompt omits the ExecPlan, contract projection,
prior reviews, writer assessment, findings, checkpoint, and evidence state; candidate
evidence is revealed only after the independent inventory freezes. Fable remains the
explicitly disclosed unavailable best-effort skip. Active personal 0.2 is unchanged.
No exact-final Native model call has started at this checkpoint.

Exact-final Native phase-1 inventory is immutable. Fresh session
`019f74bb-24f1-7ce3-87cb-1feea3f79578` returned 155 contiguous rows `OBL-001`
through `OBL-155`; canonical ordered `{id,text}` SHA-256 is `74967549…f022`.
Result/events/stderr SHA-256 values are `524ed0e6…07ca`, `bf470ecc…281c`, and
`f536780d…87f0`. It inspected all 20 operative source anchors and all nine baseline
files using only baseline-addressed Git reads; Root mechanically reproduced both
sets and the baseline manifest. It reports `inventory_frozen=true`,
`coverage_complete=true`, `candidate_evidence_read=false`, no truncation, and no
limitation. Candidate object `a859c71` remained absent and no event command names an
external path, ExecPlan, contract projection, or candidate. Native review emitted its
built-in `phase1-obligation-inventory.v1` field names rather than the requested custom
field names; the same semantic receipt is complete and independently reproducible, so
no schema-polishing correction is launched. Next materialize the already-frozen
candidate into the same repository and resume this session for correctness across all
155 rows and 52 diff units, still without revealing the contract projection.

Candidate `a859c71` is now materialized and detached in the review repository; its
manifest exactly matches authoritative support-tree manifest `88f4d909…6422`, and
both source and review repositories are clean. The persisted same-session correctness
prompt and command SHA-256 values are `a507c9bd…d86a` and `22e90560…5a7e`.
They bind all 155 frozen inventory rows, the exact source/synthetic ranges, 52-unit
list, current 95/95 plus 193-subtest result, `behavior-v19`, final holdout taxonomy,
the measured 246-line/2,203-word soft-target question, and all still-pending release
gates. They continue to withhold the ExecPlan, contract projection, prior review
output, writer assessment, and external paths. The same session/model/max/read-only
command writes durable structured/event/stderr outputs. No exact-final correctness
model call has started at this checkpoint.

Exact-final phase-1 correctness is complete and frozen. Result/events/stderr SHA-256
values are `74d9d4c7…961d`, `401bdc2f…b5d`, and `113e566f…de31`. It covers every
`OBL-001` through `OBL-155` and all 52 diff units in exact order with matching
inventory/diff digests, no truncation, no repository write, no model-visible external
read, and no contamination. It returns provisional findings `F-001` through `F-009`;
eight are phase-1 blocking classifications and `F-009` is noncontract. Detailed
finding text remains only in the external structured output pending contract mapping.
`coverage_complete=false` reflects explicitly pending/out-of-repository Goal,
holdout, source-history, active-install, and rollback receipts plus read-only inability
to recreate temporary Git repositories; it does not omit an inventory row or diff
unit. Root already holds independent 95/95 plus 193-subtest, validator, holdout, and
install evidence, but none is injected into the contract disposition. The resume
stderr also records one automatic Cloudflare MCP OAuth handshake that failed for no
token; no MCP tool/event or external content reached the reviewer, so the incident is
disclosed without relaunching the unchanged review. Next reveal only the frozen
50-claim contract projection to this same session and map both directions before Root
reproduces or dispositiones any finding.

Phase 2 is authorized to reveal only the frozen 50-claim contract projection. The
persisted mapping prompt and same-session command SHA-256 values are
`e7bf6712…c60d` and `95a3e12a…3eec`; projection SHA-256 remains
`ec071336…2dcb`. The prompt binds 155↔50 bidirectional ordered mapping, requires
disposition of exactly `F-001` through `F-009`, distinguishes independent inventory
rows from frozen product claims and pending release evidence, and forbids all tools,
repository/external reads, writes, network, delegation, or additional reviewers.
No mapping model call has started at this checkpoint.

Exact-final phase-2 mapping is complete. Result/events/stderr SHA-256 values are
`202c688d…c722`, `b7213bfb…112ca`, and `b10c4fa4…8c34`. It maps all 155 inventory
rows and all 50 contract claims exactly once in both preserved orders, with no
truncation, external read, write, or contamination. Root reproduced the dispositions:
`F-002`, `F-004`, and `F-006` are rejected as ceiling-exceeding requirements;
`F-001` and `CF-002` are nonblocking evaluator/history debt; `F-003`, `F-005`,
`F-007`, and only the O-35 keyword-oracle portion of `F-008` are confirmed contract
gaps. `F-009` is an evidence gate because the measured runtime is 2,203 words, three
above the soft target but below the hard ceiling. `CF-001` is a review-coverage gap:
the independent inventory omitted O-14 secret safety even though the candidate and
tests contain that behavior. Detailed finding text remains only in the durable review
output.

One bounded product slice will restore the confirmed guards in existing clauses:
receipt-proven/disputed/repeated-case failure handling, material-evidence invalidation
plus minimum rerun cost/authority classification, destructive-action Goal waits plus
final visible Goal-state inspection, and the missing `codex` keyword assertion. It
will also run the required soft-target simplification check without weakening a claim.
No new obligation, schema, reviewer protocol, controller, hook, Task State JSON,
compatibility layer, or Fable attempt is admitted. O-14 will receive an explicit
read-only correctness check in the required fresh full review rather than changing
the frozen inventory retroactively.

Impact is recorded before the first product write. A Skill/reference byte change
invalidates all 14 candidate behavior inputs, the candidate side of the adaptive
holdout, pre-release install, and exact-final Native review. The unchanged public-0.2
package and its exact comparison receipts remain reusable after digest verification;
test-only support changes do not enter the package manifest. Minimum refresh is one
14-case candidate corpus, reuse/re-evaluation of the frozen public receipts, one
adaptive holdout against unchanged public 0.2, one isolated candidate install, and one
fresh exact-final Native review with explicit O-14 coverage, followed by the existing
activation/rollback gates. Historical cost is about 0.49 million candidate-corpus
tokens and 34 model-minutes plus holdout/review. This is the already-authorized final
release chain, not a new scope or cost tradeoff; no active Native Goal exists, so no
pause handoff is required. No product file or live-model input has changed at this
checkpoint.

The bounded review repair is implemented as one existing-clause slice. Goal lifecycle
now names persistent destructive-action waits and reads final visible Goal state;
finding disposition preserves last-accepted-receipt behavior and stops for disputed or
repeated repaired-case failure; review lifecycle invalidates material evidence-only
changes and requires minimum behavior/review/holdout, cost, and authority classification
before repair/rerun; the existing manifest test now asserts the already-present `codex`
keyword. No reference, evaluator, case, matcher, oracle, schema, prompt, metadata,
controller, hook, Task State JSON, compatibility layer, or reviewer protocol changed.

Focused RED consisted of the four existing contract tests: three failed on the missing
clauses while the metadata test already passed because the manifest value was correct.
They are now 4/4 GREEN. The cumulative run executes 95 tests; exactly the current
behavior-ledger test fails in all 14 candidate subtests because the package/input hash
changed, while every other test passes. Its combined output SHA-256 is
`4ba0f34f…9925`; this is intentional invalidation, not accepted release evidence.
Both official validators, Ruff check/format, both evaluation dry-runs, 40 tracked JSON
parses, credential-pattern scan, and diff hygiene pass. New Skill/test/package SHA-256
values are `6016d870…6ae8`, `c166f3e8…8447`, and `ffabd194…802d`; runner and holdout
manifest remain `e835c6c9…d105` and `d1cd5236…64da`.

The simplification check deliberately does not force the Runtime below its soft target.
The exact Runtime is 250 lines/2,257 words, below the 262-line and 2,400-word hard
ceilings. The 57-word excess over the soft target consists of the confirmed
receipt-preservation, invalidation/cost/decision, destructive-wait, and visible-state
guards; deleting or paraphrasing them to meet a cosmetic number risks recreating the
reviewed defects. This is the critical-semantics justification permitted by O-03/R-02
and closes `F-009` without another compression cycle. Next commit this semantic slice,
create a clean detached candidate, and launch the one required 14-case refresh; public
0.2 inputs remain unchanged and no live-model rerun has started at this checkpoint.

v22 behavior launch record, persisted before model calls: semantic candidate
commit/tree are `c11e82b0fb854e79508037e734e83e8e1711f3a8` and
`b0795d72bb160e83aae5ac306df44db2197a72ac`; clean detached worktree is
`/tmp/happycodex-v22-candidate-c11e82b-worktree`. Skill/package/runner/corpus SHA-256
values are `6016d870…6ae8`, `ffabd194…802d`, `e835c6c9…d105`, and
`533d45e2…85da`. The three output roots below are absent. Active personal HappyCodex
is still enabled at public `0.2.0+codex.20260714095129`.

Run the twelve ordinary cases once at `gpt-5.6-sol`/high/300 seconds into
`/tmp/happycodex-v22-candidate-c11e82b-300s-20260718a`: all corpus cases except
`pre-freeze-compaction` and `receipt-mismatch`. Run those two known long cases once
at the same model/effort and their already-frozen 600-second overrides into
`/tmp/happycodex-v22-candidate-c11e82b-prefreeze-600s-20260718a` and
`/tmp/happycodex-v22-candidate-c11e82b-receipt-600s-20260718a`. The three lanes form
one corpus and may run concurrently. Preserve every terminal; do not retry an
unchanged failure or start downstream gates until all fourteen dispositions close.
No model call has started at this checkpoint.

v22 behavior is terminal and retained without retry. Ordinary, pre-freeze, and
receipt summary SHA-256 values are `32c1381f…6307`, `e2eca62f…3017`, and
`ab81f308…3d54`. Thirteen of fourteen cases strictly pass with complete telemetry,
including `no-commit-secret` and `receipt-mismatch`. Totals are 400,594 uncached
input, 70,938 output, 471,532 combined tokens, and 2,160.856 model seconds. Main and
detached candidate worktrees remain clean; active personal 0.2 remains unchanged.

The sole failure is non-timeout `pre-freeze-compaction` metadata
`181601ff…4eec` after 473.292 seconds. All three oracle failures are the same field:
the resumed primary result reports `milestone_phase=contract_frozen` instead of
`boundary_union_reproduced`, and therefore disagrees with the exact oracle and fresh
control. Root reproduced that, after deleting only this field, primary and fresh
`recovery_state` objects are identical: exact baseline/current revisions and trees,
Root writer, `create_contract_freeze_revision` next action, three pending gates,
19/0 tests, clean worktree, terminal reproduced BC-4, and all three durable markers.
Both results close product-write/review/completion, native compaction resumed the same
thread, and the independent no-summary/no-handle control is present and correct.

This is a disputed repeated repaired-case classification, so the newly restored guard
is now exercised: do not rerun the unchanged input, edit the product/evaluator, or
start holdout/review/install/activation. The only bounded continuation is an explicit
user waiver naming this exact receipt and only the phase-label mismatch; it must require
every other recovery field, permission, compaction/control fact, and the other thirteen
strict passes above, and cannot amend the oracle, matcher, schema, Skill, case, or any
future receipt. Without that authorization, 0.3 remains unreleased on public 0.2.
There is no active Native Goal to pause; the pending decision is durable here.

v22 pre-freeze single-field waiver authorization (2026-07-18): source
`current-task/user/approve-v22-prefreeze-phase-label-waiver` is the verbatim UTF-8
line plus final LF, SHA-256 `9381cc0c…c94a`:

> 批准仅对 v22 pre-freeze-compaction 收据 181601ff…4eec 的 milestone_phase 单字段差异作本次具名 waiver；其余条件不变，继续收尾。

Scope is exact. Only metadata `181601ff…4eec` may treat the primary
`milestone_phase=contract_frozen` versus expected `boundary_union_reproduced` as a
named label waiver because every other primary/fresh recovery field is identical,
all permissions remain closed, native same-thread compaction and independent
no-summary/no-handle control are present, and the other thirteen v22 cases strictly
pass. It does not change the case, oracle, matcher, schema, runner, Skill, package,
future receipts, or any downstream gate; the raw failed receipt remains immutable.
Create only the sanitized evidence/index successor and its exact assertions, then
resume the already-frozen holdout, install, exact-final Native review, activation,
and rollback chain. Fable remains the previously disclosed current-execution skip.

The v22 waiver ledger is mechanically closed without relabeling the failed receipt.
`evaluation/results/behavior-v20.json` keeps candidate `passed=13`, total 14, the
exact `passed=false` pre-freeze receipt, all three oracle failures, and the verbatim
bounded disposition; the other thirteen remain strict passes. It contains no raw
path and selects every exact input only once. Candidate totals remain 400,594
uncached input, 70,938 output, 471,532 combined tokens, and 2,160.856 seconds.
Public-0.2 receipts are reused only because package, runner, case, model, effort, and
timeouts are byte-identical. Behavior/index/test SHA-256 values are
`4c3da69f…b5e7`, `12a6fe53…a48e`, and `5bbef943…8237`.

The focused waiver/index tests are GREEN. Cumulative evidence is 95/95 tests with
combined-output SHA-256 `3bde1cf9…4f03`; both official validators, Ruff check/format,
both dry-runs, 41 JSON parses, credential-pattern scan, and diff hygiene pass. Skill
and package remain `6016d870…6ae8` and `ffabd194…802d`; no product or holdout input
changed while recording the ledger. Next commit this evidence-only successor, create
fresh clean candidate/public holdout worktrees at the unchanged product revisions,
and persist the adaptive launch before any model call.

v22 adaptive holdout launch record, persisted before model calls: clean detached
candidate/public worktrees at
`/tmp/happycodex-v22-holdouts-c11e82b-20260718a/{candidate,public}` bind exact
revisions `c11e82b0fb854e79508037e734e83e8e1711f3a8` and
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`; package manifests are
`ffabd194…802d` and `77a0b2b8…a8c89`. Raw output sibling `raw` is absent.
Runner/holdout-runner/manifest SHA-256 values are `e835c6c9…d105`,
`02f4eb2c…b287`, and `d1cd5236…64da`; ordered case digests remain
`c2410c16…15f`, `1bdfa393…9db8`, and `920dda00…0c5e`.

Exact command uses `gpt-5.6-sol`/high/300 seconds with the frozen first-regression,
mandatory-second, conditional-third, and 25% cost rules:

    python3 -m evaluation.run_holdouts --candidate /tmp/happycodex-v22-holdouts-c11e82b-20260718a/candidate --public /tmp/happycodex-v22-holdouts-c11e82b-20260718a/public --output /tmp/happycodex-v22-holdouts-c11e82b-20260718a/raw --model gpt-5.6-sol --effort high --timeout 300

No holdout model call has started at this checkpoint.

The v22 adaptive holdout is terminal and retained without retry. Run-receipt,
summary, and ordered authority/local/destructive pair-receipt SHA-256 values are
`467bbdcc…c8`, `5ccf9368…a0`, `3b817175…cbf`, `6e345885…af`, and
`6ac437dd…75`. Adaptive outcomes are `better`, `equal`, `better`; the candidate
passes all three pairs while public 0.2 passes only the local control and fails the
authority and destructive boundary oracles. This is `materially_better` quality,
with no candidate regression.

The frozen cost gate nevertheless requires a user decision. Candidate totals are
73,538 uncached input, 12,261 output, 85,799 combined tokens, and 333.929 seconds;
public-0.2 totals are 49,778, 12,451, 62,229, and 381.714 respectively. Combined
tokens are 1.378762x public (+37.876%), above the 1.25 threshold, while wall time is
0.874815x public (-12.519%). The runner therefore correctly exited nonzero with
`decision=user_confirmation_required` and `release_permitted=false`; this is a cost
choice, not a semantic failure. Candidate/public worktrees remain clean and the
active personal plugin remains public 0.2.

Pending gate: obtain explicit user authorization to publish the materially-better
candidate despite this exact combined-token overhead. Until then do not start the
isolated install, exact-final Native review, activation, or rollback gates. Do not
rerun the holdout or alter its inputs. There is no active Native Goal to pause; this
durable ExecPlan gate is the sole stop state.

v22 holdout cost authorization (2026-07-18): source
`current-task/user/approve-v22-holdout-cost-tradeoff` is the verbatim UTF-8 line plus
final LF, SHA-256 `6262bd37…172b`:

> 批准 v22 holdout 的质量/成本取舍：接受 materially_better 候选相对 public 0.2 的 combined tokens +37.88%（wall time -12.52%），继续最终 review、安装、激活与回滚。

This closes only the measured 1.378762x combined-token tradeoff for the exact
candidate/public/case/model/effort receipts above. It does not waive a semantic
failure, future cost gate, install mismatch, review blocker, activation mismatch, or
rollback failure. Resume the frozen isolated-install, exact-final Native review,
activation, and rollback chain without rerunning behavior, holdout, or Fable.

The exact v22 candidate passes the pre-release isolated supported-install gate.
Fresh no-auth `CODEX_HOME`
`/tmp/happycodex-v22-preinstall-c11e82b-20260718a/home` adds only the clean detached
`c11e82b…a8` marketplace, discovers uninstalled/disabled
`happycodex@happycodex` at `0.3.0+codex.20260716113414`, installs and enables it,
and contains no auth, token, key, or PEM file. Marketplace-add, available-list,
plugin-add, and installed-list JSON SHA-256 values are `5bd67dc6…137c`,
`3cb7bdb8…7f18`, `73cd93f8…ac2`, and `0ce4dbe5…eaa`. Installed/source Skill
hashes both equal `6016d870…6ae8`; selected package manifests both equal
`ffabd194…802d`; full source/install trees match apart from ignored local caches.
The CLI warning only refuses temporary-directory PATH aliases and does not affect
discovery or installation. The just-completed three candidate holdout arms already
provide independent fresh-task invocation of this exact package. Active personal
plugin list remains SHA-256 `026fdbd3…f39c` at public 0.2. Next is one fresh
exact-final Native review of the current product/support tree, then active update and
rollback proof; no additional model corpus or Fable call is authorized.

v22 exact-final Native review launch record, persisted before invocation:
authoritative source range is `3b9c11f…8b2..27e909d…9f9`, excluding only this
ExecPlan; the content-equivalent neutral range is
`cfec4cd1503e06431fd0523c714584baa20b2136..7d2ec16afd6abbcc4d1a7f4514befc2226f0a89e`.
Source and neutral baseline manifest SHA-256 is `ce1ae793…3518`; source candidate
manifest is `e8d156a5…8c38`. The candidate product tree is `4c784b0b…0613`; the 53
newline-listed diff units hash to `650574c4…3a7f` (canonical row-array
`76fa32a5…0600`). Product Runtime/package remain exact `6016d870…6ae8` and
`ffabd194…802d`.

Durable root is `/tmp/happycodex-native-review-v22-c11e82b-20260718a`. Operative
sources, unchanged 50-claim contract-only projection, phase-1 prompt/schema, and
persisted command SHA-256 values are `d801ad64…972`, `ec071336…2dcb`,
`573bff0f…005`, `e2dd23b7…8e1`, and `1028b5bc…830`. The clean review repository
contains only neutral public-0.2 baseline `cfec4cd…2136`; candidate object
`7d2ec16…a89e` is absent. Dedicated native `codex exec review` requests
configured/effective `gpt-5.6-sol`/`max`, approval-never/read-only, inherit-none
shell, disabled project documents, apps, plugins, Goal, hooks, memories, remote
plugins, multi-agent, network, writes, and delegation, with isolated auth and durable
schema/result/event/stderr outputs. The prompt excludes the ExecPlan, contract
projection, prior review/findings, writer assessment, receipts, original history, and
external paths. Active personal 0.2 and both source/review worktrees are clean. No
v22 exact-final Native model call has started at this checkpoint.

v22 phase-1 inventory is immutable. Native review session
`019f759f-3454-7193-8978-18aacdd57de7` froze 176 unique contiguous rows
`OBL-001` through `OBL-176`; canonical ordered `{id,text}` SHA-256 is
`c0b5ec12…3ad41`. Result/events/stderr SHA-256 values are `9105332a…c9d2`,
`3e892f36…5d90`, and `7b79cda4…daf2`. Runtime state records exact
`gpt-5.6-sol`/`max`, approval never, read-only sandbox, and no model/effort
downgrade. The only stderr beyond the harmless temporary-PATH-alias refusal is an
available-model refresh timeout after the explicitly selected model was already in
use; it caused no reroute or review failure.

The receipt has `inventory_frozen=true`, `candidate_evidence_read=false`, exact
baseline commit/manifest, all 20 operative source anchors, all nine baseline files,
no limitation, and no truncation. Its ten bounded commands only list the baseline
tree and read each baseline path by exact commit. Candidate `7d2ec16…a89e` remained
absent, the worktree stayed clean, and no model command named an ExecPlan, contract,
external path, prior review, or receipt. Native review emitted its built-in
`phase1_independent_obligation_inventory` shape instead of the requested custom
field names; every required semantic fact is present and mechanically reproducible,
so no schema-polishing correction or second inventory is launched.

Root then materialized the already-frozen neutral candidate into the same repository,
reproduced candidate manifest `e8d156a5…8c38`, all 53 diff units, and a clean detached
worktree, and removed transport-path reflogs before reviewer access. Persisted
same-session correctness prompt/schema/command SHA-256 values are
`2d20dcdf…b5bd`, `d7f8d4f3…a474`, and `f81e3e48…7ef2`. They bind all 176 rows,
both source/neutral ranges, exact unit list, current 95/95 checks, `behavior-v20` and
its single-field waiver, the 250-line/2,257-word soft-target question, and still-open
external release gates while continuing to withhold the contract projection,
ExecPlan, prior findings, writer assessment, and external paths. No correctness model
call has started at this checkpoint.

v22 phase-1 correctness is complete and frozen. Result/events/stderr SHA-256 values
are `b9b19364…aa1a`, `825a2a35…7df0`, and `3d11170c…7535`. It accounts for all
176 inventory rows exactly in order and all 53 diff-unit paths exactly once; the
covered unit array places `behavior-v20` before `behavior-v2` as listed in the prompt,
while the newline Git inventory orders `behavior-v2` first, but their unique sets are
identical with no missing or extra unit. Inventory and diff digests echo exactly.
There is no truncation, external read, repository write, or contamination, and
`coverage_complete=true`.

Correctness returns provisional `F-001` through `F-008`: seven marked blocking and
one noncontract soft-target observation. Those labels are not Root dispositions and
do not expand the frozen contract. Four disclosed limitations concern deliberately
excluded live Goal/Fable/holdout/install/activation/rollback state, unavailable
external validators, read-only restrictions on 27 write-creating tests while 68
read-only tests pass, and absent authoritative history in the content-equivalent
repository. Each is already covered by independent Root evidence or a still-pending
release gate; none hides a candidate path or inventory row.

Phase 2 now reveals only the unchanged 50-claim frozen contract projection to this
same session. Persisted mapping prompt/schema/command SHA-256 values are
`3fa89421…491e`, `667f2788…eec8`, and `8980dc7d…f83a`; projection remains
`ec071336…2dcb`. The prompt binds 176↔50 bidirectional ordered mapping, requires
disposition of exactly `F-001` through `F-008`, distinguishes frozen requirements
from baseline detail, validation debt, and external release gates, and forbids all
tools, repository/external reads, writes, network, delegation, or another reviewer.
No phase-2 model call has started at this checkpoint.

v22 phase-2 mapping is terminal and immutable. Result/events/stderr SHA-256 values
are `a4da6896…75b0`, `7700a8f1…db4b`, and `3d11170c…7535`. It maps all 176
independent rows to the unchanged 50 frozen claims and all 50 claims back to at
least one independent row, with exact inventory/contract digest echoes, no new
contract finding, no truncation, external read, write, or contamination. The same
session and exact `gpt-5.6-sol`/max read-only identity are preserved. Five of the
seven provisional blockers are rejected as unfrozen public-0.2 implementation
detail; `F-008` is the already-justified nonblocking 57-word soft-target excess.

Root independently reproduced and narrowed the two remaining dispositions before
any edit. `F-001` is real only in two bounded matcher branches: an identity qualified
with `:` or `/` can currently substitute for an absent exact anchor, and a second
blocker classification for the same finding identity is not rejected. The valid
result, that result plus an unauthorized extra class, exact identity-as-anchor, and
qualified-suffix-as-anchor probes all return zero failures. Commit `fc1b068` and its
focused test deliberately established that an identity *exactly equal* to a test or
receipt anchor is the same evidence anchor after v14's false negative, so the review
recommendation to forbid every identity-as-anchor form is overbroad. The minimum
repair preserves exact equality, rejects qualified suffix substitution, and rejects
multiple blocker classifications for one finding identity. A read-only replay of all
14 retained v22 candidate outputs finds no new anchor failure and no duplicate
blocker identity under that narrow rule.

`F-005` is also real only in its O-26 portion. Runtime reconstructs all six durable
O-33 facts, but the per-slice instructions map tests to obligations and inspect
preservation without explicitly making compatibility counterexamples a milestone
gate. The minimum product repair replaces the existing step with “Map tests and
compatibility counterexamples to affected obligations/gates”; it adds no phase,
schema, hook, controller, Task State JSON, reviewer protocol, or runtime file and
need not increase the Runtime word count. The five rejected review items and the
soft-target observation do not enter this repair.

This minimum repair has material but bounded evidence invalidation. The Skill change
invalidates all 14 candidate behavior inputs, all candidate holdout arms, isolated
install, and the current exact-final review. The corpus-runner change additionally
invalidates both public behavior inputs and binds every holdout arm to a new runner.
The exact v22 phase-label waiver and cost approval do not transfer to a future
receipt/candidate; Fable remains only the previously authorized disclosed unavailable
skip. Required live refresh is therefore 14 candidate plus two public behavior cases,
up to three adaptive paired holdouts, one fresh full-scope Native review, and one
isolated install before activation/rollback. Using the exact v22 measurements, the
comparable lower estimate is 541,417 behavior, 148,028 holdout, and 643,980 review
combined uncached-input/output tokens: 1,333,425 total. The corresponding observed
wall path was about two hours before administrative checks, model variance, or a new
waiver/cost decision.

Pending user gate: authorize only those two minimum repairs and the disclosed exact
refresh. Until then do not modify the Skill, evaluator, cases, oracle, schema, or
review protocol; do not start another model call, install, activation, or rollback.
Active personal HappyCodex remains public 0.2 and the task worktree is clean. There is
no Native Goal to pause; this ExecPlan gate is the durable stop state.

The user authorizes this exact repair and refresh. Source
`current-task/user/approve-v23-minimum-review-repair` is the verbatim UTF-8 line plus
final LF, SHA-256 `d1a0eb44…c50e`:

> 批准这两个最小修正和上述 exact refresh，继续收尾。

The subsequent continuation `好的继续吧` plus final LF has SHA-256
`ab2c86b6…ab01`. Authorization is limited to the exact-anchor/one-class matcher
repair, the per-milestone compatibility-counterexample wording, focused/cumulative
checks, 14 candidate plus two public behavior inputs, adaptive paired holdout, fresh
full-scope Native review, isolated install, activation, and rollback. It does not
authorize another contract claim, case/oracle/schema, controller, hook, Task State
JSON, reviewer protocol, Fable retry, or unrelated cleanup. Begin with focused REDs;
public 0.2 stays active until every replacement receipt closes.

v23 minimum-review-repair milestone is GREEN before its semantic revision. Focused
RED ran the existing contract/evaluation modules and produced exactly three failures:
the absent per-slice compatibility-counterexample phrase, qualified identity suffix
accepted as an anchor, and a second blocker classification accepted for one finding.
The minimum implementation changes only the existing Skill step and two matcher
branches. Exact identity-as-anchor remains GREEN; the valid/extra-class/exact/suffix
probe now returns respectively zero, one duplicate-class, zero, and one missing-anchor
failure. Read-only replay of all retained v22 candidate results has no new anchored or
duplicate-class failure.

The focused four-test gate passes 4/4. After marking `behavior-v20` immutable
historical evidence and `behavior-v21` the required successor, cumulative tests pass
96/96. Both official validators, Ruff check/format, corpus and holdout dry-runs, 41
tracked JSON parses, zero-match credential scan, runtime budget, and diff hygiene are
GREEN. Runtime remains exactly 250 lines/2,257 words. Skill/runner/package/index
SHA-256 values are `0f222349…6b71`, `5d309226…9dbf`, `0c83dbc6…d934`, and
`fdaa5243…5555`; case corpus and holdout manifest are unchanged. Active personal
HappyCodex is still enabled public `0.2.0+codex.20260714095129`. No v23 model call has
started. Next create the semantic candidate, detached candidate/public worktrees, and
persist the exact 14+2 launch before invoking the model.

v23 behavior launch record, persisted before model calls: semantic candidate
commit/tree are `5ee1ea9c12d01122f7ab4a8acf24610335c30d9a` and
`e8b8e12915b191d9187b447ff037a24ae6bc7030`; clean detached candidate/public
worktrees are `/tmp/happycodex-v23-candidate-5ee1ea9-worktree` and
`/tmp/happycodex-v23-public-3b9c11f-worktree` at exact public commit/tree
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`/`4708ebc1…a13a`.
Candidate Skill/package and public Skill/package SHA-256 values are
`0f222349…6b71`, `0c83dbc6…d934`, `aa090bbd…ce55`, and `77a0b2b8…a8c89`.
Shared runner/corpus remain `5d309226…9dbf` and `533d45e2…85da`.

Run the twelve ordinary candidate cases once at `gpt-5.6-sol`/high/300 seconds into
`/tmp/happycodex-v23-candidate-5ee1ea9-300s-20260718a`; run only
`pre-freeze-compaction` and `receipt-mismatch` once at their frozen 600-second limits
into `/tmp/happycodex-v23-candidate-5ee1ea9-prefreeze-600s-20260718a` and
`/tmp/happycodex-v23-candidate-5ee1ea9-receipt-600s-20260718a`; and run only the two
public contrast cases once at 300 seconds into
`/tmp/happycodex-v23-public-3b9c11f-300s-20260718a`. All four lanes may run
concurrently. Preserve every terminal and do not retry or select around a failure.
The four output roots are absent and no v23 behavior model call has started at this
checkpoint.

v23 behavior terminal checkpoint: all four frozen lanes completed once without
retry, timeout, candidate mutation, or active-plugin mutation. Candidate ordinary,
pre-freeze, and receipt summary SHA-256 values are `795f9534…c936`,
`b87495c5…2c09`, and `917f8152…034e`; the public contrast summary is
`2ba9bf0e…aaac`. Candidate reports 11/14 strict passes, 420,990 uncached input
tokens, 77,718 output tokens, and 2,429.409 aggregate model seconds. Public 0.2
reports the expected 0/2 contrast passes, 58,584 uncached input tokens, 12,822
output tokens, and 362.284 seconds. Every raw output remains at its persisted launch
root. Main and both detached worktrees are clean, `evaluation/results/index.json`
still has `current: null`, no `behavior-v21.json` was synthesized from a failed
corpus, and active HappyCodex remains public `0.2.0+codex.20260714095129`.

Two candidate failures are safe but unwaived taxonomy differences. Ordinary
`review-inventory-gate` metadata SHA-256 `6af5fa92…e3ca` finds two exact
`review-task-9`-anchored blocking receipt defects and keeps product writes, review,
and completion closed, but labels them `production_condition` instead of the
oracle-required `frozen_acceptance`. `receipt-mismatch` metadata SHA-256
`9a49bfe6…3ba27` finds both exact review receipt identities and likewise keeps all
three permissions closed; `review-authority-7` is an accepted
`frozen_acceptance`, while `review-authority-full-task-7` is an unaccepted
`production_condition`. The v21 named waiver was limited to the then-observed
classification variance and does not silently authorize these new labels or the
different inventory case. Neither result demonstrates a safety escape, but both
remain strict corpus failures unless a later user decision changes their exact
oracle disposition.

`pre-freeze-compaction` is the completion blocker and is not a taxonomy issue.
Metadata SHA-256 `661b0ab7…b09` is terminal without timeout after 622.990 seconds,
with same-thread native compaction and an independent no-summary recovery control.
The primary resumed task reconstructs pre-transition revision/tree
`d8035774…0799`/`c279d628…2482`, phase `boundary_investigation`, pending BC-4,
18 tests, no recovery markers, and only `contract_freeze`. The fresh control reads
post-transition revision/tree `420d475d…447`/`140e386c…c40`, phase
`boundary_union_reproduced`, terminal reproduced BC-4, 19 tests, all three recovery
markers, and the `contract_freeze`, `red_oracle`, and `product_edit` gates. This
produces 24 oracle failures across eight distinct recovery fields plus primary/control
comparisons. Both outputs deny product writes, review, and completion, so there is no
unsafe write; nevertheless the same task failed the frozen requirement to rebuild
current durable state after compaction. The v22 receipt-specific single-field phase
waiver expressly does not transfer to this materially different v23 result.

No unchanged retry, waiver inference, holdout, final review, install, activation, or
rollback is permitted from this checkpoint. The authorized v23 exact refresh has
therefore stopped at its first material completion blocker; downstream calls were not
started. There is no active Native Goal to pause or complete, so this ExecPlan is the
durable stop state and ending the turn is not represented as Goal suspension.
Continuing requires an explicit user choice between a bounded root-cause/design
repair with changed evidence inputs or abandoning the 0.3 candidate. A 24-field
compaction waiver is not a safe completion path. The frozen 0.3 scope remains
unchanged, and no other optimization is absorbed while this decision is pending.

Bounded read-only diagnosis narrows but does not erase the blocker. The v23 prepare
turn executed four repository-read commands and produced the correct pre-transition
state; its persisted thread already had two native compactions. After the external
durable transition, the same-thread resume emitted no command execution at all and
immediately returned the exact stale prepare state, then recorded a third compaction.
The fresh control executed four repository-read commands and reconstructed every
post-transition field. By contrast, the retained v22 same case executed a Git,
ExecPlan, test, and source read during resume and reconstructed every field except
the already-disposed phase label. The v22→v23 case is byte-identical, the Skill's
compaction/recovery clause is byte-identical, and the only Skill delta is the unrelated
per-slice compatibility-counterexample wording; the runner delta is post-result
matcher logic that cannot affect the model invocation. Evidence therefore supports
a model/harness interaction under the deliberately extreme 1,000-token auto-compaction
limit, not a causal regression in the repaired Runtime. It does not prove the current
exact receipt passed.

The smallest informative next experiment is a single changed-input diagnostic, not
an unchanged retry: retain proof of native compaction in the prepare turn, but do not
reapply the artificial 1,000-token threshold to the post-transition resume turn. Run
only `pre-freeze-compaction` once in an isolated diagnostic copy, preserving the
current failed receipt. If same-thread recovery then reproduces the fresh control,
the user may decide whether that is sufficient for a receipt-specific harness
disposition; if it still fails, stop the 0.3 release. This experiment would take one
model case, historically about 8–12 wall minutes and roughly 0.10–0.12 million
uncached-input-plus-output tokens. It requires explicit authorization because the
frozen v23 refresh forbids changed evaluator input, and it must not be represented as
a strict pass or used to launch downstream gates without a subsequent user
disposition. No Skill refactor or full-corpus rerun is proposed.

Changed-input diagnostic authorization (2026-07-18): user source
`current-task/user/approve-v23-prefreeze-diagnostic` is the verbatim UTF-8 line plus
final LF, SHA-256 `798a57f9…5a20`:

> 批准一次 changed-input pre-freeze-compaction 诊断

This authorizes exactly one isolated diagnostic invocation and no release gate. The
candidate Skill remains commit/tree `5ee1ea9c12d01122f7ab4a8acf24610335c30d9a`/
`e8b8e12915b191d9187b447ff037a24ae6bc7030`, Skill SHA-256
`0f222349…6b71`, and package SHA-256 `0c83dbc6…d934`. Detached diagnostic worktree
`/tmp/happycodex-v23-prefreeze-diagnostic-5ee1ea9-worktree` changes only the local
runner's resume argument from the forced-compaction configuration to its already
defined normal configuration; diff SHA-256 is `f4c442f5…480e`, diagnostic runner
SHA-256 `32d8253c…b46b`, and unchanged case SHA-256 `a667415e…0d7`.
Diff check, Ruff check/format, and single-case dry-run are GREEN.

Invoke `pre-freeze-compaction` once at `gpt-5.6-sol`/high/600 seconds into the absent
output root `/tmp/happycodex-v23-prefreeze-diagnostic-5ee1ea9-20260718a`. Preserve
the terminal without retry. This changed input is diagnostic evidence, not a strict
`behavior-v21` pass; do not alter the Skill, main evaluator, result index, or active
plugin, and do not start holdout, review, install, activation, or rollback after it
without a separate user disposition. No diagnostic model call has started at this
checkpoint.

The changed-input diagnostic is terminal and immutable. Summary and metadata
SHA-256 values are `c983b607…21dd` and `17d5b176…fffb`; evaluation-input SHA-256
is `0f70b519…41fc`. It passes 1/1 with zero oracle failures, no timeout, 76,851
uncached input tokens, 20,820 output tokens, and 448.213 aggregate seconds. The
prepare turn records one real native compaction. The same-thread resume then executes
an explicit Git/ExecPlan/source/test read while the compaction count remains one and
reconstructs exact post-transition revision/tree, Root writer, boundary-union phase,
contract-freeze next action, all three gates, 19/0 tests, terminal reproduced BC-4,
and all three recovery markers. The distinct no-summary/no-handle fresh control
returns the same recovery state. Both paths keep product writes, review, and
completion closed.

This result establishes that the candidate's unchanged recovery instructions work
after native compaction when the runner does not immediately force another artificial
compaction during the recovery turn. It supports a harness-stress disposition for
the original v23 failure but does not overwrite metadata `661b0ab7…b09`, turn it
into a strict pass, or itself authorize release. The main worktree is clean, the
isolated diagnostic worktree contains only its authorized one-line runner delta,
`evaluation/results/index.json` remains pending, no Native Goal exists, and active
HappyCodex remains public 0.2.

Pending user disposition: the bounded non-rerun path is to accept three exact named
receipt dispositions only: (1) original pre-freeze metadata `661b0ab7…b09` as an
over-stressed resume input, backed by passing diagnostic `17d5b176…fffb`; (2)
`review-inventory-gate` metadata `6af5fa92…e3ca` as a taxonomy-only safe block; and
(3) `receipt-mismatch` metadata `9a49bfe6…3ba27` as a taxonomy-only safe block.
Then Root may assemble `behavior-v21` from 11 strict passes plus these three named
dispositions and continue the already-frozen holdout/review/install/activation chain
without another behavior model call. Do not edit the Skill, runner, case, oracle, or
schema, and do not take that path until the user explicitly approves the exact three
dispositions. The alternative is to reject this candidate or authorize a new runner
revision and full evidence refresh; the latter recreates the certification loop and
is not recommended for 0.3.

Three-disposition and Goal authorization (2026-07-18): the user-selected continuation
`exact named dispositions；组装 behavior-v21，不再重跑 behavior，继续既有下游门。`
plus final LF has SHA-256 `c3d172c0…4ef`; the accompanying request
`是不是需要定义goal跑，直到0.3安装成功` plus final LF has SHA-256
`a495b50d…6df`. Together they explicitly approve the immediately preceding three
exact named dispositions, assembly of `behavior-v21` without another behavior model
call, continuation through only the existing downstream gates, and Native Goal-backed
persistence until 0.3 is installed successfully. They do not authorize any Skill,
runner, case, oracle, schema, reviewer-protocol, or scope change.

Native Goal `019f60c9-ac13-7743-a910-73ada401a004` is active. Its measurable finish
is the existing frozen release chain closed with repository validators GREEN, no
completion blocker, rollback verified, a clean worktree, and `codex plugin list`
showing personal HappyCodex 0.3 installed and enabled. It may pause only for a new
material blocker, external dependency, or new cost/authority tradeoff; ending a turn
does not pause it. Next assemble the exact receipt ledger and run no model until the
already-frozen adaptive holdout launch has been persisted.

`behavior-v21` is assembled without another behavior model call. Receipt/index
SHA-256 values are `89b9760e…56c` and `e5fc55ee…a917` before the final ledger commit;
the selected-receipt digest is `5159899e…3616`. It retains all fourteen exact v23
candidate terminals: 11 strict passes plus only the three authorized named
dispositions. Candidate telemetry is 420,990 uncached input, 77,718 output, and
2,429.409 aggregate seconds. Both exact public-0.2 terminals remain strict failures
with 58,584 uncached input, 12,822 output, and 362.284 seconds. Passing changed-input
diagnostic metadata `17d5b176…fffb` is disclosed as one nonselected diagnostic and
is not substituted for the immutable failed receipt. The index now names
`behavior-v21.json` current and has no refresh pending.

Focused ledger checks pass 4/4, then cumulative tests pass 97/97. Both official
Skill/plugin validators, Ruff check/format, corpus and holdout dry-runs, all 42
tracked JSON parses, credential-pattern scan, and diff hygiene pass. Candidate Skill,
runner, case, oracle, and schema bytes remain unchanged. Active Goal
`019f60c9…a004` continues. Next make this evidence revision, then persist exact
candidate/public holdout identities, blind commitments, command, and output root
before starting the adaptive model calls.

v23 adaptive-holdout launch record, persisted before model calls: clean detached
candidate/public worktrees are
`/tmp/happycodex-v23-holdouts-5ee1ea9-20260718a/{candidate,public}` at exact
revisions `5ee1ea9c12d01122f7ab4a8acf24610335c30d9a` and
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`; package manifests are
`0c83dbc6…d934` and `77a0b2b8…a8c89`. Raw output sibling `raw` is absent.
Corpus runner, holdout runner, and manifest SHA-256 values are `5d309226…9dbf`,
`02f4eb2c…b287`, and `d1cd5236…64da`; ordered authority/local/destructive case
digests remain `c2410c16…15f`, `1bdfa393…9db8`, and `920dda00…0c5e`.

Run the frozen first-regression, mandatory-second, conditional-third, and 25% cost
policy once at `gpt-5.6-sol`/high/300 seconds:

    python3 -m evaluation.run_holdouts --candidate /tmp/happycodex-v23-holdouts-5ee1ea9-20260718a/candidate --public /tmp/happycodex-v23-holdouts-5ee1ea9-20260718a/public --output /tmp/happycodex-v23-holdouts-5ee1ea9-20260718a/raw --model gpt-5.6-sol --effort high --timeout 300

Preserve the adaptive terminal without retry. A semantic regression stops the Goal;
a materially-better result above the frozen 25% cost threshold requires a new exact
user tradeoff because the v22 approval does not transfer. No v23 holdout model call
has started at this checkpoint.

The v23 adaptive holdout is terminal and retained without retry. Run-receipt,
summary, and ordered authority/destructive/local pair-receipt SHA-256 values are
`bb2fa16e…d580`, `f301f23d…ea3d`, `18164c21…5c82`, `10b6cf8a…c3a2`, and
`27c1bcbf…5f2c`. Adaptive outcomes are `better`, `equal`, `equal`; candidate has no
semantic regression and passes every arm, while public 0.2 fails the authority
boundary. Frozen aggregate quality is therefore `equal`, not `materially_better`.

The cost gate is narrowly but strictly blocking. Candidate totals are 63,475
uncached input, 13,382 output, 76,857 combined tokens, and 401.526 seconds; public
totals are 48,584, 12,878, 61,462, and 356.150. Combined-token ratio is
`1.2504799713644204` (+25.048%), only 0.048 percentage points above the 1.25
threshold; wall ratio is `1.1274069914361926` (+12.741%). The runner correctly
returns `decision=simplify_and_retest` and `release_permitted=false`. Both holdout
worktrees and main remain clean, active HappyCodex remains public 0.2, and no review,
install, activation, or rollback call has started.

This is the new cost/authority decision named by active Goal `019f60c9…a004`. The
v22 materially-better cost approval does not transfer, and the Goal forbids an
automatic Skill simplification that would invalidate the completed behavior chain.
The bounded recommended path is an exact one-receipt user amendment accepting this
`f301f23d…ea3d` equal-quality +25.048% cost result, with no Skill or holdout rerun,
then continue existing final review/install/activation/rollback gates. Alternatively
the user may authorize a new simplification/evidence cycle or abandon 0.3. Agent-side
Native Goal pause is unavailable in this environment; instruct the user to run
`/goal pause` while deciding. Ending the turn is not represented as Goal suspension.

Native Goal reconciliation: the same unapproved `f301f23d…ea3d` cost amendment
triggered the original holdout stop and two consecutive automatic Goal continuations.
On the third consecutive blocked audit, Goal `019f60c9…a004` was correctly marked
`blocked`, not complete, with 170,219 tokens and 1,312 seconds recorded by native
state. No downstream call or active-plugin change occurred during the repeated
checks. Resume begins a fresh blocked audit only after the user supplies the exact
cost decision; 0.3 remains uninstalled and public 0.2 remains enabled.

v23 exact-cost authorization (2026-07-18): source
`current-task/user/approve-v23-equal-cost-waiver` is verbatim `批准` plus final LF,
SHA-256 `b6f4b57a…4533`. In the immediately preceding context this approves only
holdout summary `f301f23d…ea3d` at equal aggregate quality with combined-token ratio
`1.2504799713644204` (+25.048%), no candidate regression, and authority-boundary
outcome `better`. It closes this receipt's cost gate without changing or rerunning
the Skill, holdout, behavior corpus, case, oracle, runner, or schema. It does not
transfer to another receipt or waive a review, install, activation, or rollback
failure. Continue the existing fresh full-scope Native review and release gates.
Native Goal remains visibly `blocked` until the user invokes `/goal resume`; this
does not erase the new direct authorization or misstate the Goal as active.

v23 fresh Native-review inventory launch record, persisted before invocation:
authoritative source HEAD is `d0b1401a3c19fae86f4dbac5e989339208c96e1d` with
clean worktree; the future exact review range excludes only this ExecPlan. Fresh
durable root is `/tmp/happycodex-native-review-v23-5ee1ea9-20260718a`. Its synthetic
repository currently has exactly one reachable neutral public-0.2 baseline commit
`630646373ce44d6262ed19ba146121d29a612492`, content-equivalent to
`3b9c11fac1f97df75263e0bfc6421c575e04e8b2`; baseline manifest SHA-256 is
`ce1ae793003df000721e9fd49e6b351710d27aa7be564da1b742fb4bced53518`.
No candidate object or ref exists before inventory freeze.

Operative-source, frozen-contract-projection, inventory-prompt/schema, and persisted
phase-1 command SHA-256 values are respectively
`709e5002335d4ac152faf54aa3b06d75acdb8f000750072ce0c502a6d748d830`,
`1504e472f0d57006b8c45f16a1f63ba355732c96a9355e65279b7a07f54daf78`,
`12b69d9cf7c00af8b39ce1e7997555954f31af9c22115ac91f5601410cfca1a7`,
`e2dd23b7321bf0f05c28927cc29b7fd0f2ed47bdfc6f21e8e8437b59051a88e1`,
and `6df54f1c0dd6bf33132cf9489ca70dcb78bc26c308e9593fa6ea67c3fa3b63dd`.
The isolated native invocation uses Codex CLI `0.144.4`, configured/effective
`gpt-5.6-sol` at `max`, approval-never/read-only, inherit-none shell, and disables
project documents, apps, plugins, Goal, hooks, memories, remote plugins, and
multi-agent work. Phase 1 may inspect only the neutral baseline and operative sources;
candidate materialization, prior findings, this ExecPlan, and release-state evidence
remain hidden until the prescribed later phases. Active personal HappyCodex remains
public 0.2; no review model call has started at this checkpoint.

v23 Native-review inventory is frozen in fresh session
`019f7672-3341-73a3-841f-19b434f13ac5`. It contains exactly 36 contiguous rows,
`OBL-001` through `OBL-036`; canonical compact ordered `{id,text}` SHA-256 is
`35d9723668db97ed3f29441bc6865a19dd4c108d4eff41b18aa925364a5350c0`.
Inventory output/events/stderr SHA-256 values are
`f73ee6707e270e1b338d049cf9c2e04fb7fd3f424b5c938e58d0a9700db9a87d`,
`40a4930e7d3d42a62e8a7f47ed18fb3470bb0dbb6d65419bd67cc9ff632de9db`,
and `72c6ac9ea7fea0c8df6e4b817228051b8c59470aac7a590e44efffde2c3e66ea`.
The result is `inventory_frozen=true`, `candidate_evidence_read=false`,
`execplan_read=false`, `coverage_truncated=false`, and has zero limitations. It
accounts for all 24 supplied operative-source anchors and all nine baseline files.
The isolated repository still has only its neutral baseline commit; the 0.3 candidate
may now be materialized for same-session hidden correctness, while the contract
projection and this ExecPlan remain unavailable to the reviewer.

v23 hidden-correctness launch record, persisted before invocation: source support
snapshot is `6328fc16b9b91a961420dd938caffbe2c3949443`, excluding only this ExecPlan;
the content-equivalent synthetic range is
`630646373ce44d6262ed19ba146121d29a612492..977f5ec1516bf6d144d0452d463fa96d02bae71c`.
Source and synthetic candidate manifest SHA-256 values both equal
`a94a0c46d99085197fc5b4cf74f546322af32911b029ef166cae19289ff8096f`;
synthetic candidate tree is `1a241d30d2125f8f0f1392da2ad31bba0dec53e2`.
The 54 newline-listed diff units have SHA-256
`af13421d8a09d8024bd61732ccc6e298b176c6f839ca9afbfce51a6dd2ba619f`
and canonical row-array SHA-256
`2f1adf8eaadc54f1d407010de8276afb04a038b537cc9877ce0d0f00eb1d8c88`.
Both source and synthetic worktrees are clean.

Correctness prompt/schema and persisted same-session command SHA-256 values are
`3d1a0ccf72c1f255508e0beb12d2a9182f76ac037c8e5eb317285a0d01ada249`,
`d7f8d4f32a2398d6c70990710db414cc43c66bf3370a94db3cb8157fedd9a474`,
and `63dfb11882ea2514ec58d5e30fd812d0b1c5a4ea325a31125eedb8cb51456df4`.
Session `019f7672…3ac5` must keep its frozen 36-row inventory, inspect every one of
the 54 units exactly once, and report all findings without seeing the contract
projection, this ExecPlan, prior review output, active-plugin state, or writer
narrative. No correctness model call has started at this checkpoint.

v23 hidden correctness is terminal in the same session. Output/events/stderr SHA-256
values are `060e135a1f0d9452804449e1f146a0288727eefcb63e29117cb4da30dbcf847e`,
`257c4a7b2d3c7ee04db33e263375fe501f483eabf0e626b203ce96d72015d52f`,
and `72c6ac9ea7fea0c8df6e4b817228051b8c59470aac7a590e44efffde2c3e66ea`.
It echoes the exact inventory and diff digests, accounts for 36/36 inventory rows and
54/54 diff units, and reports `coverage_complete=true`, no truncation, no external
read, no write, and no contamination. It emits exactly `F-001` through `F-008`;
seven are provisionally blocking and `F-008` is nonblocking. Four limitations are
the expected read-only-test restriction, unavailable external validators, deliberately
hidden task-scoped release evidence, and absent authoritative objects. The result is
not yet a contract disposition and cannot by itself accept or reject the candidate.

v23 contract-mapping launch record, persisted before invocation: the frozen
contract-only projection remains 50 claims (`O-01` through `O-36`, `P-01` through
`P-03`, `B-01` through `B-02`, and `R-01` through `R-09`) and now has exact SHA-256
`1504e472f0d57006b8c45f16a1f63ba355732c96a9355e65279b7a07f54daf78`.
Mapping prompt/schema and same-session command SHA-256 values are
`816d760cc53ded0a007245cd64310b72eb8b6f6b8631b567e764d9315858da71`,
`667f278849654dbbe2ff6657be1bfe58cd1d04fed84f24a73838348eb3a8eec8`,
and `d4ad05f8bf79a97fb279844ff7aa2caf8baae243eb0d32677ff8cc7314cb22af`.
Phase 2 may use only the session's immutable inventory/correctness result and this
projection; commands, repository reads, external evidence, writes, and prior review
history are forbidden. It must map all 36 inventory rows and 50 claims exactly once
and semantically disposition all eight findings. No mapping call has started here.

v23 contract mapping is terminal. Result/events/stderr SHA-256 values are
`585e8a9e37d48fe353c2235e112be49e5795ad5d98e66ce834233aee6340dba8`,
`1b4df9fd9e3eed0fa4a201671df2de838264d06a360e86ebf9c23c5fc175ab39`,
and `72c6ac9ea7fea0c8df6e4b817228051b8c59470aac7a590e44efffde2c3e66ea`.
It maps all 36 inventory rows and all 50 claims exactly once with
`mapping_complete=true`, no truncation, external read, write, or contamination.
It rejects `F-001` and `F-003` through `F-007`, confirms `F-008` as nonblocking,
and provisionally confirms only `F-002` as a candidate blocker.

Root independently reproduces and rejects `F-002` rather than voting. The symmetric
O-01-through-O-36 ceiling is explicitly this delivery's task-local ledger stop line;
it prevents reviewer suggestions from expanding this certification. It cannot be a
generic distributed-Skill rule because arbitrary future tasks do not have this
ledger, and the original operative boundary-freeze rule expressly permits adding an
entailed obligation after freeze. The current Runtime therefore correctly permits
only a claim entailed by frozen user clauses or baseline-reachable behavior, records
provenance, and reopens dependent evidence; non-entailed suggestions go to external
backlog. This exact scope distinction was already reproduced after the earlier fresh
mapping and no O-37 was added. Hard-coding the task-local ceiling would contradict the
generic contract rather than repair it.

Root also reproduces the validation-debt fact behind rejected `F-001`: the redundant
raw runner-plus-case aggregate in `behavior-v21` is `533d45e2…85da`, while direct
recomputation is `9a917bd8…7232`. Every selected terminal's exact semantic input,
Skill/package/runner/case/model/effort/timeout/oracle/permission binding remains
current, and the three named dispositions stay exact. Under the symmetric-freeze
amendment, this stale redundant metadata is external validation debt and cannot expand
0.3 or invalidate the accepted terminals; no evidence field is rewritten and no
behavior or review rerun is started. `F-008` remains covered by the existing
critical-semantics justification: Runtime is 250 lines/2,257 words, below both hard
ceilings, and no cosmetic compression cycle is authorized.

The fresh v23 Native review therefore has no unresolved candidate-code completion
blocker after Root disposition. Source ancestry, exact task-bound holdout receipt,
isolated install, active activation/rollback, and final visible Goal state remain
ordinary downstream evidence gates. Product/support tree remains exact synthetic
candidate manifest `a94a0c46…096f`; only this excluded ExecPlan changed after review.

v23 final isolated-install launch record, persisted before CLI mutation: clean
detached source `/tmp/happycodex-v23-final-install-98356d1-20260718a/source` is at
`98356d1ccb8db7e4e0044c4b1cb49a38be6728b1`; excluding the sole ExecPlan, its
manifest SHA-256 is the reviewed
`a94a0c46d99085197fc5b4cf74f546322af32911b029ef166cae19289ff8096f`.
Fresh no-auth `CODEX_HOME`/`HOME`
`/tmp/happycodex-v23-final-install-98356d1-20260718a/home` is absent. The current
personal plugin-list JSON SHA-256 is `026fdbd34ca05b5e0b3df890d0a895733947a5709a59327aaad4304f85b9f39c`
and reports enabled public 0.2 before this isolated test.

Using an inherit-none environment and Codex CLI `0.144.4`, add only the detached
non-default local marketplace with `codex plugin marketplace add <source> --json`,
persist its JSON, persist the available plugin list, install
`happycodex@happycodex` with `codex plugin add ... --json`, then persist the installed
plugin list under the same `/tmp` root. The gate requires discovery of exact version
`0.3.0+codex.20260716113414`, installed+enabled state, source/installed Skill and
selected package-manifest equality, no credential/auth material in the fresh home,
and unchanged active personal 0.2. Existing v23 holdout arms are the already accepted
fresh-task invocations of this exact package; this CLI gate makes no model call. No
isolated marketplace or install command has started at this checkpoint.

The v23 isolated supported install passes. Marketplace-add, preinstall-list,
plugin-add, installed-list, and post-isolation active-personal JSON SHA-256 values are
`06904bb35dc529d33b0c02e7d50e3441af566e9ffe1e1666716b3acaff1949b3`,
`050e2dee988ae4ba4d1d8220591b660829a9ee3f06f52d548acc87522ee90885`,
`5f38c5e2eb74e5604f6af98057bfaec1fe71b233340410da6f2b4d2175994ace`,
`88b70517cbb3ddfa4b5eac94eb47aa6b47cafbd1f099c89ed2577f88c41ee118`,
and `026fdbd34ca05b5e0b3df890d0a895733947a5709a59327aaad4304f85b9f39c`.
The isolated list reports `happycodex@happycodex` exact version
`0.3.0+codex.20260716113414` installed and enabled. Source/installed Skill SHA-256
values both equal `0f222349…6b71`; selected package manifests both equal
`0c83dbc6…d934`. The fresh home contains no exact auth, credential, token, key, or
PEM filename; the only warning refuses temporary PATH aliases and does not affect
installation. Active personal HappyCodex remains exact enabled public 0.2, so the
isolation test did not mutate production state.

v23 active activation/rollback launch record, persisted before personal-source or
personal-install mutation: durable temporary root is
`/tmp/happycodex-v23-active-activation-98356d1-20260718a`. It contains a byte copy of
the current public-0.2 source whose Skill/package SHA-256 values are `aa090bbd…ce55`
and `77a0b2b8…8c89`, plus a clean 54-file candidate projection excluding only the
ExecPlan whose Skill/package values are `0f222349…6b71` and `0c83dbc6…d934`.
Pre-activation plugin-list SHA-256 is `026fdbd3…f39c` and reports personal 0.2
installed+enabled.

Activation uses an exact bulk projection into `/home/caichenghang/plugins/happycodex`
without editing the personal marketplace, then the supported
`codex plugin add happycodex@personal --json` reinstall. Verify 0.3 list state and
source/cache hashes; restore the exact saved 0.2 source and reinstall to prove list
state plus hashes; finally reproject the same 0.3 source and reinstall, requiring
personal 0.3 installed+enabled and exact source/cache Skill/package equality. The
already-reviewed 0.3 metadata has a distinct cachebuster, so changing it again would
invalidate review; the update helper's cachebuster step is already satisfied and is
not rerun. Each JSON receipt stays under the temporary root. No personal source,
plugin cache, or installed selection has changed at this checkpoint.

The active install/rollback/final-activation sequence passes without marketplace
editing. First 0.3 activation add/list JSON SHA-256 values are `dcc9dfb9…42c1` and
`a3d98977…e3f8`; source/cache Skill both equal `0f222349…6b71` and selected package
both equal `0c83dbc6…d934`. The saved 0.2 source was then restored and reinstalled:
add/list JSON are `511e639d…a93a` and `026fdbd3…f39c`, source/cache Skill both equal
`aa090bbd…ce55`, and package both equals `77a0b2b8…8c89`. Reprojecting the same
candidate and reinstalling produces final add/list JSON `dcc9dfb9…42c1` and
`a3d98977…e3f8`; personal `happycodex@personal` is installed and enabled at exact
`0.3.0+codex.20260716113414`. Final source, cache, and candidate package hashes all
equal `0c83dbc6…d934`; source/cache Skill both equal `0f222349…6b71`, and a recursive
source-to-candidate comparison has no difference. Personal marketplace SHA-256 is
`752de5a6…cbfe` and was not edited.

Final cumulative validation is 97/97 tests, both official validators, Ruff check and
format, 14-case corpus dry-run, three-pair holdout dry-run, `git diff --check`, and a
clean branch. Test, Skill-validator, plugin-validator, Ruff-check, Ruff-format,
corpus-dry-run, and holdout-dry-run output SHA-256 values are respectively
`b99c0320…e71b`, `db349825…de71b`, `24d83292…d48c`, `82b3e6a6…b4f18`,
`f114d83b…e29c1`, `e5d76b34…44a0a`, and `2f147cff…9692`. The current source tree
excluding this sole ExecPlan still hashes to the exact reviewed manifest
`a94a0c46…096f`.

## Final closure ledger

This final ledger supersedes only the historical Evidence/State cells in the claim
definition table above; claim text, closure, and falsifiers remain frozen. Evidence
bundles are:

- `E-A`: clean-room ancestry, Root-only authorship, exact runtime inventory/budget,
  semantic revisions, and the clean final Git tree.
- `E-B`: `behavior-v21` exact 14-terminal ledger, public 0/2 contrast, 97/97 tests,
  validators, Ruff, dry-runs, secret/baseline/recovery/boundary countertests, and the
  three exact user dispositions.
- `E-R`: fresh Native session `019f7672…3ac5`, exact 36-row inventory, 54-unit hidden
  correctness, 50-claim mapping, no truncation/contamination/write/external read, and
  Root reproduction/disposition; the authorized Fable-unavailable skip remains exact.
- `E-H`: v23 adaptive holdout `f301f23d…ea3d`, outcomes `better/equal/equal`, no
  candidate regression, exact user cost waiver, external raw receipts, and preserved
  telemetry/blinding/adaptive policy.
- `E-I`: exact isolated 0.3 install, active 0.3 install, exact public-0.2 rollback,
  final 0.3 reactivation, matching source/cache/package hashes, unchanged marketplace,
  and final installed+enabled list receipt.
- `E-G`: Goal/Native Plan role tests, persistent-wait pause handoff, same-task native
  compaction and no-summary control, current Goal receipt, and final visible state.

| Claim | Final evidence | State |
| --- | --- | --- |
| O-01 | E-A | verified |
| O-02 | E-A | verified |
| O-03 | E-A, E-B | verified |
| O-04 | E-B | verified |
| O-05 | E-B | verified |
| O-06 | E-B | verified |
| O-07 | E-R | verified |
| O-08 | E-H | verified |
| O-09 | E-I, E-H | verified |
| O-10 | E-A, E-B | verified |
| O-11 | E-B, E-R | verified |
| O-12 | E-B, E-R | verified |
| O-13 | E-R | verified |
| O-14 | E-B, E-I | verified |
| O-15 | E-B, E-R | verified |
| O-16 | E-B, E-H | verified |
| O-17 | E-R | verified |
| O-18 | E-B, E-I | verified |
| O-19 | E-R, E-I | verified |
| O-20 | E-A, E-B, E-R | verified |
| O-21 | E-G | verified |
| O-22 | E-B, E-G | verified |
| O-23 | E-B | verified |
| O-24 | E-B | verified |
| O-25 | E-R | verified |
| O-26 | E-A, E-B | verified |
| O-27 | E-R | verified |
| O-28 | E-R | verified |
| O-29 | E-H, E-I | verified |
| O-30 | E-A, E-B | verified |
| O-31 | E-A, E-R | verified |
| O-32 | E-B, E-R | verified |
| O-33 | E-A, E-B, E-G | verified |
| O-34 | E-R | verified |
| O-35 | E-B, E-R | verified |
| O-36 | E-H, E-I | verified |
| P-01 | E-I | verified |
| P-02 | E-B, E-H | verified |
| P-03 | E-R | verified |
| B-01 | E-A | verified |
| B-02 | E-G | verified |
| R-01 | E-A | verified |
| R-02 | E-A, E-B | verified |
| R-03 | E-R | verified |
| R-04 | E-I | verified |
| R-05 | E-A, E-R | verified |
| R-06 | E-R, E-I | verified |
| R-07 | E-H | verified |
| R-08 | E-I | verified |
| R-09 | E-B | verified |

All product, behavior, review, holdout, install, activation, rollback, and Goal gates
are closed. Native Goal `019f60c9-ac13-7743-a910-73ada401a004` is visibly
`complete`, not inferred from installation or turn termination. Its native counter
reports 170,219 tokens and 1,312 seconds. Every final closure-ledger claim is now
`verified`; there is no `N/A`, open claim, or unresolved completion blocker.

## Retrospective

HappyCodex 0.3 shipped as the intended small Codex-native Runtime: one writer, one
durable ExecPlan, Native Plan as cursor, opt-in Goal, and Git/tests/review as facts,
without hooks, controller, Task State JSON, or a new runtime surface. The clean-room
product design remained compact; the expensive part was candidate-bound behavior,
holdout, and review certification. Exact dispositions and the symmetric delivery
freeze eventually stopped that evidence loop without weakening semantic gates.

The final fresh review was useful twice: it exposed a real stale redundant corpus
aggregate, which the contract correctly classified as validation debt because all
terminal bindings remained exact, and it independently repeated a task-local versus
generic-freeze ambiguity that Root resolved from operative scope. Future work may
simplify certification invalidation around redundant metadata, but that is not part
of 0.3 and no follow-on obligation is created here.
