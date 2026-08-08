# `<task>` ExecPlan

Keep this file static. Use native plans, Git, tests, and tools for live state.

## Verbatim request

> `<copy the user request and authorized amendments>`

## Outcome

`<one observable end state>`

## Envelope

- Workspace or project boundary: `<active workspace and explicit exclusions>`
- External resources and effects: `<systems, destinations, costs, and caps>`
- Preservation: `<behavior, data, identity, and state to keep>`
- Exclusions: `<explicit non-goals and forbidden effects>`

## Baseline and allowed breaks

- Source/worktree: `<ref, commit/tree when material, and initial dirt>`
- Baseline: `<command and exact accepted failures>`
- Allowed breaks: `<intentional incompatibilities or none>`

Never call an accepted failing baseline green. No new failure is allowed unless
the user adds it here.

## Design decision (optional)

Include this section only for a durable external contract with an independent
consumer. If design is itself a durable product artifact, link its path instead
of copying it.

- Decision: `<selected contract>`
- Alternatives: `<material alternatives and why rejected>`
- Visible consequences: `<consumer-facing behavior and recovery>`

## Checks and done

- Checks: `<focused real paths, cumulative suite, diff/state checks>`
- Done: `<observable completion conditions>`

Derive changed paths from Git. Account for staged, unstaged, and untracked
paths, external effects, skipped checks, and required unverified facts.

## Stops and recovery

Stop on source/index/scope/trust drift, a new failure, a required unknown, or a
partial or ambiguous external effect. Retry an effect only after proving no
effect. Never persist secrets or raw events in product bytes.

After compaction, reread this plan, inspect live Git and external state, and
rerun the checks needed to reconstruct current facts. Do not infer live state
from this file or a summary.
