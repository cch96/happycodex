# HappyCodex 0.8.1 source release candidate

## Durable intent

- Grant: `HC-0.8.1-CANDIDATE-001`, from the user's adjacent `好的` approving
  the exact 0.8.1 proposal. This grant prepares and commits a local source
  candidate only; it does not authorize publication, activation, installation,
  provider/reviewer invocation, or any network effect.
- Recovery grant: `HC-0.8.1-CANDIDATE-RECOVERY-002` authorizes one bounded
  local correction because the initial discovery invocation exercised no
  cumulative gate. It authorizes exactly one admissible cumulative invocation
  and the already-frozen remaining local gates, candidate freeze, staging, and
  source commit; it authorizes no provider or external effect.
- Freeze grant: `HC-0.8.1-CANDIDATE-FREEZE-003` binds Root's read-only secret
  scan over the exact four current candidate paths and authorizes only this
  plan freeze, exact four-path staging, and one local source commit.
- Phase: `candidate_frozen`.
- Source branch: `codex/blocker-only-exact-final` at
  `b6e4dfa8f03fbcab26f6aca45253ea997366a444`, tree
  `206bdbd559efb41530feacdc02d072c0bfc32be9`.
- Baseline refs: local `main` and local `origin/main` both
  `7221520c982699a6a29fb979206a1c42bf27e96d`; local `v0.8.1` is absent.
- Exact mutable paths are this plan, `AGENTS.md`,
  `.codex-plugin/plugin.json`, and `tests/test_attestation_contract.py`.
  Every other repository path is excluded.
- The candidate is a source release of the already-reviewed blocker-only
  Exact-final product. It preserves the exact published
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`, the evaluator, external role
  configuration, current active install/cache/rollback state, and all
  unrelated paths. It is not a redesign, refactor, cleanup, or evaluator
  certification.

## Exact candidate effects and stop lines

1. Change the repository authority pointer in `AGENTS.md` to this local 0.8.1
   candidate plan, set the plugin manifest and contract expectation to
   `0.8.1`, and record truthful validation evidence here.
2. The contract expectation changes first and receives one focused RED run;
   the manifest and pointer change only afterward.
3. Run the implemented focused contract once. The recovery grant retains its
   existing receipt and does not rerun it. Run the full offline standard-
   library suite with exactly `timeout --signal=KILL 180s env
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`, exactly
   once under that grant, in one clean disposable local clone that projects and
   commits exactly the four candidate paths.
   The synthetic commit is validation identity only, never a source or release
   ref. Remove the exact temporary root only after its receipt is bound.
4. The full-suite admissible result is exactly 164 tests, exit 1, with zero
   errors, skips, unexpected successes, new failures, or missing failures and
   exactly these two known failures:
   `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
   with `mutation='old-source'`, and
   `test_old_source_components_cannot_back_a_new_dirty_evalspec`. It must never
   be described as green.
5. Run each named Skill and plugin validator once, then JSON/AST parsing,
   `git diff --check`, protected-tree, exact-path, and secret checks. Any
   unexpected identity, output, path, timeout, partial/ambiguous effect, or
   need to retry stops and returns to Root without widening scope.
6. Only when all gates match, change this phase to `candidate_frozen`, stage
   exactly the four candidate paths, and make one unsigned, non-amended commit
   named `chore(release): prepare HappyCodex 0.8.1`. Root alone decides
   completion, review, publication, or activation.

No external effect is authorized by this plan. A later, separately granted
publication may use exactly one non-force push of the reviewed candidate to
`main`; it must not use a second closeout push. The external release-note file
and the mode-0600 external `ReleaseReceipt` are future effects, and the latter
must carry terminal post-publication receipts. Until those effects are
separately authorized and verified, this plan must not claim them complete.

## Frozen external release-note body

The body below is frozen. Its completed validation values are bound to the
actual candidate evidence. Only `[RELEASE_EXACT_FINAL_RESULT]` remains a
placeholder, and it may be resolved only in a future external release-note
file from real evidence under separate exact authority.

````markdown
# HappyCodex v0.8.1

HappyCodex v0.8.1 is the reviewed source release of the blocker-only
Exact-final product. It is not a maintainer-evaluator certification.

## Highlights

- Exact-final closes only for frozen-obligation failures or candidate-new,
  material safety/correctness blockers in the named workflow.
- Style preferences, speculative concerns, new guarantees, unfrozen tests,
  and pre-existing issues are suppressed rather than promoted to blockers.
- The reviewed artifact and review identity are immutable; unchanged bytes do
  not receive a friendlier rerun.
- This release closes the blocker-only contract. It does not claim general
  optimization.

## Validation

- Focused repository contract: expected RED ran 19 tests with only the 0.8.0
  versus 0.8.1 manifest mismatch; implemented candidate passed 19/19.
- Full offline suite: 164 tests, exit 1, exactly two accepted baseline
  failures, zero errors, skips, unexpected successes, new failures, or missing
  failures; admissible but not green.
- Skill validator: pass.
- Plugin validator: pass.
- Repository integrity checks: JSON/AST parse, diff check, protected v0.6.5
  tree, exact four-path inventory with empty index, and secret scan passed.
- Release-specific Exact-final: [RELEASE_EXACT_FINAL_RESULT]

## Install

```sh
codex plugin add happycodex@happycodex
```
````

## Candidate receipts

- Focused contract receipts are the intended 19-test RED with only the
  `0.8.0 != 0.8.1` manifest mismatch, followed by the implemented 19/19 pass.
- The first zero-test discovery and the later parse-time scan command exercised
  no gate and remain inadmissible, no-effect observations.
- The sole admissible cumulative run used clean synthetic commit
  `f464ab4e7ccebffd0c9cefbe9c9f58f4ade06efb`, tree
  `429461cc65c7e7bd8035876a0684a39ef661d2fc`, parent
  `b6e4dfa8f03fbcab26f6aca45253ea997366a444`, whose byte-equal inventory was
  exactly the four candidate paths. It ran 164 tests in 75.115 seconds and
  exited 1 with exactly the two accepted baseline failures, zero errors, zero
  skips, zero unexpected successes, and no new or missing failures. This is
  admissible and is not green.
- Skill and plugin validators, JSON/AST parsing, `git diff --check`, protected
  tree, and exact four-path/empty-index gates each passed once. Under
  `HC-0.8.1-CANDIDATE-FREEZE-003`, Root's independent read-only `rg -l -I`
  scan for GitHub, OpenAI, AWS, and private-key token forms returned the exact
  expected no-match exit 1 with no file output; its wrapper exited 0.
- No publication, review, provider, network, tag, push, install, activation,
  external note/receipt, or personal source/marketplace/config/cache effect
  occurred. Release-specific Exact-final and every external effect remain
  pending separate exact authority.
