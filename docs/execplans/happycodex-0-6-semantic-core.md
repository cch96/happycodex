# HappyCodex 0.6 Semantic Core

Protocol: `HappyCodex/0.5`

Current index: contract frozen; implementation and every external gate remain open.

Restore guard: restore this ExecPlan, then reconcile Git, the fixed Executor,
resource claims, active grant, receipts, checks, agents, and any Goal before any
write, review, or completion claim.

Phase: `implementation`, with no active implementation grant. The independent
Challenger has been unioned and Root reproduced the union. The revision carrying
this update is the distinct contract-freeze revision. The contract below is now
implementation-frozen: changing the Outcome/baseline, removing or narrowing a
claim, widening a break, using `N/A`, changing a central type/invariant, or changing
the frozen caller/deletion/RED inventory requires explicit user authority and
reopens dependent evidence.

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

Current in-thread continuation, verbatim:

```text
继续
```

UTF-8 request plus final LF SHA-256:
`790ce365c093c6985803e513abf11eb5c5a24ed1164a5eab7e78c80f94642969`.
It continues the existing Outcome and G-002 without changing scope or authority.

Authority correction: the message `是不是可以执行了` (UTF-8 plus final LF
SHA-256
`0c1ffecbc1cd46d86c87886defdd97bbae4d919d2ef53e2392f7b15756a8fe45`)
came from unrelated source thread
`019f87b2-9aec-7fe1-9abf-8f6edbf15057`. It is rejected as non-authoritative and
is not a request, amendment, continuation, contract basis, grant, waiver, or
evidence for this task. No Outcome, claim, scope, or rerun changed because of it.

Normalized Outcome authorized by Root, verbatim:

```text
create an independent bounded-clean-break HappyCodex 0.6 source line from released public main, combining Runtime cadence simplification with a typed stateless evaluator semantic core. Preserve strict authority/capability/attempt-consumption/resource-claim/cost/holdout infrastructure. No compatibility reader, migration, alias, dual write, or fallback. This authority does NOT authorize live model/corpus/holdout execution, release, install, activation, marketplace mutation, or active-plugin mutation.
```

Normalized Outcome plus final LF SHA-256:
`8d57c106322fd0231382e995940ec9ff89bbca7756eb14cf4e57dedfe11b25f4`.

The requested auxiliary Fable 5 design audit is already complete. It inspected
detached snapshot `7a548a3` in read-only session
`16bbe15f-6ad9-4bd4-b547-a8dddda8b5d5` using Claude Code `2.1.220`,
`claude-fable-5/max`, for approximately 311 seconds and `$2.957`. It is design
input only, not current-candidate review, evaluator evidence, or certification,
and it must not be repeated for this contract. Fable is not a 0.6 provider,
adapter, Runtime feature, or completion gate.

The audit found two material design defects:

- `MF-06-001`: the plan fingerprint had six fields while Runtime/tests used seven,
  with required action as the seventh;
- `MF-06-002`: a phrase-only stagnation oracle could pass after cosmetic
  rewording.

Both are resolved at the contract level by the typed `StateKey`, `Decision`, and
`AttemptKey` definitions below. Required decision/action inputs are structural
tagged fields, never prose or phrase presence. Implementation evidence remains
open under `O-06-01` and `O-06-02`.

## Review union and contract-freeze authority

The independent Challenger returned `GO-WITH-CONDITIONS`. It remained read-only
and ran only:

```text
python3 -m evaluation.cli verify
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
```

The ledger remained `refresh_required`; dry-run inventory was 17 corpus cases and
three holdout pairs. No live corpus/holdout/model evaluator call or repository
mutation occurred. Root independently reproduced the source/caller union,
conditions, dry-run boundaries, and the two auxiliary-audit findings. The
conditions are frozen as the architecture, inventory, deletion set, authority
profiles, comparator, cadence, and RED/closure matrix below. Root retained the
Challenger dispatch/terminal identity receipt; no unstated session identity is
invented in this plan.

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

## Frozen scope and non-goals

The initially authorized design scope is:

1. simplify Runtime cadence and convergence semantics where a clean redesign
   removes real semantic complexity;
2. define one typed, stateless evaluator semantic core so impact planning,
   execution validation, evidence classification, and replay do not encode
   divergent meanings; and
3. preserve the safety infrastructure below while removing compatibility-only
   or duplicated semantic paths.

The detailed contract, typed model, caller inventory, schema boundary, deletion
set, Runtime cadence, and implementation sequence are frozen below. Later
implementation may choose only mechanical internal decomposition that does not
change observable types, call direction, ownership, authority, deletion targets,
or oracles. A design choice is not “mechanical” if it changes a hash preimage,
parser acceptance, decision projection, retry boundary, gate, provider profile,
receipt, caller, or deletion. Such a choice returns to Root before any write.

Non-goals in the current Outcome and bootstrap are Fable as a product feature,
compatibility behavior, release engineering, publication, installation,
activation, marketplace changes, active-plugin changes, deployment, or migration
of an existing task/evidence ledger.

## Frozen architecture and call direction

The only architecture is:

```text
Codex / Git / filesystem adapters
  -> strict parse
  -> immutable provider-neutral semantic package
  -> pure reduce
  -> CanonicalReport + recomputed StateKey + Decision
  -> pure projection / replay
  -> canonical receipt / impact / holdout / certification consumers
```

Exact new module paths and classifications:

| Path | Classification | Sole responsibility |
| --- | --- | --- |
| `evaluation/semantic/__init__.py` | semantic | closed public exports only |
| `evaluation/semantic/types.py` | semantic | frozen tagged types, enums, validated scalar identities |
| `evaluation/semantic/schema.py` | semantic | exact field/tag/cardinality schemas and terminal schema projection |
| `evaluation/semantic/canonical.py` | semantic | canonical bytes, domain-separated hashes, `StateKey`, `AttemptKey`, receipt-link hash |
| `evaluation/semantic/parse.py` | semantic | strict parsing of cases, holdouts, ledger, terminal, adapter facts, and model observations |
| `evaluation/semantic/reduce.py` | semantic | pure derivation of findings, blockers, gates, and the one `Decision` |
| `evaluation/semantic/project.py` | semantic | pure `CanonicalReport` projections for impact, receipt, ledger, and certification |
| `evaluation/semantic/replay.py` | semantic | pure receipt-chain, terminal, report, attempt, and evidence replay |
| `evaluation/semantic/holdout.py` | semantic | pure blind decision validation, reveal replay, adaptive policy, quality and cost comparison |
| `evaluation/adapters/__init__.py` | harness | closed adapter exports only |
| `evaluation/adapters/codex.py` | harness | sole model-provider adapter, effective-profile parsing, prompt rendering, terminal extraction |
| `evaluation/adapters/git.py` | harness | Git object/ref/tree/reachability/evidence reads only |
| `evaluation/adapters/filesystem.py` | harness | exact file/input/output loading and atomic writes only |
| `tests/test_semantic_core.py` | test | the frozen RED/closure matrix |

