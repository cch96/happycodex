# HappyCodex 0.7.2 capability-proportional admission

## Contract

- Intent and fixed write grant: `HC-0.7.2-WRITE-001`.
- Phase: `closed`. This is a closed local uncommitted candidate, not an
  installation, activation, release, or completion decision.
- Verbatim user request and amendments: `是的，这个问题是不是要改一下，对用户来说太麻烦`;
  `自动降级是什么意思，现在有什么级别吗，需要输入什么吗`; `现在严格验证什么东西`;
  `这些需要严格校验吗`; `好的改一下`.
- Normalized Outcome: replace 0.7.1's blanket rule that missing runtime
  effective metadata makes all child output inadmissible and stops the task
  with deterministic capability-proportional admission. Normal users choose
  no mode and enter no continuation phrase. Missing observability reduces only
  the guarantee or use that depends on it; explicit mismatch, malformed or
  ambiguous claimed evidence, unauthenticated output identity, authority or
  scope drift, candidate drift, and ambiguous or partial effects remain hard
  stops.
- Root owns the behavior plan, grant, evidence reproduction, candidate freeze,
  review, and completion decision. Fixed Executor
  `/root/capability_proportional_executor` is the sole controlled-domain writer.
- No Goal was requested or created.

## Source and preservation

- Repository/worktree: `/home/caichenghang/projects/happycodex`.
- Branch: clean `main`, tracking `origin/main`.
- Frozen source commit: `c9476242c259cfe84ba2c9b7866f62d5694c3ee6`.
- Frozen source tree: `1d91d18eac039cca2be64707584cb34424507337`.
- Initial index, unstaged set, and untracked set: empty.
- Published `v0.6.5:skills/happycodex` tree to preserve exactly:
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Only these repository paths are writable:
  - `docs/execplans/happycodex-0-7-2-capability-proportional-admission.md`
  - `.codex-plugin/plugin.json`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `README.md`
  - `README.en.md`
  - `tests/test_attestation_contract.py`
- Preserve `AGENTS.md`; every historical ExecPlan, including 0.7.0 and 0.7.1;
  `evaluation/**` and all evaluator tests except the owned repository contract
  test; `skills/happycodex/agents/openai.yaml` and scripts; the published tag;
  external profiles/configuration; marketplace/source/install/cache/rollback;
  Git index, refs, and worktrees; network and external systems.
- No commit, stage, push, fetch, install, cachebuster, marketplace/config edit,
  release, deployment, provider/model invocation, network, migration, alias,
  compatibility path, dual write, active ledger, new durable record type, or
  generic runtime/evaluator engine is authorized.

## Baseline

- Targeted command: `python3 -m unittest tests.test_attestation_contract -v`.
  Frozen receipt: exit `0`; 14 tests; `OK`.
