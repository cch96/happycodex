# HappyCodex 0.6 Bounded Redesign

Protocol: `HappyCodex/0.5`

Current index: G001-G005 are accepted Batch 1 source at commit
`27ea46e27254426ee5737078117d43f28c9df523`. G006-G011 and Batch 2 are
accepted at commit `788c42917bf1e1bcec2515a361ce68b32a25fb46`, tree
`c1e5ba545399ac4a3a37a1396f1fccb5f69534f8`. G009 remains a rejected
intermediate corrected by G010. G012 is the plan-only Batch 3 contract
correction; it authorizes no G013 implementation.

Restore guard: restore this entire ExecPlan, then reconcile the exact Git source,
fixed Executor identity, three resource claims, external intent and receipts,
current grant, phase, families, checks, candidate, evidence, agents, and any Goal
before any write, review, effect, or completion claim. Conversation summaries,
copied handles, and another task's source do not reconstruct authority.

Phase: `plan-only contract correction`. Active grant
`HC06BR-G-012-B3-contract`, sequence 12, family `F-06BR-EVALUATOR`,
repair batch `RB-06BR-004/plan-contract`, recurrence 0. It binds accepted
commit/tree `788c42917bf1e1bcec2515a361ce68b32a25fb46` /
`c1e5ba545399ac4a3a37a1396f1fccb5f69534f8`, the accepted G011 terminal
receipt SHA-256
`c843a2edc454a1e3fd4c1d59051e82672439977577c6a18813db11a4251de0fb`,
the same fixed Executor and claim, this one plan edit, exact checks, staging,
commit, and post-commit verification.

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