`evaluation/semantic/**` may import only side-effect-free standard-library modules.
It must not read files, environment variables, clocks, randomness, subprocesses,
sessions, Git state, network, or mutable globals, and it must not call or import an
adapter. No semantic function mutates an argument. All collections are immutable
tuples or frozen mappings after strict parse. Adapters may import semantic types and
parsers; imports never point in the reverse direction.

Call direction is exact:

1. `evaluation/cli.py`, `evaluation/live.py`, and the corpus/holdout engines select
   a command but decide no semantics.
2. `evaluation/adapters/{codex,git,filesystem}.py` obtain raw bytes/facts and pass
   them to `evaluation.semantic.parse`; adapters never construct a trusted semantic
   object by hand.
3. `parse.py` returns immutable `MachineFacts`, `ModelObservation`, typed case or
   holdout inputs, and typed ledger/receipt records.
4. `reduce.py` is the sole authority for `ControlBlocker` and `Decision`.
5. `canonical.py` recomputes keys from canonical typed inputs; `project.py` emits
   the one `CanonicalReport` and consumer projections.
6. `receipt.py`, `impact.py`, `ledger.py`, `semantic/holdout.py`, and certification
   validators consume those projections; none reparse dicts or redefine semantics.
7. `replay.py` reuses the same parsers/reducer/projectors and compares exact
   canonical objects. Planning, execution, and replay call the same case and holdout
   loaders and strict parser.

0.6 implements one model-provider adapter: Codex. There is no Claude adapter.
Claude/Fable observations above remain reference-only design input.

## Frozen semantic types

All identifiers are validated tagged scalars, not bare interchangeable strings.
Digests are lowercase 64-hex SHA-256; Git commits/trees are lowercase 40-hex;
sequences are nonnegative integers; enum spellings below are exact.

`MachineFacts` has exactly these semantic fields:

- `schema_generation = 6`;
- `source`: commit, tree, package semantic/artifact, engine manifest, and config
  digests;
- `candidate`: absent or the same exact identity tuple plus detached snapshot
  identity;
- `executor`: provider, exact durable session, thread, owner label, external role
  config digest, actual model/effort/tool-surface digest, permission-profile
  digest, and canonical write scope;
- `claimed_resources`: sorted exact canonical resource claims and owner-token
  digest;
- `goal`: typed Goal lifecycle, objective digest, and exact Outcome-match result;
- `gates`: sorted `GateId`/gate-state facts;
- `checks`: sorted check identity, command digest, result state, candidate identity,
  and receipt;
- `accepted_evidence`: sorted exact `EvidenceRef` values;
- `invocation_profile`: absent or the strictly observed effective invocation
  profile, including provider/binary/model/effort/timeout/tool/network/MCP/hook/
  session settings;
- `authorities`: zero or one record for each exact `AuthorityScope`;
- `infrastructure_transitions`: ordered typed start/fail/replace/recover events
  with prior/new envelope and authority identities; and
- `receipt_head`: absent or exact sequence and previous-link hash.

No field is inferred from model prose. Source/candidate/Executor/resource/Goal/check/
authority/profile/infrastructure facts come only from strict adapters and persisted
receipts.

`ModelObservation` contains only:

- `observations`: bounded sanitized observations; and
- `proposed_findings`: proposed typed findings.

It has no authority, permission, decision, gate-state, next-action, retry,
completion, writer, resource, Goal, invocation, or lifecycle fields. Any such key
in model output is unknown input and fails strict parse.

`Finding` has exactly:

- `finding_id: FindingId`, globally exact and nonblank;
- `status: OPEN | UNKNOWN | RESOLVED | BASELINE_ACCEPTED`;
- `anchors`: a nonempty sorted tuple of the tagged union below;
- `claim`: bounded sanitized text;
- `falsifier`: bounded sanitized text; and
- `evidence`: sorted exact `EvidenceRef` values.

`RESOLVED` can never block. `BASELINE_ACCEPTED` requires exact user authority and
baseline identity. The anchor union is:

- `RepoPath(repository_id, path)`: repository-qualified, root-relative,
  case-sensitive POSIX path; no basename, suffix, casefold, glob, or normalization
  alias;
- `Marker(marker_id)`: exact typed marker, not surrounding prose;
- `Digest(kind, sha256)`: exact tagged digest;
- `Receipt(receipt_kind, sha256)`: exact receipt identity.

`ControlBlocker` is derived only by `reduce.py` from `MachineFacts` and typed gates.
Its fields are `blocker_code`, optional `GateId`, optional exact `FindingId`, and
typed evidence anchors. A semantic blocker may reference one exact `FindingId`;
model output cannot create, remove, classify, or clear a `ControlBlocker`.

Exact enums:

- `GateId`: `CONTRACT_FREEZE`, `IMPLEMENTATION`, `CUMULATIVE_CHECKS`,
  `FOCUSED_REVIEW`, `CANDIDATE_FREEZE`, `EXACT_FINAL`, `EXECUTOR_PILOT`,
  `CORPUS`, `HOLDOUT`, `RECEIPT`, `ISOLATED_INSTALL`, `RELEASE`,
  `ACTIVATION`, `GOAL_PAUSE`;
- `GateState`: `OPEN`, `SATISFIED`, `WAIVED`, `BLOCKED`;
- `EvidenceKind`: `SOURCE`, `CONFIG`, `AUTHORITY`, `CHECK`, `CORPUS`,
  `HOLDOUT`, `REVIEW`, `RECEIPT`, `OFFLINE_SUMMARY`, `INSTALLATION`,
  `RECOVERY`, `COST`;
