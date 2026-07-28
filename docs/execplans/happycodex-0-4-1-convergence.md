# HappyCodex 0.4.1 convergence

Protocol: `HappyCodex/0.3` (active 0.4.0 maintainer runtime)
Invocation: `$happycodex:happycodex`
Writer: Root only for the mutable resources listed below
State: candidate_frozen
Resume: restore this file and reconcile Git, tests, Goal, worktree, agents, and gates before any write, review, or completion.

## Outcome and baseline

**Operative sources.** Current Codex task
`019fa9c7-0d4c-72e0-b920-7231a4dab31c`, user plan turn
`019faa10-e00f-75d1-a392-1cdbf6f098da`, item `item-92`, SHA-256
`c5ebab432ca06d054d971f98c5c9bda9d6cecdf250b24f71293b183986e92eb0`;
budget question turn `019faa13-3753-7820-9a01-b9345bca7330`, item `item-102`,
SHA-256 `653f3936eaf713b623af0018622509b65de17c776da7d9662b42c3c885b65ed7`;
and direct continuation/amendment turn `019faa15-4a99-7283-9aee-06148df64285`,
item `item-107`, SHA-256
`3c0077c9863e135c710592c17be11511b5b335651d358b3c71e76ec015de4189`.
The amendment replaces the inherited Runtime budget with a 300-line target,
340-line hard ceiling, 2,600-word target, and 3,000-word hard ceiling. It changes
only the Runtime/template budget and its tests; no product or evidence existed to
invalidate.

**Normalized outcome.** First ship a clean-break HappyCodex 0.4.1 from public 0.4.0:
resource-scoped single writers, family hardening and repair batches, compact current
ExecPlans, `protocol_review_mode`, fresh evidence, exact-final review, public release,
personal upgrade, and retained 0.4.0 rollback. Then use separate successor tasks and
ExecPlans to resume the two named long tasks and port the protocol to the frozen 0.5
candidate. No controller, Task State JSON, compatibility reader, dual write, schema
alias, Evidence DAG, automatic old-task evidence conversion, or unapproved live cost.

**Frozen protocol contract.**

- The lifecycle is `implementation → focused_hardening → candidate_frozen →
  exact_final → closed`. Open families, active writes, incomplete reviewer union, or
  unreconciled grants prohibit `exact_final`; any product-source change returns to
  hardening and invalidates all candidate evidence and final reviews.
- Root assigns stable finding IDs and `family_id` values. A family shares an invariant
  and implementation boundary. Each family scans source/identity, type/cardinality,
  ordering/terminal state, alias/mutability/TOCTOU, serialization/replay, and all
  consumers/failure propagation. Every surface needs a counterexample, positive case,
  evidenced `N/A`, or open status.
- Reviewers of one candidate all reach terminal state before Root unions, reproduces,
  and groups findings. A frozen `repair_batch` may contain coupled families and several
  narrow grants/commits; sibling findings add RED coverage and enlarge the batch.
  Full final review never runs mid-batch.
- Focused reviewers may see history, the family ledger, counterexamples, and repair
  story; their receipts are non-neutral hardening evidence only. Exact-final reviewers
  receive exact frozen product bytes and neutral instructions without that material or
  a preferred verdict.
- A closed family recurring in final review requires replacement or strengthening of
  its frozen abstraction boundary and removal of old bypasses. A second recurrence
  after boundary replacement stops automatic repair and requires user choice to expand
  the refactor, change the contract, or abandon.
- One owner exists per shared mutable resource. Every task names worktree, branch/ref,
  ledger, external-output namespace, and activation target. Disjoint resources may run
  concurrently; any overlap rejects the second writer.
- The ExecPlan is a current index: target at most 8,000 words and hard limit 12,000.
  It keeps frozen contract, open claims/families, current grant, candidate identity,
  valid evidence, invalidation edges, and pending gates. Closed detail becomes a
  checkpoint, Git revision, receipt digest, and invalidation link; complete history
  remains on a reachable Git ref or approved content-addressed archive. Missing,
  inconsistent, or tampered summaries fail closed and recover along that chain.
- Runtime plus template target at most 300 lines/2,600 words, with hard limits of
  340 lines/3,000 words. The public invocation remains `$happycodex:happycodex`.
  Evaluator input uses only `protocol_review_mode: none | focused_hardening |
  exact_final`; there is no compatibility alias and no model-generated `family_id`.

