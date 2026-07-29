# HappyCodex 0.6 Semantic Core

Protocol: `HappyCodex/0.5`

Current index: bootstrap skeleton only.

Restore guard: restore this ExecPlan, then reconcile Git, the fixed Executor,
resource claims, active grant, receipts, checks, agents, and any Goal before any
write, review, or completion claim.

Phase: `contract_discovery`. This plan is intentionally not
implementation-frozen until independent Challenger review is unioned,
Root reproduces the union, and a separately granted contract-freeze revision
records the resulting claims and implementation boundaries.

## Operative request and normalized Outcome

User request 1, verbatim:

```text
好的，你看看还有没有遗漏， 如果考虑重构不考虑兼容收益高吗，是否有更好更优雅的方案，让fable5也可以看看、
```

UTF-8 request plus final LF SHA-256:
`d02b3387c6b7a2381e96f22259ab27c0825829a363141aafc73096536edee3f3`.

User request 2, verbatim:

```text
好的执行吧
```

UTF-8 request plus final LF SHA-256:
`092bba03db327e3feea788e30c57c31c6c5dd320c7603512e2143c9b23a61be5`.

Normalized Outcome authorized by Root, verbatim:

```text
create an independent bounded-clean-break HappyCodex 0.6 source line from released public main, combining Runtime cadence simplification with a typed stateless evaluator semantic core. Preserve strict authority/capability/attempt-consumption/resource-claim/cost/holdout infrastructure. No compatibility reader, migration, alias, dual write, or fallback. This authority does NOT authorize live model/corpus/holdout execution, release, install, activation, marketplace mutation, or active-plugin mutation.
```

Normalized Outcome plus final LF SHA-256:
`8d57c106322fd0231382e995940ec9ff89bbca7756eb14cf4e57dedfe11b25f4`.

The request to let Fable 5 review the design is captured but is not execution
authority in this bootstrap. Any Fable/model-reaching review requires its own
explicit future authority, neutral read-only packet, bounded invocation, and
receipt. Fable is not part of the 0.6 Runtime Outcome.

## Immutable baseline and generation boundary

- Repository: `/home/caichenghang/projects/happycodex`.
- Released base commit:
  `1ea888ddeac94ebbb9f92e5dc80b1de289e6aec0`.
- Released base tree:
  `ab42724288e3e588c30bd0f4a941436f4a8f35f5`.
- Base identity: released public `main` / tag `v0.5.0`; commit subject
  `test: refresh HappyCodex 0.5 package identity`.
