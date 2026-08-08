# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 高风险工程任务的开源可靠性指引。*

HappyCodex 用一个静态 ExecPlan 固化任务结果、修改边界、消费者身份与完成条件，
并继续使用 Codex 原生 Plan、agents、Git、测试和 diff。它不是 controller、授权
系统、ledger、调度器或重试引擎。

## 何时使用

适用于跨系统修改、公共契约、迁移、持久化、并发、破坏性或生产 effect、穷尽性
声明，以及可能跨上下文压缩的长期任务。边界明确、可逆的本地修改继续使用原生
Plan；风险或范围扩大时，再创建 ExecPlan。

## 安装与调用

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后新建 Codex 任务，再调用：

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## 核心模型

- ExecPlan 只保存静态请求、Outcome、修改边界、消费者、effect、检查和停止条件；
  live state 始终从 Git、测试和工具重新推导。
- 上下文隔离与并行是两件事：一个噪声通道可以只派一个原生只读 agent；只有独立
  通道才按需并行。较大实现优先使用一个原生 worker，重叠资源始终只有一个 writer。
- 中断或压缩后先确认旧 writer 不会恢复，再完整重读计划并重建 Git、candidate 和
  effect 事实。
- candidate 使用消费者原生的不可变身份冻结，例如 Git tree、package、image 或
  revision；可变 worktree 的 digest 不是 frozen candidate。
- 普通可逆工作不强制 review。公共、外部、不可逆或高风险 candidate 只运行一次
  fresh、blocker-only 终审；失败不会自动修复或重审。
- 外部 effect 一次尝试后以真实只读观测归类为 `landed`、`not_landed` 或
  `unknown`；partial、ambiguous 或 unknown 必须停止。
- 最终明确报告 achieved、not achieved 或 unknown，并如实列出 dirt、跳过检查和
  未验证事实。

HappyCodex portable、zero-config、model-agnostic，不要求自定义 agent、固定模型或
固定推理强度。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