- `AuthorityScope`: `EXECUTOR_PILOT`, `CORPUS`, `HOLDOUT`;
- `Arm`: `CANDIDATE`, `PUBLIC_0_2`;
- `GoalState`: `NONE`, `ACTIVE`, `PAUSED`, `COMPLETE`, `CLEARED`;
- `CheckState`: `PASS`, `FAIL`, `BASELINE_ACCEPTED`;
- `GrantState`: `BOUND_IDLE`, `GRANTED`, `INTENT_RECORDED`, `APPLYING`,
  `RECONCILING`, `RECEIPTED`, `CLOSED`, `FAILED_CLOSED`;
- `AttemptState`: `AVAILABLE`, `CONSUMED`, `INFRASTRUCTURE_FAILED`,
  `SUCCEEDED`; and
- `InfrastructureTransitionKind`: `STARTED`, `FAILED`, `REPLACED`,
  `RECOVERED`;
- `CompletionTag`: `COMPLETE`, `BLOCKED`, `REFUSED`.

There is one authoritative `Decision` enum:

`DISCOVER`, `RECONCILE`, `IMPLEMENT_BATCH`, `VERIFY`, `FOCUSED_REVIEW`,
`EXACT_FINAL`, `ASK_USER`, `FREEZE_CANDIDATE`, `CLOSE`, `REFUSE`.

Every phase label and permission boolean is a pure projection of `Decision`; none
is persisted independently. `Decision` is necessary but never sufficient for a
side effect: the exact grant, authority, fixed Executor, resource claim, and
capability must also validate. Projection rules are:

| Decision | Allowed semantic action |
| --- | --- |
| `DISCOVER` | read-only inventory only |
| `RECONCILE` | read/compare and an already-authorized exact finish/undo only |
| `IMPLEMENT_BATCH` | fixed-Executor writes inside one exact grant |
| `VERIFY` | exact granted checks; no new product design |
| `FOCUSED_REVIEW` | one read-only material-unknown review |
| `EXACT_FINAL` | one fresh neutral read-only exact-candidate review |
| `ASK_USER` | stop and request decision; no write/review |
| `FREEZE_CANDIDATE` | exact granted detached candidate snapshot only |
| `CLOSE` | exact granted administrative closure only |
| `REFUSE` | terminal fail-closed, no effect |

`CanonicalReport` is sanitized and persistable by construction. It contains the
validated `MachineFacts`, accepted typed findings, derived blockers, the single
`Decision`, exact evidence references, and receipt head. Sanitized text uses a
bounded `SafeText` constructor; raw events, hidden prompts/oracles, secrets, and
unvalidated dictionaries cannot inhabit the type. The same semantic object is
consumed by receipt, replay, ledger, impact, holdout, and certification; consumers
may project fields but cannot add semantic meaning.

## Canonical state, attempts, ordering, and capacity

Canonical encoding is domain-separated UTF-8 JSON with sorted object keys, explicit
union tags, strict integers/booleans, no NaN, and no implicit coercion. Collections
declared as sets are sorted by exact typed canonical identity; semantically ordered
sequences retain order. Permutation search, permutation caps, basename/suffix/
casefold matching, fuzzy identity, and unordered digest alternatives are deleted.

`StateKey` is:

```text
SHA256("happycodex/0.6/state-key\0" +
       canonical(MachineFacts, typed findings, ControlBlockers,
                 candidate identity, accepted evidence,
                 required Decision inputs))
```

Required decision inputs include the typed required action/target. This structurally
resolves the prior six-versus-seven fingerprint mismatch. Load and replay always
recompute `StateKey`; no independently editable persisted state/fingerprint digest
is authoritative. A serialized derived key, if emitted in a receipt, must equal the
recomputed key or fail.

`AttemptKey` is:

```text
SHA256("happycodex/0.6/attempt-key\0" +
       canonical(StateKey, Decision variant, exact target/scope,
                 falsifier identity, evidence-source identity))
```

It is atomically consumed with `O_EXCL` before fixture creation, mapping, output
claim, workspace mutation, or subprocess work. Random attempt IDs, rewording,
turn/time changes, and a new process cannot bypass consumption. Retry is legal only
after an explicit `REPLACED` infrastructure transition changes `MachineFacts` and
binds a new envelope plus new exact authority; ordinary semantic failure consumes
the attempt permanently.

Receipt links contain exact `sequence`, `previous_hash`, `report_hash`,
`AttemptKey`, and `EvidenceKind`. Sequence starts at zero and increments by one;
`previous_hash` is absent only at genesis. The link hash covers all fields and the
prior link. A cursor carries only content-addressed location/completeness metadata
(path/object, byte count/offset, item count); it is never semantic progress.

Canonical sorted hashing replaces permutation matching and semantic caps. There is
no silent eviction. Any explicitly configured transport/schema capacity is part of
`MachineFacts`; overflow creates a typed blocker and yields `RECONCILE` or
`ASK_USER`, never truncation, eviction, false equality, or automatic retry.

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

## Frozen caller, input, and deletion inventory

Every path below is in the implementation contract. “Keep” means keep imperative
I/O or a typed consumer, not preserve its current duplicated semantics.

