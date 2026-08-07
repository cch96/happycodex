# HappyCodex blocker-only Exact-final — current index

## Current snapshot

| Field | Current value |
| --- | --- |
| Phase | `closed` |
| External authority evidence | Exact amendment text `好的继续`, clear assent to Root's immediately preceding exact proposal for the one admitted Exact-final-triggered repair, bounded gates, Root refreeze, and one replacement neutral Exact-final |
| Active Executor grant | Fixed `happycodex_executor`, host output identity `/root/blocker_only_executor`; model `gpt-5.6-sol`, effort `high`; persist the single replacement Exact-final GO and Root closure decision, then create exactly one local plan-only closure receipt commit |
| Prestate | `/home/caichenghang/projects/happycodex`; branch `codex/blocker-only-exact-final`; refreeze receipt commit `f2846729d15faa5a1dff22c062a34dc802045f44`, tree `6ab7aac9a1a540a5fcede08208d9fb97699a25f1`; repaired product source `10c7691103077771193be5dccacb10fdf7f3a24c`; ProductArtifact record `0823c7e0091c2f53100a2cbb854d3b0706083baed279a0d55a05e07a4090e126`; worktree/index clean |
| Repair budget | `1 / 1`; the single admitted repair wave is consumed by this grant |
| Latest falsifier | `none`; the first adverse review is retained but invalidated, and the replacement Exact-final reports no blocker or required unknown |
| Reconciliation latch | inactive; effects are `none` |
| Receipts | repaired ProductArtifact/check identities retained below; replacement handle `/root/blocker_only_replacement_exact_final`, brief digest `c7b9412d17b7af6333f9ed87db542e5716dc4a9f966000457c1a0c4754921992`, neutral projection digest `2c17256c7e1fb04d5af4dcbbdd6d89e391eed601820d1bb2c03c6f70d6f176d7`, and sanitized GO digest `bd81d68eb701bd04e4a1bd699b7e9a09f8e596a29b7653e225b753b57cd527d5` bound |
| Obligations and gates | every obligation verified; replacement Exact-final GO with complete coverage, no blocker, and no required unknown; effects reconciled; Root closure decision complete |
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

Only `docs/execplans/happycodex-blocker-only-exact-final.md` may change for this
closure receipt. Every product, test, evaluator, configuration, plugin,
marketplace/cache/install, README/reference, and protected v0.6.5 path is
excluded.

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
| `EF-ONE-REPAIR` | one admitted blocker may consume one repair wave; mutation requires replacement Exact-final; after refreeze blocker/unknown returns to user | a second write or friendlier rerun is permitted | verified; budget exhausted `1 / 1` |
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

The first review used handle `/root/blocker_only_exact_final`, role config
SHA-256 `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`,
brief SHA-256
`7bdd558b9769e098d1f85de7bbca8e360cde93f1471fb5be52f9201642ce55cd`,
and sanitized `NOT_YET` result SHA-256
`529433323164fc4f698525ad90a2dd35093abca63caeee19a65d2dd742afd1fb`.
It was bound to source `8841d78353f98f29e6dc57be2a66b55a118ce3b6`
and ProductArtifact
`2931dceb4a243970fb99ee9c888ca15cee7de081a2a25e94fe6eccd2b614602a`.
Root admitted its sole `EF-ADMISSIBILITY-CLASSIFIER` blocker. Repair commit
`10c7691103077771193be5dccacb10fdf7f3a24c` invalidated that review while this
sanitized adverse receipt remains retained.

## Replacement Exact-final and closure

- Host-authenticated handle: `/root/blocker_only_replacement_exact_final`.
- Invocation: one fresh custom `happycodex_exact_final`, `fork_turns=none`,
  configured `gpt-5.6-sol` at `max`, read-only, approval `never`; role config
  SHA-256
  `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`.
- Neutral brief SHA-256:
  `c7b9412d17b7af6333f9ed87db542e5716dc4a9f966000457c1a0c4754921992`.
- Neutral review projection SHA-256:
  `2c17256c7e1fb04d5af4dcbbdd6d89e391eed601820d1bb2c03c6f70d6f176d7`;
  prior administrative receipts were excluded from reviewer input.
- Terminal result: `GO`; coverage complete; blocker findings `none`;
  non-blocking uncertainty `none`; sanitized result SHA-256
  `bd81d68eb701bd04e4a1bd699b7e9a09f8e596a29b7653e225b753b57cd527d5`.

The admitted replacement result is bound to the repaired ProductArtifact,
neutral brief, neutral projection, and role configuration/receipt identity.
Root independently rechecked the branch/source/product/protected identities,
clean status/index, aligned blocker contract and operative classifier, focused
assertion, one-repair/post-refreeze stop line, and all frozen check receipts.
Root also reproduced the exact neutral six-path projection—`AGENTS.md`,
`README.en.md`, `README.md`, `skills/happycodex/SKILL.md`,
`skills/happycodex/references/execplan.md`, and
`tests/test_attestation_contract.py`—with aggregate digest above and an empty
evaluator/configuration projection.

Every obligation is verified. The first adverse review remains retained but
invalidated; repair budget is exhausted `1 / 1`; replacement review has no
blocker or required unknown; effects are `none` and reconcile; Goal is absent.
Root decides phase `closed`.

## Terminal boundary

No more repair, write, refreeze, or review is authorized for this task without
new user authority and a new task envelope. This Executor may only commit this
plan closure receipt and perform read-only verification. No amend, additional
commit/ref/archive, product/test/evaluator/config edit, reviewer/model call,
push, network, install, activation, publication, release, cleanup, or external
effect is authorized.
