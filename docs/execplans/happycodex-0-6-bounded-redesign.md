# HappyCodex 0.6 Bounded Redesign

Protocol: `HappyCodex/0.5`

Current index: independent 0.6 bounded-redesign contract plus active same-batch
action recomputation. G001/G002 are accepted source. G003 is unaccepted. G004
is reachable but its receipt is invalidated; G005 owns its action-forge sibling.

Restore guard: restore this entire ExecPlan, then reconcile the exact Git source,
fixed Executor identity, three resource claims, external intent and receipts,
current grant, phase, families, checks, candidate, evidence, agents, and any Goal
before any write, review, effect, or completion claim. Conversation summaries,
copied handles, and another task's source do not reconstruct authority.

Phase: `implementation`. Active grant:
`HC06BR-G-005-attempt-recompute`, sequence 5. It binds G004 commit
`e500340ce7c4de8e50f5aa8292515478b1b4bc66`, tree
`4a7c9db64c4551fc6fb588d5062eccaf38f2be9f`, the same fixed Executor/claim,
and only canonical, decision, semantic-test, and ExecPlan paths. G001/G002 are
Root-accepted/`CLOSED`; G003/G004 are not terminal evidence.

## Operative request and normalized Outcome

Current user authorization, verbatim:

```text
PLEASE IMPLEMENT THIS PLAN:
- Current Root creates this single fixed child Executor; independent base/branch/worktree/ExecPlan/claims; no communication with the original Root; no automatic cherry-pick of its later work.
- Preserve Runtime convergence optimization, typed semantic kernel, task authority, false-green repair, fresh ledger, cost gates, recovery, exact-final isolation, install/release and atomic rollback.
- Supersede the old 9-module/8-slice/single-family topology. Reject a full evaluator rewrite, timers, cross-Root scheduling, compatibility paths, a new adapters subsystem, and moving `holdout/compare.py` merely for symmetry. Existing Fable5/Claude Code CLI audits are retained design evidence and are not rerun.
- Batch 1: only `evaluation/semantic/{__init__,types,canonical,parse,decide}.py` as final semantic package; <=20 public exports; immutable facts/tagged IDs; `TaskBinding`; adapter-issued `AuthorityProvenance`; `NextAction`; `EffectGate`; one canonical encoder; strict facts-only parse; pure reduce/enforce. `ProgressKey = H(TaskBinding + stable semantic facts)`. `AttemptKey = H(ProgressKey + reducer-produced NextAction target/scope + FalsifierId + EvidenceSourceId)`. Domain-primary-key duplicates reject. Authority/resource claims/receipts/cursors/timestamps/consumption/derived action do not change ProgressKey. Direct target ALLOW; legitimate delegated ASK_USER; missing/spoofed/wrong destination or lineage REFUSE. Delete MachineEnvelope/AdminFacts/public canonical_set/wrapper inflation. Repair the known full-suite inventory and two relative-import-policy failures. Simplify Runtime early to event correction on repeated AttemptKey failure, new family, repair-batch end, pre-effect, and candidate freeze; one diagnosis/repair wave/cumulative check per family and one post-freeze exact-final.
- Batch 2: existing CLI/live/ledger/corpus/holdout remain I/O/effect owners; no adapters directory. Share strict terminal parsing, exact matching, decision and replay-by-recompute. Migrate corpus engine and ledger, then delete corpus/contract.py and proven duplicate casefold/basename/permutation/manual-sanitizer semantics. Keep holdout/compare.py. Invocation profile is required only at executor/corpus/holdout/live boundaries, not ordinary Runtime state. Keep 17 corpus cases and 3 holdout pairs; deterministic offline authority fixture; behavior not proved by phrase-presence tests.
- Batch 3: fresh generation-6 current.json, no old evidence reader/reuse; offline remains refresh_required; process-local capability rebind; authority consumption; O_EXCL attempt/resource claims; raw model events outside repo; recovery needs current ExecPlan/Git/receipts/claim/same Executor and rejects summary/copied handle/replacement/cross-task authority; prove compaction plus no-summary/no-handle reconstruction; source inventory/package/config docs; Git-reachable candidate with normalized artifact/manifest/source match and evidence strictly post-source.
- Separate future gates: Executor pilot cost envelope+exact invocation+user authority; Corpus exact impact/invocation authority; Holdout exact impact/invocation authority; fresh isolated gpt-5.6-sol/max exact-final after freeze; isolated install with plugin-creator cachebuster; activation only under later authority with paired atomic package/config/cache rollback. Product change invalidates candidate/review/evidence.
- Three families: runtime convergence/progress; task authority/effect gating; evaluator terminal/identity/replay. Holdout/cost stays separate.
- Test matrix includes primary-key duplicates, derived-state injection, serialize/parse/reduce key roundtrip, action mismatch impossible, empty REPLACED evidence, admin-only non-progress, direct/delegated/spoofed/missing/wrong-destination/wrong-lineage authority, pending-release+complete, negation, path alias/casefold/basename, extra terminal, marker overflow, raw/ledger divergence, pre-effect capability/claim/attempt consumption, compaction/no-summary recovery/writer nonreplacement, old generation rejection/offline noncertification, and all evaluator dry-runs with no model/attempt/fixture/output effects. Every coherent implementation batch ends in a reachable full offline GREEN commit.
- Complexity budgets: semantic production LOC <=1200; semantic public exports <=20; evaluation production Python LOC <=6900; Runtime <=262 lines, target <=2200 words, hard <=2400; ExecPlan target 6000-6500 words while HappyCodex protocol hard maximum remains 12000.
- Existing 0.5 tasks remain 0.5 or are abandoned; no migration.
```

The normalized Outcome is exact:

```text
Create an independent HappyCodex 0.6 bounded clean-break line from commit 96ac756. Preserve all effective prior 0.6 goals and safety gates while replacing the additive nine-module/eight-slice/single-family design with a four-module semantic kernel, three coherent GREEN batches, event-driven Runtime correction, trustworthy task authority, fresh generation-6 evidence, recovery, isolated exact-final, and separately authorized cost/install/release/activation gates. No compatibility reader, migration, alias, dual write, fallback, cross-Root coordination, live execution, installation, release, marketplace mutation, or activation is authorized by implementation.
```

Implementation means the three offline batches and their source/test/docs
revisions only. It cannot imply permission for a model call, live evaluator,
install, release, activation, external coordination, or task migration.

