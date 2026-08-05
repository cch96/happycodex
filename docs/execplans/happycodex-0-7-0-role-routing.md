# HappyCodex 0.7.0 role routing

## Contract

- Intent ID: `HC-0.7.0-ROLE-ROUTING-001`.
- Phase: `closed`.
- Outcome: implement the authorized 0.7.0 role-routing behavior contract in the
  public plugin and add three optional, machine-local read-only custom-agent
  profiles without publishing, installing, activating, or releasing anything.
- Root owns decomposition, grants, evidence reproduction, routing-receipt
  verification, and the completion decision. The fixed Executor is the only
  writer for every authorized repository and local-config path in this task.
- No Goal was requested or created.

## Frozen request and preservation

The exact active authorization is the Root grant for Intent ID
`HC-0.7.0-ROLE-ROUTING-001`: create this live ExecPlan before any other product
write; update only the named public contract surfaces and, if necessary, the
existing static contract test; create exactly three namespaced local profiles;
run only the named offline checks; do not stage, commit, push, install,
reinstall, cachebust, release, use the network, invoke an external model, or
delegate.

Frozen prestate:

- Repository: `/home/caichenghang/projects/happycodex`.
- Branch: `main`.
- HEAD: `a28413a23afa31b50ede8d530f064fc86c37d146`.
- Tree: `66ac7bcb4d7b918a1de3633e70f1fd1a5447a4f0`.
- Initial tracked worktree: clean.
- Preserved published skill tree:
  `v0.6.5:skills/happycodex = d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Preserved local Executor:
  `/home/caichenghang/.codex/agents/happycodex_executor.toml`, SHA-256
  `d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`.
- Preserve all evaluator bytes, closed 0.6.6 ExecPlans,
  `skills/happycodex/agents/openai.yaml`, config, marketplace, active install,
  cache, rollback, refs, index, and external state.

Authorized write paths are exactly:

- `docs/execplans/happycodex-0-7-0-role-routing.md`
- `.codex-plugin/plugin.json`
- `README.md`
- `README.en.md`
- `skills/happycodex/SKILL.md`
- `skills/happycodex/references/execplan.md`
- `tests/test_attestation_contract.py`, with one dedicated stdlib static test
  file allowed only if the existing file cannot express the contract
- `/home/caichenghang/.codex/agents/happycodex_explorer.toml`
- `/home/caichenghang/.codex/agents/happycodex_challenger.toml`
- `/home/caichenghang/.codex/agents/happycodex_exact_final.toml`

Any changed prestate, need for another path/effect, non-offline validation,
identity/config drift, or ambiguous/partial effect returns to Root without
retry or cleanup.

Root later added exact offline validation authority
`HC-0.7.0-SNAPSHOT-001`. After the other checks, the Executor may create
exactly one recoverable `mktemp -d /tmp/happycodex-role-routing.XXXXXX`
directory, make a local no-network clone/copy of baseline HEAD, apply the
current tracked diff exactly, and stage/commit only inside that temporary
repository with a fixed temporary identity so its HEAD represents the
candidate. Run the same full stdlib suite there; preserve the temporary
directory for Root/Exact-final and report its absolute path, candidate commit,
and tree. This grant does not permit staging or committing in the current
repository, changing its index/HEAD, or projecting untracked files.

Root then issued exact repair authority
`HC-0.7.0-ROUTING-REPAIR-001` to the same fixed Executor. It reopens the
routing contract in `working` only to replace the impossible pre-work receipt
claim with a two-stage dispatch/admission gate; narrow zero-configuration and
verifiable-routing claims to host capability; use `behavior-plan freeze`
consistently; strengthen the existing static contract test; record the
Root-supplied runtime and custom-profile receipts; classify the exact two
full-suite failures as accepted baseline-unchanged; and rebuild the already
authorized temporary snapshot. Its only writable repository paths are this
plan, `.codex-plugin/plugin.json`, both READMEs, `skills/happycodex/SKILL.md`,
`skills/happycodex/references/execplan.md`, and
`tests/test_attestation_contract.py`, plus the existing authorized temporary
repository `/tmp/happycodex-role-routing.1eTKh1/repo`. The three local profiles,
fixed Executor, evaluator, all other tests, old plans, current index/HEAD, and
all install/network/release state remain immutable. Manual edits use
`apply_patch`; no delegation is permitted.

Root finally issued `HC-0.7.0-ROUTING-REPAIR-002` to the same fixed Executor.
It keeps the task in `working` while splitting routing evidence into an
authenticated Root-owned dispatch/tool receipt, runtime-issued session/turn
metadata, and Root's cross-bound admission decision. Runtime metadata must not
be required to echo Root-owned logical role, fork, or input identities. The
grant also fixes the live-plan sentence break, classifies parsed-but-not-active
profiles as a deferred non-blocker for the 0.7.0 source candidate, strengthens
the existing static test without pinning a volatile phase, appends one new
commit to the existing authorized temporary repository, and reruns the exact
offline checks. Only this plan, both READMEs, `skills/happycodex/SKILL.md`,
`skills/happycodex/references/execplan.md`,
`tests/test_attestation_contract.py`, and the existing temporary repository are
writable. Manifest, profiles, Executor, evaluator, other tests/files, current
index/HEAD, network/install/release state, and delegation remain forbidden.
After all required validation, the plan may enter `candidate_frozen`; Root
still owns exact-final and completion.

Root subsequently issued the control-record-only authorization
`HC-0.7.0-EXACT-FINAL-RECEIPT-001` to the same fixed Executor. Its sole writable
path is this ExecPlan. It authorizes exactly one Exact-final receipt from the
Root-supplied dispatch, runtime, admission, and terminal records, followed by a
transition to `closed`. Product, test, profile, snapshot, index, HEAD, install,
network, release, activation, and delegated effects remain forbidden. Manual
edits use `apply_patch` only. After the receipt, run only the targeted static
contract suite, `git diff --check`, `git status --short --branch`, and this
plan's SHA-256; do not create another snapshot or commit.

## Selected design

Plugin installation does not bundle or require custom agents. Complete routing
is available only when the host supports exact selectors and runtime-issued
session/turn metadata. Before dispatch, Root verifies its own effective route
is `gpt-5.6-sol/max` and confirms the selector can request the target logical
role, platform/custom name, model, effort, and a `fork_turns` value of `none` or
a bounded positive integer. Root creates an authenticated dispatch/tool receipt
that owns logical role, selected request, requested model/effort or custom
config SHA-256, fork, input baseline/candidate identities, and prompt/brief
digest; platform acceptance of the spawn completes it. The portable
builtin/default path explicitly pins model and effort. For a namespaced custom
agent, its file's model/effort take precedence and conflicting or redundant
explicit model/effort arguments are omitted. The machine-local `happycodex_*`
profiles are optional strict/convenience profiles and are not packaged or
installed by the plugin.

The complete matrix is:

| Logical role | Effective model | Effort | Access and lifecycle |
| --- | --- | --- | --- |
| Root | `gpt-5.6-sol` | `max` | decomposes, grants, reproduces, verifies |
| Explorer | `gpt-5.6-terra` | `high` | read-only, one bounded decision-changing question |
| Challenger | `gpt-5.6-sol` | `high` | read-only, before behavior-plan freeze |
| Executor | `gpt-5.6-sol` | `high` | the unique fixed controlled-domain writer |
| Exact-final | `gpt-5.6-sol` | `max` | one fresh read-only instance after candidate freeze |

Root first decomposes work into independent decision-changing axes. Multiple
Explorers may run concurrently only when multiple such axes exist; each gets
one bounded question. Root reproduces and merges their evidence without voting.
Challenger runs before behavior-plan freeze. Only after that challenge is
resolved and the behavior plan is frozen does the fixed Executor write. After
candidate freeze, Root starts exactly one fresh Exact-final with empty history
and a neutral brief; any repair returns to `working`, invalidates the affected
frozen evidence, and requires a newly frozen candidate and new Exact-final.

Spawn may start immediately. Runtime-issued session/turn metadata owns actual
platform/custom role or name when exposed, effective model/effort, effective
sandbox/approval, and child/run/session identity. It need not echo Root-owned
logical role, fork, input identities, or prompt digest. Root admits output only
after cross-binding the runtime metadata to the authenticated dispatch receipt.
Before admission, child output cannot enter the behavior plan, trigger a write
grant, advance phase, or count as a final verdict. A missing required source or
mismatch requires immediate interrupt if the child still runs, output discard,
and fail-closed routing. Logical role and platform/custom-agent name remain
distinct.

Permissions are effective-runtime facts. In a full-access parent task, a local
profile's `sandbox_mode = "read-only"` may be overridden by the live parent.
Neither profile defaults nor prompt text are hard isolation. When technical
read-only isolation is required, establish a read-only top-level or parent
environment before dispatch, then verify effective permissions from the
receipt; unverified output remains inadmissible.

## Runtime routing receipts

Root verified its own active route as `gpt-5.6-sol/max`. The Root-owned dispatch
excerpt records these accepted spawn requests:

| Logical role | Selected agent request | Requested route/config | Platform acceptance |
| --- | --- | --- | --- |
| Explorer | builtin `agent_role=explorer` | `gpt-5.6-terra/high`; no custom config | session `019fd0fe-6294-7270-a204-4a68d63df579` created |
| Challenger | builtin `agent_role=explorer` | `gpt-5.6-sol/high`; no custom config | session `019fd0fe-81ee-79c2-896d-b2c0f87203c0` created |

The corresponding runtime-issued metadata is:

| Runtime session | Actual platform role | Custom name | Effective model/effort | Approval | Effective sandbox |
| --- | --- | --- | --- | --- | --- |
| `019fd0fe-6294-7270-a204-4a68d63df579` | `explorer` | not exposed | `gpt-5.6-terra/high` | `never` | `danger-full-access` |
| `019fd0fe-81ee-79c2-896d-b2c0f87203c0` | `explorer` | not exposed | `gpt-5.6-sol/high` | `never` | `danger-full-access` |

The shared platform role name does not erase the distinct Root-owned logical
roles. The effective `danger-full-access` metadata also demonstrates that
profile/prompt read-only wording is not hard isolation under this parent. The
supplied dispatch excerpt does not include fork, input identities, or prompt
digest, so these observations do not prove a complete cross-bound admission
record and must not be represented as one.

A same-task hot-load attempt returned
`unknown agent_type 'happycodex_explorer'`. Classify this as the current task's
agent-registry snapshot, not as invalid TOML or permanent host incompatibility.
Existing `tomli 2.4.1` parsed all three namespaced profile files successfully,
but activation can be verified only in a new task. This parse result is not a
current custom-profile runtime receipt and must not be represented as one.
Current status remains `working`; no local custom profile has been admitted in
this task.

## Obligations

| ID | Observable contract | Evidence | State |
| --- | --- | --- | --- |
| `ROUTE-VERSION` | Manifest and public docs identify the 0.7.0 behavior candidate without a release action. | JSON/static test and diff | verified |
| `ROUTE-MATRIX` | All five logical roles use the exact frozen model/effort matrix. | static contract test | verified |
| `ROUTE-PIN` | Dispatch preflight checks Root/host selectors; builtin/default pins model/effort; custom config takes precedence; output remains inadmissible until effective receipt verification. | Runtime text and static contract test | verified |
| `ROUTE-ORDER` | Decompose, bounded independent exploration, pre-behavior-plan-freeze challenge, unique write, candidate freeze, then one fresh neutral exact-final; repair returns to working. | Runtime text and static contract test | verified |
| `ROUTE-MERGE` | Root reproduces and merges evidence without voting. | Runtime text and static contract test | verified |
| `ROUTE-RECEIPT` | ExecPlan schema assigns Root-owned request fields to authenticated dispatch/tool evidence, effective fields to runtime metadata, and admission/phase gate to Root's cross-bind. | reference text and static contract test | verified |
| `ROUTE-PERMISSION` | Public docs state that profile/prompt read-only is not hard isolation and describe verified top-level/parent read-only isolation. | bilingual docs and static contract test | verified |
| `ROUTE-PORTABLE` | Plugin installation requires no custom agent; local profiles are optional, namespaced, and unbundled; complete routing is conditional on host selector/metadata capability. | manifest/docs/profile inventory | verified |
| `ROUTE-PROFILES` | Explorer is Terra/high/read-only; Challenger is Sol/high/read-only; Exact-final is Sol/max/read-only; instructions prohibit mutation, effects, and delegation and require evidence. | Configuration parse/hash verified; new-task activation deferred, not a 0.7.0 source-candidate blocker; activation is not claimed. | verified with deferred activation |
| `ROUTE-PRESERVE` | Executor, evaluator, published v0.6.5 tree, index, install/cache/rollback, and all unlisted paths stay unchanged. | hashes, Git status/diff inventory | verified |

## Frozen product candidate

The repair-002 product identity is frozen. This ExecPlan is a control record;
its bytes and final receipt are excluded from product identity.

- Baseline HEAD `a28413a23afa31b50ede8d530f064fc86c37d146`, tree
  `66ac7bcb4d7b918a1de3633e70f1fd1a5447a4f0`.
- Product/test paths are exactly `.codex-plugin/plugin.json`, `README.md`,
  `README.en.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`.
- Their tracked binary/full-index diff SHA-256 is
  `aa9ea342e45eb20a10eaab38cbfb71fc8a95960b56485e64d39fa66a1928708d`.
- Configuration identities remain Explorer
  `3bae55fd510b7187dcd9d41b25bd5ee3a78590957dacc3f71e227c77108cf7bd`,
  Challenger
  `164a35d7275f0607f68c5c26ed0874cc39b2c36fa295b6b4b6cb6f3050172f9a`,
  and Exact-final
  `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`.
- Current repository state is intentionally uncommitted with a clean index;
  this plan is the only untracked path. Branch `main`, HEAD, and baseline tree
  remain unchanged.
- The exact temporary snapshot is
  `/tmp/happycodex-role-routing.1eTKh1/repo`, commit
  `465cf39e31af038a449a994a9ff52b04c3b9266d`, parent
  `1711669d4921fd01974838dc6bf38db063d16a69`, tree
  `c71d777a5f17e8dd6d5f9e11dc3eb6782056336a`. Before the terminal control-only
  update, all 53 candidate paths, including this plan, matched source bytes and
  modes exactly; temporary status was clean.
- The full suite ran 159 tests in 68.964 seconds, exited 1, timed out false, and
  had zero errors and exactly two baseline-unchanged accepted limitations:
  `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
  with `mutation='old-source'`, and
  `test_old_source_components_cannot_back_a_new_dirty_evalspec`. There were no
  new failures. This suite is not green.