- Full command: `python3 -m unittest discover -s tests -q`.
  Frozen receipt: exit `1`; 159 tests; exactly two accepted failures and no
  errors:
  - `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
    subtest `mutation='old-source'`
  - `test_old_source_components_cannot_back_a_new_dirty_evalspec`
- Candidate acceptance requires those exact two failures unchanged and no new
  failure or error. The full suite must not be described as green.

## Selected design

Before dispatch and before substantive child output is read, Root records the
logical role, intended use and consequence, requested route/config/fork, input
identities and prompt digest, and each guarantee required by task, source, or
user. Automatic handling cannot manufacture authority or silently waive a
required guarantee.

Always require platform acceptance of the exact spawn request and a
mechanically authenticated child/run/result handle binding terminal output to
that dispatch. Always stop for an absent output identity; explicit mismatch in
a requested or required identity/route; malformed or ambiguous claimed
evidence; an unsafe exposed value relative to a predeclared guarantee; grant,
source, path, effect, candidate, or scope drift; and ambiguous or partial
effects.

Treat missing optional telemetry proportionally:

- Record an exposed effective agent name; if missing, record `unverified`.
- If effective model/effort is missing, record `unverified` and continue unless
  exact routing was predeclared required. Discard and stop on exposed mismatch.
  Never claim exact routing while unverified.
- If effective sandbox/approval is missing, record `unverified`. When technical
  isolation was predeclared required, independently prove the isolation/effect
  boundary or stop. Otherwise continue without claiming technical isolation.
  Full access mismatches only a predeclared read-only technical-isolation
  guarantee. Prompt/profile read-only is not proof.
- Unverified Explorer or Challenger route/isolation output supplies advisory
  leads only; Root reproduces each material fact from source before using it in
  a plan, grant, or phase decision.
- Executor output may correspond to writes despite missing route/permission
  telemetry only when host-issued output identity, fixed-writer ownership,
  exact grant, source/prestate, paths/resources, and allowed effects are bound.
  Root trusts actual Git, tests, and receipts rather than Executor prose.
- Exact-final may count without verified model/permission telemetry only if
  exact routing and hard isolation were not predeclared required, the reviewer
  is fresh with empty history and a neutral brief, output identity is bound,
  candidate identity is unchanged, and Root reproduces material findings.
  Disclose unverified guarantees. Required but unproven hard isolation leaves
  review open.

Missing optional telemetry requires no user input. Ask only when continuation
would change the Outcome, authority, trust boundary, or an explicitly required
guarantee. Introduce no user-facing mode, level, or `普通模式继续` command.
Preserve the exact role matrix as requested routing and keep all existing
authority, unique-Executor, resource-claim, baseline, event-correction, Goal,
effect, candidate, and closure invariants.

## Obligations

| ID | Observable contract | Evidence | State |
| --- | --- | --- | --- |
| `CPA-RED` | Updated 0.7.2 contract assertions fail against unchanged 0.7.1 product text. | Targeted RED receipt below. | verified |
| `CPA-PRE` | Dispatch record binds role, consequence, requested route/config/fork, inputs/prompt, and predeclared guarantees before substantive output is read. | Skill, template, README, and passing contract assertions. | verified |
| `CPA-HARD` | Spawn acceptance, authenticated output identity, exact boundaries, mismatch, malformed/ambiguous evidence, unsafe exposed value, drift, and ambiguous/partial effects remain hard stops. | Product text and passing contract assertions. | verified |
| `CPA-OPTIONAL` | Missing optional name, route, or permission telemetry records `unverified` and reduces only dependent claims/use. | Product text and passing absent-versus-mismatch assertions. | verified |
| `CPA-ROLES` | Explorer/Challenger are advisory until reproduction; Executor depends on bound authority/Git/tests; Exact-final has the frozen-candidate and disclosure conditions. | Product text and passing role-consequence assertions. | verified |
| `CPA-NO-UX` | Users choose no mode and enter no continuation phrase; questions occur only at authority/trust/Outcome/required-guarantee boundaries. | Product text and passing forbidden-mode assertions. | verified |
| `CPA-PRESERVE` | Role matrix and existing lifecycle/safety invariants remain; protected bytes and every out-of-scope path remain unchanged. | Diff inventory, tag-tree check, index/status receipts below. | verified |
| `CPA-CHECKS` | Targeted test and offline validators pass; full-suite difference matches the two accepted baseline failures exactly. | Targeted/validators pass; clean-snapshot suite has only the two accepted failures. | verified |
| `CPA-REVIEW` | Final review uses mandatory output identity and proportional requested/exposed/unverified route and permission evidence; hard technical isolation is required only when predeclared. | Passing repair assertions and product/template text. | verified |
| `CPA-RUNTIME-ID` | Optional Runtime identity supplements but never replaces mandatory Output identity; terminal evidence binds the host-authenticated output identity and terminal result. | Passing repair assertions and template field ownership. | verified |
| `CPA-README-REVIEW` | Both four-phase summaries describe Exact-final as logically read-only, make hard technical isolation conditional, and disclose optional unverified telemetry without blocking. | Passing README repair assertions and text. | verified |

## Execution, effects, and stop conditions

1. Update the repository contract test to 0.7.2 first. Preserve historical
   plan and receipt assertions, but stop asserting the blanket 0.7.1 rule as
   current behavior. Run the targeted test and require a real RED caused by
   unchanged product text.
2. Update the manifest, active Skill, active ExecPlan template, and both
   READMEs coherently. Use concise imperative prose; do not create a generic
   mode or state machine.
3. Run the targeted contract, Skill validator, plugin validator,
   `git diff --check`, and full offline suite once. Compare full-suite failure
   identities to baseline.
4. Verify the protected tag tree, exact changed-path inventory, source HEAD,
   index, and status. Record candidate diff/tree identities if all gates pass.
5. Update only this plan with the complete RED/GREEN, test, identity, effect,
   and unresolved-item receipts. Set `candidate_frozen` only if every gate
   passes. Do not modify product after freeze or claim exact-final/closed.

The permitted effects are local writes to the seven owned paths and offline
read/test processes. Any prestate or identity drift, out-of-scope path change,
new test failure/error, inability to establish output identity, ambiguous or
partial effect, or need to widen authority returns the task to Root without
retry, cleanup, or scope expansion.

### Clean-snapshot amendment

After the one dirty-worktree cumulative run produced 41 source-identity errors,
Root granted `HC-0.7.2-CLEAN-SNAPSHOT-002` to the same fixed Executor. It permits
exactly one fresh `/tmp/happycodex-0.7.2-candidate-*` directory, one local
no-network clone of the frozen baseline source, mechanical projection of
exactly the seven owned candidate paths, one temp-repository-only commit with
task-local author configuration, and exactly one full offline suite there.
Capture the exit, count/failure identities, output digest, temp HEAD/tree, and
package identity; then remove only that validated temporary directory.

Stop on source/clone/path/projection mismatch or any failure beyond the exact
two accepted baseline failures. This amendment permits no source-repository
object, index, ref, worktree, HEAD, config, cache, install, marketplace,
provider/network, release, or external effect. The temporary validation commit
is not source-repository commit authority. After validation, update only this
control record; product/test bytes may not change after candidate freeze.

### Repair grant and findings

Root returned the candidate to `working` under
`HC-0.7.2-REPAIR-003` and invalidated affected candidate/Exact-final evidence.
This repair may write only `skills/happycodex/SKILL.md`,
`skills/happycodex/references/execplan.md`,
`tests/test_attestation_contract.py`, and this control record.

- `F-CPA-001`: the final Skill review section and template Candidate/review
  section still universally require isolated read-only review and exact
  model/effort/isolation evidence. That contradicts proportional admission when
  exact routing or hard technical isolation was not predeclared required.
- `F-CPA-002`: the template still requires Runtime identity from runtime
  metadata and binds Terminal receipt to runtime terminal metadata, allowing
  absent optional runtime metadata to override mandatory Output identity.

Record a contract-first RED/characterization, repair only those contradictions,
and run the targeted contract, both validators, and diff check. Because product
bytes change, do not repeat the known dirty-source full suite. Instead, create
exactly one `/tmp/happycodex-0.7.2-repair-*` directory, one local no-network
baseline clone, project exactly the seven candidate paths, create one temp-only
commit, and run the full suite exactly once. Acceptance remains 159 tests with
only the two accepted baseline failures and zero errors/new failures. Capture
identities and remove the exact temporary root. Any mismatch stops without
retry. No source-repository commit, stage, ref, worktree, install, network,
provider, config, cache, marketplace, release, or external effect is permitted.

### Adverse Exact-final and README repair

Root persisted the adverse review into this control record under
`HC-0.7.2-REPAIR-004` before any README or test mutation. The review receipt is:

- host-authenticated Output identity:
  `/root/capability_proportional_exact_final`;
- fork: `none`; intended consequence: final review;
- per-run effective model/effort and permissions: not exposed, recorded
  `unverified`; hard technical isolation was not predeclared required;
- candidate identity: unchanged; external reads, network, and provider effects:
  none;
- verdict: `NOT YET`;
- exact finding `F-EF-001`: `README.en.md` four-phase summary line 54 and
  `README.md` line 46 still universally call Exact-final an `isolated read-only
  reviewer` / `隔离、只读的评审者`. This contradicts the later conditional
  hard-isolation language and normative Skill/template. The contract test did
  not reject those stale phrases, so `CPA-REVIEW` was overstated.

This adverse receipt is preserved and must not be rerun against unchanged
bytes. The repair may write only `README.en.md`, `README.md`,
`tests/test_attestation_contract.py`, and this control record. Update the test
first for a real RED, then make each summary say fresh logically read-only,
technical read-only isolation only when predeclared required, and missing
optional route/permission telemetry alone does not block and is disclosed.

Run the targeted contract, Skill/plugin validators, and diff check. Validate
changed product bytes in exactly one clean
`/tmp/happycodex-0.7.2-readme-repair-*` snapshot: one no-network baseline clone,
exact seven-path projection, one temp-only commit, one full suite, receipt
capture, and exact cleanup. Acceptance is 159 tests with exactly the two
accepted baseline failures and zero errors/new failures. Do not run the known
dirty-source path. No source commit, stage, ref, worktree, push, install,
network, provider, release, or other product/version/template/Skill change is
authorized. Changed bytes require a new fresh Exact-final after refreeze.

## Current receipt

Prestate and RED:

- On 2026-08-05 UTC, branch `main`, source commit
  `c9476242c259cfe84ba2c9b7866f62d5694c3ee6`, tree
  `1d91d18eac039cca2be64707584cb34424507337`, clean status, empty index, and
  empty untracked inventory matched the grant. This durable intent was the
  first mutation.
- The contract test was updated before product text. Its first run exited `1`
  after 14 tests with three failures: the two expected 0.7.1/0.7.2 product
  version failures plus one self-scan failure because a newly asserted phrase
  contained a retired token literally. The assertion was represented by string
  concatenation without changing its runtime value; product bytes were still
  unchanged.
- Definitive RED command:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_attestation_contract -v`.
  It exited `1` after 14 tests in 0.120 seconds with exactly two failures and no
  errors: both current candidate/version tests observed manifest `0.7.1`
  instead of required `0.7.2`. Every unrelated test passed.