## Immutable source, independence, and writer

- Common repository: `/home/caichenghang/projects/happycodex`.
- Exact base commit:
  `96ac7563f22eb42d84c827717eba346ecfd80090`.
- Exact base tree:
  `88df9e9f4819dfc84d6ba3057b0e7069aa4d4108`.
- Exact base parent:
  `38e5e0d2a1d08d0da21c70f77c0e6f339e712d08`.
- Branch: `codex/happycodex-0.6-bounded-redesign`.
- Ref:
  `refs/heads/codex/happycodex-0.6-bounded-redesign`.
- Worktree:
  `/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign`.
- ExecPlan:
  `docs/execplans/happycodex-0-6-bounded-redesign.md`.
- Fixed Executor task: `/root/bounded_redesign_executor`.
- Fixed role/effective profile: `happycodex_executor`,
  `gpt-5.6-sol/high`.
- Owner label: `happycodex-0.6-bounded-redesign-executor`.

Root reads, decides, grants, and verifies. This fixed Executor is the only writer
for the controlled domain and never delegates. Identity or configuration drift
fails closed; no replacement writer may resume. The separate worktree
`/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-semantic-core`,
its ref, its Root, claims, later commits, and task state are unrelated. This task
does not message that line, inspect its later commits as implementation input,
coordinate scheduling, cherry-pick, merge, rebase, alter its resources, or infer
authority from it. Shared Git history before the immutable base is source history
only.

Existing 0.5 tasks finish under 0.5 or are abandoned. No task, ledger, authority,
attempt, evidence, receipt, claim, or recovery handle migrates from 0.5 or from
the other 0.6 task.

## Baseline facts and open candidate-new findings

The immutable base is a source construction point, not an accepted GREEN
baseline. It already contains the inherited partial semantic-core work:
`evaluation/semantic/{__init__,types,schema,canonical}.py`,
`tests/test_semantic_core.py`, associated input classification, and the old
semantic-core ExecPlan. Those bytes are inputs to this redesign, not accepted
implementation evidence and not a topology to preserve.

A Root reproduction against the accepted G001 plan-only product baseline ran
exactly:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

It completed 195 tests in 8.524 seconds with exactly three failures and no other
failure. This result is `candidate-new/open`, not baseline-accepted:

- `BR-FIND-BASE-001`: the certification full-suite module inventory did not
  match the newly present semantic package at
  `CertificationIdentityTests.test_inventory_classifies_every_engine_module_and_schema`;
- `BR-FIND-BASE-002`: the stdlib/import-policy subtest failed for
  `evaluation/semantic/__init__.py` at
  `HappyCodexContractTests.test_python_validation_uses_only_declared_stdlib_dependencies`;
- `BR-FIND-BASE-003`: the same import-policy test's second subtest failed for
  `evaluation/semantic/types.py`.

The fixed Executor reproduced the same exact 195-test/three-failure set in 8.549
seconds. External baseline receipt:
`/home/caichenghang/.codex/happycodex-0.6-bounded-redesign-g003-b1-baseline.txt`,
SHA-256
`d6d7a7f3da1bf992382117a4511dc5120997f5ec5c928cad6c352e5fc1158f5a`.
Batch 1 repairs all three without weakening fail-closed inventory or import
policy; final focused/full GREEN is required before they become resolved.

The earlier Fable 5 review performed through the Claude Code CLI remains retained
design evidence. It established the need for structural action identity and
phrase-independent progress. The existing CLI audit evidence likewise remains
design input only. Neither audit is rerun, treated as current-candidate review, or
used as generation-6 certification evidence. No bootstrap test, evaluator CLI, or
model command has run on this branch.

## Superseded topology and design boundary

This plan supersedes the old additive nine-semantic-module, adapter-subsystem,
eight-slice, single-family topology. The superseded active path is removed on this
branch; its history stays reachable in Git. Effective goals are preserved, but its
module count, slice count, family grouping, wrapper types, and symmetric file moves
are not requirements.

The selected design has four substantive semantic modules—`types`, `canonical`,
`parse`, and `decide`—plus a closed `__init__.py`. It reuses the existing I/O
owners rather than wrapping them in a new subsystem. The design is bounded because
semantic meaning moves to one kernel while imperative Git/filesystem/process/model
boundaries remain where they already execute.

Rejected alternatives are contract boundaries:

- no full evaluator rewrite or second evaluator CLI;
- no timers, polling cadence, event queue, controller, daemon, or scheduler as
  progress semantics;
- no cross-Root scheduling or shared task authority;
- no compatibility reader, migration, alias, dual read/write, fallback, or prior
  evidence reuse;
- no `evaluation/adapters/` package;
- no relocation of `evaluation/holdout/compare.py` merely to make the directory
  graph symmetric;
- no public wrappers that restate one immutable value under multiple names;
- no phrase-presence oracle as proof of behavior;
- no invocation profile in ordinary Runtime state;
- no Fable/Claude provider or team feature.

`evaluation/holdout/compare.py` remains the pure holdout policy owner unless a
future source-proved semantic reason requires change under a new contract grant.
Holdout and cost are separate release-quality gates, not a fourth implementation
family.

## Four-module semantic kernel

The final semantic package contains exactly:

```text
evaluation/semantic/__init__.py
evaluation/semantic/types.py
evaluation/semantic/canonical.py
evaluation/semantic/parse.py
evaluation/semantic/decide.py
```

`__init__.py` exports at most 20 named public values and has no wildcard export.
Private implementation helpers remain private. `types.py` owns immutable fact
types, tagged scalar IDs, `TaskBinding`, adapter-issued
`AuthorityProvenance`, reducer-produced `NextAction`, and `EffectGate`.
`canonical.py` owns the sole canonical encoder and domain-separated hashes.
`parse.py` strictly turns untrusted mappings/events into fact objects.
`decide.py` owns pure reduction, enforcement, decision, and replay-by-recompute
entry points. The package imports only side-effect-free standard-library modules
and performs no file, environment, clock, randomness, subprocess, Git, network,
session, or mutable-global operation.

Facts are frozen dataclasses or equally immutable tagged values. Every ID with a
different domain is a different type: task, claim, finding, falsifier, evidence
source, gate, check, family, repair batch, action target, action scope, repository,
marker, receipt, resource, commit, tree, and digest identities cannot be
interchanged as strings. Bounded display text is never semantic identity.

