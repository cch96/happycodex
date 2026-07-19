# HappyCodex 0.4 main integration

Protocol: `HappyCodex/0.3`
Invocation: `$happycodex:happycodex`
Writer: Root only
State: skeleton committed; remote reconciliation pending
Resume: read this entire ExecPlan and reconcile Git, remote refs, checks, and push
receipts before any merge, push, or completion claim.

## Operative source

Source: current task, direct user message. Exact UTF-8 SHA-256:
`1d66977c95611c426e2f9991c897018f942e776425192a6809435f65ace0a1cc`.

<!-- operative-source-begin -->
合并到主分支然后push吧
<!-- operative-source-end -->

## Outcome and exclusions

Integrate the already reviewed local HappyCodex 0.4 certification-engine candidate
into the current remote `main` and push `main` without rewriting remote history.
Preserve remote-main-only work if any, preserve every shipped-package byte and the
public 0.3 Runtime invocation, and keep the 0.4 ledger `refresh_required` with null
live authority/certification.

This Outcome does not reopen product certification, authorize live corpus/holdout
calls, publish a 0.4 plugin release, change marketplace/active installation, invoke
Fable, or add controller/hook/Task State work. No force-push, branch deletion, direct
remote ref overwrite, or history rewrite is allowed.

## Immutable starting snapshot

| Item | Value |
| --- | --- |
| Repository | `/home/caichenghang/projects/happycodex` |
| Source branch | `feat/happycodex-0.4-certification-engine` |
| Reviewed semantic candidate | `1c1fa4fc46c7396f514171ec5d4cce559944f06c` |
| Source closure HEAD | `f633a664cfc6bde9afa071dee390067627376a9e` |
| Local `main` before fetch | `2836d7363db364807a2ec384dc1b6c2cc13df95e` |
| Cached `origin/main` before fetch | `2836d7363db364807a2ec384dc1b6c2cc13df95e` |
| Starting worktree | clean |
| Writer | Root only |

## Claims and gates

| ID | Claim | Closure / blocker |
| --- | --- | --- |
| MI-01 | Current `origin/main` is fetched before integration and any remote drift is reconciled without dropping main-only work. | Fetch receipt, ancestry/range inventory; unexpected conflicting drift stops the merge. |
| MI-02 | The reviewed 0.4 product projection remains exact; this task adds only its administrative ExecPlan before integration. | Source-closure-to-integration-source diff names only this file; shipped paths remain identical. |
| MI-03 | Integration uses ordinary non-force Git history and leaves an auditable `main` descendant of both fetched `origin/main` and the source closure. | Parent/ancestry receipts; force/history rewrite falsifies. |
| MI-04 | The integrated tree passes the full offline unit suite, official Skill/plugin validators, Ruff, CLI verify/impact/dry-runs, JSON parsing, and diff hygiene. | Exact command receipts; any new failure blocks push. |
| MI-05 | Push updates only `origin/main` to the verified local `main`; remote and local IDs match afterward. | Push receipt plus post-push fetch/`ls-remote` identity. |
| MI-06 | No excluded live/release/install/Fable/plugin/controller action occurs. | Command and final-state inventory. |

## Execution plan

1. Commit this minimal recovery skeleton on the source branch.
2. Fetch the remote and reconcile `origin/main`, local `main`, and source ancestry.
3. Freeze the exact integration strategy and pre-merge identities here.
4. Integrate on local `main` without force or history rewriting.
5. Run the complete offline integration matrix and inspect the final diff/tree.
6. Push `main`, verify the remote identity, and record closure.

## Checkpoint

- Milestone: source closure recovered; integration skeleton pending commit.
- Next: commit this file, then fetch `origin` and freeze current remote state.
- Owned path before merge: this ExecPlan only.
- Missing facts: current fetched `origin/main`, integration topology, post-merge test
  receipts, final local/remote `main` identity, and push receipt.

## Retrospective

Fill only after every integration and remote-identity gate closes.
