---
name: happycodex
description: High-risk, cross-system, or compaction-prone work; one fixed Executor writes while Root decides, grants, and verifies.
---

# HappyCodex

HappyCodex adds a durable contract to native planning, Git, tests, agents, review,
and an explicitly requested Goal. It is guidance, not a controller. Authorization
permits an action; the ExecPlan defines completion; evidence binds a candidate;
Goal controls automatic continuation. Never infer one from another.

## Select and freeze

Use HappyCodex for public contracts, migrations, persistence, concurrency,
destructive or production work, exhaustive replacement, long research, or work
likely to cross compaction. Uncertainty qualifies. A clearly local low-risk edit
may use native Plan, tests, and diff; if its scope grows, establish the ExecPlan
before the next product write.

Persist the template in `references/execplan.md` at the repository policy path or
`docs/execplans/<task-slug>.md`. Freeze the verbatim request and amendments,
normalized Outcome, exclusions, allowed breaks, immutable source/worktree, exact
baseline command and failures, claims, families, grants, checks, and gates. A
contract revision freezes these facts before product work. Narrowing a claim,
widening a break, changing Outcome or baseline, or waiving a gate requires
explicit user authority; derived claims may grow only when entailed by the frozen
contract, with provenance and invalidation recorded.

Map every request clause and baseline-reachable behavior to observable claims,
including defaults, boundaries, malformed input, callers, persistence, output,
recovery, and downstream failure. Give material findings stable identities and
classify them as baseline-unchanged, resolved, candidate-new, or unknown. Unknown
stays open. Irrelevance and `N/A` require evidence.

Before freeze, compare materially distinct decision-changing designs and
challenge omissions until no clearly better in-contract design remains. For an
exhaustive or architecture-shaping claim, Root obtains a fresh baseline-only
read-only challenge from the frozen request and source, without sharing preferred
answers or the findings ledger.

## Roles and grants

Root reads, decides, grants, reproduces, and verifies. One fixed Executor is the
sole controlled-domain writer for the whole task: it owns the ExecPlan, tests,
product, commits, and receipts, never delegates, and cannot be replaced after
compaction. Explorers, Challengers, and reviewers are read-only. Root never edits,
stages, commits, installs, releases, or activates controlled bytes.

Record each participant's runtime-issued task/session identity, effective
model/effort, permissions, source, and terminal receipt. A role label, summary, or
completion sentence is not evidence. Give a read-only agent one bounded,
decision-changing question; parallelize only independent questions and do not
duplicate them. Root reproduces the union of findings, not a vote.

Every write grant binds one Executor, exact paths/resources, source commit/tree
and dirty state, allowed operations, acceptance checks, cost boundary, and stop
conditions. The Executor persists durable intent before mutation and a complete
receipt afterward. Changed prestate, identity/config drift, ambiguous or partial
effect, unknown input, or wider scope returns to Root without retry or cleanup.

## Event correction

`ProgressKey` binds stable task identity and semantic facts. `AttemptKey` also
binds the reducer-produced action target/scope and the falsifier/evidence source.
Administrative cursors, timestamps, receipts, claims, and wording do not create
progress. Correct only on these events:

| Event | Required correction |
| --- | --- |
| `repeated_attempt_failure` | Reconcile durable facts; never retry by rewording. Before terminal GREEN, join a same-family sibling to the active batch with RED. After GREEN, apply recurrence and boundary rules or return the decision to Root. |
| `new_family` | Root assigns a stable family and one coherent diagnosis/repair wave covering source, type, ordering, mutability, replay, and consumers. |
| `repair_batch_end` | Run the family's one cumulative offline check; focused checks inside the wave localize RED/GREEN but create no extra review loop. |
| `pre_effect` | Recompute the action and enforce current authority, capability, resource and attempt claims, and consumption immediately before the effect. |
| `candidate_freeze` | Require closed/evidenced families, full offline GREEN, controlled dirt, bound source/package/config, and no material unknown; then freeze once. |

## Implement and recover