Each parsed domain collection declares one primary key. A duplicate primary key
rejects the whole input even when both entries are byte-identical; sort-and-dedup
is forbidden. This rule covers claims, findings, evidence sources, gates, checks,
families, repair members, resources, authorities, attempts, terminal identities,
receipt links, and case/holdout identities. Ordered event streams retain order.
Unordered semantic collections are encoded in exact primary-key order only after
duplicate rejection.

`TaskBinding` is the stable task identity in progress:

```text
TaskBinding {
  task_id,
  root_task_id,
  executor_task_id,
  owner_label,
  destination_id,
  lineage_digest,
  role_config_digest
}
```

It binds this task to the fixed Root/Executor relationship and destination.
Runtime supplies it from durable task/config facts. It is not inferred from prose,
a conversation summary, or a live handle.

`AuthorityProvenance` is separately issued by the current boundary adapter after
exact event/user/config validation. It contains provenance kind
`DIRECT | DELEGATED`, issuer, destination, lineage, source-event digest, exact
scope, and authority digest. Model output cannot construct it. It is enforcement
administration, not semantic progress.

`NextAction` is produced only by the reducer from parsed facts. It has an exact
variant, target, scope, family, falsifier, and evidence-source identity.
`EffectGate` is produced only by enforcement and contains
`ALLOW | ASK_USER | REFUSE`, the exact action target/scope, and a typed reason.
No parser accepts serialized `NextAction`, `EffectGate`, permission boolean,
phase, completion decision, or other derived action as a fact. Derived-state
injection fails unknown-field validation.

The one canonical encoder is domain-separated UTF-8 JSON with sorted object keys,
explicit union tags, exact booleans and integers, no NaN/coercion, exact
case-sensitive paths, and one final byte definition. There is no public
`canonical_set`, alternative canonical digest, permutation search, or wrapper
encoder.

The key formulas are normative:

```text
ProgressKey =
  SHA256("happycodex/0.6/progress-key\0" +
         canonical(TaskBinding, stable_semantic_facts))

AttemptKey =
  SHA256("happycodex/0.6/attempt-key\0" +
         canonical(ProgressKey,
                   reducer-produced NextAction target and scope,
                   FalsifierId,
                   EvidenceSourceId))
```

Stable semantic facts include source/candidate identity, claims/findings and
their semantic evidence, gate work/evidence state, checks, normalized
infrastructure `REPLACED` facts with nonempty evidence, Goal/Outcome match, family
and repair-batch state, and the facts needed to derive the next action. They do
not include authority records, resource claims, intent/receipts, receipt-chain
cursors, timestamps, transport IDs, attempt consumption, display prose, raw
events, or any serialized derived action. Adding only administrative records
therefore leaves `ProgressKey` unchanged and cannot manufacture progress or retry.

Serialize/parse/reduce always recomputes both keys. A stored key is comparison
material only and must match recomputation. The reducer's action object is the
only input to `AttemptKey`; callers cannot pass a different action target/scope.
This construction makes action mismatch unrepresentable at the effect boundary.

Enforcement is exact:

| Provenance/binding condition | EffectGate |
| --- | --- |
| direct authority to the exact bound destination, lineage, scope, and action | `ALLOW` |
| legitimate delegated authority with exact issuer/destination/lineage but user decision required | `ASK_USER` |
| missing provenance or authority | `REFUSE` |
| spoofed issuer/source event | `REFUSE` |
| wrong destination | `REFUSE` |
| wrong lineage/task/config | `REFUSE` |
| target or scope differs from reducer-produced `NextAction` | `REFUSE` |

`ASK_USER` authorizes no effect. `ALLOW` is necessary but not sufficient: the
fixed Executor, exact grant, process-local capability, resource claim, authority
consumption, and `O_EXCL` attempt claim must all pass immediately before effect.

## Runtime event correction and convergence

Ordinary Runtime remains Markdown guidance, not an evaluator engine. It corrects
on five semantic events:

1. the same `AttemptKey` fails or is presented again;
2. a new material invariant family is confirmed;
3. a repair batch reaches its end and needs the one cumulative check;
4. an authorized side effect is about to occur; and
5. a candidate is about to freeze.

Clocks, elapsed time, turns, wakes, polling, summaries, receipt appends, and
administrative cursor changes are not progress events. On repeated AttemptKey
failure, Runtime reconciles facts and either joins a pre-GREEN same-family sibling
to the active batch with RED coverage, establishes the boundary after a qualifying
recurrence, or returns the decision to Root. It does not retry by rewording.

Each family gets one source diagnosis, one coherent repair wave, and one cumulative
offline check at terminal GREEN. Focused checks may run inside the wave to localize
RED/GREEN, but they do not create per-slice review/cumulative loops. A new family
gets its own wave. Same-family findings before terminal GREEN join the same batch.
A Root-confirmed material recurrence after GREEN increments recurrence and invokes
the existing boundary-required rule; a second recurrence after boundary repair
returns to the user.

Candidate freeze requires all three families closed or explicitly evidenced,
full offline GREEN, no uncontrolled dirt, source/package/config inventory, and no
open material unknown. Exactly one fresh isolated exact-final follows freeze.
Any product-source change unfreezes the candidate and invalidates affected review
and evidence. There is never an exact-final during a repair wave.

Aggregate Runtime Markdown—`skills/happycodex/SKILL.md` plus
`skills/happycodex/references/execplan.md`—stays at or below 262 lines, targets at
most 2,200 words, and hard-fails above 2,400 words. Repository evaluation files
remain maintainer support and are never linked from Runtime Skill Markdown.

## Convergence Ledger

| Family | Invariant | Six-surface closure | Status | Batch | Recurrence |
| --- | --- | --- | --- | --- | --- |
| `F-06BR-RUNTIME` | semantic progress and event correction prevent equivalent repeated work and false GREEN | G003 siblings joined before acceptance; G004 covers sealed parse/reduction; G005 recomputes action at both consumers | `G005 GREEN; Root acceptance open` | `RB-06BR-001/instance` | `0` |
| `F-06BR-AUTHORITY` | exact `TaskBinding`, provenance, reducer action, capability, claim, authority, and attempt gate every effect | G004 covers private authority/report issuance; G005 rejects sealed arbitrary action at AttemptKey and effect gate | `G005 GREEN; Root acceptance open` | `RB-06BR-002/instance` | `0` |
| `F-06BR-EVALUATOR` | terminal, identity, decision, ledger, and replay share strict parsing and exact recomputation | same six surfaces, including duplicate/order/terminal/path/key/raw-ledger divergence and consumer propagation | `open` | `RB-06BR-003/instance` | `0` |

