# HappyCodex

[简体中文](README.md)

*Open-source guidance for reliable high-risk engineering work in OpenAI Codex.*

HappyCodex freezes completion conditions in a repository ExecPlan. Root decides,
grants, reproduces, and verifies; one fixed Executor owns all controlled writes.
It composes Codex's native Plan, Git, tests, agents, and review. It is not a
controller, daemon, scheduler, authority system, or retry engine.

## When to use it

Use HappyCodex for public contracts, cross-system changes, migrations,
persistence, concurrency, destructive or production effects, exhaustive claims,
long research, and work likely to cross context compaction. Keep bounded local
low-risk edits on native Plan, tests, and diff unless their scope grows.

## Install and invoke

Marketplace support is required:

```bash
codex plugin marketplace add cch96/happycodex
codex plugin add happycodex@happycodex
```

Start a new Codex task after installation, then invoke:

```text
Use $happycodex:happycodex for this high-risk cross-system change.
```

Goal is created or changed only when explicitly requested. Goal continues
authorized work; it never grants an amendment, waiver, review, cost, authority,
or effect, and it never replaces the ExecPlan.

## Four phases

1. `working`: freeze the request, Outcome, supported workflows, boundaries,
   current authority and grant, obligations, checks, effects, and stop rules;
   implement one coherent authorized wave.
2. `candidate_frozen`: account for all owned changes, preserve accepted
   baseline failures, and bind a clean candidate identity and receipts.
3. `exact_final`: one fresh empty-history, logically read-only reviewer receives
   a neutral brief for the frozen candidate. Root reproduces and classifies its
   findings. Only one Root-admitted in-envelope blocker may consume the default
   single repair wave. After the replacement review, another blocker or unknown
   returns to the user before any write or rerun.
4. `closed`: Root closes only after obligations, checks, review, effects,
   ownership, receipts, and any explicitly requested Goal reconcile.

The requested role matrix is:

| Logical role | Model | Effort |
| --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` |
| Explorer | `gpt-5.6-terra` | `high` |
| Challenger | `gpt-5.6-sol` | `high` |
| Unique Executor | `gpt-5.6-sol` | `high` |
| Fresh Exact-final | `gpt-5.6-sol` | `max` |

A host-authenticated output identity is mandatory. Missing effective route or
permission telemetry is recorded `unverified` and only limits the guarantee
that depends on it; an exposed mismatch or predeclared required guarantee that
cannot be established stops. Prompt/profile read-only text is not technical
isolation. Explorers answer bounded independent questions and are advisory
until Root reproduces material facts from source.

## The 0.8 clean break

HappyCodex keeps one current snapshot rather than per-grant history or mutable
control state. External user authority, Root's exact active Executor grant,
candidate evidence, effect authority, and Goal remain distinct.

A bare continuation grants nothing unless an exact content-addressed proposal
is pending. Clear assent to the immediately preceding exact proposal authorizes
only that proposal. An old or mismatched snapshot shape is unknown and returns
to the user; there is no compatibility reader or migration.

The reconciliation latch is derived safety state persisted only across context
loss, not a fifth phase or durable record type. It activates only for a partial
or ambiguous external-effect terminal. Repeated local or review falsifiers,
unchanged failures, and exhausted repair budgets use the normal stop-line.
While active, only read-only reconciliation, verification, and return to the
user are allowed; grants, effects, candidate freeze, and Exact-final are
forbidden. It clears only after reconciliation binds the exact current effect
state and prestate, Root freezes an exact bounded recovery proposal and digest,
and the user explicitly authorizes that proposal. Neither state nor action must
change.

New durable state or schema, cross-context coordination, and compatibility or
control-plane machinery outside the frozen boundary are envelope expansion.
Candidate failures cannot be relabeled. If repair machinery caused a finding,
compare removal, rollback, and simplification before adding another control.

Secrets and raw events never enter controlled product bytes; only sanitized
summaries or digests live outside them. When commits are forbidden, keep the
index untouched and ask the user to select a durable location, preserving the
milestone in an approved reachable ref or content-addressed archive. Without a
selected archive or approved location, durability is not ready: `STOP_FOR_USER`.

Plugin installation does not bundle or activate custom agents. Optional local
profiles are convenience configuration and are not routing or isolation proof.
Publication, release, installation, and activation are not claimed before their
separate receipts exist.

[See GitHub Releases for published versions and verification status.](https://github.com/cch96/happycodex/releases)

## License

HappyCodex is available under the [MIT License](LICENSE).
