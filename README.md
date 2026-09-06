# HappyCodex

[English](README.en.md)

*面向 OpenAI Codex 长期任务与重要工程操作的可靠性指引。*

HappyCodex 补充任务边界、协作、评审与操作恢复约定，日常规划和实施使用 Codex
原生能力。它是便携指引，不能替代宿主的权限控制或真实执行结果。

## 适用方式

- 小而明确的任务直接完成；有独立问题或较大工作量时，按任务选择模型和子代理。
- 将大段调查留在子任务，返回结论、证据与未决项，减少主任务的重复阅读。
- 只协调实际重叠的写入；按真实风险和用户要求评审，避免做完一轮后默认追加终审。
- 需要跨压缩续接时保留必要事实；共享、破坏性、公开或付费操作前核对目标和已有授权。
- 操作结果不明时先查权威状态，保留回执，不盲重试。

2.0 使用原生计划与按需笔记，取消固定 ExecPlan 模板和默认 hooks。模型与 effort
由可用配置和任务需要决定，产品不绑定某个型号。

## 安装与调用

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

安装后新建 Codex 任务，再调用：

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

详细规则见 [HappyCodex Skill](skills/happycodex/SKILL.md)；实际操作前按需读取
[操作与恢复说明](skills/happycodex/references/effects.md)。

从旧版本切换时，新任务使用新插件与隔离配置。若个人角色仍包含旧版唯一 Executor、
固定授权或逐次 intent/receipt 指令，需要单独更新这些配置；安装插件不会修改它们。
保留活跃旧任务的写入归属与恢复材料，未决操作不能通过新建任务重试。

[已发布版本与验证状态请查看 GitHub Releases](https://github.com/cch96/happycodex/releases)。

## 许可证

HappyCodex 使用 [MIT License](LICENSE)。
