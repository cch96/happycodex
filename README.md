# HappyCodex

[English](README.en.md)

*Open-source skill and plugin for reliable long-running, high-risk engineering work in OpenAI Codex.*

HappyCodex 是面向 OpenAI Codex 长流程、高风险工程任务的开源可靠性工作流。它用仓库内的 ExecPlan 固化完成条件，由一个固定 Executor 执行受控写入，Root 负责决策、授权、复核与最终验证；它不替代 Codex 原生的 Plan、Git、测试或 review。

## 适合与不适合

### 适合

HappyCodex 适用于公共契约、跨系统变更、迁移、持久化、并发、破坏性或生产
操作、穷尽性声明、长期研究，以及可能跨越上下文压缩的工作。

### 不适合

边界清晰、风险较低的局部修改应继续使用原生 Plan、测试和 diff 流程。如果
范围或风险扩大，应在下一次产品写入前建立 ExecPlan。

<a id="install"></a>
## 安装

安装需要 Codex 支持插件市场。

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后请新建一个 Codex 任务，使其发现已安装的 Skill。

## 调用

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## 四阶段工作流

1. `working`：在仓库 ExecPlan 中冻结请求、Outcome、保留边界、角色、精确
   授权、义务、检查、效果与停止条件；实现一个已授权的修复波次，并运行真实
   路径检查。
2. `candidate_frozen`：清点所有归属内变更，证实各项义务，确认已接受的基线
   失败保持不变，并绑定源码、产品和配置身份。
3. `exact_final`：由一个全新、逻辑只读的评审者检查冻结源码、检查结果、义务与
   排除项。只有预先声明为必需时，才要求技术只读隔离；
   缺失可选 route/permission telemetry 本身不阻塞评审，但必须披露。Root 先
   根据冻结的受支持工作流边界对每个发现分类。只有一次由 Root 准入、获得显式
   授权、边界内且仍有已授权预算的修复，才会退回 `working`。修复后 Root 重新
   冻结 candidate，并只取得一次替代性的全新 Exact-final。重新冻结后，任何
   `in-envelope blocker` 或 `unknown` 都保持 open、truthful 且 blocking，Root
   在另一次产品写入、grant 或 review rerun 前返回用户。`envelope expansion`
   保持为已披露的 follow-up，除非另行授权，并且绝不触发或消耗自动修复。预算
   耗尽后，不允许自动产品写入、重新冻结或 review rerun；不存在循环。
4. `closed`：仅当义务、检查、评审、效果、回执、所有权以及任何由用户明确
   请求的 Goal 全部完成核对后才可关闭。最终完成结论由 Root 作出。

只有用户明确请求时，才会创建或修改 Goal。Goal 永远不会扩大权限，也不会
取代 ExecPlan 或验证。

## 0.7.2 能力比例准入

0.7.2 使用 capability-proportional admission，并保留以下请求路由矩阵：

| 逻辑角色 | 模型 | 推理强度 |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| 唯一 Executor | `gpt-5.6-sol` | `high` |
| 唯一全新 Exact-final | `gpt-5.6-sol` | `max` |

普通用户不选模式，也不输入继续口令。dispatch 前且读取实质输出前，Root 记录
角色、用途与后果、请求的 route/config/fork、输入身份与 prompt digest，以及
task/source/user 预先要求的保证。平台接受精确 spawn 请求与 host 认证的
child/run/result handle 始终必需；缺失 output identity 永远不是可降级项。

缺失可选 telemetry 时记录 `unverified`，只降低依赖它的保证或用途。缺失
effective name 只影响记录；缺失模型/强度时继续，除非已预先声明必须精确路由；
缺失 sandbox/approval 时继续，除非已预先声明必须技术隔离且无法独立证实。
暴露值不匹配，或预先声明的必需保证缺失时，必须停止。prompt/profile 的只读声明不
是技术隔离证明；full access 只有在预先要求只读技术隔离时才构成错配。
不得声称未验证的精确路由或技术隔离。