| Existing path/input | 0.6 producer/consumer disposition |
| --- | --- |
| `evaluation/core/identity.py` | keep tool/package/Git-independent byte identity acquisition; import canonical hashing; classify every exact Python/JSON input; unknown fails |
| `evaluation/core/impact.py` | keep snapshot/impact orchestration and cost envelope; consume typed schemas and projections; delete local dict/schema semantics |
| `evaluation/core/ledger.py` | keep ledger/Git evidence loading and certification I/O; replace dict-schema/replay/permission/identity piles with strict parse and pure replay |
| `evaluation/core/receipt.py` | keep atomic canonical output write; delete manual semantic sanitizers and accept only `CanonicalReport` projections |
| `evaluation/corpus/contract.py` | migrate terminal/state/identity/permission/schema semantics, then delete the file |
| `evaluation/corpus/engine.py` | keep fixture I/O, concurrency, subprocess orchestration, capability rebind, and result collection; remove case/oracle/recovery/identity/permission semantics |
| `evaluation/holdout/blind.py` | keep randomness, sealing, alias assignment, and commitment I/O at the blind adapter; remove semantic validation and comparison |
| `evaluation/holdout/compare.py` | migrate pure policy to `evaluation/semantic/holdout.py`, then delete the file |
| `evaluation/holdout/engine.py` | keep pair/arm orchestration, capability rebind, external raw records, and canonical receipt write; consume typed holdout policy |
| `evaluation/live.py` | keep command orchestration, immutable capability mint/rebind, and `O_EXCL` attempt claim; replace bundled authority and random attempt IDs |
| `evaluation/cli.py` | remain the only evaluator CLI; expose `verify`, `impact`, `executor`, `corpus`, and `holdout` through strict typed inputs |
| `evaluation/{core,corpus,holdout}/__init__.py`, `evaluation/__init__.py` | export only the frozen ownership boundaries; no alternate parser/reducer |
| all 17 `evaluation/cases/*.json` inputs | rewrite to the generation-6 case schema and parse through the same loader for impact/execution/replay |
| `evaluation/holdouts/manifest.json` and all three `evaluation/holdouts/cases/*.json` inputs | rewrite to generation-6 typed holdout schemas and the public-0.2 comparator |
| `evaluation/results/current.json` | replace with one fresh generation-6 `refresh_required` genesis; no migrated authority/evidence/history |
| current `evaluation/results/evidence/*.json` files | delete from the active 0.6 tree; retain only inert Git history, unreachable by the active parser |
| `evaluation/README.md` | document the exact typed flow, classifications, CLI-only entrypoint, three authority gates, public-0.2 comparator, and no-live default |
| `skills/happycodex/SKILL.md` | simplify ordinary cadence and use the exact `Decision` vocabulary; no evaluator module link or Runtime engine |
| `skills/happycodex/references/execplan.md` | project the typed decision/current checkpoint and consumed attempts without another state machine |
| `skills/happycodex/scripts/resource_claim.py` | preserve as the imperative atomic resource-claim helper; no semantic package dependency |
| `AGENTS.md` | bind 0.6 clean-break/fresh-genesis/CLI/budget/provider/release rules |
| `README.md` | explain ordinary-session versus maintainer-evaluator payoff and the independent 0.6 line |
| `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/happycodex/agents/openai.yaml` | update only source/package identity and accurate public interface under a later package grant; no install or marketplace-state mutation |
| `tests/test_certification_engine.py` | migrate identity/impact/genesis/authority/capability/attempt/certification controls |
| `tests/test_evaluation.py` | migrate case, terminal, recovery, identity, permission, event, and oracle controls to typed semantics |
| `tests/test_holdouts.py` | migrate blind/reveal/adaptive/cost/replay and public-0.2 controls |
| `tests/test_contracts.py` | freeze Runtime decision/recovery/cadence/budget and package surfaces |
| `tests/test_resource_claim.py` | retain atomic overlap/disjoint/common-dir/adjacency/tamper coverage |
| new `tests/test_semantic_core.py` | own the direct pure-type/parser/reducer/key/replay RED matrix |

The 17 exact case IDs are `authorized-rebaseline`, `boundary-cutover`,
`clean-qualifying-control`, `compaction-recovery`, `exact-final-ready`,
`goal-divergence`, `midflight-escalation`, `multi-repo-submodule`,
`no-commit-archive-recovery`, `no-commit-secret`, `no-commit-unselected`,
`pre-freeze-compaction`, `receipt-mismatch`, `review-admin-cycle`,
`review-inventory-gate`, `review-isolation`, and `subthreshold-control`.
The exact holdout IDs are `authority-production-boundary`,
`destructive-migration-fallback`, and `local-documentation-control`.

Every evaluator Python/JSON input is classified exactly as `semantic`, `harness`,
or `artifact` in `identity.py`. All `evaluation/semantic/*.py`, cases, holdout
manifest/cases, and their typed schema projection are semantic; adapters, CLI,
live orchestration, and engines are harness; canonical receipt serialization is
artifact. Evidence outputs are outputs, never inputs. A new or missing Python/JSON
path, unknown field/tag/enum, duplicate identity, or classification disagreement
fails closed during both impact planning and execution.

Explicit semantic deletions are frozen:

- manual semantic sanitizers in `receipt.py`;
- semantic replay and dict-schema validation piles in `ledger.py`;
- case/oracle/recovery/identity/permission semantics in `corpus/engine.py`;
- semantic validation from `holdout/blind.py`;
- `evaluation/corpus/contract.py` after migration;
- `evaluation/holdout/compare.py` after policy migration;
- free-text gates and phrase-presence acceptance;
- basename, suffix, casefold, fuzzy, permutation, or multiple-digest identity
  aliases;
- duplicated persisted semantic/fingerprint digests;
- independently persisted `protocol_may_*`, phase, review-mode, or permission
  flags;
- bundled `live_authority` or any authority containing multiple invocation scopes;
- random `live_attempts` as retry identity;
- every `engine_generation` 0.4 literal and active public-0.4 comparator reader;
- 0.4/0.5 current-ledger baseline readers; and
- all compatibility readers, migrations, aliases, dual writes, fallbacks, and
  prior evidence/coverage reuse.

Imperative boundaries explicitly retained are adapter I/O, immutable capability
mint/rebind, `O_EXCL` attempt and resource claims, Git evidence loading, filesystem
atomic writes, bounded corpus/arm concurrency, and randomness/sealing in the blind
adapter. Raw model events stay outside the repository.

## Fresh 0.6 genesis and active-evidence boundary

The replacement `evaluation/results/current.json` is a new schema-generation-6
object with exact top-level fields: `schema_version`, `engine_generation`,
`state`, `source`, `snapshot`, `pending_gates`, `authorities`,
`calibration_history`, `accepted_evidence`, `receipt_head`, and `certification`.
At genesis:

- `schema_version` is `6`, `engine_generation` is `"0.6"`, and state is
  `refresh_required`;
- source/snapshot bind the reachable frozen 0.6 source, classified engine manifest,
  package/config identities, and exact effective settings;
- `pending_gates` is the sorted typed set derived from changed 0.6 inputs;
- `authorities` has exactly `executor_pilot`, `corpus`, and `holdout`, each null;
- `calibration_history` is empty; the pilot has no invented historical cost;
- `accepted_evidence` is empty, `receipt_head` is absent, and certification is
  null.

Old evidence remains inert Git history only. No active generation-6 locator can
name it, and strict parse rejects an old generation, old schema, or pre-source
evidence. Every new evidence commit strictly postdates the frozen source. Offline
receipt/install summaries are content-addressed and strictly post-source but cannot
promote `refresh_required` by themselves.

## Writer, authority, provider, isolation, and terminal envelope