- Branch: `codex/happycodex-0.6-semantic-core`.
- Worktree:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-semantic-core`.
- Executor owner label: `happycodex-0.6-semantic-core-executor`.

The 0.6 line is an independent source generation from that exact base. Its Runtime
and evaluator contract may be redesigned only within the later frozen 0.6 contract.
There will be no 0.5 evidence reader, schema migration, alias, dual read/write,
prior-coverage reuse, parser fallback, or task migration. Existing 0.5 tasks remain
0.5 tasks or are abandoned. Public `main`, released package bytes, the active
installation, rollback cache, and external role configuration remain unchanged.

## Scope, open contract, and non-goals

The initially authorized design scope is:

1. simplify Runtime cadence and convergence semantics where a clean redesign
   removes real semantic complexity;
2. define one typed, stateless evaluator semantic core so impact planning,
   execution validation, evidence classification, and replay do not encode
   divergent meanings; and
3. preserve the safety infrastructure below while removing compatibility-only
   or duplicated semantic paths.

The detailed contract, typed model, caller inventory, schema boundary, deletion
set, Runtime wording, and implementation file set remain open. Challenger review
must first search for omitted callers, bypasses, stateful semantics, serialization
consumers, recovery effects, and regressions. Root must reproduce and union those
findings before contract freeze. No product or evaluator implementation is
authorized by this skeleton.

Non-goals in the current Outcome and bootstrap are Fable as a product feature,
compatibility behavior, release engineering, publication, installation,
activation, marketplace changes, active-plugin changes, deployment, or migration
of an existing task/evidence ledger.

## Preserved infrastructure

The 0.6 design must preserve, with fresh-generation typed validation:

- Root decisions and one fixed Executor as the sole controlled-domain writer;
- exact grant authority, durable intent, complete receipts, monotonic grant
  sequence, stop conditions, and Root read-only verification;
- one immutable process-local capability, rebound before any model-reaching
  fixture, mapping, workspace mutation, or subprocess action;
- atomic exclusive resource claims and fixed owner-token verification before
  every write;
- attempt-consumption, terminal-state, recovery, and no-blind-retry semantics;
- resource and output claims, source/package/config identity binding, and
  content-addressed evidence;
- source-derived cost envelopes and separate exact authority for Executor pilot,
  corpus, and adaptive holdout work; and
- holdout isolation, frozen-arm comparison, first-regression rejection, and
  release/install/activation gates.

No offline result can promote `refresh_required` to `certified`. Any future 0.6
ledger is a fresh 0.6 genesis whose evidence strictly postdates its frozen 0.6
source.

## Writer binding, resource claims, and bootstrap grant

Root is read-only. The fixed writer is canonical task `/root/executor`, selected
role `happycodex_executor`, effective contract `gpt-5.6-sol/high`, and owner label
`happycodex-0.6-semantic-core-executor`. Host/config receipts remain a contract-
freeze input; identity or configuration drift fails closed and permits no
replacement writer.

Installed helper:
`/home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/skills/happycodex/scripts/resource_claim.py`;
SHA-256
`c06c4b670940bbe4078ae056ae8809168a5507f8e4f647a1a46dd2ab653e97f5`.

Private claim receipt:
`/tmp/happycodex-0.6-semantic-core-resource-claim.json`; mode `0600`;
receipt SHA-256
`11079cb0aa1d1d7dc4e9af352c7eadb5e3b585b87d7dc99128a392325e3e0cf8`.
Generated owner-token SHA-256:
`2d0381225c3d4dcf5c8bfe0e68fb0b85ced9511018c00d3f006d0e1d8c79f90b`.

The atomic claim binds exactly three resources:

- worktree:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-semantic-core`;
- ref:
  `/home/caichenghang/projects/happycodex::refs/heads/codex/happycodex-0.6-semantic-core`;