## Progress

- [x] Re-read the exact grant and applicable repository instructions.
- [x] Verify branch, HEAD, tree, initial tracked cleanliness, and preserved
  Executor SHA-256.
- [x] Persist this live ExecPlan before any other product mutation.
- [x] Update public manifest, bilingual README, Runtime, and ExecPlan reference.
- [x] Add the narrow offline static contract coverage.
- [x] Create the three optional local profiles and perform the available
  non-parser structure checks; runtime parsing remains with Root.
- [x] Run every named acceptance command that the local interpreter supports
  and record passes, failures, and the unavailable `tomllib` check.
- [x] Build the one authorized committed temporary candidate snapshot and run
  the full suite there.
- [x] Return the candidate and evidence to Root; do not decide completion.
- [x] Repair dispatch/admission semantics, host-capability boundaries, freeze
  terminology, bilingual/static coverage, and receipts under
  `HC-0.7.0-ROUTING-REPAIR-001`.
- [x] Rebuild the existing temporary candidate, reproduce the accepted
  baseline failure set with no new failure, and return the repair receipt.
- [x] Split authenticated dispatch evidence from runtime metadata, validate the
  repaired source candidate, freeze its identity, and return the repair-002
  receipt without deciding completion.
- [x] Admit the single fresh Exact-final review receipt, record its limitations,
  and close the unchanged source-candidate work under
  `HC-0.7.0-EXACT-FINAL-RECEIPT-001`.

