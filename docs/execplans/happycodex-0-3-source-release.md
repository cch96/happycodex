# HappyCodex 0.3 source release integration

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: skeleton; contract freeze pending
Guard: restore this ExecPlan before any write, review, or completion claim.
Goal: none; this independent Outcome uses Native Plan plus this ExecPlan.

## Operative source

Source anchor: `current-task/user/source-release-integration`
SHA-256 of the dequoted UTF-8 block with LF line endings and a final LF:
`50fcc8f0cabea29d126acc3a1bfb63d9bf7c511a745f07efe0f345c2ef809d66`

<!-- operative-source-begin -->
这是一个全新、非 Fork 的 Codex Session。

开始前先报告当前加载的 `happycodex:happycodex` Skill locator/version。只有确认加载的是
`0.3.0+codex.20260716113414`
才继续；如果仍是 0.2，立即停止并告诉我，不要执行任何修改。

使用 $happycodex:happycodex 完成 HappyCodex 0.3 的源码发布收尾。

工作区：
/home/caichenghang/projects/happycodex-cleanroom-0.3

已知事实，请独立核验：
- 候选分支：feat/happycodex-0.3-cleanroom
- 候选 HEAD：89e6a8b2711b869e8fad0ce3d112cfd97b9c3833
- origin/main：5c5d4c0a4d7590871acd14e4f1ef282f2f564177，仍为 0.2
- 最终 ExecPlan：
  docs/execplans/happycodex-0-3-cleanroom.md
- 本机 personal 插件已安装并启用 0.3
- main 与候选已经分叉，存在 11 个 main-only 和 172 个 candidate-only 提交
- 0.3 的产品、测试、review、holdout、安装、回滚和原 Goal 已完成

这是新的“源码发布集成”Outcome，不得重新打开已经关闭的 0.3 产品认证，也不得吸收 0.4 优化建议。

要求：

1. 阅读仓库政策、最终 ExecPlan closure、main-only 提交及候选最终产品树。
2. 建立一个最小的新 ExecPlan，范围只包括源码集成、公开安装验证和发布交付。
3. 从最新 origin/main 创建独立 release 分支；保留 main-only 工作，并以少量语义提交集成最终 0.3 产品树。不要把 172 个实验过程提交原样合入主线。
4. 保持已认证的 Skill、manifest 和产品支持文件字节语义不变。若只能改变 Git 历史，可复用既有认证证据。
5. 只运行离线单元测试、官方 Skill/plugin validators、diff hygiene，以及一次隔离的公开 marketplace 安装验证。
6. 如果必须修改 Skill、manifest 行为、测试 oracle、runner 或 evaluator，先停止，报告失效证据、最小重跑范围和预计成本；不要自动重跑昂贵 behavior、holdout 或完整 review。
7. Fable 仅在可用时使用；不可用不得阻止本次发布。
8. 不增加 schema、hook、controller、Task State JSON、reviewer 协议或其他 0.4 工作。
9. 验证通过后，推送 release 分支并创建 PR；禁止 force-push、直接覆盖 main 或删除分支。
10. 最终报告：集成策略、精确提交、测试结果、公开安装得到的版本、PR 地址，以及是否仍有 completion blocker。
<!-- operative-source-end -->

## Normalized Outcome

Starting from the fetched `origin/main`, create a release branch whose history retains
all main-only commits but whose final repository tree, excluding this one release
ExecPlan, is byte-for-byte identical to certified candidate
`89e6a8b2711b869e8fad0ce3d112cfd97b9c3833`. Validate only the authorized offline
and isolated public-install gates, then push the branch and open a pull request.

## Immutable starting state

| Item | Value |
| --- | --- |
| Repository/worktree | `/home/caichenghang/projects/happycodex-cleanroom-0.3` |
| Release branch | `release/happycodex-0.3` |
| Fetched base | `origin/main` = `5c5d4c0a4d7590871acd14e4f1ef282f2f564177` |
| Certified source | `feat/happycodex-0.3-cleanroom` = `89e6a8b2711b869e8fad0ce3d112cfd97b9c3833` |
| Merge base | `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` |
| Divergence | 11 main-only; 172 candidate-only commits |
| Starting worktree | clean |
| Writer/ownership | Root only; entire release worktree |
| Native Goal | none |
| Accepted baseline failures | none |

## Scope and exclusions

Allowed: this ExecPlan, a small number of semantic integration commits, offline unit
tests, official Skill/plugin validators, diff hygiene, one isolated public marketplace
install, Git push, and pull-request creation.

Excluded: any behavioral change to Skill, manifest, tests, oracle, runner, evaluator,
schema, hook, controller, Task State JSON, reviewer protocol, behavior corpus,
holdout, full review, Fable retry, or 0.4 suggestion. A need for such a change stops
before the edit and requires an invalidation/cost report.

## Claims and gates

| ID | Claim / gate | State |
| --- | --- | --- |
| SR-01 | Release ancestry contains `origin/main` and all 11 main-only commits, without merging/cherry-picking the 172 candidate-only commits. | open |
| SR-02 | Final tree excluding this ExecPlan exactly equals certified candidate `89e6a8b...3833`, including modes, paths, and blob identities. | open |
| SR-03 | Certified Skill, manifest, and every product-support file retain exact bytes; no unclassified path remains. | open |
| SR-04 | Authorized offline unit tests, official validators, and diff hygiene pass. | open |
| SR-05 | One fresh isolated public marketplace install discovers and installs exact 0.3, with source/install equality and no mutation of the personal install. | open |
| SR-06 | Release branch is pushed without force and a PR targets `main`. | open |
| SR-07 | Final worktree is clean and no completion blocker remains. | open |

## Current checkpoint

Read-only baseline verification is complete: Skill locator/version matched the
required 0.3 build; repository policy and the complete 3,629-line certified ExecPlan
were read; candidate/base/merge-base/divergence values matched; main-only subjects and
file effects were inventoried; candidate has 55 tracked files and main has 65. The
release branch now points at the fetched base. Next: commit this skeleton, freeze the
integration design and exact tree identities in a separate revision, then integrate.

## Pending gates

- skeleton revision
- contract-freeze revision
- semantic tree integration
- exact tree/blob preservation proof
- authorized offline validation
- one isolated public marketplace install
- push and pull request
- administrative closure with unchanged integrated product tree

## Retrospective

Fill only after every completion gate closes.
