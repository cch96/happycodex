# HappyCodex 0.4.2 Release

Protocol remains `HappyCodex/0.4.1`; package release identity advances to `0.4.2`.
Root owns the isolated release worktree, branch, ledger, publication, and activation.

## Outcome

Release the bounded corpus/holdout concurrency and live-attempt safety changes from the
validation-speed branch on top of the latest public 0.4.1 `main`, preserving all final
0.4.1 fixes. Publish 0.4.2, then activate that exact marketplace package.

## User directives and gates

- `合并主分支作为0.4.2直接发布吧`: authorizes merge, tag, push, publication, and activation.
- `不用review`: explicitly waives the 0.4.2 review gate. No reviewer result may be claimed.
- `不用验证回滚缓存`: explicitly waives rollback-cache verification and rollback rehearsal.
  The existing 0.4 installation/cache remains untouched until activation.
- `不跑并豁免 0.4.2 live corpus/holdout`: explicitly waives both 0.4.2 live behavior gates.
  No live authority was granted, no call ran, and no live certification may be claimed.

## Candidate and checks

Baseline is the current `origin/main` carrying tag `v0.4.1` plus its release-closure
successors. Candidate source is this release branch after the 0.4.2 cachebuster commit.
Required non-model checks are unit tests, Ruff, official Skill/plugin validators,
AST/JSON parsing, evaluator dry-runs, ledger verification/impact, diff checks, and a
fresh isolated plugin install/readback of the exact candidate.

Product candidate `0723bd2` uses package version `0.4.2+codex.20260729091527`;
package semantic/artifact IDs are `0bbd3a543fc605a2c7b70f110eca28aad4b30da120b3590aab3a68a8f141b6e7`
and `5d0955e9466897720257ff5c3ac9c3e89de139b0b8b47804b6f97aaad1bd7e88`.
The engine manifest is `1c10a92d206f13748e2b1cf61ca0ee3a4a54e1060316b6d17daeafec3f794f9a`.
All 173 tests, Ruff check/format, both official validators, AST/JSON parsing,
dry-runs, ledger verify/impact, and diff checks passed. A fresh isolated Codex home
installed and discovered that exact version.

## Completion

Record final source/tag/package identities, check results, isolated install receipt,
publication/activation result, every waiver, and every unrun gate. Do not claim live
behavior certification.
