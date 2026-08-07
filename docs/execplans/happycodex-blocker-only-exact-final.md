# HappyCodex blocker-only Exact-final — current index

## Current snapshot

| Field | Current value |
| --- | --- |
| Phase | `working` |
| External authority evidence | Exact amendment text `好的继续`, clear assent to Root's immediately preceding exact proposal for the one admitted Exact-final-triggered repair, bounded gates, Root refreeze, and one replacement neutral Exact-final |
| Active Executor grant | Fixed `happycodex_executor`, host output identity `/root/blocker_only_executor`; model `gpt-5.6-sol`, effort `high`; update only this plan, the operative Skill classifier, and the existing focused assertion; create one clean repair commit; run the exact offline gates once; then leave only this receipt unstaged |
| Prestate | `/home/caichenghang/projects/happycodex`; branch `codex/blocker-only-exact-final`; adverse receipt commit `ca937a51c4485e6caf6cd09dee0b9097633799c6`, tree `6b26ae36bb04f749f7ad7d717d6ad35d251f856b`; worktree/index clean; adverse review source `8841d78353f98f29e6dc57be2a66b55a118ce3b6`; frozen ProductArtifact `2931dceb4a243970fb99ee9c888ca15cee7de081a2a25e94fe6eccd2b614602a` |
| Repair budget | `1 / 1`; the single admitted repair wave is consumed by this grant |
| Latest falsifier | `EF-ADMISSIBILITY-CLASSIFIER`: candidate-new material correctness-only regressions are admitted by the frozen obligation but omitted by the operative Root classifier |
| Reconciliation latch | inactive; effects are `none` |
| Receipts | adverse Exact-final handle `/root/blocker_only_exact_final`, brief digest `7bdd558b9769e098d1f85de7bbca8e360cde93f1471fb5be52f9201642ce55cd`, and result digest `529433323164fc4f698525ad90a2dd35093abca63caeee19a65d2dd742afd1fb` retained; product mutation invalidates that review; repair commit/check receipts pending |
| Obligations and gates | exact `EF-ADMISSIBILITY-CLASSIFIER` correction open; focused/cumulative/validator/identity gates open; Root refreeze and one replacement fresh neutral Exact-final pending |
| Goal | absent |

Effective sandbox and approval telemetry are `unverified`; no hard-isolation
claim depends on them. Platform acceptance and this host-authenticated output
identity are present. This file is the one current snapshot for this wave, not
a grant history or a new durable record type.

## Frozen envelope

### Outcome

Refine the existing v0.8.0 product guidance without redesign: make Exact-final
a blocker-only closure check rather than an optimization pass. An admissible
blocker is only:

1. a reproduced failure of a frozen obligation, including a candidate that
   simply failed to fix the original obligation; or
2. a candidate-new material safety or correctness regression reachable through
   a named workflow.

Every blocker must identify a concrete, actionable, evidence-backed or
reproducible scenario. Style or naming preferences, general cleanup or
refactoring, speculative hardening, alternative designs or new guarantees,
unfrozen test suggestions, and pre-existing issues unrelated to frozen
obligations do not block closure.

Bind one admitted result to one exact frozen review identity: candidate,
neutral brief, and relevant bound configuration or receipt identity. An
unchanged identity cannot be rerun by rewording the brief or swapping reviewers.

### Preservation