## Decisions

- Use one concise routing section in the Runtime and keep field-level receipt
  detail in `references/execplan.md` to preserve progressive disclosure.
- Extend `tests/test_attestation_contract.py`; do not add another test file
  unless the existing contract-test surface proves insufficient.
- Treat the authenticated dispatch/tool receipt as the source for Root-owned
  request fields, runtime metadata as the source for effective fields, and the
  Root cross-bind as the only admission evidence. A selected profile or
  self-description is only requested configuration.
- Do not follow plugin development cachebuster/reinstall guidance because the
  exact grant forbids those effects and asks only for source validation.
- Do not forward-test with subagents because delegation is explicitly
  forbidden for this grant.
- Use `HC-0.7.0-SNAPSHOT-001` only to overcome the evaluator test fixture's
  committed-HEAD assumption. The temporary commit is validation evidence, not
  a repository commit, release, install, or activation.

## Validation

Commands requested by the grant:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_attestation_contract -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 /home/caichenghang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/happycodex
python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
git diff --check
python3 stdlib tomllib validation for the three new local profiles
SHA-256 inventory for the three profiles and preserved Executor
```

Terminal receipts:

- Targeted repair contract suite: 14 tests, exit 0. It independently binds the
  Runtime, both READMEs, reference, manifest, and this live plan.
- The first full-suite run in the dirty source worktree did not pass. A focused
  reproduction failed with `frozen source package identity differs`: the
  existing fixed-host fixture commits copied worktree product bytes into its
  temporary source repository while its `ProductArtifact` still derives from
  this repository's committed `HEAD`. This is a committed-candidate fixture
  requirement, not yet evidence that candidate behavior fails.
- Repair-run Skill validator: exit 0, `Skill is valid!`.
- Repair-run plugin validator: exit 0, `Plugin validation passed`.
- Repair-run `git diff --check`: exit 0.
- Default `python3` remains 3.10.12 without stdlib `tomllib`. The already
  installed offline `tomli 2.4.1` parser successfully parsed all three local
  profiles and verified their exact names, models, efforts, `read-only`
  sandboxes, and `never` approval policies; no file changed. This is syntax and
  field validation, not activation or a custom-profile runtime receipt.
- `git diff --quiet HEAD -- evaluation
  tests/test_fixed_host_transaction_v2.py tests/fake_external_host.py
  tests/attestation_fixtures.py` exited 0, proving the accepted failure surfaces
  are byte-unchanged from the 0.6.6 baseline commit.
- Local-profile SHA-256 values:
  - `happycodex_explorer.toml`:
    `3bae55fd510b7187dcd9d41b25bd5ee3a78590957dacc3f71e227c77108cf7bd`
  - `happycodex_challenger.toml`:
    `164a35d7275f0607f68c5c26ed0874cc39b2c36fa295b6b4b6cb6f3050172f9a`
  - `happycodex_exact_final.toml`:
    `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`
- Preserved Executor SHA-256 remained
  `d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`.
- The single authorized candidate snapshot is
  `/tmp/happycodex-role-routing.1eTKh1/repo`, commit
  `95a7999c40afe26835c68cf73cc25762da35e0fe`, tree
  `783e81c85be48a7d30e7fff37e19f2dbf46537ef`, clean status. All 52 baseline
  tracked paths were compared byte-for-byte with the current source worktree.
  The live ExecPlan is untracked by design and was not projected under the
  exact tracked-diff grant.
- The first snapshot-suite invocation used `/tmp` as cwd and failed during
  unittest discovery before any test ran. This proven pre-test no-effect
  invocation error was corrected in the same snapshot, not by making another
  snapshot. Tool output truncation then required a final logged run to obtain
  an exact terminal receipt.
- Snapshot full suite terminal result: 159 tests in 68.057 seconds, exit 1,
  with exactly two failures:
  `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
  (`mutation='old-source'`) and
  `test_old_source_components_cannot_back_a_new_dirty_evalspec`. This is a
  baseline-unchanged accepted validation limitation. The 0.6.6 plan
  recorded the same two accepted failure identities with zero errors over 158
  tests; 0.7.0 adds one static contract test. Baseline-to-candidate comparison
  has no diff in `evaluation`, `tests/test_fixed_host_transaction_v2.py`,
  `tests/fake_external_host.py`, or `tests/attestation_fixtures.py`. The tests
  intentionally expect source/evaluator drift between the current worktree and
  committed HEAD; a clean committed candidate removes that drift, so the
  expected rejection is not raised. Do not describe this suite as green.
  Evidence log:
  `/tmp/happycodex-role-routing.1eTKh1/full-suite-v.log`, SHA-256
  `c36254013df72ce7abe09d50cb9c38413941593ee61d7c671288ded36ffa24c8`;
  exit receipt SHA-256
  `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`.