Holdout quality and cost comparison remain separate gated evidence. They do not
collapse into a family merely because their engines consume shared semantics.

## Batch 1: kernel, authority semantics, and early Runtime correction

Batch 1 replaces the inherited partial semantic package with the exact five-file
surface above. `schema.py` is deleted after its required definitions move into
`types.py`/`parse.py`. `MachineEnvelope`, `AdminFacts`, public `canonical_set`, and
wrapper inflation are deleted. No compatibility import or forwarding alias remains.

Batch 1 first persists RED or exact characterization for:

- all primary-key duplicates, including identical duplicates;
- wrong tagged ID use and mutable fact members;
- derived action/phase/permission injection;
- canonical serialize/parse/reduce `ProgressKey` roundtrip;
- stored key mismatch and caller-supplied action mismatch;
- empty-evidence `REPLACED`;
- admin-only changes that must not change progress;
- direct, legitimate delegated, spoofed, missing, wrong-destination, and
  wrong-lineage authority;
- reducer/enforcer purity and side-effect-free imports;
- marker/schema capacity overflow without truncation;
- the historical 195-test inventory failure and two relative-import-policy
  failures.

It then migrates direct semantic callers only as necessary to compile and prove the
kernel, repairs the inventory oracle by explicitly classifying the final package,
and repairs relative-import policy without weakening the policy. It rewrites
Runtime Skill/reference early to the five event corrections, one wave/cumulative
check per family, and one post-freeze exact-final. Runtime cannot import or link
the evaluator.

Batch 1 ends only at a reachable commit whose focused checks and entire offline
suite are GREEN and whose plan records the RED receipts, changed paths, budgets,
and exact check receipt. It authorizes no model/provider/evaluator live effect and
does not advance an accepted baseline merely by becoming GREEN. Batch 1 closes
semantic production LOC at or below 1,200, public exports at or below 20, and both
Runtime line/word limits. It measures total evaluation production Python LOC but
does not treat the 6,900 ceiling as a Batch 1 closure gate. Its evaluator commands
are only `verify`, `corpus --dry-run`, and `holdout --dry-run`; the accepted
prestate has no `executor` subcommand, and Batch 1 cannot edit the CLI.

## Batch 2: shared terminal, corpus, ledger, and replay semantics

Existing `evaluation/cli.py`, `evaluation/live.py`,
`evaluation/core/ledger.py`, corpus engine, holdout engine/blind/compare, impact,
receipt, identity, and Git/filesystem code remain I/O/effect owners. No adapters
directory is created. Imperative modules may acquire bytes and perform granted
effects; they do not redefine semantic meaning.

Batch 2 routes strict terminal parsing, exact identity matching, decision, and
replay-by-recompute through the kernel. The terminal stream is exact: one bound
terminal agent-result carrying facts and one legal completion tag, then one
matching usage-only nonsemantic completion event, then EOF. Provider/session/
thread/turn/AttemptKey/result-digest fields match exactly. Missing, duplicated,
contradictory, late, unbound, semantic completion, extra terminal, trailing byte,
or raw/ledger divergence refuses.

Corpus retains exactly 17 case IDs. Holdout retains exactly three pair IDs.
Planning, execution, and replay use the same strict loader and semantic decisions.
Batch 2 migrates `evaluation/corpus/engine.py` and ledger consumers, then deletes
`evaluation/corpus/contract.py`. It proves and deletes duplicate casefold,
basename, suffix/path-alias, permutation matching, and manual semantic-sanitizer
logic. Exact case-sensitive repository-qualified paths replace aliases. Receipt
code serializes already-sanitized typed projections rather than deciding what
facts mean.

`evaluation/holdout/compare.py` stays in place. Blind randomness/sealing and engine
I/O remain imperative; comparator decisions are exact and replayable. Phrase
presence, negation-blind substring checks, or prose completion markers cannot
prove behavior. Tests include pending-release plus `COMPLETE`, explicit negation,
path alias/casefold/basename variants, extra terminal events, marker overflow, and
raw versus ledger mismatch.

The invocation profile—effective provider/binary/model/effort/timeout/tool/
network/MCP/hook/session facts—is mandatory at executor-pilot, corpus, holdout,
and live boundaries. It is not ordinary Runtime state and does not change
`ProgressKey` merely because administrative invocation data is recorded.

Offline authority tests use deterministic fixtures with no current user authority
and prove allow/ask/refuse behavior without issuing a provider call. Batch 2 ends
only in another reachable full offline GREEN commit with the exact 17/3 inventory,
deletion proof, focused receipts, dry-run non-effect receipts, and budgets.
Batch 2 owns `evaluation/cli.py` and adds one strict offline
`executor --dry-run` entrypoint under an observed RED and GREEN. That dry-run
must create no model call, capability, attempt consumption, fixture, output,
workspace mutation, or authority consumption. From Batch 2 onward, terminal
checks include `verify` plus executor, corpus, and holdout dry-runs.

## Batch 3: fresh evidence, effect ordering, recovery, and candidate source

Batch 3 replaces `evaluation/results/current.json` with a fresh generation-6
genesis. No old-generation reader, alias, migration, fallback, prior-coverage
reuse, or evidence locator is added. Old evidence may remain only as inert Git
history and cannot be named by the active parser. Genesis has
`engine_generation = "0.6"`, state `refresh_required`, exact source/snapshot/
package/config/manifest identities, sorted pending gates, null executor/corpus/
holdout authorities, empty calibration history, empty accepted evidence, no
receipt head, and no certification.

Offline checks and content-addressed `offline_summary` evidence never promote
`refresh_required` to `certified`. Every accepted generation-6 evidence commit
strictly postdates the Git-reachable source it proves. A zero-live `receipt` or
`isolated_install` gate still needs its own strictly post-source offline summary;
receipt evidence binds current artifact identity and install evidence binds the
exact source/installed-package/config receipt.