- Preserve the immutable published `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Preserve v0.8.0's four phases, one current snapshot, one fixed Executor,
  Root-owned decisions, neutral brief with no prior findings or desired
  verdict, one repair wave, replacement Exact-final after product mutation,
  and post-refreeze return-to-user stop.
- Preserve open-ended architecture and simplification challenge before freeze
  and deterministic checks before Exact-final.
- Preserve evaluator separation, the four durable record types, stateless
  verification, provider boundaries, one-shot provider semantics, fixed
  holdouts, proportional token bound, and adverse Exact-final persistence.

### Allowed paths

Only these paths may change:

1. `docs/execplans/happycodex-blocker-only-exact-final.md`, for current intent
   and terminal receipts;
2. `skills/happycodex/SKILL.md`, only the operative Root classifier's second
   admission form; and
3. `tests/test_attestation_contract.py`, only one assertion inside the existing
   blocker-only contract method.

All other paths, including `evaluation/**`, `.codex-plugin/**`, agent
configuration, marketplace/cache/install state, README/reference surfaces, and
the immutable v0.6.5 Skill tree are excluded.

### Design boundary

This wave changes guidance and focused static contract assertions only. It does
not add provenance or control flow for original, repair-caused, or late
findings. It adds no phase, role, state field, finding class, durable record,
schema, hook, controller, ledger, compatibility reader, migration, evaluator
coupling, or new product guarantee.

### Obligations

| ID | Observable contract | Falsifier | State |
| --- | --- | --- | --- |
| `EF-BLOCKERS` | Exact-final is explicitly a blocker-only closure check, not an optimization pass | retained invitation to optimize or broaden the frozen candidate | verified by focused contract and source diff |
| `EF-ADMISSIBILITY` | only the two admitted blocker forms qualify, with a concrete actionable evidence-backed or reproducible scenario | a supported correctness-only candidate regression cannot be admitted by the operative classifier | repair authorized: exact classifier/test alignment pending |
| `EF-SUPPRESS` | the named non-blocking categories are explicitly suppressed | any named category is invited as closure-blocking work | verified by focused contract and source diff |
| `EF-IDENTITY` | one result binds candidate + neutral brief + relevant bound configuration/receipt identity; unchanged identity cannot rerun through wording/reviewer substitution | equivalent review can be retried by rewording or reviewer swap | verified by focused contract and source diff |
| `EF-ONE-REPAIR` | one admitted blocker may consume one repair wave; mutation requires replacement Exact-final; after refreeze blocker/unknown returns to user | a second write or friendlier rerun is permitted | verified; budget consumed `1 / 1` |
| `EF-PRESERVE` | all preservation and exclusion constraints above remain intact | any prohibited semantic, path, evaluator, configuration, or effect drift | verified by exact path and protected-surface receipts |

## Bound candidate and checks

- Product source: `a3a3d3dd0ea7bf4a741f77a73bc53e9b2b811a08`;
  source tree `a7f09e76d599bad1845b5c27e43414bb4ed34b4d`.
- ProductArtifact record:
  `2931dceb4a243970fb99ee9c888ca15cee7de081a2a25e94fe6eccd2b614602a`;
  package tree `f1e2481b0964e2906c9846d300db05b1ca3c5f45`;
  artifact SHA-256
  `bfe77bdf1a9419431d154376075421d9e22e89ae0e03b1c7355f5e58a223e31e`;
  semantic SHA-256
  `1c623b3d38a340d81a5a635f2774c2b06c10655c968a981d288a57e510b99413`.
- Focused contract: RED characterized, then 19/19 passed.
- Clean cumulative gate: 164 tests, exactly the two accepted source-baseline
  failures, zero errors/skips. Skill and plugin validators, parent diff, exact
  seven-path projection, empty protected projection, and immutable v0.6.5
  Skill tree all passed. Root independently reproduced these receipts.
- The earlier dirty-worktree run is retained only as resolved precondition
  evidence; its exact-source identity errors are not candidate evidence.

## Exact-final receipt and Root disposition

- Host-authenticated handle: `/root/blocker_only_exact_final`.
- Invocation: one fresh custom `happycodex_exact_final`, `fork_turns=none`,
  configured `gpt-5.6-sol` at `max`, read-only, approval `never`; role config
  SHA-256
  `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`.
- Neutral brief SHA-256:
  `7bdd558b9769e098d1f85de7bbca8e360cde93f1471fb5be52f9201642ce55cd`.
- Terminal result: `NOT_YET`; coverage complete; non-blocking uncertainty
  `none`; sanitized result SHA-256
  `529433323164fc4f698525ad90a2dd35093abca63caeee19a65d2dd742afd1fb`.
- Adverse result identity is frozen candidate + neutral brief + bound role
  configuration/receipt. It is persisted and cannot be replaced for unchanged
  identity by rewording the brief or swapping reviewers.

`EF-ADMISSIBILITY-CLASSIFIER` is the one blocker. Candidate Skill lines 84-87
admit a candidate-new material safety or correctness regression, while the
operative Root classifier at lines 174-175 admits only candidate-new safety
regression. The concrete named-workflow scenario is a candidate-new material
correctness-only supported-export field swap that the classifier cannot admit.
The smallest correction is to use the exact broader class in the operative
classifier.

Root independently read current and baseline source and reproduced the
mismatch. Root classifies it as a reproduced failure of frozen obligation
`EF-ADMISSIBILITY`, hence an in-envelope blocker under admissibility form (1),
not style, envelope expansion, unknown, or an unrelated baseline issue. Phase
is `exact_final`; closure is rejected.

## Stop and repair boundary

Exact user authority consumes the single repair budget, now `1 / 1`. The only
repair is to broaden the operative classifier to the already frozen exact
class and add one isolating assertion inside the existing test method. Product
mutation invalidates the adverse Exact-final and returns phase to `working`.

After the three-path repair commit, run exactly once in order: the 19-test
focused module; the 164-test cumulative suite with only the two accepted
failures and zero errors/skips; the Skill validator; the plugin validator; and
the parent diff, exact path/protected projections, status/index, HEAD/tree, and
ProductArtifact checks. Any unexpected count, failure, error, skip, validator,
identity, path, or protected-tree drift is terminal without retry or another
repair.

Root refreeze is pending. Only after Root refreezes may exactly one replacement
fresh neutral Exact-final run. After that review, any blocker or unknown returns
to the user; no third review or automatic write is permitted.

Authorized effects are one local three-path repair commit and one later
unstaged plan receipt. No amend, extra commit/ref/archive, model/reviewer call,
push, network, install, activation, publication, release, cleanup,
evaluator/config edit, or other path/effect is authorized.
