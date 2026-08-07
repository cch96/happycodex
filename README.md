# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 高风险工程任务的开源可靠性指引。*

HappyCodex 把高风险工作的结果、边界和完成条件固化为一个简短的仓库内
ExecPlan，并继续使用 Codex 原生 Plan、Git、测试、diff 和 agents。它不是
controller、授权系统、调度器或重试引擎。

## 何时使用

适用于跨系统修改、公共契约、迁移、持久化、并发、破坏性或生产效果、穷尽性
声明，以及可能跨越上下文压缩的长期工作。

边界明确、可逆的本地修改继续使用原生 Plan、测试和 diff。只有风险或范围扩大
时，才在下一次高风险写入前创建一个 ExecPlan。

## 安装与调用

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后新建 Codex 任务，再调用：

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## 核心约定

- 每个任务最多一个静态 ExecPlan；HappyCodex 不要求额外的控制 PRD 或 `run.md`。
  若产品设计本身是面向独立消费者的长期交付物，它可以作为明确 scope 内的产品
  artifact；ExecPlan 只记录选定边界和路径，不复制全文。
- 一次用户同意覆盖已冻结的 Outcome、scope 和 effect envelope；范围内可逆本地
  修复不重复询问，边界扩大时才重新授权。
- 只有重叠的可变路径或资源要求同一时刻一个 writer；单 agent 可以直接写入，
  其他 agent 仅在能改变决策时只读参与。
- 本地可逆工作默认不评审。难以逆转的架构决策最多一次前置 challenge；公共、
  外部、不可逆或高风险 candidate 最多一次 blocker-only 终审。
- 外部 effect 只尝试一次。只有证明上次没有产生 effect 才能重试；partial 或
  ambiguous 时停止写入、只读核对并返回用户。
- secrets 和 raw events 不进入产品字节；基线失败、未运行检查、工作区 dirt 和
  `unverified` 事实必须如实报告。

ExecPlan 只保存请求、Outcome、路径/资源/effect 边界、baseline/allowed breaks、
可选设计决策、检查、完成条件、停止条件和恢复方法。上下文压缩后，从计划、Git、
测试和工具重新构建当前事实，不保存 grant 历史、可变快照或 reconciliation latch。

HappyCodex 是 portable、zero-config、model-agnostic 的产品指引；不要求自定义
agent、固定模型或固定推理强度。Goal 仅在用户明确请求时使用，且不能创造授权。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
