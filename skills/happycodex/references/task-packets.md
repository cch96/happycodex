# Read-only investigation packet

Use this as a compact checklist, not a protocol. Include only context needed to
answer the question, and keep known facts neutral.

## Task packet

- **Gate ID:** The identifier already recorded in the ExecPlan.
- **Decision:** The named decision or verification gate this can change.
- **Question:** One bounded question.
- **Snapshot:** The exact inspected snapshot, including relevant dirty state.
- **Persisted status:** Record `pending` and the required evidence before dispatch.
- **Native identity:** After dispatch, record the native agent or task ID; prose that
  merely claims a challenger ran is not evidence of dispatch.
- **Scope:** Paths, symbols, tests, logs, or primary sources to inspect.
- **Context:** Known facts and exclusions; do not reveal a preferred answer.
- **Independence:** Prerequisites and what must wait. A boundary challenger works
  without Root's inventory.
- **Boundary:** Read-only observational work; no edits, stateful side effects,
  implementation, commits, external models, or child delegation.
- **Deliverable:** A concise answer with evidence locations, unique evidence, and
  remaining uncertainty.
- **Stop:** Report missing access or ambiguity instead of guessing.

## Scout return

- **Native completion:** The same native agent or task ID and its terminal status.
- **Inspected snapshot:** Revision and relevant worktree state actually examined.
- **Answer:** Direct answer to the bounded question.
- **Evidence:** File and symbol, command and output, or primary-source section.
- **Unique evidence:** New fact not already supplied in the packet.
- **Uncertainty:** What remains unknown and why.
- **Root reproduction:** The smallest independent reproduction step.

## Root uptake

- **Decision:** Decision or gate affected.
- **Reproduction:** Root-owned source trace, command, test, or primary source.
- **Freshness:** Whether the evidence still holds on the current candidate.
- **Disposition:** `use`, `reject`, or `defer`, with reason.
- **Plan or gate delta:** The resulting change, or `none`.
- **Follow-up:** Root action, a genuinely new bounded question, or stop.

Treat a return without reproducible unique evidence as a no-op. Do not seek a
second opinion merely to produce agreement. If a child is lost, inaccessible, or
interrupted, or if Root cannot verify both dispatch and return, its persisted gate
remains pending; never infer success from absence or from Root's own second search.
