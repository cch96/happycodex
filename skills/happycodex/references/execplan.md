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
- Root must freeze a named supported-workflow envelope before the behavior-plan
  freeze. Record named workflows/preconditions, user-visible outcomes, source
  basis, exclusions, the selected design/complexity boundary, and the bounded
  Exact-final-triggered repair budget with its consumed count.

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
fresh empty-history neutral Exact-final after candidate freeze. Its brief binds
the frozen supported-workflow envelope, obligations, checks, accepted failures,
and exclusions, but excludes prior findings and desired verdicts. It
may count under missing optional route/permission telemetry only when exact
routing and hard isolation were not predeclared required, output identity is
bound, candidate identity is unchanged, Root reproduces material findings, and
unverified guarantees are disclosed. Only a Root-admitted in-envelope repair
with remaining authorized repair budget returns to `working` and requires a new
candidate and Exact-final receipt.

Findings after the behavior-plan freeze cannot manufacture obligations or write
authority. Root must reproduce and classify every Exact-final finding before any
affected-surface expansion or write grant. An `in-envelope blocker` is a
reproduced failure of a frozen obligation, or a candidate-new safety regression
reachable through an already named supported workflow; it remains blocking. An
`envelope expansion` is a request for a new supported workflow, trust/design
guarantee, or architectural complexity not required to repair an in-envelope
blocker. It may be recorded as follow-up but cannot automatically become an
obligation or write grant. New durable state/schema, cross-context coordination,
compatibility/control-plane machinery, or equivalent complexity outside the
frozen design boundary is expansion. If prior repair machinery caused the
finding, compare removal, rollback, or simplification before adding control.

Unknown classification remains open and returns to the user before any write.
Unknown evidence blocks closure only when it concerns a frozen required
guarantee; out-of-envelope uncertainty is disclosed rather than silently
promoted. The default automatic repair budget is exactly one
Exact-final-triggered repair wave. Only a Root-admitted `in-envelope blocker`
may consume that automatic repair wave. While authorized budget remains, it may
trigger one coherent repair, then one refreeze and one new fresh empty-history
neutral Exact-final. After refreeze, any `in-envelope blocker` or `unknown`
classification remains open, truthful, and blocking, and Root must return to
the user before another product write, grant, or review rerun. An
`envelope expansion` remains a disclosed follow-up unless separately authorized
and never consumes the automatic repair wave. After the budget is exhausted, no
automatic product write, refreeze, or review rerun is permitted. Exact-final
identifies findings; Root owns admission and disposition. The user may explicitly
authorize a different bounded budget before work. The cap limits automatic
repair authority, never reviewer truth; no user-facing mode, level, or
continuation phrase is added.

No user-facing mode, level, or continuation phrase is part of this protocol.
Ask the user when continuation would change the Outcome, authority, trust
boundary, or an explicitly required guarantee; expand the frozen envelope; or
exceed or continue after exhaustion of the bounded automatic repair budget.

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
Unknown stays open. Separately record review admission and stop-line disposition:

| Finding identity | Reproduced evidence | Envelope class | Disposition | Repair budget / consumed | Stop-line decision |
| --- | --- | --- | --- | --- | --- |
| `<exact ID>` | `<source-backed evidence>` | `in-envelope blocker/envelope expansion/unknown` | `blocking/follow-up/return-to-user` | `<bounded count>` | `<write, review, or closure consequence>` |

Do not store a derived lifecycle action. A source-derived obligation may be
added only when the frozen envelope requires it; record provenance and
invalidation.

## Event state and checks

For each new falsifier, Root must reproduce and classify the finding against the
frozen envelope before it may expand the affected-surface inventory. Only an
in-envelope blocker joins the current coherent diagnosis and repair wave. Record
that diagnosis and wave, changed paths, real-path RED or characterization,
focused and cumulative offline commands, exits, failures, output digests, and
source tree. An unchanged failure cannot be retried. After terminal GREEN, only
a Root-admitted in-envelope material recurrence may use at most one
boundary-level alternative while an applicable explicit repair budget remains;
using the alternative consumes that budget. It must address the failure and
rerun affected checks. A post-refreeze Exact-final finding follows the
Exact-final stop-line above and cannot use this recurrence clause to bypass
return-to-user or no-more-write behavior. If the alternative fails unchanged or
the issue recurs again, return the decision to the user.

Corrections occur only on new evidence, check completion, source/config drift,
pre-effect revalidation, candidate freeze, review findings, or explicit user
authority. Administrative updates and elapsed time are not progress.

## Candidate and review

At `candidate_frozen`, bind the clean product snapshot, baseline/candidate
identities, manifest equality, complete affected-diff inventory, package/config
and toolchain, remaining dirt, the frozen supported-workflow envelope,
obligations, checks, effects, automatic repair budget/consumed count, finding
dispositions, stop-line decisions, and closed gates.

At `exact_final`, bind one fresh logically read-only review, its neutral brief
and command. The brief includes the frozen envelope, obligations, checks,
accepted failures, and exclusions, and excludes prior findings and desired
verdicts. Bind requested route and permissions, exposed values or `unverified`,
and hard technical isolation only when predeclared required. Always bind the
authenticated Output identity, frozen source/candidate identities, external
reads, checks, diff and obligation coverage, truncation limits, terminal result,
findings, Root reproduction, classification, and dispositions. Missing optional
route or permission telemetry alone does not leave review open. A required but
unproven guarantee, missing output identity or coverage, explicit mismatch,
candidate drift, unsupported evidence, or an unchanged rerun does. Any product
change returns to `working`.

## Recovery

Bind task/root/executor identities, owner token and resource claims, selected ref
or approved archive, source commit/tree/worktree, contract, active grant,
frozen supported-workflow envelope, obligations, finding classes/dispositions,
automatic repair budget/consumed count, stop-line decision, current phase/gates,
test receipts, agent receipts, candidate/review identities, effects, Goal state,
and exactly one checkpoint.
After resume, record fresh reads from the ExecPlan, Git, tests, claims, receipts,
agents, and Goal. Unknown or mismatched facts remain open.

## Closure

Closure records the final reachable source and product tree, checks, review,
evidence/effect receipts, exclusions, accepted baseline failures, owned status,
install/release/activation state, any explicitly waived or unrun gate, and final
Goal state. Retrospective text is not completion evidence and is never exposed
to exact-final.