The immutable base was a source construction point, not a GREEN baseline. Its
inherited partial semantic package produced the recorded three-failure
inventory/import-policy RED under 195 tests. The fixed Executor reproduced it;
external receipt SHA-256 is
`d6d7a7f3da1bf992382117a4511dc5120997f5ec5c928cad6c352e5fc1158f5a`.
Accepted Batch 1 repairs all three without weakening fail-closed inventory or
import policy. The old partial topology remains reachable history, not current
implementation evidence.

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
  role_config_digest,
  repository_digest,
  outcome_digest
}
```

It binds the fixed Root/Executor relationship, destination, exact repository
artifact, and normalized Outcome. Runtime supplies both lowercase-64hex digests
from a trusted adapter; neither is inferred from result prose, a conversation
summary, or a live handle.

`AuthorityProvenance` is separately issued by the current boundary adapter after
exact event/user/config validation. Its sealed fields are channel, root/source/
target task, executor task, destination, lineage, message, turn, content digest,
and reducer target/scope. The private kind is derived, never caller-declared:
`current_task_user` requires source equals target;
`cross_task_user_delegation` requires distinct tasks. Model output cannot
construct it. It is enforcement administration, not semantic progress.

`NextAction` is produced only by the reducer from parsed facts. It has an exact
variant, target, scope, family, falsifier, and evidence-source identity.
`EffectGate` is produced only by enforcement and contains
`ALLOW | ASK_USER | REFUSE`, the exact action target/scope, and a typed reason.
No parser accepts serialized `NextAction`, `EffectGate`, permission boolean,
phase, completion decision, or other derived action as a fact. Derived-state
injection fails unknown-field validation.

There is no semantic `pending` domain. An active gate is exactly
`id/state/family_id/nonempty evidence`; its family must exist. The reducer owns
the ordered policy: user selection asks; contract freeze, RED, checks, and
release verify; product edit, family hardening, and boundary repair implement;
reconciliation reconciles; focused review, candidate freeze, and exact final use
their exact variants. Unknown or blocked effectful gates reconcile. User
selection remains dominant; unresolved checks preempt effectful work/review/
freeze, and unresolved semantics preempt downstream review/freeze. An unlinked
fact uses a task-derived family rather than guessing a family association.

Corpus repository binding hashes canonical
`{domain:"happycodex/0.6/repository", repositories:[{namespace:"case:<id>",
baseline_revision:<first>, baseline_tree:<first>}]}`
and Outcome binding hashes canonical
`{domain:"happycodex/0.6/outcome", operative_request:<exact prompt>}`.

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
| exact cross-task user delegation to the bound task/executor/destination/lineage | `ASK_USER` |
| missing provenance or authority | `REFUSE` |
| spoofed or malformed channel/task/message/turn/content metadata | `REFUSE` |
| wrong destination | `REFUSE` |
| wrong root/lineage/task/executor/config | `REFUSE` |
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
| `F-06BR-RUNTIME` | semantic progress and event correction prevent equivalent repeated work and false GREEN | sealed parse/reduction plus action recomputation at both consumers | `Batch 1 accepted` | `RB-06BR-001/instance` | `0` |
| `F-06BR-AUTHORITY` | exact binding, provenance, reducer action, capability, claim, authority, and attempt gate every effect | private issuance, recomputation, and exact enforcement | `Batch 1 and G010 accepted` | `RB-06BR-002/instance` | `0` |
| `F-06BR-EVALUATOR` | terminal, identity, decision, ledger, and replay share strict parsing and exact recomputation | duplicate/order/terminal/path/key/raw-ledger divergence and consumer propagation | `Batch 2 accepted at 788c429` | `RB-06BR-003/instance` | `0` |
| `F-06BR-SEMANTIC-ACTION-BOUNDARY` | facts cannot inject actions and trustworthy metadata cannot be reclassified | parser/reducer/replay/authority/projection attack matrix | `Batch 3 contract frozen; implementation unauthorized` | `RB-06BR-004/instance` | `0` |

Holdout quality and cost comparison remain separate gated evidence. They do not
collapse into a family merely because their engines consume shared semantics.

## Batch 1: kernel, authority semantics, and early Runtime correction

Accepted Batch 1 replaces the inherited partial package with the exact five-file
surface, deletes `schema.py`, `MachineEnvelope`, `AdminFacts`, public
`canonical_set`, wrapper inflation, and every compatibility alias. Its RED/GREEN
matrix covers duplicate primary keys, tagged-ID/mutability violations, derived
action injection, key roundtrip/mismatch, action substitution, evidenced
`REPLACED`, admin-only nonprogress, authority variants, purity, capacity, and the
historical inventory/import-policy failures. It repairs Runtime to the five event
corrections, one wave/cumulative check per family, and one post-freeze exact-final.
The accepted full offline GREEN commit closes the 1,200-line/20-export semantic
budgets and Runtime limits without any live effect.

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

Offline authority fixtures prove allow/ask/refuse without a provider call. The
accepted full offline GREEN commit closes exact 17/3 inventory, deletion proof,
focused receipts, and dry-run non-effects. Its new `executor --dry-run`, like
corpus and holdout dry-runs, creates no model call, capability, attempt, fixture,
output, workspace mutation, or authority consumption.

## Batch 3: fresh evidence, effect ordering, recovery, and candidate source

The completed read-only Batch 3 audit verdict is **GO-WITH-CONDITIONS offline /
NOT YET live**. The 6,900-line ceiling is feasible by deleting uncalled legacy
validation and duplicate phase/projection semantics, but the current standalone
CLI has no authenticated current-message/turn metadata and therefore cannot mint
trustworthy authority. G012 freezes this design only; G013 and G014 require later
exact grants.

The existing generation-6 genesis is a clean-break pre-anchor ledger. A null
`source_anchor` is legitimate only while state is `refresh_required`, all three
gate authorities are null, calibration and accepted evidence are empty, and
certification is absent. It is not a compatibility path, migration, alias,
fallback, prior-source reader, or authority. Old generation evidence is inert and
must be physically deleted in G013. Offline checks and content-addressed
`offline_summary` evidence never promote `refresh_required` to `certified`.

Live authority may originate only in private trusted host provenance for the
current user message and turn. The host adapter validates exact root/source/
target task, fixed Executor, destination, lineage, role config, message, turn,
content digest, reducer-produced target, scope, and complete invocation before a
private issuer constructs `AuthorityProvenance`. Argument strings, environment,
ledger or fixture JSON, model prose, copied handles, and self-reported records
cannot mint it. Standalone CLI execution remains fail-closed until this trusted
host bridge exists. Offline tests use a deterministic private adapter fixture to
prove one exact ALLOW; that fixture is not importable production authority.

After semantic enforcement returns ALLOW, the validator mints one sealed
immutable process-local capability. Live owns issuance and claims; corpus and
holdout can only rebind the same capability at gate, unit, and phase boundaries.
The exact pre-effect sequence is normative:

```text
read-only validate identities, invocation, safe paths, claim keys, and provenance
  -> enforce ALLOW and mint sealed process-local capability
  -> O_EXCL consume gate authority digest
  -> recompute reducer action and O_EXCL consume AttemptKey
  -> O_EXCL acquire sorted resource digests
  -> O_EXCL acquire output digest
  -> rebind the same capability
  -> create authorized fixture/output/workspace/mapping effects
  -> derive and O_EXCL consume the phase child attempt
  -> invoke the model subprocess
  -> sanitize, persist receipt, and replay by recomputation
