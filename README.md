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

## 包含与不包含

插件包含核心 Runtime 指引和资源声明辅助工具。HappyCodex 不是控制器、守护
进程、调度器、MCP server、自动授权系统或自动重试系统。

HappyCodex 不附带模型矩阵或自定义代理配置。可用的模型与推理强度由用户和
Codex 配置选择；每位参与者实际使用的模型、推理强度与权限都会被记录。

## 0.6.6 要点

0.6.6 聚焦于受支持工作流中实际可达的重大风险。它把用户、维护者、本地状态
和所选配置视为可信但可能出错；验证状态与身份而不是动机；优先采用最小充分
控制；扩大范围或信任边界前必须获得用户明确授权。

[完整发布历史与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