The live validator mints one immutable process-local capability. Every
model-reaching executor/corpus/holdout helper rebinds it before fixture creation,
mapping, workspace mutation, output creation, or subprocess execution. Authority
is gate-scoped and consumed for its exact invocation. `AttemptKey`, resource, and
output claims use `O_EXCL`; consumption precedes every effect and recording it
does not change progress. A failed semantic attempt is not retried. Only a
validated infrastructure `REPLACED` fact with nonempty evidence and new exact
authority can create a new semantic prestate.

Raw model events, hidden prompts/oracles, secrets, and unsanitized streams stay
outside the repository. Tracked evidence contains only sanitized summaries,
hashes, fixed fixtures, prompts, hidden-oracle hashes, and executable evaluator
code. Raw-event and ledger digests must agree or refuse.

Recovery requires all of:

- this current ExecPlan and its unique checkpoint;
- exact Git commit/tree and owned dirty-path reconciliation;
- external intent and complete receipts;
- the active three-resource claim and owner-token digest;
- the same fixed Executor task/session/thread/config/permission identity;
- exact grant, family/batch, checks, candidate/evidence, and attempt state.

A conversation summary, copied live handle, replacement writer, fork, concurrent
resume, other Root, other task authority, or cross-task claim is insufficient and
refuses. Maintainer evaluation proves native same-task compaction and separately
proves reconstruction with no summary and no handle. It also proves writer
identity cannot be replaced; ordinary tasks do not rerun this control every turn.

Batch 3 completes source inventory and package/config documentation. The source
candidate must be Git-reachable. Its normalized Git package artifact, engine
manifest, external role-config digest, source commit/tree, and documented
identities must match the snapshot exactly. The ledger already binds the three
future gate scopes to the pending phase but contains no authority. All evidence
strictly postdates source. The candidate freeze itself remains a separate
post-GREEN Root grant; Batch 3 does not infer it.

Batch 3 ends in a third reachable full offline GREEN commit after all focused and
cumulative checks, dry-run non-effects, source/deletion/classification inventory,
Runtime and LOC budgets, clean owned status, and complete receipt. Product changes
after that commit invalidate candidate, review, and affected evidence and reopen
the relevant family.

## Exact batch path and ownership inventory

Later grants bind exact prestates and may narrow this inventory. They may not add a
path, combine a future live/release gate, or cross a batch boundary without Root
first reconciling the contract. The ExecPlan is the only path common to every
batch because it is the current index and receipt checkpoint.

Batch 1 may own only the final semantic package, deletion of
`evaluation/semantic/schema.py`, direct classification/import-policy repairs in
`evaluation/core/identity.py`, semantic and contract/certification tests needed
for its RED/GREEN, the two Runtime Markdown files, and this ExecPlan. If a direct
caller outside that set cannot import the final package, the Executor returns its
exact path and needed mechanical change to Root before editing it. Batch 1 does
not migrate corpus, ledger, terminal, holdout, result, manifest, or evidence
behavior opportunistically.

Its expected path set is therefore:

```text
evaluation/semantic/__init__.py
evaluation/semantic/types.py
evaluation/semantic/canonical.py
evaluation/semantic/parse.py
evaluation/semantic/decide.py
evaluation/semantic/schema.py                 # delete
evaluation/core/identity.py
tests/test_semantic_core.py
tests/test_contracts.py
tests/test_certification_engine.py
skills/happycodex/SKILL.md
skills/happycodex/references/execplan.md
docs/execplans/happycodex-0-6-bounded-redesign.md
```

Batch 2 owns semantic consumers and their exact fixtures/tests:
`evaluation/{cli,live}.py`, `evaluation/core/{identity,impact,ledger,receipt}.py`,
`evaluation/corpus/{engine,contract}.py`,
`evaluation/holdout/{blind,compare,engine}.py`, package `__init__.py` files as
needed to close exports, the 17 case JSON files, the holdout manifest and three
case JSON files, and `tests/{test_semantic_core,test_evaluation,test_holdouts,
test_certification_engine}.py`. `corpus/contract.py` is deleted. The holdout
comparator is edited only if shared exact types/replay require it; it is not moved
or deleted. Any other consumer discovered by exact source search is an open
inventory finding, not implied authority.

The 17 corpus identities remain:
`authorized-rebaseline`, `boundary-cutover`, `clean-qualifying-control`,
`compaction-recovery`, `exact-final-ready`, `goal-divergence`,
`midflight-escalation`, `multi-repo-submodule`,
`no-commit-archive-recovery`, `no-commit-secret`, `no-commit-unselected`,
`pre-freeze-compaction`, `receipt-mismatch`, `review-admin-cycle`,
`review-inventory-gate`, `review-isolation`, and `subthreshold-control`.
The three holdout identities remain `authority-production-boundary`,
`destructive-migration-fallback`, and `local-documentation-control`. IDs,
cardinality, and behavior are preservation claims; schema bytes may change only
to generation 6.

Batch 3 owns `evaluation/results/current.json`, active old evidence deletion,
effect/recovery implementation and tests not closed earlier, `evaluation/README.md`,
`AGENTS.md`, `README.md`, candidate source inventory, and tracked package/config
source documentation needed to identify 0.6. A later exact grant must enumerate
any `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, or external
role-config source change explicitly. A tracked source-manifest edit is not
permission to touch installed plugin bytes, personal marketplace/cache state, or
external config. The plugin-creator cachebuster and all external marketplace
effects remain future install/release work.

Before each batch, the Executor records an external intent containing exact
prestate, paths, allowed commands, stop conditions, and checks, then verifies the
fixed claim before every repository/index/commit effect. At the end it persists a
complete external receipt, commits a reachable full-offline-GREEN revision with
the ExecPlan trailer, and stops for Root verification. Root acceptance, not the
writer's local GREEN sentence, advances the checkpoint.

## Exact decision, effect, terminal, and replay flow

The ordinary deterministic flow is:

```text
strict raw input
  -> parse facts and reject unknown/duplicate/derived fields
  -> bind TaskBinding and recompute ProgressKey
  -> pure reduce to one NextAction
  -> validate adapter-issued AuthorityProvenance
  -> pure enforce to ALLOW, ASK_USER, or REFUSE
  -> if ALLOW, rebind capability and verify grant/claim/authority
  -> compute and O_EXCL-consume AttemptKey
  -> only then create fixture/output/workspace/subprocess effect
  -> strict terminal parse and sanitized typed projection
  -> canonical receipt/ledger write
  -> replay from raw sanitized facts by parse/reduce/enforce/recompute
