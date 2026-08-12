# HappyCodex

[简体中文](README.md)

*Open-source guidance for reliable high-risk engineering work in OpenAI Codex.*

HappyCodex records the outcome, change boundary, consumer identity, and done
conditions of risky work in one static ExecPlan, then relies on Codex's native
Plan, agents, Git, tests, and diffs. It is not a controller, authority system,
ledger, scheduler, or retry engine.

## When to use it

Use HappyCodex for cross-system changes, public contracts, migrations,
persistence, concurrency, destructive or production effects, exhaustive
claims, and long work likely to cross context compaction. Keep bounded,
reversible local work on the native Plan; create an ExecPlan when risk grows.

## Install and invoke

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation, then invoke:

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

## Mental model

- The ExecPlan stores only the static request, Outcome, change boundary,
  consumer, effects, checks, and stops. Re-derive live state from Git, tests,
  and tools.
- Route stable boundaries. Before a recommendation, assessment, or design verdict that depends on unverified current facts spanning artifacts or requiring search, the Primary sends bounded observable questions
  to one native read-only scout before deciding. It returns cited facts, searched scope, and unknowns, never recommendations; judgment stays with the Primary.
  Skip it for one or two bounded lookups or facts verified in-session; delegate other evidence bodies only when search, summary, comparison, or filtering is required. Once ownership and
  Done evidence are stable, send substantial implementation to one native
  worker before editing. Keep small coherent corrections direct. Limit an
  external model or tool challenge/review to its assigned question, and have
  the Primary invoke and observe it directly; never create a native agent to
  call, relay, or wrap the external invocation. State any native-agent fallback
  before direct work. Context offload needs neither parallel work nor low
  remaining context; add agents only for independent bodies when concurrency
  helps, with one writer per overlap.
- After interruption or compaction, confirm the old writer cannot resume, read
  the whole plan, and rebuild Git, candidate, and effect facts.
- Freeze with the consumer's native immutable identity, such as a Git tree,
  package, image, or revision. A mutable worktree digest is not a candidate.
- Create a native Goal only on explicit user request. Continue autonomously only
  while its Goal, Outcome, boundary, candidate surface, effect target/identity/
  cap, and pending-decision state are unchanged. Goals, replies, and `GO` add no
  authority; unconfirmed Goal identity stops mutation.
- Before deleting a branch, worktree, or other recovery surface, prove the
  candidate, cutover, effect, and rollback evidence remains durably reachable.
- Ordinary reversible work needs no review. Iterative convergence review is
  advisory and uncapped. Run one separate fresh native read-only, blocker-only
  terminal review for a public, external, irreversible, or high-risk candidate;
  it must be no-history, return strict `GO` or `NOT_YET`, and echo an immutable
  consumer-native identity; any byte change invalidates it. A plan `GO`
  validates only the plan, and a composite candidate uses one envelope binding
  all component identities. Follow-up or messaging after terminal review makes
  later output convergence-only; one authorized repair plus one fresh
  replacement review remains the automatic limit before returning to the user.
- After one external-effect attempt, use real read-only observation to classify
  it as `landed`, `not_landed`, or `unknown`. Stop on partial or ambiguity.
- Close explicitly as achieved, not achieved, or unknown, accounting for dirt,
  skipped checks, and unverified facts.

HappyCodex is portable and model-agnostic; it requires no custom agent or pinned
model/effort. Default hooks are optional, trust-dependent, bypassable guardrails, not enforcement.

[See GitHub Releases for published versions and verification status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