- ledger:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-semantic-core/docs/execplans/happycodex-0-6-semantic-core.md`.

The adjacent untracked claim directory is protocol control state, not product or
commit content. It remains claimed after this bootstrap and must be accounted for
or explicitly released under a future reconciliation grant.

Bootstrap grant `HC06-G-001-bootstrap`, sequence 1, authorizes only exact base and
conflict checks; branch/worktree creation; the three-resource claim; this
ExecPlan skeleton; staging this file alone; one skeleton commit with the mandatory
trailer; verification; and external intent/receipt control records. Its first
durable intent is
`/home/caichenghang/.codex/happycodex-0.6-semantic-core-bootstrap-intent.json`,
SHA-256
`c665dcf919ff6c8dd432ba513c89c1de4883093627078e8a1b6e9da9057355df`.
The grant is non-renewable and stops after its receipt.

## Claims and future gates

| ID | Type | Claim | Closure | Falsifier / oracle | Evidence | State |
| --- | --- | --- | --- | --- | --- | --- |
| `O-06-01` | outcome | 0.6 simplifies Runtime cadence without weakening semantic-progress or convergence safety | Frozen contract, real-path controls, and final review | Less prose or state permits an equivalent consumed attempt, authority drift, or repeated unchanged work | Challenger and caller inventory pending | `open` |
| `O-06-02` | outcome | One typed stateless semantic core governs every evaluator semantic consumer | Complete producer/consumer map, schema validation, replay, and negative controls | A caller retains divergent parsing, hidden mutable semantics, or a bypass | Challenger and boundary trace pending | `open` |
| `P-06-01` | preservation | Authority, capability, attempt, claim, cost, corpus, and holdout safety remain strict | Fresh 0.6 controls and exact-product review | Any preserved gate can be bypassed, reused, or inferred | Contract freeze and implementation pending | `open` |
| `A-06-01` | allowed-break | 0.6 has no compatibility path to 0.5 evaluator evidence or tasks | Source/caller search and fresh-genesis checks | Reader, migration, alias, dual write, fallback, or prior evidence reuse exists | Contract freeze and implementation pending | `open` |

Separate future gates remain open and confer no present authority:

1. independent Challenger review, Root union/reproduction, and contract freeze;
2. each implementation/RED/repair commit under a new exact grant;
3. fresh 0.6 offline evidence genesis and exact-product neutral review;
4. Fable 5 or any other model-reaching design review;
5. one bounded Executor calibration after its exact cost envelope;
6. corpus and adaptive holdout execution, each with separate exact user authority;
7. isolated install and release proof; and
8. release, push/merge/tag/publication, marketplace cachebuster, installation,
   activation, and rollback/cutover.

## Verification plan

For this bootstrap:

- prove branch/worktree HEAD and tree equal the immutable base before the edit;
- verify the installed three-resource claim and fixed owner label before every
  repository/index mutation;
- inspect the staged diff and prove only this ExecPlan is staged;
- run `git diff --check` without invoking an evaluator;
- commit once with
  `HappyCodex-ExecPlan: docs/execplans/happycodex-0-6-semantic-core.md`;
- prove parent/base ancestry, commit/tree, changed-path inventory, claim status,
  and final `git status --short --branch`; and
- persist a complete external terminal receipt, then stop.

Future verification remains open until the Challenger union freezes exact RED
oracles, semantic/harness/artifact classification, caller coverage, cumulative
offline checks, neutral review, live-cost gates, and release gates. If evaluator
commands are later authorized, use only `python3 -m evaluation.cli`.

## Progress and decision log

- `2026-07-29`: Reconfirmed base commit/tree and absence of the target branch,
  worktree, ExecPlan, receipt, and conflicting target claims.
- `2026-07-29`: Persisted `HC06-G-001-bootstrap` durable intent before branch,
  worktree, claim, repository, index, or commit mutation.
- `2026-07-29`: Created the exact branch/worktree from the immutable base; no
  rebase, merge, cherry-pick, or existing worktree mutation occurred.
- `2026-07-29`: Acquired and verified the worktree/ref/ledger claim as
  `happycodex-0.6-semantic-core-executor`, resource count 3.
- Decision `D-06-001`: use released public 0.5 as a generation boundary, not the
  separate 0.5.1 development worktree or abandoned convergence branches.
- Decision `D-06-002`: keep implementation contract and file claims open until a
  fresh independent Challenger is reproduced and unioned; this bootstrap chooses
  no detailed semantic-core design.

## Checkpoint

- Milestone: bootstrap skeleton; affected gates: contract discovery only.
- Last source identity: base commit
  `1ea888ddeac94ebbb9f92e5dc80b1de289e6aec0`, tree
  `ab42724288e3e588c30bd0f4a941436f4a8f35f5`.
- Controlled domain: the exact branch, worktree, ledger, private claim receipt,
  and external bootstrap intent/receipt; no product, evaluator, active-plugin, or
  external release state.
- Active grant: `HC06-G-001-bootstrap`, `intent_recorded` while this skeleton is
  created; terminal receipt and Root acceptance remain pending.
- Agents/review: fixed Executor only; no Explorer, Challenger, reviewer, Fable,
  or model-reaching evaluator call has run.
- Goal: none created or inferred.

## Retrospective

Fill only after final Outcome completion. Do not expose it to a reviewer or use it
as evidence.