```

No caller may skip, reorder, or precompute a later arrow. In particular, output
directories and fixtures do not exist before capability/claim/authority/attempt
consumption. A dry-run stops before capability mint and consumption. `ASK_USER`
and `REFUSE` stop before every effect. A terminal tag says what the provider
reported, not whether release or completion gates are satisfied. Thus
`pending RELEASE + CompletionTag.COMPLETE` reduces to the pending release action
or blocker and cannot close.

Parser output has two channels: stable semantic facts and validated administrative
enforcement facts. Only the first plus `TaskBinding` feeds `ProgressKey`.
Authority provenance, resource and output claims, grant/intent/receipt lifecycle,
attempt registry, cursor, timestamps, and transport identity remain in the second
channel. They can make enforcement refuse but cannot make semantic progress.
Normalized `REPLACED` is the sole infrastructure transition admitted to stable
facts, and only with an exact old/new envelope plus nonempty evidence; transient
start/fail/recover administration remains non-progress.

Replay never trusts a stored decision, gate, key, sanitized summary conclusion, or
ledger status. It parses stored fact projections with the current strict
generation-6 schema, recomputes `ProgressKey`, reduces `NextAction`, revalidates
the recorded provenance and effect gate, recomputes `AttemptKey`, and compares
canonical values byte-for-byte. The persisted action/key fields are assertions to
check, not inputs to accept. If raw terminal receipt and ledger projection name
different provider/session/thread/turn/action/attempt/result digests, both are
rejected.

Completion requires reducer facts for every pending gate. A model's
`COMPLETE`, an affirmative phrase inside negated prose, a matching basename, or a
casefolded path supplies no such fact. Marker counts are bounded at strict parse;
overflow returns a typed blocker without keeping the first N. Terminal parsing
consumes the entire stream so an exact-looking first terminal followed by another
event is failure, not success with ignored trailing material.

Recovery executes the same flow from durable facts. It does not synthesize
`AuthorityProvenance` from the fact that a task handle is live. The current adapter
must prove that the resumed durable Executor equals `TaskBinding`; it then proves
the grant and claim before any effect. Cross-task authority can be well-formed yet
still refuses because task, destination, and lineage do not match. This distinction
keeps malformed/spoofed inputs separate from legitimate delegation that needs an
explicit user decision.

## Required test and falsification matrix

The following are behavior/state-transition oracles, not phrase checks:

| Surface | Required negative/positive proof |
| --- | --- |
| primary identity | reject byte-identical and conflicting duplicate primary keys in every domain; exact unique positive |
| parse/derive | reject derived-state injection; serialize/parse/reduce recomputes equal keys; stored mismatch refuses |
| action/attempt | caller cannot substitute action target/scope; falsifier/evidence source changes attempt; admin-only facts do not |
| infrastructure | `REPLACED` with empty evidence rejects; exact evidenced replacement changes stable facts |
| authority | direct exact target ALLOW; legitimate delegated ASK_USER; spoofed/missing/wrong destination/wrong lineage REFUSE |
| completion | pending-release plus `COMPLETE` remains blocked; negation is interpreted structurally, not as phrase presence |
| path identity | repository-qualified case-sensitive exact path passes; alias/casefold/basename/suffix variants reject |
| terminal | exact result/completion/EOF passes; extra/missing/late/mismatched/semantic terminal or trailing byte rejects |
| capacity | marker/input overflow blocks without truncation, eviction, permutation cap, or false equality |
| raw/ledger | terminal/raw digest and ledger projection recompute identically; divergence refuses |
| pre-effect | capability rebind, exact claim verification, authority and AttemptKey consumption all precede fixture/output/workspace/subprocess effect |
| recovery | native compaction, no-summary/no-handle reconstruction, copied-handle rejection, and writer nonreplacement |
| fresh evidence | old generation/evidence rejects; pre-source evidence rejects; offline summary remains noncertifying |
| dry-run | every evaluator dry-run makes no model call, capability/attempt consumption, fixture, output, or workspace effect |

Each family also records one counterexample or positive/N/A for all six HappyCodex
surfaces. A mock alone cannot prove an imperative seam. Effects require temporary
fresh repositories/homes and explicit before/after manifests. Every coherent
batch ends in full offline GREEN, not merely focused GREEN.

## Complexity and source budgets

- semantic production LOC: at most 1,200 across the exact five-file package;
- semantic public exports: at most 20;
- evaluation production Python LOC: at most 6,900 across `evaluation/**/*.py`;
- aggregate Runtime: at most 262 lines, target at most 2,200 words, hard ceiling
  2,400 words;
- this ExecPlan: target 6,000–6,500 words; HappyCodex protocol hard maximum
  12,000 words.

Comments/docstrings count as production LOC. Test LOC does not count toward the
evaluation production limit. Generated evidence/output does not count as source
and may not hide production behavior. Semantic/public-export and Runtime budgets
are blocking Batch 1 closure gates and remain checked later. Total evaluation
production Python LOC is measured after every batch but becomes a blocking closure
gate only in Batch 3, after duplicate consumer semantics are deleted. A due budget
miss blocks terminal GREEN and is not waived by passing tests.

## Future authority and release gates

All gates below are separate, future, and currently unauthorized:

1. **Executor pilot.** Persist a conservative source-derived historical-cost
   envelope and the complete exact bounded calibration invocation first. Then
   request separate canonical user authority bound to exact impact token,
   source/package/config/role identities, model, effort, timeout, scope, output,
   command, and approval-request digest. The pilot has no prior cost. Only a
   sanitized successful actual becomes historical basis.
2. **Corpus.** Persist exact source-derived impact and complete invocation for the
   17 cases, then request its own exact authority. Pilot authority cannot be
   reused.
3. **Holdout.** Persist exact impact and adaptive invocation for the three pairs
   and candidate/public arms, then request its own exact authority. Corpus
   authority cannot be reused. First completion-blocking regression rejects;
   after first success use a second distinct pair; use the third only for
   split/uncertain results. At equal quality, uncached input plus output tokens
   and wall time each stay within 125% of public 0.2.
4. **Candidate freeze and exact-final.** After three batch GREEN and source freeze,
   materialize an exact isolated candidate under a separate grant. Run one fresh,
   isolated, neutral `gpt-5.6-sol/max` exact-final with no original worktree,
   writer narrative, ledger/history, network, tools, MCP, hooks, or write access.
5. **Isolated install.** Under separate authority use the plugin-creator
   cachebuster helper, never hand-edit personal marketplace state, and prove a
   fresh isolated install/invocation of the exact release plus external role
   config.
6. **Release and activation.** Release/publication and active-plugin mutation each
   need later exact authority. Activation is atomic and retains paired prior
   package, config, and cache for rollback. Rollback switches the paired set, not
   one component.

No `impact_token`, persisted invocation, candidate, check, or plan grants
permission. Only the canonical affirmative line derived from the exact
approval-request digest is authority. Prose agreement is not. Implementation
contains no live authority and performs no network action.

Any product-source change invalidates candidate identity, exact-final, install
proof, and source-bound evidence. A semantic input change reopens every dependent
gate. A harness change reopens affected execution receipts. An artifact-only
change reopens artifact/install evidence. A config/role digest change invalidates
Executor recovery and every bound authority. An Outcome, baseline, allowed-break,
family, or claim change requires explicit user authority; Root cannot infer it.

## Claims Ledger

| ClaimId | Type | Claim and closure | State |
| --- | --- | --- | --- |
| `O-06BR-01` | outcome | four-module kernel plus three GREEN batches delivers the normalized Outcome; exact package/inventory/deletion checks and exact-final required | `open` |
| `O-06BR-02` | outcome | event correction reduces repeated Runtime work without weakening progress, recurrence, or review gates; Runtime tests/budget required | `verified for Batch 1 Runtime; final closure pending later integration` |
| `P-06BR-01` | preservation | exact task authority, fixed writer, capabilities, attempts, resource claims, receipts, recovery, and false-GREEN repair remain fail-closed | `open` |
| `P-06BR-02` | preservation | fresh ledger, cost gates, corpus/holdout controls, source/evidence ordering, exact-final isolation, install/release, and atomic rollback remain | `open` |
| `A-06BR-01` | allowed break | old 9-module/8-slice/single-family topology and named wrappers/duplicates are removed with no compatibility path | `open` |
| `N-06BR-01` | exclusion | no cross-Root work, other-line commit input, live execution, install, release, marketplace mutation, activation, or 0.5 task migration | `verified for bootstrap; must remain` |

Irrelevance is positive evidence: a retained I/O owner or holdout comparator must
be shown not to encode duplicated semantic meaning. Unknown callers or inputs fail
closed. No claim can close from display prose or test-name presence.

## Exact command contract

Bootstrap commands are limited to the already corrected sequence:

```text
git worktree add -b codex/happycodex-0.6-bounded-redesign /home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign 96ac7563f22eb42d84c827717eba346ecfd80090
python3 /home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/skills/happycodex/scripts/resource_claim.py acquire --owner happycodex-0.6-bounded-redesign-executor --task /root/bounded_redesign_executor --execplan /home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign/docs/execplans/happycodex-0-6-bounded-redesign.md --receipt /tmp/happycodex-0.6-bounded-redesign-resource-claim.json --resource worktree=/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign --resource ref=/home/caichenghang/projects/happycodex::refs/heads/codex/happycodex-0.6-bounded-redesign --resource ledger=/home/caichenghang/projects/happycodex-worktrees/happycodex-0.6-bounded-redesign/docs/execplans/happycodex-0-6-bounded-redesign.md
python3 /home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/skills/happycodex/scripts/resource_claim.py verify --receipt /tmp/happycodex-0.6-bounded-redesign-resource-claim.json
git add -- docs/execplans/happycodex-0-6-bounded-redesign.md
git diff --check
git diff --cached --check
git commit -m "docs: bootstrap HappyCodex 0.6 bounded redesign" -m "HappyCodex-ExecPlan: docs/execplans/happycodex-0-6-bounded-redesign.md"
```

The helper verification runs again immediately before edit, stage, commit, and
terminal receipt. Its raw owner token remains only in the mode-0600 private
receipt; repository/control documents record its SHA-256 only.

Batch 1 has grant-specific RED/focused commands, then exactly:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m evaluation.cli verify
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
git diff --check
wc -l -w skills/happycodex/SKILL.md skills/happycodex/references/execplan.md
wc -l evaluation/semantic/{__init__,types,canonical,parse,decide}.py
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import evaluation.semantic as semantic; print(len(semantic.__all__))'
find evaluation -type f -name '*.py' -print0 | sort -z | xargs -0 wc -l
wc -l -w docs/execplans/happycodex-0-6-bounded-redesign.md
```