**Current task boundary.** This ExecPlan owns the 0.4.1 source, certification, release,
and personal-upgrade outcome. Existing-task successors and the 0.5 port are ordered
downstream outcomes that require fresh task-owned ExecPlans after 0.4.1 closure.

**Immutable snapshot.** Repository: `happycodex`; baseline revision:
`730c6a59d4f15eab9b40895e7ea9e0f4ee3522f5`; baseline tree:
`a7a0d228f8368244bb8799acd491646430c81ef9`; worktree:
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.4.1-convergence`;
branch: `codex/happycodex-0.4.1-convergence`; owner: Root.

**Mutable-resource ownership.** Owned now: this worktree/index, the branch above,
`evaluation/results/current.json` in this worktree, and this ExecPlan. Reserved but
read-only until their gates: a new 0.4.1 external evidence namespace, public release
refs, `/home/caichenghang/plugins/happycodex`, the personal installed cache, and the
active plugin. Other worktrees, branches, ledgers, evidence outputs, active tasks, and
the installed 0.4.0 bytes are preserved.

**Baseline check.** `python3 -m unittest discover -s tests -p 'test_*.py'` ran 123
tests in 7.656 seconds: 122 passed and one errored at
`test_verify_and_impact_commands_are_read_only_json` because the certified ledger was
stale against current inputs. Finding `F-BL-001` is resolved by the fresh 0.4.1
`refresh_required` genesis at the exact 0.4.1 snapshot; no compatibility path reads
the old ledger.

**Independent design advice.** Fable 5 session
`40eddcce-9b0a-4f27-bf87-637ea44c867e` used `claude-fable-5/max`, no tools or
network, and cost `$1.3704`. It supported the two-phase direction but is advisory only,
not product evidence or exact-final review. Its suggestions to treat ordinary commit
hashes as sufficient no-commit evidence, auto-release unreproducible security findings,
ignore accepted baseline failures, or place phase state in every finding were rejected.

**Alternatives rejected.** Sibling scan alone lacks lifecycle and recovery semantics;
an Evidence DAG risks stale-evidence reuse; a controller/full pipeline rewrite creates
a second state machine; compatibility readers, dual writes, aliases, and in-place old
task conversion enlarge the state space without helping convergence.

## Claims Ledger

| ID | Type | Claim | Closure / falsifier | Evidence | State |
| --- | --- | --- | --- | --- | --- |
| `C-01` | outcome | Single-writer ownership is scoped to overlapping mutable resources; disjoint worktrees may run concurrently. | Protocol text plus positive and collision counterexamples. | Runtime/template, public surfaces, and fixed collision replay GREEN | verified |
| `C-02` | outcome | Family hardening and frozen repair batches precede exact-final certification. | Open-family, reviewer-union, recurrence, and source-drift tests. | protocol and cumulative offline tests GREEN | verified |
| `C-03` | outcome | `protocol_may_review` is removed and receipts bind `none`, `focused_hardening`, or `exact_final`. | Shared schema, oracle, receipt, and ledger tests; no alias. | five-phase transition matrix and contradiction tests GREEN | verified |
| `C-04` | outcome | ExecPlan is a bounded current index with fail-closed Git/archive recovery. | Size, tamper, no-commit, multi-repo, and compaction tests. | current-index, no-commit, multi-repo, tamper, and compaction tests GREEN | verified |
| `C-05` | preservation | Public invocation stays `$happycodex:happycodex`; resource-scoped Root ownership and unrelated behavior remain. | Package/runtime tests and behavior comparison. | package and isolated install GREEN; live behavior comparison pending authority | open |
| `C-06` | outcome | Exact 0.4.1 release, public install, personal upgrade, and 0.4.0 rollback are proven. | Fresh evidence, three GO reviews, install/readback, rollback rehearsal. | pending | open |
| `C-07` | premise | No live evaluator call runs without a persisted exact impact receipt and direct gate-scoped user authority. | Ledger/CLI refusal and later authority receipt. | current protocol | verified |
| `C-08` | constraint | Runtime/template report the amended 300/2,600 optimization target and never exceed the 340/3,000 hard ceiling. | Contract tests compute totals and fail at hard limits; simplification review explains any target excess. | 308 lines/2,686 words after resource-scoped discovery wording; 8/86 above target, 32/314 below hard ceiling | open |

## Convergence Ledger

| Family | Invariant / boundary | Members | Scan surfaces | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `F-CONV-001` | Review eligibility is phase- and evidence-exact across Runtime, evaluator, receipts, recovery, and every consumer. | `protocol_may_review`, hardening/final distinction, source invalidation, `F-CONV-001-S01`, `F-CONV-001-S02`, exact-final checkpoint, oracle input validation, completion/write agreement | source/identity=clean-break enum; type/cardinality=three exact strings; order/terminal=one lifecycle transition table; alias/mutability/TOCTOU=no old key or stale review authority; serialization/replay=receipt and recovery; consumers/failure propagation=schema/oracle/ledger/cases | closed by focused confirmation | `RB-004` | three contradictory completion states RED then loader/matcher/receipt GREEN; focused GO | 0 |
| `F-CONV-002` | Writer uniqueness applies exactly to shared mutable resources, not globally to unrelated worktrees. | worktree, branch/ref, ledger, evidence output, activation target, paired overlap/disjoint oracles, Skill discovery metadata | source/identity=all five named; type/cardinality=one owner per overlap; order/terminal=ownership before writes; alias/mutability/TOCTOU=overlap rejects; serialization/replay=template; consumers/failure propagation=Runtime/AGENTS/public surfaces/paired behavior fixtures | closed by focused confirmation | `RB-003` | false-green/stale-frontmatter RED; anchored overlap, resolved disjoint, discovery, cumulative GREEN, and no recurrence in the next two focused scans | 0 |
| `F-CONV-003` | Current-index recovery is bounded, complete, content-addressed, and fail closed. | checkpoint chain, no-commit ref/archive, compaction, multi-repo identity, `F-CONV-003-S01`, valid/tampered/unselected archive matrix | source/identity=checkpoint/ref/digest/selection; type/cardinality=one selected locator; order/terminal=select then persist then recover; alias/mutability/TOCTOU=tamper and bare object fail; serialization/replay=exact five-phase enum including `closed`; consumers/failure propagation=Runtime/template/ledger/cases | closed by focused confirmation | `RB-004` | missing-case RED then dedicated bare-object blocker and three-way matrix GREEN; focused GO | 0 |
| `F-CONV-004` | The fresh 0.4.1 evidence inventory behaviorally exercises the new convergence protocol rather than relabeling 0.3 oracles. | protocol identity, family/repair batch, resource collision, current index, lifecycle transitions, sibling grouping | source/identity=0.4.1 corpus and holdout fixtures; type/cardinality=one owner and stable families; order/terminal=all five phases; alias/mutability/TOCTOU=collision and drift; serialization/replay=current index; consumers/failure propagation=fixed case/oracle inventory and genesis | closed by focused confirmation | `RB-004` | 17-case RED then inventory, coverage, dry-run, fresh genesis, and focused GO | 0 |
| `F-CONV-005` | Live cost authority distinguishes observed receipts from conservative proxy estimates and binds the complete current inventory. | historical receipt provenance, proxy case envelopes, impact cost basis, impact token, approval digest | source/identity=0.3 receipt hashes plus named 0.4.1 proxies; type/cardinality=one envelope per case; order/terminal=impact before authority; alias/mutability/TOCTOU=source/tool drift invalidates; serialization/replay=historical-cost and impact receipts; consumers/failure propagation=impact/ledger/live authority/tests | closed by focused confirmation | `RB-004` | mislabeled-basis RED then exact basis, 23–25 calls, approval-bound impact, and focused GO | 0 |

## Implementation and verification boundary

`RB-001` may modify only Runtime/template/maintainer protocol text, plugin version and
change notes, evaluator shared contracts and consumers, fixed offline cases/oracles,
tests, `evaluation/results/current.json` through the canonical CLI, and this ExecPlan.
It must not modify the installed/public 0.4.0 bytes, marketplace state, other worktrees,
other task ledgers, active task state, public refs, or external evidence. Product changes
begin only after this freeze commit.

RED must prove open-family final-review rejection, focused/final receipt separation,
source drift, recurrence escalation, reviewer contamination, trusted unknown safety,
accepted baseline identity, multi-repository identity, no-commit recovery, compaction
equivalence and tamper failure, family replay for snapshot/manifest/actor-receipt/
identity siblings, and parallel disjoint-resource acceptance versus overlap rejection.
GREEN requires the full offline unit suite, Ruff, both official validators, CLI dry-run,
Runtime budgets, isolated install/invocation, and compaction recovery equivalence.
Model-reaching evaluator, live corpus/holdout, public release, active installation, and
task successor creation remain later gated operations.

`RB-002` is frozen from the complete focused-review union. It may modify the same
product boundary as `RB-001` and must first add executable RED for the lifecycle
transition table, `closed` serialization, exact-final membership assertion, and fixed
0.4.1 behavioral fixtures. It then replaces the scattered phase checks with one shared
constraint, updates the fixed case inventory without adding a compatibility reader,
and creates a new fresh genesis. No exact-final review may run inside this batch.

`RB-003` is frozen from the complete second focused-review union. It may modify the
same product boundary and adds no controller, compatibility path, or model-generated
`family_id`. RED must prove that the fixed inventory can currently omit exact-final,
ignore resource ownership, ignore sibling batching, reject every no-commit archive,
accept invalid oracle states, and retain global-writer discovery wording. The repair
must bind paired positive/negative behavior to dedicated oracles and refresh genesis
only after all six members are cumulatively GREEN. No exact-final review runs inside
this batch.

`RB-004` is frozen from the complete third focused-review union. It may modify only the
shared permission constraint and its consumers/tests, fixed no-commit cases and coverage,
cost basis/envelopes, fresh genesis, and this current index. RED must prove unselected
bare-object recovery is absent, three contradictory completion/write states are accepted,
and the live impact labels proxy estimates as wholly observed. The repair adds one
dedicated recovery negative, enforces one shared bidirectional completion constraint,
binds the amended cost basis into impact/authority, and refreshes genesis once. No
exact-final review runs inside this batch.

## Checkpoint

- Milestone: exact 0.4.1 source is frozen at revision `a56f0b41c78466d180709223d414e776310b8846`, tree `be4a632c3fb40eff2907ebf46bc49e802a258a38`, product-manifest SHA-256 `981f8412f64d44af8d246255531371dd8f1478af0b45f08c873a16fc3fd608c8` excluding only this ExecPlan. All five families are closed, no repair batch or reviewer remains active, and product writes are prohibited.
- Last green: after final-version metadata, 133/133 tests passed in 8.280s; Ruff check/format, diff/JSON checks, official Skill/plugin validators, and corpus/holdout list/dry-run passed. Runtime/template remain 308 lines/2,686 words: below 340/3,000 hard limits and 8/86 above the optimization target.
- Fresh genesis: stored/current snapshots are exact for `0.4.1+codex.20260728205019`; `verify` reports `refresh_required`, engine `d9b73df6…7b20`, snapshot `f900e138…966c`, ledger `b3df9259…5d27`; full 17-case/three-pair impact is 23–25 calls, 719,051–770,869 combined tokens, and 3,757.028–4,032.239 seconds, with no authority. Its basis explicitly distinguishes 0.3 observed receipts from the three new 0.4.1 conservative single-call proxies. Impact token is `9f546507…2b28`. Origin remains `730c6a5:docs/execplans/happycodex-0-4-release.md`, never old `current.json`.
- Isolated install: `/var/tmp/happycodex-041-rb003.oyKhro` installed `0.4.1+codex.dev`; source/cache Skill SHA-256 both `fd33e911…8d6c`, source/cache manifest SHA-256 both `430f9f11…77e`, byte comparisons equal.
- Focused review prelaunch: candidate `943c47c6b8971723c0f59bcc2c0fa6d69b6e13aa`, tree `901601e47d8d0712ad8c904aaa22e01b99d597fb`, base `8099aeb05bdb5ae0aab3a9d39a3ca77c64d89b30`, product-manifest SHA-256 excluding this plan `e53f38a7…24f7`; 29 diff units listed by `git diff --name-only`. Brief is the 901-byte focused-hardening text with final LF, SHA-256 `474873b0…051e`. The first predeclared `codex review --base … -` command exited before launch because this CLI forbids a selector plus custom prompt; it produced no reviewer result. Corrected exact command: `printf '%s\n' '<brief>' | codex review -c 'model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' -c 'sandbox_mode="read-only"' - | tee /home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-943c47c.txt`; the brief itself binds the exact range. It is non-neutral, read-only, no-network, and cannot satisfy exact-final.
- Focused review terminal receipt: native session `019faa2a-f31e-7ce1-824e-b2803c55bde3`, effective `gpt-5.6-sol/max`, approval `never`, read-only sandbox, output SHA-256 `bc541ae0…c7bc`. Verdict `NOT YET`: `F-CONV-001-S01`, `F-CONV-004`, `F-CONV-003-S01`, and `F-CONV-001-S02`. Root reproduced completion/mode disagreement, accepted `exact_final` plus active writes, rejected `closed`, absent 0.4.1 fixtures, and the constant-truth assertion.
- Second focused-review prelaunch: exact repair range `943c47c…13aa..8bb7ce9…09e8`; candidate tree `3936dbe9…9fbc`; product-manifest SHA-256 excluding this plan `619e80db…8d21`; 1,134-byte/131-word brief with final LF, SHA-256 `1d051dac…8a62`; output `/home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-8bb7ce9.txt`. Command: `printf '%s\n' '<brief>' | codex review -c 'model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' -c 'sandbox_mode="read-only"' - | tee /home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-8bb7ce9.txt`.
- Second focused-review terminal receipt: native session `019faa4b-1c81-7fd1-9d34-d9d85ab417bb`, effective `gpt-5.6-sol/max`, approval `never`, read-only sandbox, output 4,587 bytes/501 words, SHA-256 `2ae6488e…23e5`. Verdict `NOT YET`: exact-final has no positive checkpoint/oracle; resource collision is prose-only and lacks a disjoint positive; family/batch labels do not affect action; no-commit has no valid-archive/tamper contrast; case loading accepts invalid review states; Skill discovery still says unqualified one writer. Root reproduced each counterexample. During review the bundled `rg` changed from 15.1.0 to 15.2.0, invalidating the stored toolchain snapshot independently of product source.
- Third focused-review prelaunch: exact repair range `8bb7ce9…09e8..b88300a…ceda`; candidate tree `ee3be17a…cb95`; product-manifest SHA-256 excluding this plan `e6732ca8…091a`; 1,238-byte/135-word brief with final LF, SHA-256 `a5ca448d…4cba`; output `/home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-b88300a.txt`. Exact command: `printf '%s\n' '<brief>' | codex review -c 'model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' -c 'sandbox_mode="read-only"' - | tee /home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-b88300a.txt`. It is history-aware, non-neutral, read-only/no-network, and cannot satisfy exact-final.
- Third focused-review terminal receipt: native session `019faa64-44be-7b90-b080-f5e7581f04f0`, effective `gpt-5.6-sol/max`, approval `never`, read-only sandbox, output 2,076 bytes/233 words, SHA-256 `bde08ef6…9ee`. Verdict `NOT YET`: the selected-valid/tampered archive pair lost the unselected/bare-object negative; completion decision, permission, and write states disagree in the shared loader/receipt path; live impact labels conservative proxy costs as wholly observed. Root reproduced all three. Reviewer tests had 129/129 writable-independent tests GREEN; three sandbox-isolation tests could not write under the deliberately read-only review profile and are not product failures.
- RB-004 RED: targeted five-test run produced eight failures and one error: all three contradictory permission states were accepted, shared receipts accepted the contradictions, the unselected recovery case was absent, and the fixed snapshot/impact still contained 16 cases.
- Fourth focused-review prelaunch: exact repair range `b88300a…ceda..00a48e3…6271`; candidate tree `11f33b63…bd0f`; product-manifest SHA-256 excluding this plan `3d982fad…2b57`; 1,079-byte/116-word brief with final LF, SHA-256 `1c2aa420…eae`; output `/home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-00a48e3.txt`. Exact command: `printf '%s\n' '<brief>' | codex review -c 'model="gpt-5.6-sol"' -c 'model_reasoning_effort="max"' -c 'sandbox_mode="read-only"' - | tee /home/caichenghang/.codex/happycodex-0.4.1-reviews/focused-00a48e3.txt`. It is history-aware, non-neutral, read-only/no-network, and cannot satisfy exact-final.
- Fourth focused-review terminal receipt: native session `019faa76-dcce-77f1-95f8-c5c5b53be02a`, effective `gpt-5.6-sol/max`, approval `never`, read-only sandbox, output 225 bytes/30 words, SHA-256 `7db1188b…7899`. It independently exercised the three recovery outcomes, all three shared permission consumers, the 17-case impact, and the approval-bound mixed cost basis; verdict `GO`.
- Finalization: plugin-creator cachebuster helper changed only the manifest version from `0.4.1+codex.dev` to `0.4.1+codex.20260728205019`; README already carries the synchronized 0.4.1 change note. Fresh genesis and cumulative checks bind the frozen source above.
- Owned dirty paths: this administrative candidate-frozen checkpoint only. Product source is clean and frozen; old evidence files remain untouched.
- Goal: none.
- Agents/reviewers: all three focused reviewers terminal and reconciled; no reviewer active.
- Pending gates: fresh post-source evidence and exact isolated install, exact-final
  reviews, any separately
  authorized live behavior evaluation, public release, personal upgrade, rollback, and
  downstream successor task creation.

## Retrospective

Fill only after closure; never expose it as review evidence.