Implementation and focused GREEN:

- `.codex-plugin/plugin.json` declares 0.7.2 and capability-proportional
  admission.
- `skills/happycodex/SKILL.md` and its ExecPlan template distinguish mandatory
  dispatch/output identity and predeclared guarantees from optional effective
  route/permission/name telemetry; bind the Explorer/Challenger, Executor, and
  Exact-final consequences; withhold unsupported routing/isolation claims; and
  add no mode or continuation command.
- Both READMEs expose the same normal-user behavior and preserve the exact
  requested routing matrix and native Explorer rule.
- The first post-implementation targeted run had one failure caused only by a
  Markdown line break inside an exact Chinese contract phrase. Reflowing that
  sentence changed no semantics. The final targeted command exited `0`: 14
  tests in 0.122 seconds, `OK`.
- Skill validator:
  `PYTHONDONTWRITEBYTECODE=1 python3 /home/caichenghang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/happycodex`;
  exit `0`, `Skill is valid!`.
- Plugin validator:
  `PYTHONDONTWRITEBYTECODE=1 python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`;
  exit `0`, plugin validation passed.
- `git diff --check`: exit `0`, no output.

Cumulative-suite blocker:

- The single candidate command
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` exited
  `1` after 159 tests in 40.283 seconds with the exact two accepted baseline
  failures unchanged and 41 candidate-new errors.
- All 41 errors share
  `evaluation.identity.IdentityError: frozen source package identity differs`
  at `evaluation/identity.py:183`, exposed as
  `evaluation.provider.ProviderError: frozen source package identity differs`
  through `evaluation/provider.py:91-97`. The dirty owned product bytes differ
  from committed frozen-source fixtures. These errors are not accepted or
  called green. The full suite was not retried.
- The original grant did not authorize a clean snapshot, temporary validation
  commit, index/ref change, or fixture/evaluator adjustment, so the Executor
  stopped without retry. Root then issued the exact amendment recorded above.

Clean-snapshot resolution:

- The one temporary root was
  `/tmp/happycodex-0.7.2-candidate-DLILEv`, created by the authorized `mktemp`
  prefix with mode `0700`. The local no-network clone matched baseline commit
  `c9476242c259cfe84ba2c9b7866f62d5694c3ee6` and tree
  `1d91d18eac039cca2be64707584cb34424507337` and began clean.
- The source dirty inventory matched exactly the seven owned paths. Mechanical
  projection proved source/clone byte and filesystem-mode equality for all
  seven, with no additional modified or untracked clone path.
- One unsigned temp-repository-only commit was created with task-local identity
  `HappyCodex Validation <happycodex-validation@invalid>` and subject
  `validation: 0.7.2 capability-proportional candidate`. Commit:
  `0be8c727c2034e219ec9385fa553c20b9b0dd8c9`; parent: frozen baseline;
  validation tree: `6b529ef3988ae573730eae8f6abc0e63976530e0`;
  seven-path binary diff SHA-256:
  `0a2f8a12ad4536f4e84a3d4994bf1c65768b65a05f5625d07898ed86ab21b646`.
- The exactly-once clean candidate command was
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`.
  It exited `1` after 159 tests in 67.160 seconds with exactly the two accepted
  baseline failures, zero errors, and no new failure. Terminal log SHA-256:
  `3a6fd003df261d1338540141db3be8e088b65670488f30df5dca148a949bc3d1`.
  The dirty-run 41 errors are therefore classified as validation-environment
  source-identity effects, not candidate failures.
