# HappyCodex ExecPlan

Persist this current index before qualifying research or product work. Use the
repository policy path when one exists, otherwise
`docs/execplans/<task-slug>.md`. Keep one authoritative checkpoint and compress
closed history into content-addressed receipts.

## Contract

- Record the protocol invocation, restore guard, one of `working`,
  `candidate_frozen`, `exact_final`, or `closed`, the exact active grant, and
  Goal state.
- Freeze the verbatim request and amendments with anchors/digests; normalized
  Outcome, preservation, exclusions, allowed breaks, waivers, and required
  reruns.
- Bind repositories, source revisions/trees, refs, worktrees, package/config
  identities, baseline command/exit/failures, and accepted failure identities.
- Record decision-changing designs, the selected boundary, rejection reasons,
  and remaining uncertainty.

## Roles and authority

Record one row per role invocation with all of these fields and evidence
sources:

| Field | Required value | Evidence source |
| --- | --- | --- |
| Logical role | `Root`, `Explorer`, `Challenger`, `Executor`, or `Exact-final`; separate from platform naming | authenticated Root-owned dispatch/tool receipt |
| Selected agent request | platform agent type and/or namespaced custom-agent name | authenticated Root-owned dispatch/tool receipt |
| Single question | one bounded decision-changing question for each read-only role; `N/A` with reason for Root/Executor | authenticated Root-owned dispatch/tool receipt |
| Requested route or config | explicit model/effort for builtin/default, or namespaced custom-agent path and SHA-256 whose model/effort take precedence | authenticated Root-owned dispatch/tool receipt |
| Fork mode | requested `none` or bounded positive integer, never `all` | authenticated Root-owned dispatch/tool receipt |
| Parallel independence | exact independent axis and non-overlapping read-only scope, or `not parallel` | authenticated Root-owned dispatch/tool receipt |
| Input identities | exact baseline and candidate identity; use explicit `not-yet-created` before a candidate exists | authenticated Root-owned dispatch/tool receipt |
| Prompt/brief digest | digest of the exact bounded question or neutral brief | authenticated Root-owned dispatch/tool receipt |
| Spawn acceptance | platform accepted the exact spawn request | authenticated dispatch/tool result |
| Actual agent role/name | effective platform/custom role or name when the runtime exposes it | runtime-issued session/turn metadata |
| Effective route | effective model and effort | runtime-issued session/turn metadata |
| Effective permissions | effective sandbox and approval policy, not profile or prompt claims | runtime-issued session/turn metadata |
| Runtime identity | child/run plus task/session identity | runtime-issued session/turn metadata |
| Phase | phase in which the invocation starts and its output is admitted or discarded | Root admission record |
| Admission state | `inadmissible` until Root cross-binds both receipts; then `admitted` or `discarded` with reason | Root admission record |
| Phase gate | before admission, output cannot enter the behavior plan, trigger a write grant, advance phase, or count as a final verdict | Root admission record |
| Terminal receipt | terminal state, output/evidence digest, truncation, and receipt identities | Root admission record bound to runtime terminal metadata |

Before dispatch, Root verifies its own effective route is `gpt-5.6-sol/max` and
that the host can request the exact selector and expose the required effective
metadata. Platform acceptance completes the authenticated dispatch receipt and
the child may start immediately. Root then reads the runtime-issued
session/turn metadata and cross-binds it to the dispatch receipt. Runtime
metadata is not required to echo logical role, fork, input identities, or
prompt digest because those belong to the authenticated dispatch receipt. Until
both required sources cross-bind, all child output is inadmissible and the phase
gate above remains closed. A missing source or mismatch requires Root to
interrupt the child if still running, discard the output, and fail closed.

Names, agent self-reports, profile defaults, and prompt text do not prove
routing or isolation. A full-access parent may override a custom profile's
`sandbox_mode = "read-only"`. When technical isolation is required, establish a
read-only top-level or parent environment before dispatch and verify effective
permissions after dispatch; unverified output remains inadmissible.