Use `implementation → focused_hardening → candidate_frozen → exact_final →
closed`. Root assigns each invariant family and repair batch. Before terminal
GREEN, a same-family finding joins the wave. A material recurrence after GREEN
sets `boundary_required`: repair the unique choke point, delete bypasses, rescan
the six surfaces, and run one focused bypass falsification. A second recurrence
after boundary repair stops for user choice. A genuinely new family starts its
own wave.

The Executor first records RED or an explicit characterization, then applies one
coherent granted change and runs real-path focused and cumulative checks. A mock
cannot prove its own seam. Each terminal wave has durable source and check
evidence. Do not run exact-final during repair. Product change after freeze
returns to focused hardening and invalidates affected candidate/review evidence.

Keep the ExecPlan as a current index, not a history dump. Its Recovery Manifest
binds the task, Root, fixed Executor, owner token digest, source/ref/worktree,
claims, one authoritative checkpoint, tests, agents, phase, families, batch,
gates, and receipt digests. After compaction or resume, read the full plan and
reconcile it with current Git, tests, claims, receipts, agents, and Goal before
any write or completion claim. Conversation summary, copied handle, or prose
cannot reconstruct authority. Missing or mismatched durable facts fail closed.

## Safety invariants

| Boundary | Invariant |
| --- | --- |
| `authority` | Only the exact current grant authorizes writes. Direct authority may allow its exact target; legitimate delegation asks the user; missing, spoofed, wrong issuer/destination/lineage/target/scope refuses. |
| `recovery` | Restore the full current index and exactly one content-addressed checkpoint; reconnect only the recorded Executor and never substitute a writer. |
| `resource_claim` | Before every write, stage, commit, receipt mutation, or authorized effect, acquire/verify all sorted worktree/ref/ledger/output keys under one owner token; conflict or stale ownership stops. |
| `review_isolation` | Exact-final uses one fresh isolated read-only session after freeze with a neutral brief, exact source range, objective checks, accepted baseline failures, and no ledger, repair story, writer narrative, or preferred verdict. |
| `cost` | Model, corpus, holdout, install, release, and activation effects need separate exact impact/invocation authority; a token or estimate alone grants nothing, and dry-runs cause no effect. |
| `no_commit` | If commits are forbidden, require a user-selected durable location, leave the index untouched, and preserve every milestone in a reachable private ref or approved content-addressed archive; otherwise stop. |
| `goal` | Goal exists only when explicitly requested. It continues existing authority but grants no amendment, waiver, review, cost, or effect; complete it only after all matching gates close. |
| `secret` | Never persist secrets or raw model events in repository, control, brief, receipt, log, or review artifacts; retain only sanitized summaries and digests outside product bytes. |
| `baseline_failure` | Record every baseline failure by stable identity. It blocks unless explicitly accepted and unchanged; candidate failures cannot be relabeled as baseline. |

## Review and complete

The Executor projects every owned staged, unstaged, and untracked product path
into a clean snapshot. Freeze neutral baseline and candidate source identities;
Root proves manifest equality, complete diff-unit inventory, checks, and allowed
control-file exclusions. Persist the review command, neutral brief, source,
permissions, limits, and output before launch.

The fresh exact-final reviewer receives the verbatim request, frozen source
range, accepted failures, checks, and exclusions. Its runtime receipt binds
session, source/config, model/effort, read-only isolation, external reads,
diff-unit and obligation coverage, truncation limits, and findings. Missing
coverage, contamination, mismatch, or unsupported evidence leaves review open.
Never rerun an unchanged candidate to seek a verdict.

Root classifies a finding only against the frozen request, accepted behavior,
safety/data integrity, production conditions, or exhaustive replacement. It
records confirmed, rejected with counter-evidence, or unresolved; unresolved
material findings stop. Repair identifies invalidated evidence and cost, returns
to the applicable family wave, refreezes, and obtains a new neutral exact-final.
Only explicit user text waives a named gate, and completion discloses every
unrun gate.

Complete only when all claims and families are verified or evidenced `N/A`, real
paths pass, baseline failures are resolved or accepted unchanged, no new secret
finding exists, owned status is accounted for, all required effects and receipts
are bound to the frozen product, and the matching Goal—if any—is complete.