- Candidate package tree:
  `72e49a9e41671b0405afd79ccf5545d513faaccf`;
  package artifact SHA-256:
  `af42b81939eaf2be371db2db1f944db1cca259baaff1a73ee1c0566b98485602`;
  package semantic SHA-256:
  `48d36d34c622f3c69f644ae9c9e9ec78feee30c118b665c4aacbed3ce720ddea`;
  `ProductArtifact` record SHA-256:
  `fa2f841495765c5eeb942b6c0f663cfc07bf1bc75df94e453496539f9bb2576d`.
- After receipt capture, the exact temporary root was revalidated against its
  path, mode, HEAD/tree, and log digest, then removed as authorized. A first
  `rm -rf` request was rejected before execution by command safety and had no
  effect; after revalidation, exact-path `rm -r` succeeded. The temporary
  directory no longer exists.

Identity, inventory, and effects:

- HEAD/tree remain the frozen source identities; the index is empty and no ref
  changed. `v0.6.5:skills/happycodex` remains exactly
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`. `AGENTS.md` remains SHA-256
  `3eed318e17b2733435c737bc335aecfb29f2ba0abfe28a3d4a65c8c1019ea716`.
- Exact tracked modifications: `.codex-plugin/plugin.json`, `README.en.md`,
  `README.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`. Exact untracked path: this ExecPlan.
  No staged or out-of-scope path exists.
- Tracked diff summary: six files, 275 insertions and 193 deletions. Binary
  full-index tracked diff SHA-256:
  `5e390cbcfa6555b0e68f26a14c4b715c407c6a55deba523a67e98811dc07a3b4`.
- Candidate content SHA-256 values: manifest
  `536d210dd251588fc29c00ede04c7a305e3ef2d517f26a4cfdc8cfc1ac5bd93e`;
  Skill `61746b1c1b9f2dbf304bff6cd83787ed2a66cd089e3268c7f0bad88ba18ad3d2`;
  template `047db428ddf3b8515137dbf78be6ddbc634a4a48e5ac0dc234fe77be8887db56`;
  Chinese README
  `feaad75ab85ee843ce90f0989dc24c99724291925d9e3e168d1d12ef3987c1d9`;
  English README
  `49d4082b1b1e9327c21e5139dc9eaeec76ab1c5193fc3ef1483bd10e79830554`;
  contract test
  `6b1a3eaff5a18257fce8260a7b3577efcb4377a57d89d741c5509f5a4e5d7fc6`.
- The validation candidate tree and package identity are recorded above; no
  source-repository tree object was created. Effects were limited to the seven
  owned local paths, the one removed temporary clone
  and commit, and offline test/validation processes. The validation tree above
  binds the projected seven-path candidate before this terminal control-receipt
  update; the package identity excludes this control record and remains frozen.
  No source-repository commit, stage, ref, network, provider/model, install,
  activation, marketplace/config, cache, rollback, release, deployment, or
  external-system effect occurred.

### Repair receipt

- Pre-repair candidate identities matched the prior frozen receipt exactly;
  HEAD/tree, index, seven-path status, protected tag tree, and `AGENTS.md` had no
  drift. This plan returned to `working` and persisted
  `HC-0.7.2-REPAIR-003`, `F-CPA-001`, and `F-CPA-002` before repair mutation.
- The contract test was strengthened first. RED command:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_attestation_contract -v`;
  exit `1`, 14 tests in 0.125 seconds, exactly one failure and no error. The
  failing field was `Runtime identity`, whose unchanged template row lacked
  `exposed runtime supplement or unverified; never substitutes for Output
  identity`. This directly characterized `F-CPA-002`; later assertions bound
  the reproduced `F-CPA-001` final-review contradiction.
