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
| Intended use/consequence | advisory lead, behavior-plan/grant/phase input, controlled write, or final review consequence | authenticated Root-owned dispatch/tool receipt |
| Selected agent request | platform agent type and/or namespaced custom-agent name | authenticated Root-owned dispatch/tool receipt |
| Single question | one bounded decision-changing question for each read-only role; `N/A` with reason for Root/Executor | authenticated Root-owned dispatch/tool receipt |
| Requested route or config | explicit model/effort for builtin/default, or namespaced custom-agent path and SHA-256 whose model/effort take precedence | authenticated Root-owned dispatch/tool receipt |
| Fork mode | requested `none` or bounded positive integer, never `all` | authenticated Root-owned dispatch/tool receipt |
| Parallel independence | exact independent axis and non-overlapping read-only scope, or `not parallel` | authenticated Root-owned dispatch/tool receipt |
| Input identities | exact baseline and candidate identity; use explicit `not-yet-created` before a candidate exists | authenticated Root-owned dispatch/tool receipt |
| Prompt/brief digest | digest of the exact bounded question or neutral brief | authenticated Root-owned dispatch/tool receipt |
| Required guarantees | exact routing, technical isolation, and every other guarantee required by task, source, or user; explicit `none` where justified | authenticated Root-owned dispatch/tool receipt |
| Spawn acceptance | platform accepted the exact spawn request | authenticated dispatch/tool result |
| Output identity | authenticated child/run/result handle; missing is a hard stop | host-issued dispatch/result receipt |
| Actual agent role/name | exposed value or `unverified`; record-only | runtime-issued session/turn metadata |
| Effective route | exposed model/effort, `unverified`, or mismatch | runtime-issued session/turn metadata |
| Effective permissions | exposed sandbox/approval, `unverified`, or mismatch against a required isolation guarantee | runtime-issued session/turn metadata |
| Runtime identity | exposed runtime supplement or `unverified`; never substitutes for Output identity | runtime-issued session/turn metadata when exposed |
| Phase | phase in which the invocation starts and its output is admitted or discarded | Root admission record |
| Admission state | `admitted`, `restricted`, `advisory`, or `discarded`, with the evidence and consequence | Root admission record |
| Phase gate | role-specific consequence after applying required guarantees and evidence restrictions | Root admission record |
| Terminal receipt | terminal state, output/evidence digest, truncation, and receipt identities | Root admission record bound to host-authenticated Output identity and terminal result, plus any exposed runtime metadata |

Before dispatch and before reading substantive output, bind the role, intended
consequence, selected request, requested route/config/fork, input identities,
prompt digest, and predeclared required guarantees. Platform acceptance of the
exact request and a mechanically authenticated output identity are always
required. Missing output identity is a hard stop. Missing optional telemetry
never waives a required guarantee. Record an absent effective name, route, or
permission as `unverified`; continue only the consequence that does not depend
on it. Exact routing and technical isolation claims remain withheld while their
evidence is `unverified`. Discard explicit mismatch, malformed or ambiguous
claimed evidence, an unsafe value against a required guarantee, identity/scope
drift, and ambiguous or partial effects.

Names, agent self-reports, profile defaults, and prompt text do not prove
routing or isolation. A full-access parent may override a custom profile's
`sandbox_mode = "read-only"`. When technical isolation is required, establish a
read-only top-level or parent environment before dispatch and verify effective
permissions or independently establish the same isolation/effect boundary.
Required hard isolation that is not independently established leaves review
open. When hard isolation was not required, missing permission telemetry does
not block unrelated use and does not support an isolation claim.

Root decomposes the problem into independent decision-changing axes before
spawning. For two or more qualifying independent decision-changing axes, Root
concurrently dispatches one native Explorer per axis through the host's builtin
`explorer` selector or an admitted namespaced custom Explorer selector.
Ordinary parallel tool calls are not Explorer dispatches. Give each Explorer
one bounded question. Unverified Explorer or Challenger routing/isolation gives
advisory leads only until Root reproduces every material fact from source.
Record Challenger before behavior-plan freeze and the unique Executor after
that freeze. Executor effects require authenticated output identity, fixed
ownership, exact grant, source/prestate, paths/resources, and allowed effects;
Root relies on Git, tests, and receipts rather than Executor prose. Record one
fresh empty-history Exact-final with a neutral brief after candidate freeze. It
may count under missing optional route/permission telemetry only when exact
routing and hard isolation were not predeclared required, output identity is
bound, candidate identity is unchanged, Root reproduces material findings, and
unverified guarantees are disclosed. A repair returns the task to `working`
and requires a new candidate and Exact-final receipt.

No user-facing mode, level, or continuation phrase is part of this protocol.
Ask the user only when continuation would change the Outcome, authority, trust
boundary, or an explicitly required guarantee.

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

At `exact_final`, bind one fresh logically read-only review, its neutral brief
and command, requested route and permissions, exposed values or `unverified`,
and hard technical isolation only when predeclared required. Always bind the
authenticated Output identity, frozen source/candidate identities, external
reads, checks, diff and obligation coverage, truncation limits, terminal result,
findings, Root reproduction, and dispositions. Missing optional route or
permission telemetry alone does not leave review open. A required but unproven
guarantee, missing output identity or coverage, explicit mismatch, candidate
drift, unsupported evidence, or an unchanged rerun does. Any product change
returns to `working`.

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
