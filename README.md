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
3. `exact_final`：由一个全新、隔离、只读的评审者检查冻结源码、检查结果、
   义务与排除项。任何产品变更都会退回 `working`，并要求重新评审。
4. `closed`：仅当义务、检查、评审、效果、回执、所有权以及任何由用户明确
   请求的 Goal 全部完成核对后才可关闭。最终完成结论由 Root 作出。

只有用户明确请求时，才会创建或修改 Goal。Goal 永远不会扩大权限，也不会
取代 ExecPlan 或验证。

## 0.7.1 角色路由

0.7.1 定义以下协议级路由矩阵：

| 逻辑角色 | 模型 | 推理强度 |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| 唯一 Executor | `gpt-5.6-sol` | `high` |
| 唯一全新 Exact-final | `gpt-5.6-sol` | `max` |

完整路由只在 host 支持精确 selector 和 runtime-issued metadata 时成立。
dispatch 前，Root 先核验自身为 `gpt-5.6-sol/max`，并确认 selector 能请求目标
角色、模型、推理强度和 `fork_turns = none` 或有界正整数。Root 的经认证
dispatch/tool receipt 绑定逻辑角色、所选 agent 请求、请求的模型/强度或 custom
配置 SHA、fork、输入 baseline/candidate 身份以及 prompt/brief digest；平台接受
spawn 即完成 dispatch receipt。portable builtin/default 路径显式 pin 模型与
强度；选择 namespaced custom agent 时，以其配置文件的模型与强度为准，并省略
冲突或重复的显式参数。

spawn 可以立即启动。runtime-issued session/turn metadata 提供实际
platform/custom 角色或名称（如可见）、effective 模型与强度、effective
sandbox/approval 以及 child/run/session 身份；不要求它重复 Root 已绑定的逻辑
角色、fork、输入身份或 prompt digest。Root 只有交叉绑定 dispatch receipt 与
runtime metadata 后才可 admission。此前 child 输出不可采纳：不得写入行为计划、
触发写授权、推进 phase 或充当 final verdict。缺少任一必需来源或发生错配时，
Root 立即 interrupt 仍在运行的 child、丢弃输出并 fail closed。

Root 先把问题拆成独立且会改变决策的轴。只有存在多个这种轴时，才可并行多个
Explorer。0.7.1 的规范性并行规则是：For two or more qualifying independent
decision-changing axes, Root concurrently dispatches one native Explorer per
axis through the host's builtin `explorer` selector or an admitted namespaced
custom Explorer selector. Ordinary parallel tool calls are not Explorer
dispatches. 每个 Explorer 只回答一个有界问题。Root 复现并合并证据，不投票。
Challenger 在行为计划冻结前工作；计划冻结后才由唯一 Executor 写入。候选冻结
后只启动一个空历史、使用中性 brief 的全新 Exact-final；任何修复都返回
`working`，重新冻结并重新评审。

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
后核验实际 sandbox 与 approval policy；未经核验的输出不可采纳。

## 0.7.1 要点

0.7.1 在既有四阶段与最小充分控制之上，为由 host 能力约束、receipt gate
控制且与插件打包解耦的角色路由契约加入多轴时强制使用 native Explorer 的规则；
这是源码候选说明，不代表已经发布或激活。

[完整发布历史与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