- The Skill final section now makes Exact-final fresh and logically read-only,
  makes hard technical isolation conditional on a predeclared requirement,
  always binds authenticated output identity and frozen candidate evidence,
  records requested/exposed/unverified route and permission evidence, and lists
  the exact conditions that leave review open.
- The template makes Runtime identity an optional exposed supplement, binds the
  terminal receipt to mandatory host-authenticated Output identity and terminal
  result, and applies proportional route/permission evidence in Candidate and
  review. Output identity was not weakened.
- Final targeted command: exit `0`, 14 tests in 0.124 seconds, `OK`. Skill
  validator: exit `0`, `Skill is valid!`. Plugin validator: exit `0`, passed.
  `git diff --check`: exit `0`, no output.

Repair snapshot and cumulative suite:

- Exactly one temporary root,
  `/tmp/happycodex-0.7.2-repair-NcbyYZ`, was created with mode `0700`. Its local
  no-network clone matched the frozen baseline commit/tree and began clean.
  Source status matched exactly the seven candidate paths; projection proved
  byte and filesystem-mode equality with no extra clone dirt.
- One unsigned temp-only commit used
  `HappyCodex Validation <happycodex-validation@invalid>` and subject
  `validation: 0.7.2 proportional review repair`. Commit:
  `200378241799514d077192a8192f131faad742f4`; parent: frozen baseline;
  validation tree: `9230569fbf8df6d68677c261307b9e1708539eab`;
  seven-path binary diff SHA-256:
  `299ea553ecbd52a211686c027065d5cfcc1501a5f5278192442a97dee9f08775`.