- Final source identity remained branch `main`, HEAD
  `a28413a23afa31b50ede8d530f064fc86c37d146`, tree
  `66ac7bcb4d7b918a1de3633e70f1fd1a5447a4f0`, with a clean index. The
  published v0.6.5 skill tree remained
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- The tracked diff contains exactly `.codex-plugin/plugin.json`, `README.md`,
  `README.en.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`. Its `git diff --binary --full-index
  --no-ext-diff` SHA-256 is
  `9f7fcf69fe11168bc28c9c6c7671cd2d1ceb5ca856cc6bb2a3d0e0b105ff1af4`.
  The only repository untracked path is this live ExecPlan.

### Routing repair terminal receipt

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_attestation_contract -v`: 14 tests, exit 0 after one corrected
  test-only newline-normalization assertion.
- Skill validator, plugin validator, and `git diff --check`: exit 0.
- Existing `tomli 2.4.1` parsed all three unchanged namespaced profiles and
  verified the exact matrix, sandbox, and approval fields. Profile SHA-256
  values remain those recorded above; the fixed Executor SHA-256 remains
  `d98fac1a0fe1bcc3071eac89b7246bfeb59fb85a7040417d50d07c58d74d1275`.
- The protected baseline-to-candidate diff command over `evaluation`,
  `tests/test_fixed_host_transaction_v2.py`, `tests/fake_external_host.py`, and
  `tests/attestation_fixtures.py` exited 0.
- The existing authorized temporary repository retains baseline
  `a28413a23afa31b50ede8d530f064fc86c37d146` and the prior snapshot. Its new
  repair commit is `1711669d4921fd01974838dc6bf38db063d16a69`, parent
  `95a7999c40afe26835c68cf73cc25762da35e0fe`, tree
  `5f701ac7a908c23c1257bf6739abb7faae773f5c`. At synchronization time, all 53
  candidate repository files, including this live ExecPlan, matched the source
  path set, modes, and bytes exactly; temporary status was clean.
- The repair snapshot full suite ran 159 tests in 68.413 seconds under a
  120-second offline timeout. It exited 1 with zero errors and exactly the two
  accepted baseline-unchanged failures named above; new failures `0`, timeout
  `false`. Do not report this as a green suite. Raw log:
  `/tmp/happycodex-role-routing.1eTKh1/repair-full-suite-v.log`, SHA-256
  `4c9500e071179327e04cba368d8a28d6ec94725c3543cd98dad769f498c86c3a`.
  Exit receipt value `1`, SHA-256
  `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`.
- Per the authorized order, this terminal receipt was added to the source plan
  after the snapshot suite. Therefore this receipt-only plan update is not in
  the snapshot commit; no second repair commit was authorized or created.
- Final tracked diff paths remain exactly `.codex-plugin/plugin.json`, both
  READMEs, `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`. The tracked binary/full-index diff
  SHA-256 is
  `f53424e3b2dc0974ee28537c227141c144bf6caa0de95f361d3c54c6f454f1df`;
  this plan remains the only untracked repository path. Branch `main`, HEAD
  `a28413a23afa31b50ede8d530f064fc86c37d146`, tree
  `66ac7bcb4d7b918a1de3633e70f1fd1a5447a4f0`, index, and published v0.6.5
  Skill tree remain unchanged.

### Routing repair-002 pre-snapshot receipt

- The strengthened targeted contract suite ran 14 tests and exited 0. It binds
  Root-owned dispatch fields to the authenticated dispatch/tool receipt,
  effective fields to runtime metadata, admission fields to Root's cross-bind,
  and does not pin the live plan to `working`.
- Skill validator, plugin validator, `git diff --check`, and the protected
  baseline-to-candidate diff command all exited 0.
- Existing offline `tomli 2.4.1` parsed the three unchanged profiles and
  verified their exact model, effort, `read-only` sandbox, and `never` approval
  fields. This is configuration validation only; new-task activation remains
  deferred and is not claimed.

### Routing repair-002 terminal receipt

- The first multi-source synchronization command was rejected during argument
  validation because its target was not a directory. It changed no byte and
  created no path. The corrected `cp -p --parents` synchronization was therefore
  a proven pre-effect recovery within the same authorization, not a retry of an
  ambiguous or partial effect.
- The existing authorized temporary repository appended exactly one commit:
  `465cf39e31af038a449a994a9ff52b04c3b9266d`, parent
  `1711669d4921fd01974838dc6bf38db063d16a69`, tree
  `c71d777a5f17e8dd6d5f9e11dc3eb6782056336a`, message
  `HappyCodex 0.7.0 routing evidence split snapshot`. It changed the five
  repair-002 product/test paths plus this plan; manifest bytes were already the
  frozen 0.7.0 candidate bytes and did not change in this repair.
- At snapshot time, all 52 current tracked paths plus this live plan matched the
  temporary repository byte-for-byte and mode-for-mode; temporary status was
  clean. The current repository index remained clean and its HEAD/tree did not
  move.
- The repair-002 snapshot full suite ran 159 tests in 68.964 seconds under the
  120-second offline timeout. Exit was 1, timeout false, error count 0, failure
  count 2, new failure count 0. The exact two accepted baseline-unchanged
  limitation identities are recorded in the frozen product section above.
  Raw log:
  `/tmp/happycodex-role-routing.1eTKh1/repair-002-full-suite-v.log`, SHA-256
  `cfa5a04f1dac081f1820ed4d9315dba2f0202b9ec450daf85e7c4da80edbf0cb`;
  exit receipt value `1`, SHA-256
  `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`.
- Per the repair-002 grant, this terminal receipt and phase transition were
  written only to the source control plan after the suite. They are intentionally
  absent from the snapshot commit and do not require another snapshot because
  the plan is excluded from product identity.
- Frozen product/test paths and tracked diff SHA-256 remain exactly those in the
  frozen product section. Profile configuration hashes and the preserved
  Executor hash remain unchanged. No current-repository stage/commit, profile
  mutation, install, activation, network, release, external-model, or delegated
  effect occurred.

### Exact-final receipt (`HC-0.7.0-EXACT-FINAL-RECEIPT-001`)

This is the single admitted Exact-final receipt for the frozen candidate.

- Root-owned authenticated dispatch: logical role `Exact-final`; selected
  platform agent `explorer`; task `/root/routing_exact_final`; requested model
  `gpt-5.6-sol`; requested effort `max`; `fork_turns = none`. Baseline identity
  is commit `a28413a23afa31b50ede8d530f064fc86c37d146`, tree
  `66ac7bcb4d7b918a1de3633e70f1fd1a5447a4f0`. Candidate identity is snapshot
  commit `465cf39e31af038a449a994a9ff52b04c3b9266d`, tree
  `c71d777a5f17e8dd6d5f9e11dc3eb6782056336a`, with tracked diff SHA-256
  `aa9ea342e45eb20a10eaab38cbfb71fc8a95960b56485e64d39fa66a1928708d`.
  The neutral brief was 4,748 bytes, SHA-256
  `13d2584ebfa43fedeba719e59a0fdc08e4b24e3bb389427a3e1036db51603c00`.
- Runtime-issued metadata: session
  `019fd11b-51c3-7293-9f26-0b24102d2f23`; platform `agent_role=explorer`;
  agent path `/root/routing_exact_final`; actual route `gpt-5.6-sol/max`;
  approval `never`; effective sandbox `danger-full-access`; parent session
  `019fd0d3-616f-7e11-a0a1-86659639f8ff`.
- Root admission cross-binds the authenticated dispatch and runtime metadata.
  Logical role `Exact-final` remains distinct from platform role `explorer`.
  Admission state is `admitted`. The effective `danger-full-access` sandbox
  means the review was behaviorally read-only under instruction, not hard
  technically isolated.
- Exact-final output was 2,310 bytes, SHA-256
  `cbc75f3c3a5baf3f1748b62dbd18bdecea72bf72871b38be466bd07a96bbadce`.
  Verdict: `GO`; material findings: none; terminal state:
  `COMPLETE/read-only/candidate unchanged`.
- Review limitations: Exact-final did not rerun the full suite, activate or
  hot-load the local profiles, replay dispatch, access the network, or invoke
  an external model. The receipt grants no commit, release, install, or
  activation authority. The previously recorded full suite remains non-green:
  159 tests, zero errors, and exactly two accepted baseline-unchanged failures.
- This closure is a plan/control-receipt-only mutation. The frozen product
  candidate and its six product/test paths, tracked diff SHA-256, snapshot
  commit/tree, and local profile identities remain unchanged: Explorer
  `3bae55fd510b7187dcd9d41b25bd5ee3a78590957dacc3f71e227c77108cf7bd`,
  Challenger
  `164a35d7275f0607f68c5c26ed0874cc39b2c36fa295b6b4b6cb6f3050172f9a`,
  and Exact-final
  `6730690a5466a144bbe031e409f9d7dad6f3c1570d9b5abb96d6848654212309`.
  Profile activation remains deferred and unclaimed, while the 0.7.0
  source-candidate work is closed.

Current phase is `closed`. The single Exact-final review is complete and
admitted; no product, snapshot, profile, index, HEAD, install, activation,
network, release, external-model, or delegated effect was authorized or
performed by this closure.