Batch 1 must not run the nonexistent `executor --dry-run`. Batch 2 first adds that
entrypoint under RED/GREEN. From Batch 2 onward, the terminal schedule is:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m evaluation.cli verify
python3 -m evaluation.cli executor --dry-run
python3 -m evaluation.cli corpus --dry-run
python3 -m evaluation.cli holdout --dry-run
git diff --check
wc -l -w skills/happycodex/SKILL.md skills/happycodex/references/execplan.md
wc -l evaluation/semantic/{__init__,types,canonical,parse,decide}.py
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import evaluation.semantic as semantic; print(len(semantic.__all__))'
find evaluation -type f -name '*.py' -print0 | sort -z | xargs -0 wc -l
wc -l -w docs/execplans/happycodex-0-6-bounded-redesign.md
```

Only `python3 -m evaluation.cli` invokes evaluator behavior. Every dry-run must
prove zero model, capability, attempt, fixture, output, workspace, and
authority-consumption effect. No evaluator command runs during G001 or G002.

## Accepted source and resource binding

G001 is accepted commit
`39401d20ffa900f277a3317e0422a6d1c14f3ea2`, tree
`14ab3b7279dacd6114ae66dc66164c83aa2ee9d2`; its receipt SHA-256 is
`055564e7d593732080df6017ee59dc3d3472456a51291c67a8d8db7218f8e898`.
G002 is accepted commit
`293f9ce34ffee0894fa889d9d3db9b441739b973`, tree
`802a122b0761be2fae648e9d69ffce64ca353b0f`; its receipt SHA-256 is
`7150690668e2525ae24596f1f9875ca5d75ed771b373c669710e8833cc5371e8`.
Both carry the mandatory ExecPlan trailer and are closed/non-renewable.

The installed claim helper remains:
`/home/caichenghang/.codex/plugins/cache/personal/happycodex/0.5.0+codex.20260729104011/skills/happycodex/scripts/resource_claim.py`.
Private claim receipt
`/tmp/happycodex-0.6-bounded-redesign-resource-claim.json` is mode `0600`,
SHA-256
`7ca4471b7633ac6389b57011de429929638526f7746a602f8cf370382fa9c926`;
owner-token SHA-256 is
`7fb27f436e544db813365b6cfb974b8f8bf50e1e8893f5d4fc9e2d600bd90f4c`.
One token claims exactly the bounded-redesign worktree, branch ref, and this
ledger. Its adjacent untracked claim directory is private control state, excluded
from product/commit content, and is not released automatically.

## Unaccepted G003-G005 same-batch hardening

G003 produced reachable commit
`f87b9dce68c88f537c0a18bd13da3d248248eebf`, tree
`89944223582465667e84ea2982bd31e810f64a28`, with exact subject/trailer and
mode-`0600` receipt SHA-256
`2c6e288edfab2e1c5b981ddfb298b1111d17d335d1286a2d75dddb305cd0d18e`.
Its recorded baseline/RED/focused/full checks remain historical characterization,
but Root did not accept G003 or its terminal closure.

Independent source review and executable probes on that exact commit confirmed
four material same-batch sibling families:

| Finding | Family | Exact reproduced G003 behavior | G004 boundary |
| --- | --- | --- | --- |
| `BR-FIND-B1-004` | `AUTHORITY-PUBLIC-FORGE` | public `from_adapter` and positional true marker each produced `ALLOW` | public construction/factory removed; only private issuance seam carries an identity seal; unissued authority refuses |
| `BR-FIND-B1-005` | `REPORT-ACTION-FORGE` | caller-built report with arbitrary action produced an AttemptKey | public construction fails; reducer-only seal required; AttemptKey also recomputes ProgressKey |
| `BR-FIND-B1-006` | `PARSER-TYPE-BYPASS` | duplicate evidence and a `str, Enum` identity were accepted; trusted Facts/record construction bypassed parse | exact string types, state/tag/domain/PK validation, duplicate rejection, canonical evidence order, immutable parser-issued Facts |
| `BR-FIND-B1-007` | `FALSE-CLOSE` | unresolved facts with no pending action reduced to `CLOSE` | exact terminal sets; deterministic `RECONCILE` before any close while stable state is unresolved |

All arrived before Root acceptance/terminal GREEN, join
`RB-06BR-001/instance` or `RB-06BR-002/instance`, and keep recurrence at 0.
No boundary-required recurrence or new repair wave is created.

Grant `HC06BR-G-004-B1-boundary-hardening`, sequence 4, binds G003 as exact
prestate, the same fixed Executor/role/owner and verified three-key claim, the
same two repair waves, and no other family. Durable intent:
`/home/caichenghang/.codex/happycodex-0.6-bounded-redesign-g004-b1-intent.json`,
mode `0600`, SHA-256
`8af7bb240c4fdbaad1a5349a8bb2a632bf23821c3668c4eb779db0ca5f8681d4`.
Its only repository paths are the five final semantic modules,
`tests/test_semantic_core.py`, and this ExecPlan. Runtime, identity, other
tests/consumers, package metadata, and later batches cannot change.

G004 produced commit
`e500340ce7c4de8e50f5aa8292515478b1b4bc66`, tree
`4a7c9db64c4551fc6fb588d5062eccaf38f2be9f`. Its mode-`0600` receipt at
`/home/caichenghang/.codex/happycodex-0.6-bounded-redesign-g004-b1-receipt.json`
has SHA-256
`3ee8276b50c969721733c5b82e54e0ce8d51e73297ca9c80fcbc2ac4a221203e`,
but is superseded and invalidated: Root's post-receipt acceptance amendment
changed the intent SHA, and a sealed arbitrary action still passed both
AttemptKey and effect enforcement. G004 source/intent/receipt remain immutable
historical inputs; they are not amended or rewritten.

Grant `HC06BR-G-005-attempt-recompute`, sequence 5, binds G004 as prestate and
permits only `evaluation/semantic/{canonical,decide}.py`,
`tests/test_semantic_core.py`, and this ExecPlan. Its mode-`0600` intent is
`/home/caichenghang/.codex/happycodex-0.6-bounded-redesign-g005-attempt-recompute-intent.json`,
SHA-256
`aada0d261a04dd035b1c7241a1c2ff3d6d1cbc60c31162d609727fc1d168736d`.
It authorizes one commit, subject `fix: recompute HappyCodex reducer actions`,
with trailer `HappyCodex-Grant: HC06BR-G-005-attempt-recompute`, then a
mode-`0600` receipt at the same basename ending `-receipt.json`.

G005 RED is
`/home/caichenghang/.codex/happycodex-0.6-bounded-redesign-g005-attempt-recompute-red.txt`,
SHA-256
`021f1c7382ccc281c4412cd66d4913588030e8bfd8a765628a192719e10da6e6`:
33 focused tests, exactly two failures, proving `_make_report` could seal an
arbitrary action accepted by both consumers. Focused GREEN is the corresponding
`-green.txt`, SHA-256
`298982308aa5ec7908e28e6179ade0f17fc20498fb2285a89c209b3600957b83`:
33/33 pass. The pure derivation remains owned by `decide.py`; effect enforcement
calls it directly, while AttemptKey locally imports `reduce_facts` and compares
the recomputed action without a module-level cycle.

The semantic package remains exactly five files and 20 exports; it is 1,092
production lines, below 1,200. Runtime bytes remain unchanged at 227 lines/1,919
words. No Goal, model/network/live call, authority/attempt, install, release,
activation, cross-line action, delegation, or claim release exists.

Current checkpoint: both Batch 1 family portions are G005 GREEN at recurrence 0,
but Root acceptance stays open. The Executor runs the complete offline terminal
schedule against this index, commits only the four authorized paths, verifies
source/status/claim/trailer, persists and reads back the G005 receipt, and stops.
The receipt is terminal evidence and the G005 intent cannot change afterward.
Batch 2 and every later live/cost/install/release/activation gate require new
exact authority.

Uncertainty rule: an outside path, changed prestate, unverified claim, ambiguous
or partial effect, reproduction mismatch, unknown input, identity/config drift,
unexpected live effect, or unbound evidence returns to Root before mutation. The
Executor never widens, retries, cleans up, accepts, waives, substitutes, releases,
or decides completion.

## Retrospective

Fill only after the normalized Outcome and every later gate close. Do not expose
the convergence history or writer narrative to exact-final review.