- The one clean full-suite command
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` exited
  `1` after 159 tests in 57.633 seconds with exactly the two accepted baseline
  failures, zero errors, and no new failure. Log SHA-256:
  `77b1c8531f4cc56d26f5e786ac9b3c28cab0c3779cade46876f40f8485d676eb`.
- Candidate package tree:
  `49dd643cdce8be6bad3cb6578a6b3a48bfb9df0c`; package artifact SHA-256:
  `e84451605925140d649cce567cfe86e1eb59f85d3b30d08210da43b1e7dfade4`;
  package semantic SHA-256:
  `a57631748ef458e0c0793e160b66c72fe61a5e73abe520864c8a5218bd2c9a55`;
  `ProductArtifact` record SHA-256:
  `2ea2ff3a990452c4b56cef66654ec9b0fb557be6994f7e0d7c28c723fffdbbbb`.
- The temporary root was revalidated against exact path, mode, HEAD/tree, and
  log digest, then removed with exact-path `rm -r`. It no longer exists.

Final source-repository inventory remains the same six modified tracked paths
and this untracked ExecPlan, with an empty index and no out-of-scope path.
Tracked diff summary: six files, 354 insertions and 211 deletions. Tracked
binary diff SHA-256:
`806739e2915bbb72dcd5c3b968322f151135dfc0d0d5ec1533cbe0783ee0f7f3`.
Repaired Skill SHA-256:
`53e768ac3cecbcc564609e8f879758286b457a84d70cc82601f34397bdb18f33`;
template SHA-256:
`9e34eb15caaece1a425540da87ce37d39961f1cd435421654c647cabf9816cd1`;
contract test SHA-256:
`93e4bcd84d948f700a6f96bb0e12d34822abbd70d3550e9f6ea188b3af077100`.

All obligations are verified and product/test bytes are refrozen. The only
post-validation mutation is this terminal control receipt. Exact-final evidence
from the prior candidate is invalid; no repaired Exact-final has been conducted
and no overall completion decision is claimed. Root owns the next phase and
final decision.

### README Exact-final repair receipt

- The pre-repair source candidate matched the prior frozen hashes, seven-path
  inventory, empty index, frozen HEAD/tree, protected tag tree, and unchanged
  `AGENTS.md`. The adverse Exact-final and `F-EF-001` were persisted above
  before README/test mutation. That `NOT YET` remains durable and was not rerun
  against unchanged bytes.
- The contract test changed first. RED command:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_attestation_contract -v`;
  exit `1`, 14 tests in 0.139 seconds, four failures and zero errors. All four
  failures came from the unchanged English four-phase summary: three missing
  proportional clauses and the retained exact stale phrase
  `one fresh isolated read-only reviewer`. No unrelated test failed; the same
  test also rejects the exact stale Chinese phrase.
