# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 高风险工程任务的开源可靠性指引。*

HappyCodex 用一个静态 ExecPlan 区分 workspace/task-owned 授权边界、freeze 时精确的
consumer input closure 与有界 incidental footprint，并继续使用 Codex 原生 Plan、
agents、Git、测试和 diff。它不是 controller、授权系统、ledger、调度器或重试引擎。

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

- ExecPlan 只保存静态请求、Outcome、workspace/project 或 task-owned 授权边界、预期
  primary surface、消费者、effect、检查和停止条件；精确 mutable path 不是授权边界。
  同一边界内、且不改变消费者、Outcome、preservation、exclusion 或 primary effect 的
  task-owned 新增或迁移可在 freeze 前继续；这不授权删除旧/shared surface。
- bounded、additive、可重建、非权威且不进入消费者输入的 cache/tmp/log/compiled output
  是 incidental footprint，继续并在 closure 核算；shared/system install、shared-cache
  删除或覆盖、trust/credential/shared config、其他 owner、remote/paid 或无法分类时停止。
- 按稳定边界路由：当建议、评估或设计结论依赖尚未核实、跨多个 artifact 或需搜索
  枚举的当前事实时，Primary 先写一小组可观察回答的开放事实问题，交给一个原生只读
  agent；它只返回带引用的事实、搜索范围和 unknown，不作建议，最终判断仍由 Primary
  完成。一两个有界直接查询足够或事实已在当前 session 核实时跳过 scout。其他稳定
  问题仅在要求搜索、摘要、比较或筛选辅助证据体时，才在 Primary 读取正文前委派；
  所有权和 Done 证据稳定后，较大实现则在编辑前交给一个原生
  worker。小而完整的修正可直接完成。外部模型或工具的 challenge/review 只覆盖已
  分配问题，并由 Primary 直接调用和观察；
  不得创建原生 agent 代为调用、中转或包装外部调用。原生 agent fallback 要在直接
  处理前说明。上下文卸载不要求并行或低剩余
  上下文；仅在独立证据体并发确有帮助时增加 agent，重叠资源始终只有一个 writer。
- 中断或压缩后先确认旧 writer 不会恢复，再完整重读计划并重建 Git、candidate 和
  effect 事实。
- freeze 时派生包含 mode 和 deletion 的精确完整 consumer input closure，并使用 Git
  tree、package、image 或 revision 等消费者原生不可变身份；可变 worktree digest
  不是 frozen candidate。
- 原生 Goal 只在用户明确要求时创建；仅当 Goal、Outcome、修改边界、candidate
  surface、effect target/identity/cap 均未变化且没有待决用户选择时才自治继续。
  Goal、用户回复与 `GO` 都不扩权；Goal 身份无法确认时停止 mutation。
- 删除 branch、worktree 或其他恢复面之前，先证明 candidate、cutover、effect 与
  rollback 证据仍已持久保存且可达；否则停止清理。
- 普通可逆工作不强制 review；迭代 convergence review 可不限轮复用，但始终只提供
  advisory evidence。每个新 pass 必须有可能改变 verdict 的有界理由；旧 standing
  instruction 不自动续轮。公共、外部、不可逆或高风险 candidate 只运行一次独立的 fresh
  原生只读、blocker-only 终审；reviewer 必须 no-history，对一个消费者原生不可变
  身份给出严格 `GO`/`NOT_YET`
  并回显身份，任何 byte 变化都使结论失效。计划 `GO` 只验证计划；组合 candidate
  使用一个绑定全部组件身份的 envelope。终审后再 followup/message 会使后续输出降级
  为 convergence-only；仍只允许一次已授权修复和一次 fresh 替换终审，之后交还用户。
- 外部 effect 一次尝试后以真实只读观测归类为 `landed`、`not_landed` 或
  `unknown`；partial、ambiguous 或 unknown 必须停止。
- 最终明确报告 achieved、not achieved 或 unknown，并如实列出 dirt、跳过检查和
  未验证事实。

HappyCodex portable、model-agnostic，不要求自定义 agent、固定模型或推理强度。
默认 plugin hooks 只是可选、依赖信任且可绕过的 guardrail，不是完整 enforcement。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