Root 先把问题拆成独立且会改变决策的轴。只有存在多个这种轴时，才可并行多个
Explorer。规范性并行规则仍是：For two or more qualifying independent
decision-changing axes, Root concurrently dispatches one native Explorer per
axis through the host's builtin `explorer` selector or an admitted namespaced
custom Explorer selector. Ordinary parallel tool calls are not Explorer
dispatches. 每个 Explorer 只回答一个有界问题。未验证路由或隔离的
Explorer/Challenger 输出只能提供 advisory leads；Root 必须从源码复现每个重要
事实后，才能让它影响 plan、grant 或 phase。Challenger 在行为计划冻结前工作。
Executor 写入仍受固定身份、精确 grant、source/prestate、paths/resources 与
allowed effects 约束，Root 依赖 Git、测试和 receipts，而不是 Executor 文字。
Exact-final 只可在全新空历史、中性 brief、candidate 不变时按可选 telemetry
未验证处理，且精确路由与硬隔离未被预先声明为必需、output identity 已绑定、
Root 已复现重要发现并披露未验证保证；必需硬隔离未经证实时 review 保持 open。
Root 先根据冻结的受支持工作流边界对每个发现分类。只有一次由 Root 准入、获得
显式授权、边界内且仍有已授权预算的修复，才会退回 `working`。修复后 Root
重新冻结 candidate，并只取得一次替代性的全新 Exact-final。重新冻结后，任何
`in-envelope blocker` 或 `unknown` 都保持 open、truthful 且 blocking，Root 在
另一次产品写入、grant 或 review rerun 前返回用户。`envelope expansion` 保持为
已披露的 follow-up，除非另行授权，并且绝不触发或消耗自动修复。预算耗尽后，
不允许自动产品写入、重新冻结或 review rerun；不存在循环。

## 包含与不包含

插件包含核心 Runtime 指引和资源声明辅助工具。HappyCodex 不是控制器、守护
进程、调度器、MCP server、自动授权系统或自动重试系统。

插件安装不打包、安装、激活或要求自定义代理。本机可选的
`happycodex_explorer`、`happycodex_challenger` 和
`happycodex_exact_final` profiles 只是严格/便利配置，不覆盖 builtin，也不是
插件能力保证。逻辑角色与平台 agent type/custom-agent name 必须分开记录；名称、
profile 和代理自述都不是有效路由证据。

在 full-access 父任务中，custom agent 的 `sandbox_mode = "read-only"` 可能被
live parent 覆盖，因此 profile 默认值和提示词都不是技术硬隔离。需要硬只读
隔离时，必须在 dispatch 前从 read-only 顶层或父环境启动，并在 receipt 到达
后核验实际 permissions，或独立绑定等价的 no-effect boundary；否则停止。未预先
要求硬隔离时，将缺失权限 telemetry 记录为 `unverified`，继续但不声称隔离。

## 0.7.3 评审停止线

0.7.3 明确 Exact-final 修复的准入与耗尽规则。Root 先根据冻结的受支持工作流
边界对每个发现分类。只有一次由 Root 准入、获得显式授权、边界内且仍有已授权
预算的修复，才会退回 `working`。修复后 Root 重新冻结 candidate，并只取得一次
替代性的全新 Exact-final。重新冻结后，任何 `in-envelope blocker` 或 `unknown`
都保持 open、truthful 且 blocking，Root 在另一次产品写入、grant 或 review
rerun 前返回用户。`envelope expansion` 保持为已披露的 follow-up，除非另行授权，
并且绝不触发或消耗自动修复。预算耗尽后，不允许自动产品写入、重新冻结或 review
rerun；不存在循环。0.7.3 保留 0.7.2 的 capability-proportional admission 契约。
在对应回执存在之前，不声称已经发布、release 或激活。

[完整发布历史与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