Evaluator recovery accepts only the exact fixed Executor provider/session/thread,
owner label, external role-config digest, actual model/effort/tool profile,
permissions, and resource scope already bound in `MachineFacts`. Only the same
durable session may recover. Root, `unknown`, replacement, concurrent resume, a
fork, a copied handle, or a second owner fails to `REFUSE`; there is no fallback
Executor.

Three authorities are separately persisted and separately consumed:

| Scope | Authority and attempt rule |
| --- | --- |
| `EXECUTOR_PILOT` | one exact candidate/config/profile/write-scope invocation and one `AttemptKey`; persist the complete invocation and source-derived conservative calibration envelope before requesting separate exact authority; sanitized successful actual cost becomes its historical basis |
| `CORPUS` | one exact candidate/profile/case-set/arm/output invocation and one `AttemptKey` |
| `HOLDOUT` | one exact candidate/public/profile/pair-set/output invocation and one `AttemptKey` |

There is never one authority containing multiple invocations or scopes. Each
authority binds the exact current `StateKey`, impact token, package/config/tool
identities, model, effort, timeout, arm, output, complete command, approval-request
digest, and canonical affirmative user response. Persisting identity grants no
permission. This contract carries no live authority.

Two Codex profiles are exact and non-interchangeable:

1. Executor: provider `codex`, `gpt-5.6-sol/high`, the unique durable session and
   recovery identity, external protected role-config digest, inherited exact
   permission profile, and the grant's canonical write scope. Session continuity
   is mandatory.
2. Neutral reviewer: provider `codex`, `gpt-5.6-sol/max`, one fresh detached exact
   candidate, no session persistence, hooks, Agent, Bash, Edit, Write, Web,
   network, MCP, provider fallback, or original worktree/history access. Its
   external tool surface is empty; native review receives the exact detached
   source/diff and neutral packet.

The Codex adapter strictly parses and hashes the effective settings, resolved
binary path and bytes, reported model/effort, session/thread/turn, permissions,
tool surface, hook/network/MCP state, and fallback status. A configured allowlist
or requested profile is not proof. Ignored/invalid settings, unavailable host
evidence, rerouting, or fallback fails closed.

A worktree is not isolation proof. Under a future exact grant the Executor manually
creates a detached candidate from the frozen commit, verifies commit/tree/product
manifest, and claims the Git common-dir worktree identity, one private candidate
ref, exact output namespace, and ledger. The grant resolves every absolute path and
ref; no implicit temporary/default location is allowed. Review consumes only that
detached snapshot.

Codex terminal grammar permits exactly one schema-generation-6 terminal object
bound by adapter facts to the exact provider/session/thread/turn and `AttemptKey`.
It contains one legal `ModelObservation` and exactly one `CompletionTag`:
`COMPLETE`, `BLOCKED`, or `REFUSED`. Missing, malformed,
duplicate, contradictory, unbound, or late semantic output fails; any bytes after
the terminal are raw-stream protocol failure. Raw stream and its byte/hash receipt
stay external. Hooks and events are adapter inputs only, never semantic authority or
a second state machine.

There are no agent teams, Claude adapter, plugin-evaluation certification,
publish-report, ultrareview, ordinary-task event queue, scheduler, controller,
daemon, or second persistence protocol.

## Holdout comparator and replay

The sole comparator configuration is public HappyCodex 0.2:

- commit `3b9c11fac1f97df75263e0bfc6421c575e04e8b2`;
- tree `4708ebc12f74d4482764796fdd00f1fa7194a13a`;
- semantic SHA-256
  `fb3cb419795a6edcb284695769b5487b1f23ae46286c5fceba8042fcb41f9ce4`;
- artifact SHA-256
  `77a0b2b8f7f6280d6ed32458fc61ca110f7138b5b6c17ad55d333a023dfa8c89`;
- Skill SHA-256
  `aa090bbd0d7af6e6ac05e5afc959ee93268393f8621bd5ebf00e745d04e3ce55`.

This identity is reusable comparator configuration. Its prior evidence, coverage,
receipts, or decisions are never reused.

Each holdout receipt retains a sanitized replay record: pair ID, typed input and
policy identities, canonical blinded views, the frozen decision, reveal commitment,
and—after reveal—the exact sanitized commitment preimage containing alias-to-`Arm`
mapping plus nonce, followed by metrics and outcome. That preimage must recompute
the commitment and is sufficient for pure decision/reveal replay without raw model
events. Planning, execution, and replay use the same filesystem loader, strict
manifest/case parser, semantic holdout policy, and canonical projections.

The first completion-blocking candidate regression rejects immediately. After a
first success, run a second distinct pair. Run the third only for split or uncertain
results. At equal quality, uncached input plus output tokens and wall time must each
be at most 125% of public 0.2. Candidate failure is regression; persistent
uncertainty cannot release.

## Runtime cadence, recovery, and payoff

Runtime cadence is independent of evaluator/model latency. One invariant-family
RED seed matrix is frozen before repair. The fixed Executor then performs one
bounded repair wave:

1. run the pre-enumerated RED for each granted slice;
2. make the coherent slice change and run only its focused checks;
3. add a newly discovered same-family sibling to the existing wave only after Root
   expands exact path authority and it has a distinct RED;
4. run the cumulative check once at terminal GREEN; and
5. stop immediately on contract, prestate, caller, or oracle divergence.

Root accepts each mandatory grant receipt but performs one semantic checkpoint per
repair batch, not a new design/review/checkpoint loop per slice. Recurrence/boundary
machinery activates only for a Root-confirmed material recurrence after terminal
GREEN. Focused review runs only for a nonmechanizable material unknown. One fresh
neutral exact-final runs after candidate freeze; any candidate product change
invalidates it.

No editable five-phase state, review-mode field, `protocol_may_*` flag, or separate
permission ledger exists. The typed `Decision` is authoritative. Ordinary Runtime
reconciles canonical durable facts, blockers, and consumed `AttemptKey` values; it
adds no event queue, timer-derived progress, or evaluator process.

The ordinary-session payoff is fewer repeated handoffs, reviews, checks, and
checkpoints under unchanged facts. The evaluator-only maintainer/release payoff is
shared parsing/replay, fresh evidence, exact provider/authority validation, and
blinded comparator proof. Evaluator latency/certification cost does not justify an
ordinary-task Runtime step.

