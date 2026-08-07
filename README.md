# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 高风险工程任务的开源可靠性指引。*

HappyCodex 用仓库内 ExecPlan 固化完成条件。Root 决策、授权、复现和验证，一个
固定 Executor 负责全部受控写入。它组合 Codex 原生 Plan、Git、测试、agents 和
review；它不是 controller、daemon、scheduler、授权系统或重试引擎。

## 何时使用

适用于公共契约、跨系统修改、迁移、持久化、并发、破坏性或生产效果、穷尽性
声明、长期研究，以及可能跨越上下文压缩的工作。边界清晰的本地低风险修改继续
使用原生 Plan、测试和 diff；范围扩大时再建立 ExecPlan。

## 安装与调用

安装需要 Codex 支持插件市场：

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后新建 Codex 任务，再调用：

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

只有用户明确请求时才创建或修改 Goal。Goal 只能延续已有授权，不能授予 amendment、
waiver、review、cost、authority 或 effect，也不能替代 ExecPlan。

## 四个阶段

1. `working`：冻结请求、Outcome、受支持工作流、边界、当前 authority/grant、
   义务、检查、效果和停止条件；执行一个连贯的授权波次。
2. `candidate_frozen`：清点全部归属内变化，保持已接受的基线失败不变，并绑定
   清洁的 candidate 身份和回执。
3. `exact_final`：一个全新、空历史、逻辑只读的 reviewer 接收冻结 candidate 的
   中性 brief。Root 复现并分类发现。只有一个经 Root 准入的边界内 blocker 可
   消耗默认的一次修复波次；替代评审后再出现 blocker 或 unknown，必须先返回
   用户，不能继续写入或重跑。
4. `closed`：只有义务、检查、评审、效果、所有权、回执以及用户明确请求的 Goal
   全部核对后，Root 才能关闭。

请求的角色矩阵：

| 逻辑角色 | 模型 | 推理强度 |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| 唯一 Executor | `gpt-5.6-sol` | `high` |
| 全新 Exact-final | `gpt-5.6-sol` | `max` |

host 认证的 output identity 始终必需。缺失 effective route 或 permission
telemetry 时记录 `unverified`，只降低依赖它的保证；暴露值不匹配，或无法建立
预先声明的必需保证时停止。prompt/profile 的只读文字不是技术隔离证明。
Explorer 只回答有界且独立的问题，重要事实在 Root 从源码复现前仅供参考。

Exact-final 是仅检查 blocker 的关闭门，不是优化轮次。可准入的 blocker 只能是已复现
的冻结义务失败（包括 candidate 未能修复原始义务），或可通过具名工作流触达且由
candidate 新增的重大安全或正确性回归；它必须给出具体、可行动、证据支持或可复现的场景。
样式或命名偏好、一般清理或重构、推测性加固、替代设计或新保证、未冻结的测试建议，
以及与冻结义务无关的既存问题都不能阻塞关闭。

一个已准入结果绑定一个精确冻结的评审身份：candidate、中性 brief，以及相关的已绑定
配置或回执身份。身份不变时，不得通过改写 brief 或更换 reviewer 重跑。中性 brief 仍不
包含先前 finding 或期望 verdict；产品变更后必须由一个全新的替代 Exact-final 评审，且
再次冻结后若仍有 blocker 或 unknown，必须返回用户。

## 0.8 clean break

HappyCodex 只保留一个当前快照，不维护逐 grant 历史或可变控制状态。外部用户
authority、Root 给 Executor 的精确活动 grant、candidate evidence、effect
authority 与 Goal 始终分离。

除非已有待确认的精确 content-addressed proposal，否则泛化的“继续”不授予任何
权限；对紧邻的精确 proposal 作出清晰同意，也只授权该 proposal。旧版或形状不匹配
的 snapshot 一律视为 unknown 并返回用户，不提供 compatibility reader 或 migration。

`reconciliation latch` 是仅为跨上下文丢失而持久化的派生安全状态，不是第五个阶段
或 durable record type。它只在外部 effect terminal 为 partial 或 ambiguous 时生效；
重复的本地或 review falsifier、未变化的失败以及已耗尽的修复预算都走普通停止线。
生效期间只允许只读 reconciliation、verification 和返回用户；不得创建 grant、执行
effect、冻结 candidate 或运行 Exact-final。只有 reconciliation 已绑定精确的当前
effect state 与 prestate、Root 冻结精确有界的 recovery proposal 及其 digest、并且
用户明确授权该 proposal 后才能解除；state 与 action 都不要求改变。

冻结边界外的新 durable state/schema、跨上下文协调、compatibility 或 control-plane
机制都属于 envelope expansion。candidate failure 不得重新贴标签；若 finding 由修复
机制本身造成，先比较删除、回滚与简化，再考虑增加控制。

secret 与 raw event 绝不写入受控产品字节；只在其外保存 sanitized summary 或
digest。禁止 commit 时保持 index 不变，并要求用户选择 durable location；里程碑
必须保存在获批的 reachable ref 或 content-addressed archive 中。若既无用户选择的
archive，也无获批位置，则 durability 尚未就绪：`STOP_FOR_USER`。

插件安装不会打包或激活 custom agents；可选本机 profiles 只是便利配置，不是
route 或 isolation 证明。在取得各自回执前，不声称 publication、release、install
或 activation 已完成。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