```

Every output is an explicit absolute absent path beneath a validated existing
safe parent; authorized paths never default to `mkdtemp`, create parents, follow
symlinks, or touch the repository before all preceding claims. Claim files use
mode `0600`, private claim directories use `0700`, and `O_EXCL` plus no-follow
where supported provides one winner. Claims are administrative durable effects,
not a transaction: any claim consumed before a later collision remains consumed
and is never deleted or retried. A new attempt requires a new reducer-derived
semantic prestate and exact authority, never wording changes. Raw model events,
secrets, unsanitized streams, and hidden oracle bodies stay outside the
repository; only sanitized summaries, hashes, fixed public fixtures/prompts,
hidden-oracle hashes, and executable evaluator code may be tracked.

Recovery reuses the existing `pre-freeze-compaction` case and creates no new paid
case. The positive matrix proves native same-task compaction/resume and, as a
distinct phase of that same case, fresh no-summary/no-handle reconstruction from
the current ExecPlan, exact Git state, external intent/receipts, fixed claims, and
durable evaluator facts. The negative matrix refuses before every effect for a
copied or serialized handle, cross-task or cross-Root authority, replacement
writer/Executor, wrong task/session/thread/config/permission, wrong role digest,
wrong destination/lineage, concurrent resume, or mismatched claim. A model output
string naming the writer is never identity evidence.

G013 creates source commit `S`. Its exact allowed inventory is production and
evaluator Python, evaluator schemas/fixtures, tests, repository/package/docs
including this ExecPlan, `AGENTS.md`, `README.md`,
`.codex-plugin/plugin.json`, and the new tracked
`evaluation/executor-role.json`; it also deletes the three old tracked 0.4
evidence JSON files. `evaluation/results/current.json` may change in G013 only to
the strict refresh-required pre-anchor form with null `source_anchor`, null
authorities, and no accepted evidence. No evidence summary is created. G013 runs
the complete offline suite, verify, all dry-runs, source/caller/deletion scans,
budget checks, and diff/status checks GREEN before committing `S`.

`evaluation/executor-role.json` is an `artifact` input containing the expected
fixed Executor role contract. Its exact canonical bytes are hashed into role and
candidate identity but confer no authority; private real host metadata must match
those bytes and the active task binding. The candidate manifest base version is
`0.6.0`. G012 does not run or imitate the plugin-creator helper. A future official
cachebuster must run under its own grant before final source freeze and
exact-final; because it changes artifact identity, the resulting source must be
re-anchored before evidence or review.

G014 creates anchor commit `A` and may edit only excluded
`evaluation/results/current.json` plus this ExecPlan. From a normalized
`git archive S`, it records the reachable `S` commit/tree, exact package artifact
and semantic identities, engine manifest, and executor-role identity; working-tree
bytes cannot substitute. `A` keeps all future gate authorities null and state
`refresh_required`. G014 also runs the full offline schedule GREEN. Since
`current.json` is excluded from package and engine identity, `A` does not create
circular source identity. Every later evidence commit must be a strict descendant
of both `S` and `A`.

Neither G013 nor G014 authorizes pilot, corpus, holdout, model or network calls,
exact-final, install, release, marketplace/cache mutation, cachebuster, activation,
claim release, or certification. Product changes after `S` invalidate the anchor
and reopen the relevant family.

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

G009 owns the minimal generation-6 pre-anchor genesis already accepted through
Batch 2. G013 owns the bounded source implementation and `S` inventory frozen
above. G014 owns only the excluded ledger anchor and this ExecPlan. A tracked
manifest or role-contract edit never authorizes installed plugin bytes, personal
marketplace/cache state, external config, or a cachebuster helper invocation.

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
  -> validate private trusted-host provenance and issue AuthorityProvenance
  -> pure enforce to ALLOW, ASK_USER, or REFUSE
  -> if ALLOW, mint sealed process-local capability
  -> O_EXCL-consume authority, AttemptKey, sorted resources, then output
  -> rebind capability and create the authorized non-model effects
  -> O_EXCL-consume the just-in-time phase child attempt
  -> only then invoke the model subprocess
  -> strict terminal parse and sanitized typed projection
  -> canonical receipt/ledger write
  -> replay from raw sanitized facts by parse/reduce/enforce/recompute
```