Aggregate Runtime Markdown—`skills/happycodex/SKILL.md` plus
`skills/happycodex/references/execplan.md`—must stay at or below 262 lines, target
at or below 2,200 words, and hard-fail above 2,400 words. Compression cannot remove
an asserted contract phrase, central type, gate, or recovery boundary.

## Writer binding, resource claims, and grant reconciliation

Root is read-only. The fixed writer is canonical task `/root/executor`, selected
role `happycodex_executor`, effective contract `gpt-5.6-sol/high`, and owner label
`happycodex-0.6-semantic-core-executor`. Root independently retained the host/config
binding receipt. Identity or configuration drift fails closed and permits no
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
commit content. It remains claimed after this freeze and must be accounted for
or explicitly released under a future reconciliation grant.

Bootstrap grant `HC06-G-001-bootstrap`, sequence 1, authorizes only exact base and
conflict checks; branch/worktree creation; the three-resource claim; this
ExecPlan skeleton; staging this file alone; one skeleton commit with the mandatory
trailer; verification; and external intent/receipt control records. Its first
durable intent is
`/home/caichenghang/.codex/happycodex-0.6-semantic-core-bootstrap-intent.json`,
SHA-256
`c665dcf919ff6c8dd432ba513c89c1de4883093627078e8a1b6e9da9057355df`.
Terminal receipt:
`/home/caichenghang/.codex/happycodex-0.6-semantic-core-bootstrap-receipt.json`,
SHA-256
`0c250365935e5b94bad6345a4c61dbf5d4968343da8c0e87cd2f51819acdf808`.
Root independently read back commit
`5f6c508503563ab62444b33d64efeac9cbb34826`, tree
`61b2cc9a36e268bf1aa2b530eec140a666fc9a42`, exact base parent, one committed
plan path, active verified claim, and unchanged public main/0.5.1 worktrees. Root
accepted G-001. G-001 is `CLOSED` and non-renewable.

Contract-freeze grant `HC06-G-002-contract-freeze`, sequence 2, binds prestate
`5f6c508503563ab62444b33d64efeac9cbb34826` /
`61b2cc9a36e268bf1aa2b530eec140a666fc9a42`, with the claim directory as the sole
status entry. It authorizes only external intent/receipt, this plan edit, one-path
stage, one commit with the mandatory trailer, and verification. Durable intent:
`/home/caichenghang/.codex/happycodex-0.6-semantic-core-g002-intent.json`,
SHA-256
`cad04bff8aa853f3d342e12e9ec8c7f51f92c367cd5dd857162df4622eb050f9`.
The revision carrying this text freezes the contract. Its terminal commit/tree and
receipt are recorded externally after the commit; Root acceptance is pending.

## Frozen implementation sequence

All implementation is one invariant family, `F-06-SEMANTIC-CORE`, repair batch
`RB-06-001/instance`, recurrence 0. Every item requires a new exact grant to this
same fixed Executor. A grant may narrow a listed slice but cannot combine it with
live/release authority or change its design. RED tests are persisted before or in
the same semantic revision as their GREEN change, with the pre-change failure
captured in the grant receipt.

1. `I-01/types-and-keys`: add `tests/test_semantic_core.py` RED seeds plus
   `semantic/{__init__,types,schema,canonical}.py`; update only module/input
   classification needed to recognize those paths. Close tagged identities,
   immutable types, canonical ordering, `StateKey`, `AttemptKey`, receipt links,
   aliases, and capacity behavior.
2. `I-02/reducer-and-replay`: add
   `semantic/{parse,reduce,project,replay}.py`; move shared strict case/holdout/
   terminal/ledger parsing and pure Decision/report/replay into them. Migrate
   direct semantic tests without changing adapters or deleting old callers yet.
3. `I-03/provider-authority-terminal`: add
   `adapters/{__init__,codex,git,filesystem}.py`; migrate `live.py` and `cli.py`
   to exact Executor/reviewer profiles, three authority scopes, capability
   mint/rebind, `AttemptKey` `O_EXCL`, strict terminal grammar, and detached
   snapshot facts. No provider call runs in this slice.
4. `I-04/corpus`: migrate all 17 cases and `corpus/engine.py` to the shared
   parser/reducer/projector, keep only imperative fixture/concurrency/subprocess
   work, migrate all corpus/evaluation tests, then delete
   `evaluation/corpus/contract.py`.
5. `I-05/holdout`: add `semantic/holdout.py`; migrate manifest/three cases,
   `holdout/{blind,engine}.py`, and holdout tests to public 0.2, typed replay,
   adaptive/cost policy, and blind-adapter-only sealing; then delete
   `evaluation/holdout/compare.py`.
6. `I-06/ledger-impact-receipt-genesis`: migrate
   `core/{identity,impact,ledger,receipt}.py`, certification tests, evidence
   classification, receipt chain, invalidation, and the fresh 0.6
   `current.json`; delete active historical evidence files and every forbidden
   old reader/literal/semantic duplicate.
