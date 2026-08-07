# HappyCodex blocker-only Exact-final — current index

## Current snapshot

| Field | Current value |
| --- | --- |
| Phase | `candidate_frozen` |
| External authority evidence | Exact amendment text `好的继续`, clear assent to Root's immediately preceding exact proposal for the one admitted Exact-final-triggered repair, bounded gates, Root refreeze, and one replacement neutral Exact-final |
| Active Executor grant | Fixed `happycodex_executor`, host output identity `/root/blocker_only_executor`; model `gpt-5.6-sol`, effort `high`; persist Root's reproduced post-repair freeze decision and create exactly one local plan-only refreeze receipt commit |
| Prestate | `/home/caichenghang/projects/happycodex`; branch `codex/blocker-only-exact-final`; frozen repair source `10c7691103077771193be5dccacb10fdf7f3a24c`, tree `568b85eca0b4d19d64129408b033d91cf353574a`; ProductArtifact record `0823c7e0091c2f53100a2cbb854d3b0706083baed279a0d55a05e07a4090e126`; index empty; this plan is the sole dirt before its refreeze receipt commit |
| Repair budget | `1 / 1`; the single admitted repair wave is consumed by this grant |
| Latest falsifier | `none` locally; `EF-ADMISSIBILITY-CLASSIFIER` is corrected and focused-verified; the adverse review is invalidated by product mutation |
| Reconciliation latch | inactive; effects are `none` |
| Receipts | repair commit/tree and ProductArtifact bound below; focused 19/19 passed; 164-test cumulative gate matched the exact two-failure baseline with zero errors/skips; both validators, diff, path, status, and protected checks passed |
| Obligations and gates | `EF-ADMISSIBILITY-CLASSIFIER` resolved; all repair gates Root-reproduced; no required unknown; Root refreeze complete; exactly one replacement fresh neutral blocker-only Exact-final pending |
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
| `EF-ADMISSIBILITY` | only the two admitted blocker forms qualify, with a concrete actionable evidence-backed or reproducible scenario | a supported correctness-only candidate regression cannot be admitted by the operative classifier | verified after repair and Root reproduction |
| `EF-SUPPRESS` | the named non-blocking categories are explicitly suppressed | any named category is invited as closure-blocking work | verified by focused contract and source diff |
| `EF-IDENTITY` | one result binds candidate + neutral brief + relevant bound configuration/receipt identity; unchanged identity cannot rerun through wording/reviewer substitution | equivalent review can be retried by rewording or reviewer swap | verified by focused contract and source diff |
| `EF-ONE-REPAIR` | one admitted blocker may consume one repair wave; mutation requires replacement Exact-final; after refreeze blocker/unknown returns to user | a second write or friendlier rerun is permitted | verified; budget consumed `1 / 1` |
| `EF-PRESERVE` | all preservation and exclusion constraints above remain intact | any prohibited semantic, path, evaluator, configuration, or effect drift | verified by exact path and protected-surface receipts |

## Bound candidate and checks

- Repair commit: `10c7691103077771193be5dccacb10fdf7f3a24c`;
  parent `ca937a51c4485e6caf6cd09dee0b9097633799c6`; source tree
  `568b85eca0b4d19d64129408b033d91cf353574a`.
- ProductArtifact record:
  `0823c7e0091c2f53100a2cbb854d3b0706083baed279a0d55a05e07a4090e126`;
  package tree `a77fb8e27802adf3c167e4bdf4d9d0d2b06d683f`;
  artifact SHA-256
  `a8afe7c2e637b8e441538887e9b5ab82c1db694d9f668cc19d68d36fed31bfd6`;
  semantic SHA-256
  `ae4ae68ca19a37bf299a7f2ad2b6624ef704731989279832e43635d1e19720d8`.
- Parent projection is exactly this plan, `skills/happycodex/SKILL.md`, and
  `tests/test_attestation_contract.py`; forbidden projection is empty; protected
  v0.6.5 Skill tree is
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Focused command ran once: 19/19 passed, exit `0`, 0.116 seconds.
- Cumulative command ran once: 164 tests in 74.943 seconds, exactly
  `test_exact_final_source_rejects_self_selected_projection_and_fake_diff` at
  `mutation='old-source'` and
  `test_old_source_components_cannot_back_a_new_dirty_evalspec` failed, with
  zero errors/skips and no other failure.
- Skill validator exit `0`, `Skill is valid!`; plugin validator exit `0`,
  `Plugin validation passed: /home/caichenghang/projects/happycodex`;
  `git diff --check ca937a51c4485e6caf6cd09dee0b9097633799c6..HEAD`
  exit `0`. Committed worktree and index were clean after all gates. Root
  reproduced the repair, assertion isolation, identities, checks, exact
  three-path projection, empty forbidden projection, and protected tree, then
  decided `candidate_frozen` with no required unknown.

## Invalidated first Exact-final receipt

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
- Its bound source is `8841d78353f98f29e6dc57be2a66b55a118ce3b6`
  and ProductArtifact is
  `2931dceb4a243970fb99ee9c888ca15cee7de081a2a25e94fe6eccd2b614602a`.
  Product mutation at repair commit `10c7691103077771193be5dccacb10fdf7f3a24c`
  invalidates this review while preserving its adverse receipt.

`EF-ADMISSIBILITY-CLASSIFIER` is the one blocker. Candidate Skill lines 84-87
admit a candidate-new material safety or correctness regression, while the
operative Root classifier at lines 174-175 admits only candidate-new safety
regression. The concrete named-workflow scenario is a candidate-new material
correctness-only supported-export field swap that the classifier cannot admit.
The smallest correction is to use the exact broader class in the operative
classifier.

Root independently read current and baseline source and reproduced the
mismatch. Root classified it as a reproduced failure of frozen obligation
`EF-ADMISSIBILITY`, hence an in-envelope blocker under admissibility form (1),
not style, envelope expansion, unknown, or an unrelated baseline issue. That
review rejected closure and is now invalidated by the repaired product bytes.

## Stop and repair boundary

The exact repair wave is complete and the single budget is consumed `1 / 1`.
Root refreeze is complete and phase is `candidate_frozen`. Exactly one
replacement fresh neutral blocker-only Exact-final is pending, bound to the
repaired ProductArtifact and a new neutral brief/configuration receipt. After
that review, any blocker or unknown returns to the user; no third review or
automatic write is permitted.

No further Executor action is granted. No amend, additional product repair,
extra commit/ref/archive, model/reviewer call, push, network, install,
activation, publication, release, cleanup, evaluator/config edit, or other
path/effect is authorized.