No caller may skip, reorder, or precompute a later arrow. Consumed claims are
never deleted or retried. In particular, output directories and fixtures do not
exist before authority, AttemptKey, sorted resources, output claim, and capability
rebind. A dry-run stops before capability mint and consumption. `ASK_USER` and
`REFUSE` stop before every effect. A terminal tag says what the provider reported,
not whether release or completion gates are satisfied. Thus an OPEN `release`
gate plus `CompletionTag.COMPLETE` reduces to VERIFY or a safer blocker and cannot
close.

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
| authority | exact direct ALLOW; exact cross-task ASK_USER; spoofed/missing/wrong task/executor/destination/lineage REFUSE |
| completion | open release plus `COMPLETE` remains blocked; negation is interpreted structurally, not as phrase presence |
| path identity | repository-qualified case-sensitive exact path passes; alias/casefold/basename/suffix variants reject |
| terminal | exact result/completion/EOF passes; extra/missing/late/mismatched/semantic terminal or trailing byte rejects |
| capacity | marker/input overflow blocks without truncation, eviction, permutation cap, or false equality |
| raw/ledger | terminal/raw digest and ledger projection recompute identically; divergence refuses |
| pre-effect | capability rebind, exact claim verification, authority and AttemptKey consumption all precede fixture/output/workspace/subprocess effect |
| recovery | reuse `pre-freeze-compaction`: native same-task compaction and distinct no-summary/no-handle reconstruction pass; copied/serialized handle, cross-task/Root, replacement writer/Executor, wrong role/config/session/thread/destination/lineage/claim, and concurrent resume refuse before effects |
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

G013 freezes these per-module hard ceilings:

| Production module | LOC | Production module | LOC |
| --- | ---: | --- | ---: |
| `evaluation/__init__.py` | 6 | `evaluation/cli.py` | 165 |
| `evaluation/core/__init__.py` | 3 | `evaluation/core/identity.py` | 650 |
| `evaluation/core/impact.py` | 450 | `evaluation/core/ledger.py` | 760 |
| `evaluation/core/receipt.py` | 260 | `evaluation/corpus/__init__.py` | 3 |
| `evaluation/corpus/engine.py` | 2,150 | `evaluation/holdout/__init__.py` | 3 |
| `evaluation/holdout/blind.py` | 205 | `evaluation/holdout/compare.py` | 152 |
| `evaluation/holdout/engine.py` | 330 | `evaluation/live.py` | 300 |
| `evaluation/semantic/__init__.py` | 44 | `evaluation/semantic/canonical.py` | 111 |
| `evaluation/semantic/decide.py` | 284 | `evaluation/semantic/parse.py` | 248 |
| `evaluation/semantic/types.py` | 513 | **Total** | **6,637** |