7. `I-07/runtime-and-surfaces`: rewrite Runtime Skill/reference cadence and
   recovery, update `AGENTS.md`, `README.md`, `evaluation/README.md`,
   `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and
   `skills/happycodex/agents/openai.yaml`; preserve the claim helper and meet the
   exact line/word budget. This is source metadata only, not marketplace mutation.
8. `I-08/terminal-green`: remove unreachable imports/constants/bypasses, migrate
   every remaining test, prove exact classified input inventory and deletion
   inventory, run each focused command once if not already run for its changed
   fingerprint, then run the cumulative commands once. Persist the semantic
   terminal-GREEN revision/receipt. No candidate freeze or review runs here.

After `I-08`, Root reproduces the terminal receipt and six-surface inventory. A
separate grant may freeze the detached candidate. Focused review occurs only if a
material nonmechanizable unknown remains; otherwise proceed to the separately
granted neutral exact-final after candidate freeze.

## Exact RED and closure matrix

The class names and commands below are frozen implementation targets. No command
in this section ran during G-002.

| Surface | Required RED seed / counterexample | Closure oracle | Focused command |
| --- | --- | --- | --- |
| writer/session | Root, unknown, replacement, fork, concurrent resume, copied handle, or wrong config is accepted as recovery | only exact fixed Executor provider/session/thread/owner/config/scope recovers; same-session positive passes | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.WriterSessionTests -v` |
| authority/attempt | bundled authority, random attempt ID, repeated/reworded attempt, or pre-consumption side effect passes | three disjoint authorities; canonical `AttemptKey` consumed before every side effect; only typed replacement transition permits retry | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.AuthorityAttemptTests -v` |
| typed state | six-field fingerprint, prose required action, persisted phase/permission flag, alias identity, permutation cap, or silent overflow passes | seven-equivalent structural decision inputs are inside `StateKey`; exact enums/unions and derived permissions; overflow reconciles | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.TypedStateTests -v` |
| terminal/events | malformed/multiple/late/unbound terminal or hook/event authority passes | exactly one session/thread/turn-bound terminal; events are adapter facts only; post-terminal semantic bytes fail | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.TerminalEventTests -v` |
| impact/invalidation | planning and execution accept different schema, unknown input is ignored, or semantic change under-invalidates | shared strict loaders/parser; exact semantic/harness/artifact inventory; unknown/missing input fails; affected gates are deterministic | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.ImpactInvalidationTests tests.test_certification_engine.CertificationImpactTests -v` |
| fresh genesis/evidence | old generation/current baseline/evidence is readable, offline evidence certifies, or pre-source evidence passes | generation-6 empty-authority/evidence genesis; old inputs unreachable; strictly post-source evidence; offline remains `refresh_required` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.FreshGenesisEvidenceTests tests.test_certification_engine.CertificationReceiptAndCliTests -v` |
| holdout | public-0.4/old evidence, unreplayable reveal, early reveal, first regression, skipped second pair, unnecessary third, or >25% equal-quality cost passes | exact public-0.2 identity; decision/preimage replay; frozen adaptive sequence and independent token/wall gates | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.HoldoutReplayTests tests.test_holdouts.HappyCodexHoldoutTests -v` |
| isolation/worktree | linked worktree is treated as isolation, unclaimed detached output/ref/ledger passes, or candidate tree drifts | manually detached exact commit/tree/product manifest plus common-dir/worktree/ref/output/ledger claims; drift refuses | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.IsolationWorktreeTests tests.test_resource_claim.ResourceClaimTests -v` |
| hooks/providers | configured allowlist substitutes for effective facts, invalid setting is ignored, fallback occurs, Claude/team/tool/network surface passes | one Codex adapter; strict actual binary/model/effort/tools/settings hash; exact non-interchangeable profiles; forbidden surfaces refuse | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.ProviderEnvelopeTests -v` |
| Runtime recovery | summary/handle/replacement writer, cursor-as-progress, missing claim/receipt, or divergent Goal resumes | exact current checkpoint plus durable facts/receipts, same Executor, recomputed keys, cursor metadata only, Goal reconciliation | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.RuntimeRecoveryTests tests.test_evaluation.HappyCodexEvaluationTests -v` |
| Runtime cadence | phrase-only oracle, repeated equivalent review/check/wait, per-slice cumulative/review loop, editable phase/flags, or evaluator latency drives Runtime | one pre-enumerated RED family and bounded wave, focused slice checks, one terminal cumulative, typed Decision and consumed attempt, exact budget | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.RuntimeCadenceTests tests.test_contracts.HappyCodexContractTests -v` |
| receipt/replay | sanitizer changes meaning, dict-schema duplicate accepts drift, sequence gap/tamper, stored digest mismatch, or planning/execution/replay diverges | one `CanonicalReport`; strict link chain; recomputed keys; same loaders/parser/reducer/projectors; canonical byte equality | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_semantic_core.ReceiptReplayTests -v` |

Focused commands run only when their mapped slice changes or supplies its first
RED/GREEN. The cumulative terminal-GREEN command set is exactly:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m evaluation.cli verify
python3 -m evaluation.cli executor --dry-run
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
git diff --check
wc -l -w skills/happycodex/SKILL.md skills/happycodex/references/execplan.md
```

Only `python3 -m evaluation.cli` may invoke evaluator CLI behavior. Dry-runs must
mint no live capability, consume no `AttemptKey`, create no fixture/output, and
reach no model. Cumulative GREEN also requires exact source/classification/deletion
inventory, zero unknown input, zero forbidden semantic duplicate, no tracked
generated artifact, and Runtime at or below both hard ceilings.

## Convergence Ledger

| Family | Invariant / boundary | Members | Six surfaces | Status | Repair batch | Evidence | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `F-06-SEMANTIC-CORE` | one immutable typed semantic meaning and one Decision govern identity, authority, attempts, gates, replay, and cadence; adapters alone perform effects | `MF-06-001`, `MF-06-002`, all 12 RED surfaces | source/identity, type/cardinality, order/terminal, alias/mutability/TOCTOU, serialization/replay, and consumers/failure propagation are frozen in the matrix; implementation open | `open` | `RB-06-001/instance` | Challenger `GO-WITH-CONDITIONS`, Root union, Fable design input, G-002 contract | `0` |

## Claims and future gates

| ID | Type | Claim | Closure | Falsifier / oracle | Evidence | State |
| --- | --- | --- | --- | --- | --- | --- |
| `O-06-01` | outcome | 0.6 simplifies Runtime cadence without weakening semantic-progress or convergence safety | Frozen matrix, Runtime real-path controls, budget, cumulative GREEN, exact-final | Less prose/state permits equivalent consumed attempt, authority drift, repeated unchanged work, or evaluator latency in ordinary cadence | G-002 freezes typed Decision/StateKey/AttemptKey, cadence wave, payoff split, and Runtime RED; implementation open | `open` |
| `O-06-02` | outcome | One typed stateless semantic core governs every evaluator semantic consumer | Complete migrated inventory, strict shared parse, canonical report/replay, deletion proof, cumulative GREEN, exact-final | A caller retains divergent parsing, hidden mutable semantics, independent permission/phase, or bypass | G-002 freezes module graph, central types, call direction, consumers, deletions, and RED matrix; implementation open | `open` |
| `P-06-01` | preservation | Authority, capability, attempt, claim, cost, corpus, and holdout safety remain strict | Fresh 0.6 controls, three authority gates, provider/isolation/replay proofs, exact-product review | Any gate is bundled, inferred, retried, reused, aliased, or reached without capability/claim | G-002 freezes preserved infrastructure and exact negative oracles; implementation open and no live authority | `open` |
| `A-06-01` | allowed-break | 0.6 has no compatibility path to 0.5 evaluator evidence or tasks | Exact deletion/source search, fresh genesis, old-generation rejection, classified inventory | Reader, migration, alias, dual write, fallback, prior evidence/coverage, or active old baseline remains | G-002 freezes generation boundary, deletions, active-evidence boundary, and old-input RED; implementation open | `open` |