- `README.en.md` and `README.md` now say the reviewer is fresh and logically
  read-only, hard technical read-only isolation applies only when predeclared
  required, and missing optional route/permission telemetry alone does not
  block review and must be disclosed. No other product/version/template/Skill
  byte changed under this repair.
- Final targeted command: exit `0`, 14 tests in 0.141 seconds, `OK`. Skill
  validator: exit `0`, `Skill is valid!`. Plugin validator: exit `0`, passed.
  `git diff --check`: exit `0`, no output.

README repair snapshot and cumulative suite:

- Exactly one temporary root,
  `/tmp/happycodex-0.7.2-readme-repair-mUSF56`, was created with mode `0700`.
  Its local no-network clone matched the frozen baseline commit/tree and began
  clean. Source status matched exactly the seven candidate paths; projection
  proved byte and filesystem-mode equality with no extra clone dirt.
- One unsigned temp-only commit used
  `HappyCodex Validation <happycodex-validation@invalid>` and subject
  `validation: 0.7.2 readme review repair`. Commit:
  `cac7afcb163c8d19e8d4ae0cb88ac6548efeaf29`; parent: frozen baseline;
  validation tree: `5a18e6ccec0ca281d30d8fd760c473f413de3a85`;
  seven-path binary diff SHA-256:
  `aedb9c071d3d6bd2dc7310267e6b645d7ceb349c89c2f611d02924c9033bcf46`.
