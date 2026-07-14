# Read-only investigation packet

Use this as a compact checklist, not a protocol. Include only context needed to
answer the question, and keep known facts neutral.

## Task packet

- **Decision:** The named decision or verification gate this can change.
- **Question:** One bounded question.
- **Snapshot:** The exact inspected snapshot, including relevant dirty state.
- **Scope:** Paths, symbols, tests, logs, or primary sources to inspect.
- **Context:** Known facts and exclusions; do not reveal a preferred answer.
- **Independence:** Prerequisites, coordination boundaries, and what must wait.
- **Boundary:** Read-only observational work; no edits, stateful side effects,
  implementation, commits, external models, or child delegation.
- **Deliverable:** A concise answer with evidence locations, unique evidence, and
  remaining uncertainty.
- **Stop:** Report missing access or ambiguity instead of guessing.

## Scout return

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
second opinion merely to produce agreement.