Root decomposes the problem into independent decision-changing axes before
spawning. For two or more qualifying independent decision-changing axes, Root
concurrently dispatches one native Explorer per axis through the host's builtin
`explorer` selector or an admitted namespaced custom Explorer selector.
Ordinary parallel tool calls are not Explorer dispatches. Give each Explorer
one bounded question. Root reproduces and merges their evidence without voting.
Record Challenger before behavior-plan freeze, the unique Executor after that
freeze, and exactly one fresh empty-history Exact-final with a neutral brief
after candidate freeze. A repair returns the task to `working` and requires a
new candidate and Exact-final receipt.

Bind the Executor owner-token digest and every resource claim.

For each grant record its identifier and sequence; fixed Executor; exact
commit/tree/status prestate; closed paths/resources; allowed operations/effects;
acceptance checks; stop conditions; and active, consumed, or returned state.
Persist an external intent before the first mutation and a terminal receipt
after the last.

Every effect needs its own source-derived impact, complete invocation, resource
claim, separate exact gate plan, and outcome receipt. One user response may
authenticate a content-addressed bundle of bounded model, corpus, holdout, and
review plans for the same candidate and snapshot; record its cumulative cap and
stop on failure, drift, or exhaustion. Install, release, marketplace, and
activation remain separate authorities.

## Obligations and evidence

Use one current table. Each row follows only affected surfaces justified by
actual risk; record `N/A` with evidence instead of manufacturing coverage.

| Obligation | Type | Observable contract | Affected surfaces and callers | Falsifier/RED | Evidence and source identity | State |
| --- | --- | --- | --- | --- | --- | --- |
| `<exact ID>` | `outcome/preservation/allowed-break/premise/exclusion` | `<behavior>` | `<risk-based inventory>` | `<counterexample>` | `<digest/receipt>` | `open/verified/N/A` |

Material findings use one exact case-sensitive identity shared with any blocker.
Classify each as baseline-unchanged, resolved, candidate-new, or unknown.
Unknown stays open. Do not store a derived lifecycle action.

## Event state and checks

Record the current coherent diagnosis and repair wave, its new falsifiers,
changed paths, real-path RED or characterization, focused command, cumulative
offline command, exits, failures, output digests, and source tree. An unchanged
failure cannot be retried. One post-GREEN recurrence may use one boundary-level
alternative; record its falsifier and affected checks. Another unchanged failure
or recurrence returns the decision to the user.

Corrections occur only on new evidence, check completion, source/config drift,
pre-effect revalidation, candidate freeze, review findings, or explicit user
authority. Administrative updates and elapsed time are not progress.

## Candidate and review

At `candidate_frozen`, bind the clean product snapshot, baseline/candidate
identities, manifest equality, complete affected-diff inventory, package/config
and toolchain, remaining dirt, obligations, checks, effects, and closed gates.

At `exact_final`, bind the neutral brief and command, isolated read-only session,
exact source/config/model/effort/permissions, external reads, diff and obligation
coverage, truncation limits, terminal receipt, findings, Root reproduction, and
dispositions. Any product change returns to `working`.

## Recovery

Bind task/root/executor identities, owner token and resource claims, selected ref
or approved archive, source commit/tree/worktree, contract, active grant,
obligations, current phase/gates, test receipts, agent receipts,
candidate/review identities, effects, Goal state, and exactly one checkpoint.
After resume, record fresh reads from the ExecPlan, Git, tests, claims, receipts,
agents, and Goal. Unknown or mismatched facts remain open.

## Closure

Closure records the final reachable source and product tree, checks, review,
evidence/effect receipts, exclusions, accepted baseline failures, owned status,
install/release/activation state, any explicitly waived or unrun gate, and final
Goal state. Retrospective text is not completion evidence and is never exposed
to exact-final.