- The one clean full-suite command
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` exited
  `1` after 159 tests in 58.412 seconds with exactly the two accepted baseline
  failures, zero errors, and no new failure. Log SHA-256:
  `91da47e6aec72298e4506c6d35e9728a4ff7f7a7f2ccd9aa263960021d580c96`.
- Candidate package tree remains
  `49dd643cdce8be6bad3cb6578a6b3a48bfb9df0c`; package artifact SHA-256:
  `8f4f7b9c19e5b664f392a1bdb673da34ae668d595dae917f14856f5e5567a2d9`;
  package semantic SHA-256:
  `47b52c20f2fd52efb393fd0fb86f18551049b3236bb8964adb7341d0d3d1ba18`;
  `ProductArtifact` record SHA-256:
  `5b3e951255bd40fa9b891e43f901289a96d8feeadca54d786434f1b03485f758`.
- The temporary root was revalidated against exact path, mode, HEAD/tree, and
  log digest, then removed with exact-path `rm -r`. It no longer exists.

Final source inventory remains the same six modified tracked paths and this
untracked ExecPlan, with an empty index and no out-of-scope path. Tracked diff
summary: six files, 380 insertions and 215 deletions. Tracked binary diff
SHA-256:
`5783169f659e9e6dac92c9140d2aca67c6fd8abd42f76d51c00dbec46a8f1f4e`.
English README SHA-256:
`2f1f684a7ba7cab858132c6895e4d8139f53430e9d5a39fbfadb0cb0ae1a2577`;
Chinese README SHA-256:
`e5e487eb0748106f833a01109ee1990825ff5977e9e03c9c91284f4de1e56805`;
contract test SHA-256:
`13c17b9e2e4890b204c7e5bce6b5db2988033550da106d3c12685ae247527455`.

All obligations are verified and the changed candidate bytes are refrozen. The
only post-validation mutation is this control receipt. The preserved adverse
Exact-final applies to the superseded bytes; Root must obtain one new fresh
Exact-final for this repaired candidate. No completion decision is claimed.

## Terminal Exact-final and Root admission

- A new fresh Exact-final returned `GO` with no blockers. Its mandatory
  host-authenticated Output identity is
  `/root/capability_proportional_exact_final_v2`; requested role/profile was
  `happycodex_exact_final` with fork `none` and intended consequence final
  review. Effective model/effort and agent name were not exposed and are
  recorded `unverified`.
- The reviewer reported unrestricted / `danger-full-access` permissions with
  approval `never`. Hard technical isolation was not predeclared required and
  is not claimed. The reviewer maintained logically read-only behavior.
- All seven exact candidate paths were fully reviewed with no unresolved
  truncation. No external-system, network, or provider read or effect occurred.
  The prior adverse Exact-final receipt remains preserved for its superseded
  bytes and was not rerun unchanged.
- Root independently reproduced baseline HEAD
  `c9476242c259cfe84ba2c9b7866f62d5694c3ee6`, tree
  `1d91d18eac039cca2be64707584cb34424507337`, the exact seven-path status,
  empty index, `git diff --check`, tracked binary diff
  `5783169f659e9e6dac92c9140d2aca67c6fd8abd42f76d51c00dbec46a8f1f4e`,
  package tree `49dd643cdce8be6bad3cb6578a6b3a48bfb9df0c`, ProductArtifact
  `5b3e951255bd40fa9b891e43f901289a96d8feeadca54d786434f1b03485f758`,
  and protected `v0.6.5` Skill tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; no candidate drift was found.
- The targeted contract remains 14/14. Skill/plugin validators and the clean
  full-suite evidence remain the frozen receipts and were not rerun: 159 tests,
  exactly the two accepted baseline failures, zero new failures/errors, log
  SHA-256
  `91da47e6aec72298e4506c6d35e9728a4ff7f7a7f2ccd9aa263960021d580c96`.
- This plan-only terminal receipt is excluded control evidence and does not
  mutate frozen product/test bytes. No Goal existed. Every 0.7.2 local
  candidate obligation is verified. `closed` applies only to this local
  candidate; it is not a commit, install, release, activation, deployment,
  publication, or marketplace change.
- No commit, stage, push, install, release, deploy, provider, network, config,
  cache, session, ref, worktree, or external effect occurred. The index remains
  empty.
