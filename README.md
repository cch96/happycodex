# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 高风险工程任务的开源可靠性指引。*

HappyCodex 把高风险任务事实保存在任务本地、未版本化的 ExecPlan 中，在候选就绪时把
稳定评审正文与消费者原生不可变身份绑定；每个外部 effect 前只刷新当前 effect 字段，
然后做一次尝试和真实观测。
它是 portable guidance，不是 controller、授权系统、ledger、调度器或重试引擎。

## 适用场景

适用于跨系统修改、公共契约、迁移、持久化、并发、破坏性或生产 effect、穷尽性声明，
以及可能跨上下文压缩的长期工作。边界明确、可逆的本地修改继续使用 Codex 原生 Plan。

## 安装与调用

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后新建 Codex 任务，再调用：

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

Skill 的核心流程是：

1. 在任务本地的未版本化 ExecPlan 中记录 Outcome、授权边界、消费者、effects、检查和
   stop facts。
2. 将 scout、supporting body 或 worker 路由到最小有界原生 agent，同时保持重叠资源单写者。
3. 以完整 consumer input closure 的 Git tree、package、image 或 revision 等不可变身份冻结。
4. material/release-bound 候选就绪后接受一次 fresh no-history blocker-only Exact-final；
   后续仅 effect 字段变化不重审代码，每个 effect 仍只尝试一次。
5. 以 achieved、not achieved 或 unknown 如实收口。

原始 ExecPlan 不进入产品 Git；长期知识须独立提炼为有明确任务后消费者的 ADR、
runbook 或 contract。

授权边界、delegation bridge、advisory stop、candidate freeze、review 与 effect 的精确规则，
请直接阅读 [HappyCodex Skill](skills/happycodex/SKILL.md)。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
