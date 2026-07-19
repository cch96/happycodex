# HappyCodex 0.3 source release integration

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: frozen by the commit with subject
`docs: freeze HappyCodex 0.3 source release contract`
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

## Baseline evidence and exact identities

| Check | Result |
| --- | --- |
| `git fetch origin`; `git rev-parse origin/main` | fetched base remains `5c5d4c0a4d7590871acd14e4f1ef282f2f564177` |
| `git rev-parse feat/happycodex-0.3-cleanroom` | certified source remains `89e6a8b2711b869e8fad0ce3d112cfd97b9c3833` |
| `git merge-base origin/main feat/happycodex-0.3-cleanroom` | `3b9c11fac1f97df75263e0bfc6421c575e04e8b2` |
| `git rev-list --left-right --count origin/main...feat/happycodex-0.3-cleanroom` | `11 172` |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` on the release skeleton | 24/24 baseline tests passed; exit 0 |
| main-only range | all 11 commits inspected by subject, ancestry, paths, and per-commit stats; every changed path belongs to the rejected 0.3 prototype/evidence surface |
| candidate tree | tree `8441b737f4dd0ffddc8860959d6e513803cd3c57`; 55 entries; all mode `100644`; no gitlink or submodule |
| candidate recursive `ls-tree` manifest | SHA-256 `05509f86830b1b97d61b9256c98e255c0ee17327f5ea90c9a51a637cd41ae459` |
| main-to-candidate path classes | 48 added, 58 deleted, 5 modified, 2 unchanged; no type or mode change |
| candidate Skill | SHA-256 `0f2223498e398325d1f9728f485b46282778f1199be4f0d80802073f191c6b71` |
| loaded/active Skill | exact same SHA-256; `codex plugin list --json` reports installed+enabled personal `0.3.0+codex.20260716113414` |
| candidate manifest | `.codex-plugin/plugin.json` version `0.3.0+codex.20260716113414` |
| starting status | clean after plan-only skeleton `e362a381da49e800fc10254dd30b80c910300327` |

The final product/support identity is the complete recursive candidate manifest above.
The only allowed additional path is this release ExecPlan. Equality is path-, mode-,
and blob-exact; prose similarity, a patch checksum, or selected-file hashes cannot
substitute.

## Design saturation and boundary decision

Material alternatives were compared:

1. Merge the candidate branch. Rejected: it imports the 172 experimental commits as
   release ancestry, contrary to the explicit request.
2. Cherry-pick a subset of the experimental range. Rejected: selecting from 172
   revisions recreates provenance ambiguity and can miss a final-tree unit.
3. Retain main-only prototype artifacts beside the certified tree. Rejected: it makes
   exact candidate-tree equality impossible, preserves rejected legacy references,
   and retains repository-local raw model-event evidence that the certified policy
   moved outside the repository.
4. Transplant the exact certified blobs onto the single-parent release history in two
   semantic commits. Selected: ancestry preserves every main-only commit, no candidate
   commit becomes a parent, and filtered final-tree equality is mechanical.

“保留 main-only 工作” is therefore frozen as Git-history/ancestry preservation, not
retention of rejected main-only artifacts in the release tree. That interpretation is
required to satisfy the same request's exact final-product-tree and no-172-history
clauses. The old artifacts remain reachable in the 11 preserved ancestor commits.

Semantic integration revisions are limited to:

- runtime/release surface: exact candidate `.codex-plugin/plugin.json`, `AGENTS.md`,
  `README.md`, and `skills/happycodex/**`, including removal of superseded references;
- certified support tree: exact candidate clean-room ExecPlan, `evaluation/**`, and
  `tests/**`, including removal of the rejected main-only ExecPlan and repository-local
  raw evidence.

`.agents/plugins/marketplace.json` and `.gitignore` already have the candidate blobs
and must remain unchanged. No intermediate product commit is independently certified;
the cumulative two-commit tree is the candidate-bound unit.

## Independent boundary receipt

Dispatch `/root/release_boundary_challenger` received no Root inventory and was
read-only, single-level, and forbidden from edits, network, model evaluation, install,
or delegation. It independently checked the exact revisions, clean state, ancestry,
path collision, modes, submodules, and path classes, then returned
`GO-WITH-CONDITIONS`.

The condition is the main-only interpretation frozen above. It found no path, mode,
submodule, or Git-history conflict under ancestry preservation. Root reproduced the
union: base is an ancestor of the release skeleton; zero candidate-only commit is
reachable; candidate+release-plan has 56 unique paths; all modes are `100644`; path
classes are A48/D58/M5; 52 deleted paths are old repository-local evidence. No
uncertainty remains after the contract interpretation is frozen.

## Scope and exclusions

Allowed: this ExecPlan, a small number of semantic integration commits, offline unit
tests, official Skill/plugin validators, diff hygiene, one isolated public marketplace
install, Git push, and pull-request creation.

Excluded: any behavioral change to Skill, manifest, tests, oracle, runner, evaluator,
schema, hook, controller, Task State JSON, reviewer protocol, behavior corpus,
holdout, full review, Fable retry, or 0.4 suggestion. A need for such a change stops
before the edit and requires an invalidation/cost report.

The user's validation envelope explicitly replaces a fresh behavior/holdout/full
review cycle for this history-only integration. Existing candidate certification is
reused only after exact tree equality. Fable is not invoked: the user limited checks
to the named offline validators plus one public install, and its absence cannot block.

## Exact validation protocol

After both semantic revisions, run only:

1. `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
2. `python3 /home/caichenghang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/happycodex`
3. `python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`
4. `git diff --check origin/main..HEAD`, clean-status checks, candidate-vs-release
   filtered manifest comparison, and candidate-vs-release filtered diff.

If offline checks pass, push the release branch once without force so the public Git
ref exists. In one fresh isolated `HOME`/`CODEX_HOME`, use the supported public Git
marketplace command `codex plugin marketplace add cch96/happycodex --ref
release/happycodex-0.3 --json`, install `happycodex@happycodex` once, and verify exact
version plus source/install Skill and filtered package equality. The personal install
must remain unchanged. Record the receipt in this ExecPlan only; that administrative
closure may not alter the integrated product tree. Push the closure and open a PR to
`main`.

## Integrated candidate and offline validation receipt

Semantic revisions are `abf594b` (certified runtime/release surface) and `5f5ce4e`
(certified support tree). Both are single-parent descendants of `origin/main`; the
release range contains no merge and zero candidate-only commit. The committed tree
contains 56 files: the candidate's exact 55-file manifest plus this release ExecPlan.

Candidate-vs-release filtered `git diff` is empty. The committed filtered recursive
manifest remains SHA-256 `05509f86830b1b97d61b9256c98e255c0ee17327f5ea90c9a51a637cd41ae459`.
`origin/main` is an ancestor, and every one of its 11 post-merge-base commits remains
reachable. These facts close SR-01 through SR-03 without reinterpreting product
behavior.

Authorized offline checks on integrated revision `5f5ce4e`:

| Command | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | exit 0; 97/97 passed in 1.475 s |
| official Skill `quick_validate.py skills/happycodex` | exit 0; `Skill is valid!` |
| official Plugin `validate_plugin.py .` | exit 0; plugin validation passed |
| `git diff --check origin/main..HEAD` and working-tree `git diff --check` | both exit 0; empty output |
| filtered candidate diff and recursive manifest | exact; empty diff; expected SHA-256 above |
| status after checks | clean; branch four commits ahead of `origin/main` |

No behavior, holdout, full review, Fable, runner, evaluator, oracle, or schema command
ran. The active personal plugin list before public verification hashes to
`a3d98977b883f10dec26ad213ed1b45d26bf9dc0ecab4d7940c6e823d236e3f8` and reports
personal 0.3 installed+enabled.

## Public install launch record

After this plan-only receipt is committed, push `release/happycodex-0.3` normally to
`origin` without force. The immutable install subject is product/support revision
`5f5ce4e` and filtered manifest `05509f86…e459`; later changes may touch only this
release ExecPlan. Fresh isolated root is
`/tmp/happycodex-public-release-install.1lQ5JC`, with absent nested `home/.codex`
before launch and no copied authentication.

Use CLI `/home/caichenghang/.local/bin/codex` 0.144.4 in an inherit-none environment
whose `HOME` is `<root>/home`, `CODEX_HOME` is `<root>/home/.codex`, and PATH contains
only the local binary plus standard system bins. Run exactly one public install:

1. `codex plugin marketplace add cch96/happycodex --ref release/happycodex-0.3 --json`
2. inspect isolated available state;
3. `codex plugin add happycodex@happycodex --json` once;
4. inspect isolated installed state and compare version, Skill SHA-256, and filtered
   source/install package manifest;
5. re-hash the non-isolated personal list and require it to remain unchanged.

Any fetch, ref, version, install, hash, credential-isolation, or personal-state
mismatch stops before PR creation. This is the sole public marketplace install for
the task; it invokes no model.

## Public marketplace install receipt

The public ref resolved to
`6fc754eeb48aace06632a13a162e6b989addf888`. The first marketplace command exited
before fetch because the declared empty `CODEX_HOME` directory itself did not yet
exist. It created no marketplace and installed no plugin. Root created only that
empty directory and repeated the same public-ref command; this preflight correction
did not touch the repository, product, authentication, or personal Codex state.

The corrected marketplace add succeeded from
`https://github.com/cch96/happycodex.git` at `release/happycodex-0.3`. Codex emitted
only its expected warning that PATH helper aliases are refused below `/tmp`. Exactly
one `codex plugin add happycodex@happycodex --json` then succeeded and reported:

| Field | Receipt |
| --- | --- |
| plugin/version | `happycodex@happycodex`; `0.3.0+codex.20260716113414` |
| isolated state | installed `true`; enabled `true`; Git marketplace source is the public repository above |
| installed path | `<root>/home/.codex/plugins/cache/happycodex/happycodex/0.3.0+codex.20260716113414` |
| installed Skill | SHA-256 `0f2223498e398325d1f9728f485b46282778f1199be4f0d80802073f191c6b71` |
| public filtered manifest | SHA-256 `05509f86830b1b97d61b9256c98e255c0ee17327f5ea90c9a51a637cd41ae459` |
| source/install comparison | recursive diff excluding `.git` is empty |
| isolated credentials | no `auth.json`, credential, token, PEM, or key file exists; config contains only the public marketplace ref and enabled plugin |
| personal state after install | list SHA-256 remains `a3d98977b883f10dec26ad213ed1b45d26bf9dc0ecab4d7940c6e823d236e3f8` |

The public checkout is clean and tracks the same public release ref. Its filtered
manifest exactly matches the certified candidate, so the install receipt closes
SR-05 without reopening product certification or invoking any model.

## Claims and gates

| ID | Claim / gate | State |
| --- | --- | --- |
| SR-01 | Release ancestry contains `origin/main` and all 11 main-only commits, without merging/cherry-picking the 172 candidate-only commits. | verified |
| SR-02 | Final tree excluding this ExecPlan exactly equals certified candidate `89e6a8b...3833`, including modes, paths, and blob identities. | verified |
| SR-03 | Certified Skill, manifest, and every product-support file retain exact bytes; no unclassified path remains. | verified |
| SR-04 | Authorized offline unit tests, official validators, and diff hygiene pass. | verified |
| SR-05 | One fresh isolated public marketplace install discovers and installs exact 0.3, with source/install equality and no mutation of the personal install. | verified |
| SR-06 | Release branch is pushed without force and a PR targets `main`. | open |
| SR-07 | Final worktree is clean and no completion blocker remains. | open |

## Current checkpoint

The certified cumulative tree is committed and every authorized offline and public
install gate is GREEN. No product path changed after exact equality was established;
only this plan records the receipt. Next: commit and push this administrative
checkpoint, open the PR to `main`, then record the PR identity and final clean state.

## Pending gates

- push and pull request
- administrative closure with unchanged integrated product tree

## Retrospective

Fill only after every completion gate closes.