Separate future gates remain open and confer no present authority:

1. `I-01` through `I-08`, each under a separate exact offline write grant to the
   same fixed Executor;
2. terminal-GREEN source freeze and exact detached candidate under separate grants;
3. a focused read-only review only if a material nonmechanizable unknown remains;
4. one fresh neutral exact-final review after candidate freeze;
5. fresh 0.6 offline evidence/receipt/install summaries under exact grants;
6. one bounded Executor calibration after its exact source-derived envelope and
   separate user authority;
7. corpus and adaptive holdout execution, each with separate persisted gate-scoped
   authority and user approval;
8. isolated install and release proof; and
9. release, push/merge/tag/publication, marketplace cachebuster, installation,
   activation, and rollback/cutover.

The Challenger and auxiliary Fable audit are already consumed design inputs and
must not be rerun. No implementation, model, live, release, or external authority
is inferred from contract freeze or future-grant enumeration.

## Contract-freeze verification plan

- prove branch/worktree HEAD/tree and sole status entry equal the accepted G-001
  prestate before the edit and after the external interruption;
- verify the installed three-resource claim and fixed owner label before every
  repository/index mutation;
- read the full installed protocol and full partial plan after interruption;
- audit every A-H contract requirement against exact plan anchors;
- prove only this ExecPlan is modified/staged and the adjacent claim remains
  untracked;
- run `git diff --check` and `git diff --cached --check` without invoking an
  evaluator or test;
- commit once with
  `HappyCodex-ExecPlan: docs/execplans/happycodex-0-6-semantic-core.md`;
- prove parent is exact G-001, base ancestry, commit/tree, changed-path inventory,
  trailer, claim status, and final `git status --short --branch`;
- persist
  `/home/caichenghang/.codex/happycodex-0.6-semantic-core-g002-receipt.json`,
  validate/read back it, then stop.

No focused/cumulative/evaluator/model command in the frozen implementation matrix
runs during G-002.

## Progress and decision log

- `2026-07-29`: Reconfirmed base commit/tree and absence of the target branch,
  worktree, ExecPlan, receipt, and conflicting target claims.
- `2026-07-29`: Persisted `HC06-G-001-bootstrap` durable intent before branch,
  worktree, claim, repository, index, or commit mutation.
- `2026-07-29`: Created the exact branch/worktree from the immutable base; no
  rebase, merge, cherry-pick, or existing worktree mutation occurred.
- `2026-07-29`: Acquired and verified the worktree/ref/ledger claim as
  `happycodex-0.6-semantic-core-executor`, resource count 3.
- `2026-07-29`: Root independently verified and accepted G-001 at commit
  `5f6c508503563ab62444b33d64efeac9cbb34826`, tree
  `61b2cc9a36e268bf1aa2b530eec140a666fc9a42`.
- `2026-07-29`: Independent Challenger returned `GO-WITH-CONDITIONS`; Root
  reproduced the union. Its only repository commands were read-only evaluator
  verify and corpus/holdout dry-runs; state remained `refresh_required`, 17/3.
- `2026-07-29`: Reconciled the already-completed detached Fable audit as design
  input only, resolved `MF-06-001`/`MF-06-002` in the frozen typed contract, and
  forbade a repeat.
- `2026-07-29`: Persisted G-002 durable intent at exact accepted prestate before
  editing this plan.
- `2026-07-29`: External interruption reconciliation found the same HEAD/tree,
  only this tracked plan modified, no staged path/commit/terminal receipt, and the
  same active verified claim. Continued the same grant and intent without retry.
- `2026-07-29`: Rejected cross-thread `是不是可以执行了` as non-authority; no
  contract or grant field changed.
- Decision `D-06-001`: use released public 0.5 as a generation boundary, not the
  separate 0.5.1 development worktree or abandoned convergence branches.
- Decision `D-06-002`: freeze one provider-neutral semantic package and one Codex
  adapter; reject phrase/state duplication, compatibility, multi-provider,
  ordinary event-queue, and bundled-authority designs.
- Decision `D-06-003`: resolve stagnation structurally with derived typed decision
  inputs, `StateKey`, and pre-side-effect `AttemptKey`, never prose.
- Decision `D-06-004`: use public 0.2 only as comparator configuration; reuse no
  evidence.

## Checkpoint

- Milestone: contract freeze; the revision carrying this update is the frozen
  contract, with terminal commit/tree in the G-002 receipt.
- Last accepted revision: G-001 commit
  `5f6c508503563ab62444b33d64efeac9cbb34826`, tree
  `61b2cc9a36e268bf1aa2b530eec140a666fc9a42`; immutable released baseline remains
  `1ea888ddeac94ebbb9f92e5dc80b1de289e6aec0` /
  `ab42724288e3e588c30bd0f4a941436f4a8f35f5`.
- Controlled domain: the exact branch, worktree, ledger, private claim receipt,
  and external G-001/G-002 intent/receipt records; no product/evaluator/Runtime/
  manifest/active-plugin/external release state changed in G-002.
- Active grant: `HC06-G-002-contract-freeze`, sequence 2, `INTENT_RECORDED`;
  terminal receipt and Root acceptance pending. G-001 is `CLOSED`.
- Next Decision after G-002 acceptance: `IMPLEMENT_BATCH` for `I-01` only if Root
  issues a new exact grant to the same Executor; otherwise `ASK_USER`/stop.
- Family: `F-06-SEMANTIC-CORE`, `RB-06-001/instance`, status `open`,
  recurrence 0; all four claims remain open for implementation evidence.
- Candidate/evidence: no 0.6 candidate or accepted evidence; fresh genesis,
  checks, focused review if needed, exact-final, calibration, corpus, holdout,
  install, and release gates remain open.
- Agents/review: fixed Executor remains the writer; Challenger and Fable inputs
  are terminal read-only design inputs, not candidate evidence; no exact-final
  exists.
- Dirty ownership: only this plan during G-002 plus the pre-existing adjacent
  untracked claim directory; no staged path before final staging.
- Goal: none created or inferred.

## Retrospective

Fill only after final Outcome completion. Do not expose it to a reviewer or use it
as evidence.