The total leaves 263 lines of required headroom beneath 6,900. Reductions must
physically delete uncalled legacy validation, compatibility-era evidence
structure, duplicate semantic projection, and repeated phase orchestration.
They may not move production behavior outside `evaluation`, hide it in generated
files/tests, collapse statements through formatting compression, or waive a
module ceiling.

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
4. **Candidate freeze and exact-final.** After G013/G014 GREEN and the separately
   authorized official cachebuster/re-anchor, materialize an exact isolated
   candidate under a separate grant. Run one fresh,
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

No `impact_token`, persisted invocation, role-contract artifact, candidate,
check, plan, JSON, environment value, argv string, or prose grants permission.
Only private authenticated current-turn host metadata matching the exact persisted
request can issue process-local provenance. Without that bridge, live execution
fails closed. Implementation contains no live authority and performs no network
action.

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

Bootstrap and Batch 1/2 command receipts are accepted history and are not
re-executed by G012. The installed helper verifies the same private receipt
immediately before every edit, stage, commit, and terminal receipt. Its raw owner
token remains only in mode-0600 control state; this plan records its SHA-256.
From accepted Batch 2 onward, every implementation terminal schedule is:

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

## Accepted Batch 1 and Batch 2

Root accepted G003-G005 together as Batch 1 commit
`27ea46e27254426ee5737078117d43f28c9df523`, tree
`e4fd88e21d0b4190ccf407b082f6ba1cbe6af59f`. The accepted boundary removes
public authority/report construction, rejects parser/type/duplicate bypasses,
recomputes action at AttemptKey and enforcement, and never closes unresolved
facts. Earlier invalidated intermediate receipts remain history, not evidence.

G006-G008 build the combined evaluator seams and close the semantic inventory.
G009 is retained as a rejected intermediate because legacy authority,
approval-string, attempt, cost, and old-evidence surfaces remained. G010 removes
those residuals and makes every non-dry executor/corpus/holdout path refuse before
effects. Root independently reproduced 206/206 GREEN,
refresh-required/noncertified verify, all three dry-runs, expected impact exit 2,
old-field/generation rejection, pre-effect refusal, exact snapshot, zero legacy
production hits, and diff/claim/hash checks.

G011 commits and closes Batch 2 at
`788c42917bf1e1bcec2515a361ce68b32a25fb46`, tree
`c1e5ba545399ac4a3a37a1396f1fccb5f69534f8`. Its mode-`0600` terminal receipt
SHA-256 is
`c843a2edc454a1e3fd4c1d59051e82672439977577c6a18813db11a4251de0fb`.
Evaluation production Python is 8,667 lines at that accepted boundary; G013 must
close the frozen 6,637-line module budget without moving or compressing behavior.
The active ledger is exact generation `0.6`, `refresh_required`, with six sorted
pending gates, all 17/3 identities, three null authorities, empty calibration
and accepted evidence, and null receipt head/certification. Historical cost,
attempt, singular-authority, compatibility, and old-evidence paths are absent
from active production.

The semantic package remains exactly five files, at most 1,200 production lines
and at most 20 exports. Runtime bytes remain unchanged. G012 records the
read-only Batch 3 audit and freezes future G013/G014 contracts only. No Goal,
pilot, corpus, holdout, model/network/live call, exact-final, authority or attempt
consumption, install, release, marketplace/cachebuster, activation, delegation,
claim release, G013, or G014 effect is authorized.

Uncertainty rule: an outside path, changed prestate, unverified claim, ambiguous
or partial effect, reproduction mismatch, unknown input, identity/config drift,
unexpected live effect, or unbound evidence returns to Root before mutation. The
Executor never widens, retries, cleans up, accepts, waives, substitutes, releases,
or decides completion.

## Retrospective

Fill only after the normalized Outcome and every later gate close. Do not expose
the convergence history or writer narrative to exact-final review.
