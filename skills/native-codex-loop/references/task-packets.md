# Task packets for read-only scouts

Use this as a semantic checklist, not a machine protocol. Adapt the wording and length
to the decision while keeping every relevant field. Give neutral known facts; do not
leak the Root's preferred answer.

## Scout task packet

- **Decision:** The named parent decision or verification gate this investigation may
  change.
- **Question:** One bounded question the scout must answer.
- **Lens:** The distinct perspective assigned to this scout, such as contract tracing,
  downstream consumers, tests and user surface, or failure/risk analysis.
- **Source of truth:** Exact repository revision, paths, symbols, tests, logs, or primary
  documentation to inspect.
- **Known facts:** Context already verified by the Root.
- **Exclusions:** Adjacent questions and paths that are out of scope.
- **Write boundary:** Read-only. No edits, commits, worktrees, external models, or child
  agents.
- **Deliverable:** A concise answer with evidence locations and remaining uncertainty.
- **Unique evidence:** What this scout must contribute that the other packets do not.
- **Verification:** How the Root can reproduce the answer.
- **Stop condition:** Missing access, ambiguity, or evidence limits that must be reported
  instead of guessed through.

## Scout return

- **Inspected revision:** The exact revision or snapshot actually examined.
- **Answer:** Direct answer to the bounded question.
- **Evidence:** File and symbol, command and observed output, or primary-source section.
- **Unique evidence:** New fact not already present in the packet.
- **Uncertainty:** What remains unknown and why.
- **Suggested verification:** Smallest Root-owned reproduction step.

## Root uptake

Record this briefly in the native plan after reproducing the evidence:

- **Decision:** Decision ID or gate affected.
- **Reproduction:** Root command, source trace, test, or primary source used.
- **Freshness:** Confirmation that cited evidence still holds on the current revision.
- **Disposition:** `use`, `reject`, or `defer`, with reason.
- **Unique evidence:** Material new evidence, or `none`.
- **Plan or gate delta:** What changes; write `none` when the plan stays correct.
- **Follow-up:** Root action, a genuinely new bounded question, or stop.

If a return has no reproducible or unique evidence, treat it as a no-op. Do not dispatch
another scout merely to seek a different opinion.
