# HappyCodex 0.7.1 release

## Contract

- Intent ID: `HC-0.7.1-RELEASE-001`.
- Phase: `working`. This record is the current release index and is not itself
  release readiness, release authority, or a release receipt.
- Frozen user request, verbatim: `好的发布吧`.
- Frozen request length: 15 UTF-8 bytes.
- Frozen request SHA-256:
  `90f3efc397e06c1c0b251d73f6e8f1bf02ad209b849ed0dedc168d064b3d45ca`.
- Authorized interpretation: publicly release HappyCodex `v0.7.1` to
  `cch96/happycodex` and update the existing local
  `happycodex@personal` installation to the same 0.7.1 cachebuster package.
- This bootstrap grant authorizes only acquiring and verifying the eight exact
  resources below and creating this plan. It authorizes no release effect.
- Root owns every later grant, freeze, admission, completion decision, and
  claim release. Fixed Executor `/root/native_parallel_explorer_executor` is
  the sole controlled-domain writer. No other writer may be created.
- No Goal was requested or created.

## Verified source prestate

- Repository: `/home/caichenghang/projects/happycodex`.
- Branch/upstream: `main` tracking `origin/main`.
- Local HEAD, upstream, and live remote `main`:
  `39a37b5e5bc497ac629a8e185309698905242e9c`.
- HEAD tree: `f54bc2a7ebc92951177a7412426a1043b17673da`.
- Origin: `git@github.com:cch96/happycodex.git`.
- Index: empty.
- Exact pre-plan worktree inventory:
  - modified `skills/happycodex/SKILL.md`;
  - modified `tests/test_attestation_contract.py`;
  - untracked
    `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md`.
- Candidate SHA-256 identities:
  - Skill:
    `cca9df6187f16e3b4fcbc6b9f78883a26a5c779b525b723c2af2d732a4951342`;
  - contract test:
    `f4fa44e6e864a14ac5c326f5eabe3fc34c0bd53a76361a189c4335444d1fbfc9`;
  - closed native-parallel control:
    `59c3b81bd4b7427246c713479230c1e17136c5b91ddee40bde857c690d629733`;
  - tracked product/test binary full-index diff:
    `1f8aaac593571411bb4afcafb36b65ef90d02164c59895668ae14e8ce70994f7`.
- Preserved published Skill tree:
  `v0.6.5:skills/happycodex = d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Current repository manifest version: `0.7.0`.
- Local and live remote tag `v0.7.1` were absent. GitHub Release `v0.7.1`
  was absent. The latest existing release was public `v0.7.0` targeting
  `main`.
- GitHub authentication was active as `cch96` with git protocol `ssh` and
  scopes `gist`, `read:org`, and `repo`. This is identity evidence only, not
  authority for a network write.

## Prior candidate and review disposition

- The closed control
  `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md` records the
  local candidate as `CLOSED WITH EXPLICIT ISOLATION WAIVER`.
- Its preserved clean snapshot is
  `/tmp/happycodex-0-7-1-native-parallel.EXMU0v/repo`, with parent
  `39a37b5e5bc497ac629a8e185309698905242e9c`, validation commit
  `c056601a34cc61218625c8fbdf2a6001c3954a76`, and tree
  `8fd66cb7131f41921c8b05b738726c69cb20bbd8`.
- That snapshot was clean and its product/test diff SHA-256 was
  `1f8aaac593571411bb4afcafb36b65ef90d02164c59895668ae14e8ce70994f7`.
- Preserved validation evidence SHA-256 values are:
  - projection receipt:
    `0c9aed81a088952787dbf6488418686cbb374778f159628282a81c3a02af9a2a`;
  - full log:
    `12e4e532539d863877f2cd605c6e7c2c2baa8b4b2d29bc498e534223f1f46e42`;
  - full-suite receipt:
    `5666b6c5008f3d696a8993b4332ad3aeca3b420eadc0f566a5b13c54755e619a`.
- The prior Exact-final was discarded and inadmissible, with disposition
  `NOT YET`. Its isolation waiver does not carry into this release candidate.
- Packaging changes below invalidate the prior candidate freeze. Before a
  release can proceed, this plan must return to working evidence, the complete
  candidate must be projected into a fresh clean snapshot, and Root must make
  a fresh freeze followed by one fresh technically read-only Exact-final.

## Preservation boundary

The exact future product/test paths are:

1. `.codex-plugin/plugin.json`
2. `README.md`
3. `README.en.md`
4. `skills/happycodex/SKILL.md`
5. `skills/happycodex/references/execplan.md`
6. `tests/test_attestation_contract.py`

The existing closed control
`docs/execplans/happycodex-0-7-1-native-parallel-exploration.md` is retained
unchanged as a control and is included in the future candidate commit. This
release plan remains untracked until the later readiness commit.

Every other repository path, the evaluator, the exact published `v0.6.5`
tree, external role configuration, active install, cache, rollback state, and
unrelated claims are preserved. Evaluator files remain maintenance support and
must not be linked from `skills/happycodex/SKILL.md`.

This bootstrap grants no product, test, README, reference, manifest, index,
commit, ref, snapshot, test, install, cachebuster, sync, note, Exact-final,
push, tag, GitHub Release, cleanup, or network-write effect.

## Eight-resource claim

- Helper: `skills/happycodex/scripts/resource_claim.py`.
- Owner: `/root/native_parallel_explorer_executor`.
- Task: `HC-0.7.1-RELEASE-001`.
- Receipt:
  `/home/caichenghang/.codex/happycodex-0.7.1-release-HC-RL-001.claim.json`.
- Receipt mode: `0600`; size: 3353 bytes; SHA-256:
  `1b6abf5363bf14468fe8a42dceb66ce3a92fef806d5f0c0b198fadb24e41c6a5`.
- Acquisition exit `0`; immediate verification exit `0`; resource count `8`.
- The raw owner token exists only in the mode-0600 receipt. Its SHA-256 is
  `40c10ab3884b1bb2f77c05d4a246d01ed3b6c51faaa40dd29609b82b6892cf42`;
  the token itself is deliberately not copied here.

| Resource | Claim SHA-256 |
| --- | --- |
| `output=/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.jsonl` | `fff0e9f4074afbccc07645a46c106e3065e4436893a652ce1a7a7c45e634b967` |
| `output=/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.md` | `b8eb5605f206ac3f132c16f4832bc0f2700a2503bc6e4575d5f2b2055c68cdc5` |
| `output=/home/caichenghang/.codex/happycodex-v0.7.1-release-notes.md` | `c97c3a0d84f2da1a527f94f17776a7b14337f4f0748bb2c51b061246b651eeee` |
| `activation=/home/caichenghang/.codex/plugins/cache/personal/happycodex` | `5d3a35638bb0814980499d83e74f2709d2f704fd6371ca49ac193059075814f9` |
| `activation=/home/caichenghang/plugins/happycodex` | `0375ae9a4fac6457086c5857627829fcc75367e0e67eee94d56afa78169f7303` |
| `worktree=/home/caichenghang/projects/happycodex` | `74804b4016d6815545a9a47dd74141854e6f42dbd61e424c9df84b19b33a1594` |
| `ref=/home/caichenghang/projects/happycodex::refs/heads/main` | `e55785d8fbef19bf9770f6a41392679affdda95222932d2aff9f927df0a060ed` |
| `ref=/home/caichenghang/projects/happycodex::refs/tags/v0.7.1` | `2f5bf31f19fbbec17acd0bab6c93e9cc7ec0714fbc82b16c6620414fd07e3bc8` |

The claims remain active until the final closeout grant. No later row may
silently widen, replace, or reacquire them. Any owner/task/token mismatch,
missing claim, conflict, or ambiguous effect stops without retry and returns
to Root.

## External and installation prestate

- These exact claimed output destinations were absent:
  - `/home/caichenghang/.codex/happycodex-v0.7.1-release-notes.md`;
  - `/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.jsonl`;
  - `/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.md`.
- Existing Root preflight captures are preserved, read-only evidence and are
  excluded from all later output destinations:
  - `/tmp/hc-v071-release-preflight.json`: mode `0600`, 0 bytes, SHA-256
    `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
  - `/tmp/hc-v071-release-preflight.err`: mode `0600`, 18 bytes, SHA-256
    `aa56bfab6b7096304f143a40473cd7c045c3becda99f0f5178a308562f423d1a`.
- Before bootstrap, the shared claim store had 20 unrelated claims. Its
  aggregate relative-path-plus-claim-SHA digest was
  `2147aecaf2281ef52c4a050bfb8cf1d36e2cd3c2772cdf8f207ec5cf1c3b92e2`.
  Those claims are unrelated and must remain untouched.
- `happycodex@personal` was installed and enabled from marketplace `personal`
  at version `0.7.0+codex.20260805092118`, sourced from
  `/home/caichenghang/plugins/happycodex`.
- The cache root was
  `/home/caichenghang/.codex/plugins/cache/personal/happycodex`, with sole
  version directory `0.7.0+codex.20260805092118`.
- Source and cache had the same eight package files. Cache additionally had
  runtime-only
  `skills/happycodex/scripts/__pycache__/resource_claim.cpython-310.pyc`.
  This is preserved prestate, not package content and not cleanup authority.
- Exact eight-file package inventory:
  `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`,
  `README.en.md`, `README.md`, `skills/happycodex/SKILL.md`,
  `skills/happycodex/agents/openai.yaml`,
  `skills/happycodex/references/execplan.md`, and
  `skills/happycodex/scripts/resource_claim.py`.
- Personal marketplace SHA-256:
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`.
- Codex config SHA-256:
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
- Official cachebuster helper:
  `/home/caichenghang/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py`,
  SHA-256
  `4fe3c5a49212f6e30a2306e245c460e01aaf5e36bc8ad3dd2852c199257eff89`.

## Release-surface design

The later release-surface implementation is bounded to the six exact
product/test paths above and must establish all of the following, without a
new scheduler, engine, gate family, dependency, profile bundle, or evaluator
surface:

- `.codex-plugin/plugin.json` reports version `0.7.1`.
- Both READMEs and the product ExecPlan reference state that for two or more
  qualifying independent decision-changing axes, Root concurrently dispatches
  one native Explorer per axis through the host builtin `explorer` selector or
  an admitted namespaced custom Explorer selector.
- Both READMEs and the product ExecPlan state that ordinary parallel tool calls
  are not Explorer dispatches.
- The existing routing-admission constraints and one-writer rule remain
  intact.
- Contract tests assert version `0.7.1` and exact public/reference consistency
  for the native-Explorer semantics.

## Obligations

| ID | Observable obligation | Admission evidence | State |
| --- | --- | --- | --- |
| `RL-SURFACE` | Only the six frozen product/test paths implement the exact 0.7.1 public contract. | RED, exact diff, file hashes, contract assertions. | pending |
| `RL-PRESERVE` | Published 0.6.5 tree, evaluator, roles, unrelated paths/config/claims, and rollback state remain unchanged. | Git/object hashes, inventories, external hashes. | pending |
| `RL-VALIDATE` | Focused tests and validators pass; one clean snapshot full suite retains exactly 159 tests, 2 known failures, 0 errors, and 0 new failures. | Command receipts and snapshot projection identity. | pending |
| `RL-FREEZE` | Root freezes the complete candidate after packaging changes. | Exact artifact/path/hash inventory and Root disposition. | pending |
| `RL-EXACT` | One fresh technically read-only neutral Exact-final returns admissible `GO`. | Claimed JSONL/Markdown outputs and invocation receipt. | pending |
| `RL-COMMIT` | Candidate and readiness commits contain exactly their planned inventories. | Commit/tree identities and clean-index receipts. | pending |
| `RL-ACTIVATE` | Personal source/cache resolve to one 0.7.1 cachebuster package using the official helper once. | Package inventory/hash diff and plugin CLI receipt. | pending |
| `RL-PUBLISH` | One main push, one annotated tag/push, and one public GitHub Release target the admitted commit. | Remote ref and release API receipts. | pending |
| `RL-CLOSE` | Plan-only closeout commit is pushed and the original eight claims plus the adverse-repair output claim are released exactly once. | Closeout commit/remote identity and both release receipts. | pending |

## Separately gated future grants

The order is fixed. Each row requires a new exact Root grant after the prior
row's terminal receipt. A row authorizes no effect from any later row.

| Order | Future grant | Exact bounded effect and terminal condition |
| --- | --- | --- |
| 1 | `HC-0.7.1-RELEASE-SURFACES-002` | Persist RED assertions, implement only the six frozen product/test paths, run focused offline checks and validators, create one fresh recoverable clean snapshot, project the complete candidate, and run the full offline suite exactly once with its hard timeout. Stop on any unexpected identity, new failure/error, timeout, partial effect, or need to retry. |
| 2 | `HC-0.7.1-FREEZE-003` | Root alone reviews exact inventory/identity/evidence and either freezes the complete candidate or stops. No mutation. |
| 3 | `HC-0.7.1-EXACT-FINAL-004` | Make exactly one separate one-shot `codex exec` invocation using `gpt-5.6-sol` at `max`, effective `--sandbox read-only`, approval `never`, empty history, neutral brief, plugins disabled, and the clean snapshot. Write only the two claimed Exact-final outputs. No retry; ambiguous/partial/provider effects stop. |
| 4 | `HC-0.7.1-CANDIDATE-COMMIT-005` | If and only if fresh Exact-final is admissible `GO`, stage exactly the six product/test paths plus the unchanged closed native-parallel control and create one commit with subject `feat: release HappyCodex 0.7.1 native parallel exploration`. Keep this release plan untracked. |
| 5 | `HC-0.7.1-PERSONAL-ACTIVATION-006` | Synchronize exactly the eight package files to the claimed personal source, keep base manifest semver `0.7.1`, invoke the official default-timestamp cachebuster helper exactly once, then invoke `codex plugin add happycodex@personal` exactly once. Do not hand-edit marketplace/config/cache. Preserve and report any partial effect; do not retry. A new thread is required to consume the activated plugin. |
| 6 | `HC-0.7.1-READINESS-COMMIT-007` | Write the exact claimed release-notes destination, update only this plan with readiness receipts, then stage exactly those two paths and create one commit with subject `docs: record HappyCodex 0.7.1 release readiness`. |
| 7 | `HC-0.7.1-MAIN-PUSH-008` | Push `main` to `origin` exactly once after proving expected local/remote identities. No force and no retry after ambiguous/partial effect. |
| 8 | `HC-0.7.1-TAG-009` | Create one annotated `v0.7.1` tag with message `HappyCodex 0.7.1` at the admitted readiness commit, then push that tag exactly once. Stop if local or remote tag exists or identities drift. |
| 9 | `HC-0.7.1-GITHUB-RELEASE-010` | Create exactly one public, non-draft, non-prerelease GitHub Release `v0.7.1`, title `HappyCodex 0.7.1`, from the exact frozen notes, with no assets. Stop if a release already exists or the effect is ambiguous. |
| 10 | `HC-0.7.1-CLOSEOUT-011` | Update only this plan to `closed` with complete receipts, create one plan-only commit with subject `docs: close HappyCodex 0.7.1 release`, push `main` exactly once, verify remote/tag/release/activation state, then release the original eight claims and the one adverse-repair output claim exactly once. Root alone decides completion. |

## Validation and Exact-final rules

- All repository validation is offline standard-library validation. No later
  test grant implies network/model/install/release authority.
- The fresh snapshot must start from the exact source commit, contain only the
  mechanically projected complete candidate, prove byte/mode/path equality,
  and receive one fixed-identity unsigned local validation commit.
- Focused contract tests, existing Skill validator, existing plugin validator,
  and `git diff --check` must pass.
- The full suite is not represented as green: acceptance is exactly 159 tests,
  exactly the two already recorded baseline failures, zero errors, and zero
  new failure/error identities under the hard timeout. One attempt only.
- The Exact-final provider invocation is one-shot. Only a proven
  pre-provider infrastructure no-effect terminal may be considered for
  recovery, and only under a later exact Root recovery grant and cap.
- Expected answers, hidden boundaries, matcher/oracle content, desired
  verdicts, and prior review prose are excluded from provider input. The
  reviewer receives immutable candidate/evidence identity and a neutral task.
- An adverse attestation is durable for unchanged artifact bytes. A friendlier
  rerun is inadmissible. Product mutation requires a new freeze and Exact-final.

## Frozen release-note content

The later notes grant may write the following body, with validation and
Exact-final statements admitted only after their evidence exists:

```markdown
# HappyCodex 0.7.1

This is a reviewed source release, not a maintainer-evaluator certification.

## Highlights

- For two or more qualifying independent decision-changing axes, Root
  concurrently dispatches one native Explorer per axis through the host
  builtin `explorer` selector or an admitted namespaced custom Explorer.
- Ordinary parallel tool calls are not Explorer dispatches.
- Existing routing admission and the one-writer rule remain intact.

## Validation

- Focused contract checks and existing Skill/plugin validators passed.
- The full offline suite ran 159 tests with exactly the two known baseline
  failures, zero errors, and zero new failures.
- A fresh technically read-only neutral Exact-final returned `GO`.

## Install

`codex plugin add happycodex@personal`
```

## Stop rules

- Identity/config/claim drift, an unexpected dirty/staged path, a changed
  published 0.6.5 tree, an unexpected test identity, non-`GO` Exact-final,
  mismatched active package, or unexpected remote state stops and returns to
  Root.
- Never infer authority from a previous row, the user's broad release phrase,
  an authenticated CLI, a clean check, or an existing claim.
- Never widen scope, repair an unlisted surface, retry an ambiguous effect,
  overwrite an existing tag/release/output, force-push, or clean preserved
  evidence.
- Partial effects are recorded exactly and returned to Root. They are not
  silently retried, rolled back, or declared complete.
- Root alone may change this phase, admit Exact-final, decide release
  completion, or authorize claim release.

## Bootstrap receipt

- The eight claims were acquired once and immediately verified with exit `0`.
- The receipt identity, claim identities, verified prestate, preservation
  boundary, future grants, budgets, order, and stop rules were persisted before
  any later release mutation.
- No product, test, README, reference, manifest, index, commit, ref, snapshot,
  test, install, cachebuster, sync, release-note, Exact-final, push, tag,
  GitHub Release, cleanup, or network-write effect occurred under this grant.
- Initial persisted plan SHA-256 before this receipt:
  `9a88b028c243e0d622374042d921e93b758b59f576154b866d5a76947f30a496`.
- Post-write claim verification exited `0`; owner/task/token and all eight
  resource identities remained verified. Raw verification output was
  suppressed so the owner token was not exposed.
- Exact final bootstrap worktree inventory is the two pre-existing modified
  product/test paths plus the pre-existing closed untracked control and this
  new untracked plan. The index remains empty; branch/upstream remain
  `main...origin/main`.
- HEAD, HEAD tree, published 0.6.5 Skill tree, all three pre-existing candidate
  hashes, and the tracked product/test diff hash exactly match the verified
  prestate above.
- All three claimed output destinations remain absent. The preserved snapshot
  remains clean. Personal source/cache manifests both remain SHA-256
  `b9e88590c77ae92aa6c3180a15b21e4c7095c5ce8a7d9a37ae284273b8c8a2bc`;
  marketplace and Codex config hashes exactly match the prestate above.
- No product, test, README, reference, manifest, index, commit, ref, snapshot,
  test, install, cachebuster, sync, release-note, Exact-final, push, tag,
  GitHub Release, cleanup, or network-write effect occurred under this grant.
  The eight claims remain active. Phase remains `working`; no next phase is
  authorized.

## Release-surface terminal receipt

### Grant and preflight

- Exact grant: `HC-0.7.1-RELEASE-SURFACES-002`; fixed Executor remained
  `/root/native_parallel_explorer_executor`. No Goal was created.
- Before the first test mutation, all eight claims reverified with exit `0`.
  HEAD, HEAD tree, `origin/main`, the empty index, published 0.6.5 Skill tree,
  bootstrap candidate/control hashes, output absence, local/remote tag absence,
  and GitHub Release absence exactly matched the bootstrap prestate. Live
  remote `main` remained
  `39a37b5e5bc497ac629a8e185309698905242e9c`.
- Closed control
  `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md` remained
  byte-for-byte unchanged at SHA-256
  `59c3b81bd4b7427246c713479230c1e17136c5b91ddee40bde857c690d629733`.

### Test-first and implementation receipts

- Test-first mutation changed only `tests/test_attestation_contract.py`: base
  candidate version became exactly `0.7.1`; the existing Skill assertions were
  preserved; common exact public/reference assertions were added for:
  - `For two or more qualifying independent decision-changing axes, Root concurrently dispatches one native Explorer per axis through the host's builtin \`explorer\` selector or an admitted namespaced custom Explorer selector`;
  - `Ordinary parallel tool calls are not Explorer dispatches`.
- The one focused RED command was
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_attestation_contract.RepositoryContractTests.test_v070_role_routing_contract_is_complete_and_fail_closed`.
  It exited `1`; one test ran in 0.001 seconds with exactly one failure and no
  import, syntax, or unrelated error. The exact reached identity was
  `AssertionError: '0.7.0' != '0.7.1'` at
  `tests/test_attestation_contract.py:95`. Because this first normal assertion
  terminated the method, the later public/reference assertions were present
  but not reached during RED; no broader RED claim is made.
- Implementation changed only the manifest, both READMEs, and product ExecPlan
  reference. It set manifest base version `0.7.1`, installed the exact common
  native-Explorer rule and ordinary-tool exclusion in all three public/reference
  surfaces, retained routing admission and one-writer semantics, and added no
  scheduler, engine, gate family, dependency, profile bundle, evaluator
  surface, or evaluator link. The pre-existing Skill candidate bytes required
  no consistency change and remained unchanged.
- The first post-implementation focused run exited `1` only because the edit
  had removed the older exact limiting sentence `Multiple Explorers run
  concurrently only when multiple such axes exist` from `README.en.md`; the
  assertion failed at `tests/test_attestation_contract.py:200`. The official
  Skill validator, official plugin validator, and `git diff --check` already
  exited `0`. One attempted repair patch failed its context precondition and
  changed no bytes. The bounded repair then restored the English limiting
  sentence and its Chinese counterpart without weakening the new mandatory
  rule.
- Final source checks on final bytes:
  - focused command above: exit `0`; one test in 0.001 seconds; `OK`;
  - `PYTHONDONTWRITEBYTECODE=1 python3 /home/caichenghang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/happycodex`:
    exit `0`, `Skill is valid!`;
  - `PYTHONDONTWRITEBYTECODE=1 python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`:
    exit `0`, plugin validation passed;
  - `git diff --check`: exit `0`, no output.
- No full suite ran in the source worktree.

### Final product/test identity

| Path | SHA-256 |
| --- | --- |
| `.codex-plugin/plugin.json` | `25537add122ca939dfc19c3cc9485b3dbcd1a3c8169c73680fad2a33d7a20c89` |
| `README.md` | `066842b78ef6835a9852d7a67b8eb59f6c229b979ccc07ba556d2925b46dd013` |
| `README.en.md` | `c5712a748e68095009d50f72add7e135e8627d5a3c68aad47d43d5e22bd6a9a4` |
| `skills/happycodex/SKILL.md` | `cca9df6187f16e3b4fcbc6b9f78883a26a5c779b525b723c2af2d732a4951342` |
| `skills/happycodex/references/execplan.md` | `6da8800d4c7b71ea0a319829fd7be37762786d2c91d9faa3b5bb95110219128f` |
| `tests/test_attestation_contract.py` | `d4e4bd8c8fa3c1ec53a051c3b2768d2f5ace426f840737cbc1deffb587de8904` |

- The six-path binary full-index product/test diff SHA-256 against exact HEAD
  is `6858586231371d9fc308e7666fa8e33875f962b538623fe18f31f5bef7459f3d`.
  Its inventory is exactly the six frozen paths; there is no omitted or extra
  product/test path.
- This plan's SHA-256 when projected, before this terminal receipt, was
  `0f35c1284484bc548dcb1fb6431d947c8a3b9956e72eab6a742144ebf724031c`.

### Clean snapshot and validation commit

- Exactly one new recoverable parent was created with the authorized template:
  `/tmp/happycodex-0-7-1-release.0VkwGc`.
- Its local no-network snapshot is
  `/tmp/happycodex-0-7-1-release.0VkwGc/repo`, cloned from exact source HEAD
  `39a37b5e5bc497ac629a8e185309698905242e9c`, source tree
  `f54bc2a7ebc92951177a7412426a1043b17673da`.
- Before projection it was detached, clean, and index-empty. Exactly the six
  frozen product/test paths plus the unchanged closed control and this working
  release plan were projected. Every source/snapshot byte and filesystem mode
  matched; observed filesystem mode was `0600` for all eight paths. The Git
  tree records all eight as `100644`.
- Exactly one fixed-identity unsigned local validation commit was created:
  - commit: `4f68ed8163769948b1a3c9a1a6ab103aed7d76e3`;
  - tree: `3c3f3ae3c9f0fd38b194ff1448ca727d690e9edc`;
  - parent: `39a37b5e5bc497ac629a8e185309698905242e9c`;
  - author/committer: `HappyCodex Validation
    <happycodex-validation@invalid>`;
  - author/committer date: `2026-08-05T00:00:00+00:00`;
  - subject: `validation: project HappyCodex 0.7.1 release surfaces`;
  - signing and hooks disabled for this local evidence commit.
- The complete eight-path projection diff SHA-256 is
  `5defa23c91a08b5caf30b9934ec1e781fd249dff09f914edbace096af59cb64b`;
  the product/test-only projection is the same
  `6858586231371d9fc308e7666fa8e33875f962b538623fe18f31f5bef7459f3d`
  recorded above. The snapshot remained clean and its published 0.6.5 Skill
  tree remained `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.

### Snapshot checks and sole full-suite attempt

- Snapshot focused contract test: exit `0`; one test in 0.001 seconds; `OK`.
- Snapshot official Skill validator: exit `0`, `Skill is valid!`.
- Snapshot official plugin validator: exit `0`, plugin validation passed.
- Snapshot `git diff --check HEAD^..HEAD`: exit `0`, no output.
- The complete offline suite ran exactly once, only in the snapshot, with hard
  cap command:
  `PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'HC_ELAPSED_SECONDS=%e' timeout --signal=KILL 120s python3 -m unittest discover -s tests -p 'test_*.py' -v`.
- Result: exit `1`; not timed out; 159 tests in 70.011 test seconds and 70.11
  command seconds; exactly 2 failures, 0 errors, and 0 new failures. This suite
  is not green. The exact baseline-unchanged identities were:
  - `test_exact_final_source_rejects_self_selected_projection_and_fake_diff (test_fixed_host_transaction_v2.FixedHostTransactionTests) (mutation='old-source')`:
    `AssertionError: ProviderError not raised` at
    `tests/test_fixed_host_transaction_v2.py:474`;
  - `test_old_source_components_cannot_back_a_new_dirty_evalspec (test_fixed_host_transaction_v2.FixedHostTransactionTests)`:
    `AssertionError: authority accepted`, reached through
    `evaluation/host.py:459` and
    `tests/test_fixed_host_transaction_v2.py:625`.
- Preserved full log:
  `/tmp/happycodex-0-7-1-release.0VkwGc/full-suite.log`, mode `0600`, 64,283
  bytes, 1,481 lines, SHA-256
  `76303c4556dd50eb4b0f72fe0ff3673d400adab0d9ff7fbda455d2c883ab68f9`.
- Machine-readable receipt:
  `/tmp/happycodex-0-7-1-release.0VkwGc/full-suite.receipt.json`, mode `0600`,
  1,492 bytes, SHA-256
  `8c27e10407e2bfea6ac6950f3ecdb70ff9a4540094e036b7cd54fe05c5f80900`.
  JSON validation exited `0`; it records attempt count `1` and no retry.

### Terminal preservation and disposition

- Immediately before this terminal receipt, all eight claims reverified with
  exit `0`; source HEAD/tree/upstream and empty index were unchanged; the source
  six-path diff exactly matched the snapshot projection; the snapshot remained
  clean; all three claimed outputs remained absent; and personal source/cache,
  marketplace, and Codex config identities remained at bootstrap values.
- No source stage/commit, notes or Exact-final output, provider/model call,
  personal source/cache/config/marketplace edit, install/cachebuster, local or
  remote ref mutation, network write, push, tag, GitHub Release, cleanup, or
  full-suite retry occurred.
- `RL-SURFACE`, `RL-PRESERVE`, and `RL-VALIDATE` now have this phase's evidence;
  Root retains admission and freeze decisions. Phase remains `working`. The
  next row, `HC-0.7.1-FREEZE-003`, requires a new exact Root grant; this receipt
  authorizes no next-phase effect. The eight claims remain active.

## Adverse Exact-final and repair amendment

### Adverse output receipt

- Root froze candidate commit
  `4f68ed8163769948b1a3c9a1a6ab103aed7d76e3`, tree
  `3c3f3ae3c9f0fd38b194ff1448ca727d690e9edc`, parent
  `39a37b5e5bc497ac629a8e185309698905242e9c`, and six-path product/test diff
  SHA-256
  `6858586231371d9fc308e7666fa8e33875f962b538623fe18f31f5bef7459f3d`
  under `HC-0.7.1-FREEZE-003`.
- `HC-0.7.1-EXACT-FINAL-004` made exactly one provider invocation and no
  retry. The process exited `0`; its session ID is
  `019fd229-770c-7591-b8b3-27d94c43d3d7`.
- The original adverse outputs are permanent immutable evidence and must never
  be overwritten, deleted, relabeled, or used as destinations for a later
  review:
  - `/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.jsonl`: mode
    `0600`, 383,055 bytes, 55 JSONL events, SHA-256
    `afb86219b80adc3ea87cf1d499d6d352461e8cd3ca45aff9992cdf2f8a3a9546`;
  - `/home/caichenghang/.codex/happycodex-v0.7.1-exact-final.md`: mode `0600`,
    2,406 bytes, SHA-256
    `b0d4433de9923d38e02a218a2e92cc20dcf56a41f1af3fbf547eefedc9b1b90f`.
- JSONL parsed completely, contained exactly one `thread.started`, one
  `turn.started`, one terminal `turn.completed`, and no `error` event. Its last
  agent message exactly matched the Markdown bytes. The Markdown first line is
  exactly `NOT YET`.
- The invocation requested `gpt-5.6-sol` at `max`, CLI sandbox `read-only`,
  approval `never`, ephemeral state, ignored user config, and disabled plugins.
  Runtime JSONL exposed the session and usage but no runtime-issued effective
  model, effort, sandbox, or approval fields. Effective technical isolation was
  therefore not independently proven. No review is admitted as a passing
  Exact-final, and no release gate may consume this verdict as `GO`.
- Preserve the adverse finding: the frozen closed native-parallel control
  contains two raw resource-claim capability tokens although product safety
  requires digest-only control records. Root independently reproduced the
  defect without relying on the model's conclusion. The evidence limitation
  about the missing companion baseline log/receipt is retained as low severity
  and is not an additional product behavior defect.

### Historical claim disposition

- Historical receipt
  `/tmp/happycodex-0-7-1-native-parallel-explorer.claim.json` has owner-token
  SHA-256
  `7b298a823a9224e8a9c8b61984c7d32c90431dd25e63372eb22b12e3c1f366b9`.
  Current verification exited `2` and failed closed with exact reason
  `claim identity mismatch: fs:/home/caichenghang/projects/happycodex`.
- Historical receipt
  `/tmp/happycodex-0-7-1-waiver-closeout.claim.json` has owner-token SHA-256
  `aa5f3b7e696f9f96bd8f80f8aa81a7bd00becb42596cec1c3a5654f5b142fa6c`.
  Current verification exited `2` and failed closed with the same exact reason
  `claim identity mismatch: fs:/home/caichenghang/projects/happycodex`.
- Neither historical token controls the current worktree claim. The current
  worktree claim remains one of the verified original eight release claims.
  No active-token rotation is needed or authorized, and no rotation effect
  occurred. No raw token is copied into this plan.

### Repair-output resource amendment

- Exact amendment/grant: `HC-0.7.1-ADVERSE-REPAIR-CLAIMS-012`. It supersedes
  only the former no-widen sentence for this one resource:
  `output=/home/caichenghang/.codex/happycodex-v0.7.1-repair-exact-final`.
- Before acquisition, both the output directory and receipt were absent.
- Receipt:
  `/home/caichenghang/.codex/happycodex-0.7.1-repair-HC-RL-012.claim.json`;
  mode `0600`; 692 bytes; SHA-256
  `51ffe37b8b388577574db7f9e5cdee48bfa5bbad0d1a56707a64ce271393eac3`.
- Owner: `/root/native_parallel_explorer_executor`; task:
  `HC-0.7.1-ADVERSE-REPAIR-CLAIMS-012`; ExecPlan: this file; resource count:
  `1`.
- Canonical key:
  `fs:/home/caichenghang/.codex/happycodex-v0.7.1-repair-exact-final`;
  claim SHA-256:
  `1ce4e473bf81541151a8ed8731c34eafb5f1e5286859a13ed74ab7a48df77ccb`.
- Acquisition exited `0`; immediate verification exited `0`. The raw owner
  token remains only in the mode-0600 receipt and is not recorded here. The
  claimed output directory remains absent. The original eight claims remain
  active, producing nine active release-line claims in total.

### Invalidated freeze and future minimal repair

- The freeze at commit `4f68ed8163769948b1a3c9a1a6ab103aed7d76e3` /
  tree `3c3f3ae3c9f0fd38b194ff1448ca727d690e9edc` is invalidated by the
  reproduced defect. It remains immutable evidence but is not a releasable
  candidate. Phase is `working`.
- The authorized future repair boundary is minimal:
  `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md` may replace
  only the two raw historical owner-token values with their matching SHA-256
  digests above and correct the adjacent stale active-claim descriptions;
  `tests/test_attestation_contract.py` may add one regression assertion that
  the closed control contains no raw owner-token field/value and records only
  digest-qualified owner-token evidence. It must not embed either raw token.
- Every other product/test byte remains frozen at the release-surface identity.
  The repair may not broaden behavior, change evaluator/product semantics,
  rotate a claim, or rewrite the permanent adverse outputs. Execution of the
  two-path repair requires a new exact Root grant; this amendment performs no
  redaction or test mutation.
- After repair, create exactly one fresh recoverable clean snapshot, prove the
  complete changed-path projection and immutable 0.6.5 tree, run focused checks
  and validators, then run the full offline stdlib suite exactly once with the
  same 120-second hard cap. Acceptance remains exactly 159 tests, the same two
  baseline failures, zero errors, and zero new failures; it is not green.
- Root must then issue a new freeze for the changed bytes and a separate exact
  authority for exactly one new neutral Exact-final. The old adverse review
  cannot be rerun or made friendlier for unchanged bytes.

### Outer-bwrap hard-isolation design

- A future Exact-final grant may create the claimed repair-output directory
  once at mode `0700` and place only the new JSONL, final Markdown, and exact
  invocation receipt beneath it. The original adverse destinations remain
  immutable and outside this writable bind.
- Launch the one-shot `codex exec` inside an outer `bwrap` namespace with
  `--die-with-parent`, `--new-session`, PID/IPC/UTS isolation, a read-only bind
  of `/`, a private tmpfs `/tmp`, the frozen repair snapshot read-only at
  `/review`, its validation log/receipt read-only at `/evidence`, and only the
  claimed repair-output directory writable at `/output`. Do not unshare the
  network namespace because the authorized provider call requires network.
  No other host path may be writable in the namespace.
- Before the provider starts, a no-provider probe in the identical mount
  topology must record `/proc/self/mountinfo`, prove writes to `/review`, source,
  config, marketplace, plugin source/cache, and original adverse-output paths
  fail with no effect, and prove only `/output` plus private ephemeral mounts
  are writable. Any mismatch stops before provider effect.
- Inside that outer boundary, retain the exact ignored-user-config,
  plugins-disabled, ephemeral `gpt-5.6-sol/max`, CLI `read-only`, approval
  `never`, neutral-brief, JSONL, final-message, and hard wall-cap requirements.
  Record the exact command, outer mount receipt, process exit, thread/event
  terminal shape, output identities, and before/after protected-state hashes.
  One provider invocation only; no retry after any provider or ambiguous effect.
- A future review is admissible only if Root can prove the outer filesystem
  boundary independently of missing CLI runtime fields, the output is
  well-formed, and first-line verdict is exactly `GO`. Otherwise preserve it as
  adverse/ambiguous evidence and stop.

### Amendment terminal boundary

- Under `HC-0.7.1-ADVERSE-REPAIR-CLAIMS-012`, only the one additional resource
  claim and this plan amendment were created. No control redaction, product/test
  or closed-control edit, test, snapshot, repair-output directory, provider
  call, stage/commit, activation, notes, config/marketplace/cache edit, ref or
  network write, tag/push/GitHub Release, cleanup, claim rotation, or claim
  release occurred.
- Final closeout must verify and release both claim receipts: the original
  eight-resource release receipt and this one-resource adverse-repair receipt.
  Root alone admits the amendment, grants repair, freezes a new candidate, and
  decides completion.

## Adverse repair terminal receipt

### Grant, RED, and minimal repair

- Exact grant: `HC-0.7.1-ADVERSE-REPAIR-013`; fixed Executor remained
  `/root/native_parallel_explorer_executor`. Both the original eight-resource
  receipt and the one-resource adverse-repair receipt verified with exit `0`
  before mutation. No Goal was created.
- Prestate exactly matched the amendment: empty source index; unchanged
  HEAD/tree/upstream and published 0.6.5 Skill tree; six frozen product/test
  hashes; original adverse outputs; absent repair-output directory, notes,
  local/remote tag, and GitHub Release; unchanged personal plugin/config state.
- Test-first changed only the existing
  `RepositoryContractTests.test_v070_role_routing_contract_is_complete_and_fail_closed`
  method. It loads the closed native-parallel control and uses one compound
  assertion to require exactly the two approved digest-qualified
  `Owner-token SHA-256` values and zero raw `Owner token` labels followed by a
  64-hex capability value. No raw token is embedded; no test method was added.
- The one RED command was
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_attestation_contract.RepositoryContractTests.test_v070_role_routing_contract_is_complete_and_fail_closed`.
  It exited `1`; one test ran in 0.002 seconds with exactly one failure and no
  syntax, import, or unrelated error. The safe observed identity was an empty
  digest tuple and raw-owner-token count `2`, versus the two approved digests
  and count `0`.
- The closed control was minimally repaired via `apply_patch`: the two raw
  historical capability values and labels became their matching
  digest-qualified values, and only adjacent present-tense claim descriptions
  were corrected to say each claim was active at that historical checkpoint,
  now verifies with exit `2` and exact worktree claim-identity mismatch, and no
  longer controls the current claim. One initial `apply_patch` failed its
  context precondition and changed no bytes; the corrected bounded patch then
  applied. No other historical evidence, phase, waiver, product/test identity,
  or disposition was rewritten.

### Final source checks and identity

- Final source checks on final repair bytes:
  - focused role-routing test: exit `0`; one test in 0.002 seconds; `OK`;
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_attestation_contract`:
    exit `0`; 14 tests in 0.121 seconds; `OK`;
  - official Skill validator: exit `0`, `Skill is valid!`;
  - official plugin validator: exit `0`, plugin validation passed;
  - `git diff --check`: exit `0`, no output.
- No full suite ran in the source worktree. Total discovery remains 159 tests
  because the regression assertion is inside the existing test method.
- Repaired path SHA-256 values:
  - `tests/test_attestation_contract.py`:
    `1d3f1c6ee41624d3a5d65491d4f6afe007bbacab7cbd5f1a9b4362524f49611a`;
  - `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md`:
    `9318871730177259bc9988bce5b38a81d51fbbd667a486ea457d754e4bf65f10`.
- The other five release-surface product bytes remain exact:
  - `.codex-plugin/plugin.json`:
    `25537add122ca939dfc19c3cc9485b3dbcd1a3c8169c73680fad2a33d7a20c89`;
  - `README.md`:
    `066842b78ef6835a9852d7a67b8eb59f6c229b979ccc07ba556d2925b46dd013`;
  - `README.en.md`:
    `c5712a748e68095009d50f72add7e135e8627d5a3c68aad47d43d5e22bd6a9a4`;
  - `skills/happycodex/SKILL.md`:
    `cca9df6187f16e3b4fcbc6b9f78883a26a5c779b525b723c2af2d732a4951342`;
  - `skills/happycodex/references/execplan.md`:
    `6da8800d4c7b71ea0a319829fd7be37762786d2c91d9faa3b5bb95110219128f`.
- The repaired six-path binary full-index product/test diff SHA-256 against
  source HEAD is
  `a5480cbeabe0a10cd57119940d96208ddd7237d13255d91ee07788d527385732`.
  This plan's SHA-256 when projected, before this terminal receipt, was
  `ee84f321e5dc06db28f374fe8631b13cfb1ff095fc1e621745bc0d2ea0438a9f`.

### Repaired clean snapshot

- Exactly one recoverable parent was created:
  `/tmp/happycodex-0-7-1-repair.X5r42W`; its local no-network snapshot is
  `/tmp/happycodex-0-7-1-repair.X5r42W/repo`.
- The snapshot began detached and clean at exact source HEAD
  `39a37b5e5bc497ac629a8e185309698905242e9c`, tree
  `f54bc2a7ebc92951177a7412426a1043b17673da`. Exactly the six product/test
  paths, repaired closed control, and current working release plan were
  projected. Every source/snapshot path, byte, and filesystem mode matched;
  filesystem mode was `0600` for all eight paths and Git tree mode is `100644`.
- Exactly one fixed-identity unsigned local validation commit was created:
  - commit: `1144515b23b760a6d91f86ca0a7c2911ad0fa53b`;
  - tree: `2f6857f30b5c0a4a68c0b245a34de3a02cd5c7ca`;
  - parent: `39a37b5e5bc497ac629a8e185309698905242e9c`;
  - author/committer: `HappyCodex Validation
    <happycodex-validation@invalid>`;
  - author/committer date: `2026-08-05T01:00:00+00:00`;
  - subject: `validation: project HappyCodex 0.7.1 repaired candidate`;
  - signing and hooks disabled for this local evidence commit.
- The complete eight-path binary full-index projection diff SHA-256 is
  `d88619017b90ce4112e5ac184d49ccabe01a4ce1f97466e2aaa80a8a40be9e3c`;
  the product/test-only projection is the same
  `a5480cbeabe0a10cd57119940d96208ddd7237d13255d91ee07788d527385732`
  recorded above. Inventory is exactly six modified product/test paths and two
  added controls; no omitted or extra path exists. The snapshot remained clean
  and `v0.6.5:skills/happycodex` remained
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.

### Repaired snapshot checks and sole full-suite attempt

- Snapshot contract module: exit `0`; 14 tests in 0.119 seconds; `OK`.
- Snapshot official Skill validator: exit `0`, `Skill is valid!`.
- Snapshot official plugin validator: exit `0`, plugin validation passed.
- Snapshot `git diff --check HEAD^..HEAD`: exit `0`, no output.
- The complete offline suite ran exactly once, only in the repaired snapshot,
  with hard-cap command
  `PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'HC_ELAPSED_SECONDS=%e' timeout --signal=KILL 120s python3 -m unittest discover -s tests -p 'test_*.py' -v`.
- Result: exit `1`; not timed out; 159 tests in 70.693 test seconds and 70.80
  command seconds; exactly 2 failures, 0 errors, and 0 new failures. This suite
  is not green. The exact baseline-unchanged identities are:
  - `test_exact_final_source_rejects_self_selected_projection_and_fake_diff (test_fixed_host_transaction_v2.FixedHostTransactionTests) (mutation='old-source')`:
    `AssertionError: ProviderError not raised` at
    `tests/test_fixed_host_transaction_v2.py:474`;
  - `test_old_source_components_cannot_back_a_new_dirty_evalspec (test_fixed_host_transaction_v2.FixedHostTransactionTests)`:
    `AssertionError: authority accepted`, reached through
    `evaluation/host.py:459` and
    `tests/test_fixed_host_transaction_v2.py:625`.
- Full log:
  `/tmp/happycodex-0-7-1-repair.X5r42W/full-suite.log`, mode `0600`, 64,277
  bytes, 1,481 lines, SHA-256
  `d48c7d866d2533de4e4f294d89749828177267113db75adbe1275f141315c3da`.
- Machine receipt:
  `/tmp/happycodex-0-7-1-repair.X5r42W/full-suite.receipt.json`, mode `0600`,
  1,487 bytes, SHA-256
  `f42ecfbd8b14468f6c27e9828d9fd9ca65735de792e15ef0ba086793088a1bad`.
  JSON validation exited `0`; attempt count is `1` and no retry occurred.

### Terminal preservation and disposition

- Immediately before this receipt, both active claim receipts reverified with
  exit `0`; source HEAD/tree/upstream and empty index were unchanged; source and
  snapshot product/test diffs matched; the repaired snapshot remained clean;
  repair-output directory and release notes remained absent.
- Permanent adverse outputs remain byte-for-byte unchanged:
  - JSONL SHA-256
    `afb86219b80adc3ea87cf1d499d6d352461e8cd3ca45aff9992cdf2f8a3a9546`;
  - Markdown SHA-256
    `b0d4433de9923d38e02a218a2e92cc20dcf56a41f1af3fbf547eefedc9b1b90f`,
    first line `NOT YET`.
- No repair-output directory, provider/model call, adverse-output overwrite or
  deletion, source stage/commit, activation/install/cachebuster, notes,
  config/marketplace/cache edit, local/remote ref or network mutation,
  push/tag/GitHub Release, cleanup, rotation, claim release, or full-suite retry
  occurred.
- Phase remains `working`. Root retains new-freeze and fresh Exact-final
  authority and admission. This receipt authorizes no next-phase effect; all
  nine claims remain active.

## Repaired Exact-final hard-isolation terminal receipt

- Terminal verdict: `NOT YET`. The first bubblewrap attempt failed
  pre-provider because `/review` could not be created under a read-only root.
  The one authorized recovery entered the corrected private-`/tmp` namespace,
  and all seven completed mount checks passed, but it stopped pre-provider on
  the stale granted marketplace path
  `/home/caichenghang/.codex/plugins/marketplaces/personal/marketplace.json`,
  which is absent. The live marketplace is
  `/home/caichenghang/.agents/plugins/marketplace.json`, SHA-256
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`.
- Total bubblewrap invocations were `2`, including `1` recovery invocation.
  Provider invocations were `0`; provider transport was false; and network,
  provider, repository, test, release, install, stage, commit, activation, tag,
  push, GitHub Release, and claim-release effects were all false. Both active
  claim receipts remain active.
- The repaired Exact-final JSONL and Markdown outputs are absent. The output
  inventory is exactly `invocation-receipt.txt`: directory mode `0700`, receipt
  mode `0600`, receipt SHA-256
  `f9f63e02f9ea16b9805f4fd7c66afa68cd70fde98a04400250cdcceea3707d86`.
  The permanent adverse JSONL and Markdown remain preserved at SHA-256
  `afb86219b80adc3ea87cf1d499d6d352461e8cd3ca45aff9992cdf2f8a3a9546`
  and `b0d4433de9923d38e02a218a2e92cc20dcf56a41f1af3fbf547eefedc9b1b90f`.
- Protected candidate identity remains frozen commit
  `1144515b23b760a6d91f86ca0a7c2911ad0fa53b`, tree
  `2f6857f30b5c0a4a68c0b245a34de3a02cd5c7ca`, with preserved published
  `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`. Current repaired-suite log and
  receipt remain SHA-256
  `d48c7d866d2533de4e4f294d89749828177267113db75adbe1275f141315c3da`
  and `f42ecfbd8b14468f6c27e9828d9fd9ca65735de792e15ef0ba086793088a1bad`;
  companion baseline evidence remains
  `12e4e532539d863877f2cd605c6e7c2c2baa8b4b2d29bc498e534223f1f46e42`
  / `5666b6c5008f3d696a8993b4332ad3aeca3b420eadc0f566a5b13c54755e619a`,
  and prior evidence remains
  `76303c4556dd50eb4b0f72fe0ff3673d400adab0d9ff7fbda455d2c883ab68f9`
  / `8c27e10407e2bfea6ac6950f3ecdb70ff9a4540094e036b7cd54fe05c5f80900`.
- Phase remains `working`, and release remains blocked at the required
  Exact-final gate. The one authorized recovery is consumed; no further
  sandbox or provider attempt is authorized without a new explicit Root grant
  based on new user authority.

## User-authorized third Exact-final recovery amendment

Verbatim user amendment:

**授权第三次修正恢复，只修正 marketplace 路径并重新执行一次硬隔离 Exact-final。**

The amendment is UTF-8 length `107` bytes, SHA-256
`ba384f2e13e6125e0b897c504385b69e59b2cd22014cfdfbb99b09cee4a50048`.
It supersedes only the prior no-further-recovery stop line and authorizes
exactly one additional corrected pre-provider probe, followed only if every
probe succeeds by exactly one one-shot provider invocation for the unchanged
repaired frozen candidate.

- The sole script correction is the protected marketplace probe identity: use
  `/home/caichenghang/.agents/plugins/marketplace.json`, exact SHA-256
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`,
  instead of the absent stale path
  `/home/caichenghang/.codex/plugins/marketplaces/personal/marketplace.json`.
- Continue using the already-bound personal source
  `/home/caichenghang/plugins/happycodex` and the exact existing cache manifest
  under version `0.7.0+codex.20260805092118`. Do not infer either identity by
  joining the marketplace file directory to `./plugins/happycodex`.
- Candidate, evidence, topology, model and effort, sandbox and approval mode,
  neutral brief, output identities, caps other than this added single attempt,
  and downstream release authority do not change.
- Total allowed next bubblewrap count is exactly `1`. The provider invocation
  cap is exactly `1`, and applies only after every probe passes. There is no
  retry after any provider invocation, any ambiguous or partial effect, or any
  failure of this newly authorized attempt. A pre-provider failure stops and
  returns to Root.
- Phase remains `working`; the required Exact-final gate remains open. This
  amendment-recording grant itself authorizes no bubblewrap, sandbox, provider,
  test, output-receipt mutation, stage, commit, install, activation,
  cachebuster, configuration or marketplace edit, network, ref, release,
  cleanup, or claim-release effect.

## Third Exact-final recovery terminal receipt

- Grant `HC-0.7.1-REPAIRED-EXACT-FINAL-RECOVERY-018`, backed by user-amendment
  SHA-256
  `ba384f2e13e6125e0b897c504385b69e59b2cd22014cfdfbb99b09cee4a50048`,
  consumed exactly one additional bubblewrap invocation. Totals are `3`
  bubblewrap invocations and `2` recovery invocations, with `1` invocation
  under that grant.
- Before `/proc`, all listed mount checks passed: read-only root, repaired
  review, current/baseline/prior evidence, source repository, configuration,
  corrected marketplace, exact personal source, exact versioned cache,
  original adverse outputs, and current/baseline/prior evidence logs; and
  writable claimed output, private `/tmp`, and private Codex tmp/log/sessions.
  The corrected protected identities were
  `/home/caichenghang/.agents/plugins/marketplace.json`,
  `/home/caichenghang/plugins/happycodex`, and cache version
  `0.7.0+codex.20260805092118`.
- The terminal was pre-provider. Mountinfo contained both the inherited
  `/proc` read-only line and the new proc read-write line, but the unchanged
  probe expected `/proc` read-write and observed
  `ro,nosuid,nodev,noexec,relatime`. It failed closed rather than
  selecting or accepting the intended proc mount. Process exit was `1`; no
  timeout occurred.
- Provider invocations were `0`; provider and network effects were false. The
  Exact-final review did not run. `exact-final.jsonl` and `exact-final.md` are
  absent. The output inventory is exactly mode-`0600`
  `invocation-receipt.txt`, size `128759`, SHA-256
  `8a47a32103d7c36cc537b292de52785a1bbdd4b5f65b64ba03b3f13afa153c06`,
  under a mode-`0700` directory. Its preserved 64,870-byte prefix remains
  SHA-256
  `f9f63e02f9ea16b9805f4fd7c66afa68cd70fde98a04400250cdcceea3707d86`.
- Both active claims and all protected source, snapshot, evidence, plugin,
  configuration, marketplace, cache, and adverse-output identities remain
  exact. Repository, test, install, release, ref, and claim-release effects
  were false; both claims remain active.
- Terminal verdict: `NOT YET`. Phase remains `working`, and the required
  Exact-final gate remains open. The newly authorized attempt is consumed; no
  fourth attempt is authorized.

## User-authorized Codex-native read-only Exact-final amendment

Verbatim user message:

没事，你继续吧

The message is UTF-8 length `21` bytes, SHA-256
`fc29623063920c31016bda32c63c6f25db054096ede47944dd61dd59e53debcb`.
Its immediate context was Root explicitly acknowledging that the `/proc` and
whole-mount audit were over-design, proposing to stop that custom harness and
instead use one fresh Codex-native `read-only` Exact-final with an explicit
isolation-scope waiver; the user authorized continuation.

- Root's authorized interpretation supersedes only the independent outer
  bubblewrap/mount-level proof requirement and the prior no-fourth-attempt
  line. Exactly one fresh, empty-history, one-shot `codex exec` review is
  authorized for unchanged repaired candidate commit
  `1144515b23b760a6d91f86ca0a7c2911ad0fa53b`, tree
  `2f6857f30b5c0a4a68c0b245a34de3a02cd5c7ca`.
- The review uses `gpt-5.6-sol` with reasoning effort `max`, CLI
  `--sandbox read-only`, approval `never`, ignored user configuration, plugins
  disabled, ephemeral state, the unchanged neutral brief, and a 900-second
  hard cap. JSONL and final-message outputs go only to the already claimed
  repair-output directory.
- There is no outer bubblewrap and no `/proc` or global-mount audit. Command
  and request evidence plus clean before/after protected-state checks are
  accepted for this release. Independent mount-level isolation is explicitly
  waived and must be disclosed.
- Provider invocation cap is exactly `1`. There is no retry after any provider
  invocation or any ambiguous or partial effect. Any result other than exact
  `GO` stops and returns to Root.
- For this release only, `RL-EXACT` is amended to require one fresh
  Codex-native read-only neutral Exact-final returning `GO` under this explicit
  mount-level isolation waiver.
- The frozen release-note Exact-final line for later materialization is:
  `A fresh Codex-native read-only neutral Exact-final returned GO; independent outer mount-level isolation was explicitly waived.`
- All existing historical and adverse facts remain unchanged. Phase remains
  `working`. This amendment-recording grant itself authorizes no provider or
  downstream action.

## Native Exact-final neutral-brief path clarification

Direct host execution requires only these seven mechanical path rebindings,
each applied exactly once:

- `/tmp/hc/review` ->
  `/tmp/happycodex-0-7-1-repair.X5r42W/repo`
- `/tmp/hc/evidence/current/full-suite.log` ->
  `/tmp/happycodex-0-7-1-repair.X5r42W/full-suite.log`
- `/tmp/hc/evidence/current/full-suite.receipt.json` ->
  `/tmp/happycodex-0-7-1-repair.X5r42W/full-suite.receipt.json`
- `/tmp/hc/evidence/baseline/full-suite.log` ->
  `/tmp/happycodex-0-7-1-native-parallel.EXMU0v/full-suite.log`
- `/tmp/hc/evidence/baseline/full-suite-receipt.json` ->
  `/tmp/happycodex-0-7-1-native-parallel.EXMU0v/full-suite-receipt.json`
- `/tmp/hc/evidence/prior/full-suite.log` ->
  `/tmp/happycodex-0-7-1-release.0VkwGc/full-suite.log`
- `/tmp/hc/evidence/prior/full-suite.receipt.json` ->
  `/tmp/happycodex-0-7-1-release.0VkwGc/full-suite.receipt.json`

The retained neutral brief was `2433` bytes, SHA-256
`10ad758993b1f2697967a737d7b3b9de00af1fdd7d3d70d82ab4384f9682fb64`.
After only those substitutions it is `2547` bytes, SHA-256
`e039425243ff63577edb7fed6aa3d2b2e36bb2334efaccfc6118ef12a1b3fea3`.
No `/tmp/hc` token remains, and every mapped host input exists.

For this release, `unchanged neutral brief` therefore means semantically
unchanged with environment-only path rebinding. Semantics, request, scope,
candidate and evidence identities, exclusions, neutrality, model and effort,
hard cap, and desired-verdict exclusion remain unchanged. Phase remains
`working`; no provider has run under this clarification grant.

## Fresh Codex-native Exact-final terminal admission

- The unchanged repaired snapshot is commit
  `1144515b23b760a6d91f86ca0a7c2911ad0fa53b`, tree
  `2f6857f30b5c0a4a68c0b245a34de3a02cd5c7ca`. The fresh neutral review used
  exactly one provider invocation, exited `0`, did not time out, and emitted
  zero stderr bytes. Its exact first line was `GO`, with no release blocker.
- The JSONL contained `77` valid and `0` invalid records, with `0` error
  events: `item.completed` `39`, `item.started` `33`, `item.updated` `2`,
  `thread.started` `1`, `turn.started` `1`, and `turn.completed` `1`. The
  final Markdown exactly equals the last agent message.
- Exact review artifacts are:
  - Markdown
    `/home/caichenghang/.codex/happycodex-v0.7.1-repair-exact-final/exact-final.md`,
    mode `0600`, size `2378`, SHA-256
    `f0d92c91c96eea4e3f02e931867d236aed9168d91d7c0890cfe9efaa3a03adbd`;
  - JSONL
    `/home/caichenghang/.codex/happycodex-v0.7.1-repair-exact-final/exact-final.jsonl`,
    mode `0600`, size `288569`, SHA-256
    `005245dd83aefb6215af143ab42726e033a68994606feab074f4415c848cfe65`;
  - invocation receipt, mode `0600`, size `139075`, SHA-256
    `1649e383cbf4a8e4b00b12b6590931a654a2c465cf6995df5bebca35574bc22c`,
    with its 128,759-byte prefix preserved.
- Required disclosure:
  `A fresh Codex-native read-only neutral Exact-final returned GO; independent outer mount-level isolation was explicitly waived.`
- The review's only evidence limitation was the absence of a standalone
  baseline-commit log. Preserved current, baseline, and prior suites all showed
  `159` tests, the same two known failures, zero errors, and no timeout; the
  failing modules were untouched. The reviewer therefore treated that
  limitation as non-blocking.
- The reviewer confirmed the seven authorized publication paths, excluding
  this release plan; the validation projection must not be published verbatim.
  It also confirmed consistent Skill/public/reference semantics, historical
  capability values represented only as labeled digests, and the immutable
  published `v0.6.5:skills/happycodex` tree.
- Root independently parsed and read the complete artifacts, verified their
  exact hashes, modes, `GO`, and final-message equality, and reverified the
  clean repaired snapshot, exact source identity, empty index, and both active
  claim receipts. Root formally admits `GO` under the user-authorized
  mount-level isolation waiver: `RL-EXACT` is satisfied and the effective phase
  advances to `exact_final`. Both claims remain active. This admission grant
  authorizes no candidate commit or downstream effect.

Source-derived mechanical correction: the earlier
`HC-0.7.1-READINESS-COMMIT-007` row's instruction to `stage exactly those two
paths` is superseded because the claimed release-notes destination is external
to the repository. The later commit must stage only this repository release
plan; the external mode-`0600` notes file is used as GitHub Release input. This
does not expand authority or change release-note bytes.

## Candidate-commit pre-effect stop and tree correction

Under `HC-0.7.1-CANDIDATE-COMMIT-024`, the source identity, active claims,
repaired snapshot, publication bytes, and exact seven-path binary diff were
verified before mutation. The exact seven authorized publication paths were
then staged, with this release plan explicitly excluded. The cached inventory
was exact, `git diff --cached --check` passed, and the cached binary full-index
diff SHA-256 was
`7c91ac84b0c60de11e8671d6793b0200c2c605ea4c5ce0afa2399f2aeb4a6d56`.

The pre-effect tree check stopped the operation before commit:
`git write-tree` produced
`2d4ce8c044ed93bcbc33df86e36cdc1e8c795979`, not the mistakenly granted
`2f6857f30b5c0a4a68c0b245a34de3a02cd5c7ca`. Read-only comparison proved the
sole difference: the repaired snapshot tree `2f6857...` contains this release
plan as blob `173837d27749bebe60322414098d1faa83fe8f3d`, while the intended publication
scope explicitly excludes this release plan.

`HC-0.7.1-CANDIDATE-TREE-CORRECTION-025` therefore supersedes only the mistaken
expected candidate tree. The correct exact seven-path candidate commit tree is
`2d4ce8c044ed93bcbc33df86e36cdc1e8c795979`. The seven-path scope, all
publication bytes, authority, cached diff identity, and release-plan exclusion
are unchanged. The validation projection remains evidence and must not be
published verbatim.

No candidate commit, retry, network, ref, install, provider, test, claim, or
release effect occurred. The exact seven-path index remains staged for a later
separate authority; this untracked release plan is the only additional changed
surface.

## Personal activation terminal receipt and acceptance

- `HC-0.7.1-PERSONAL-ACTIVATION-027` preflight verified both active claims;
  repository HEAD
  `8dfacab289241c6af9e913b5c1546e36a843cb44`, tree
  `2d4ce8c044ed93bcbc33df86e36cdc1e8c795979`, unchanged `origin/main`
  `39a37b5e5bc497ac629a8e185309698905242e9c`, empty index, and only this
  untracked release plan at SHA-256
  `fcf9f53c9c4113a304f693ec2cb1c44652785d36e9f4431c836659f7fb7b9e6a`.
  It also verified the exact eight-file committed package inventory, live
  personal marketplace and local source binding, configuration identity,
  installed/enabled `0.7.0+codex.20260805092118` prestate, official helper
  identities, and the prior single cache.
- Ordered invocation receipt: exactly eight committed repository package files
  were mechanically byte-copied to the existing personal source, with no other
  source path copied or deleted. The default-timestamp
  `update_plugin_cachebuster.py` helper ran exactly once and produced
  `0.7.1+codex.20260805155350`; the resulting source manifest SHA-256 is
  `b518189f86d55012db267eda80bcc6e8729b7b17e13b4f5a3143f920fb210222`.
  Only its version token differs from the committed base manifest, and the
  other seven package files remain byte-exact. The marketplace-name helper ran
  exactly once with exact stdout `personal`. Then
  `codex plugin add --json happycodex@personal` ran exactly once, exited `0`,
  and reported `happycodex@personal` installed and enabled at
  `0.7.1+codex.20260805155350` from
  `/home/caichenghang/plugins/happycodex`.
- Active source and the corresponding sole cache each contain exactly the same
  eight package files and are byte-identical. Their locally defined ordered
  inventory SHA-256 is
  `7ce48ff99f60fc1d068e4269f4c6860ec629bdacbd5f3819026ded127bc9dc8e` for
  both. Root independently compared all eight files and obtained matching
  SHA-list aggregate
  `c1491ba0b351a926fde2710a82554f9f588741273304bb255ca6693011a470cf`
  for source and cache.
- The official CLI automatically replaced the prior
  `0.7.0+codex.20260805092118` cache while installing the new version. No
  manual deletion, restoration, retry, second cachebuster, marketplace-name
  helper, or install occurred. Under
  `HC-0.7.1-ACTIVATION-ACCEPT-027A`, Root accepts this as the official add's
  normal single-cache replacement semantics, consistent with tracked
  `HC-0.7.0-ACTIVATION-ACCEPT-003A`. Preservation does not require retaining
  the obsolete version cache directory across the explicitly authorized
  official activation; unrelated rollback and reference state remains
  preserved. `RL-ACTIVATE` is satisfied with exactly one current matching
  `0.7.1+codex.20260805155350` cache.
- The live marketplace remained SHA-256
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`,
  and configuration remained SHA-256
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
  Repository HEAD/tree/origin, empty index, this sole untracked plan, and both
  active claims remained exact. No manual source/cache/configuration/
  marketplace write beyond the granted mechanical sync and official CLI
  effect, repository stage or commit, notes, test or provider invocation,
  push, tag, GitHub Release, network/ref effect, or claim release occurred.
- The effective phase advances to `activation`. A new thread is required to
  consume the activated plugin.

## Candidate commit and release-readiness receipt

- Candidate commit `8dfacab289241c6af9e913b5c1546e36a843cb44` was created exactly once with
  sole parent `39a37b5e5bc497ac629a8e185309698905242e9c`, tree
  `2d4ce8c044ed93bcbc33df86e36cdc1e8c795979`, and exact subject
  `feat: release HappyCodex 0.7.1 native parallel exploration`. Its diff-tree
  contains exactly `.codex-plugin/plugin.json`, `README.en.md`, `README.md`,
  `docs/execplans/happycodex-0-7-1-native-parallel-exploration.md`,
  `skills/happycodex/SKILL.md`,
  `skills/happycodex/references/execplan.md`, and
  `tests/test_attestation_contract.py`. Immediate readback found an empty index
  and only this untracked release plan; `origin/main` remained the exact
  baseline. No amend, push, tag, install, or downstream release effect occurred
  under the candidate-commit grant.
- `HC-0.7.1-READINESS-COMMIT-028` preflight verified the exact candidate
  commit/tree/parent/subject/inventory; unchanged local `origin/main` and live
  remote `main` at `39a37b5e5bc497ac629a8e185309698905242e9c`;
  empty index; this sole untracked plan at SHA-256
  `310d9da57b68b6cad6c817dc054df0822db495a17d29dff1593cf17d6ea4f255`;
  absent local and remote `v0.7.1`; absent GitHub Release; absent notes
  destination; both active claims; exact activation, marketplace,
  configuration, and Exact-final identities; and the immutable review state.
- Validation is inherited without rerun. Focused contract checks and the
  existing Skill and plugin validators passed. The preserved full offline suite
  ran `159` tests with exactly the two known baseline failures, `0` errors, `0`
  new failures, and no timeout. It is not represented as a green suite. No test
  or provider invocation occurred under this readiness grant.
- The admitted fresh Codex-native read-only neutral Exact-final returned exact
  first-line `GO` with no release blocker. Required disclosure remains:
  `A fresh Codex-native read-only neutral Exact-final returned GO; independent outer mount-level isolation was explicitly waived.`
- Personal activation remains installed and enabled from
  `/home/caichenghang/plugins/happycodex` at
  `0.7.1+codex.20260805155350`. Active source and its sole corresponding cache
  contain the exact matching eight-file package inventory, with local ordered
  inventory SHA-256
  `7ce48ff99f60fc1d068e4269f4c6860ec629bdacbd5f3819026ded127bc9dc8e`
  for each and Root's independent matching SHA-list aggregate
  `c1491ba0b351a926fde2710a82554f9f588741273304bb255ca6693011a470cf`.
  Marketplace SHA-256 remains
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`
  and configuration SHA-256 remains
  `f7d72a7e2d89f22d3565ae8f59ae1ab10e2e15cb007f09022a63a7c8c7e7eed0`.
- External Release notes were created exactly once at
  `/home/caichenghang/.codex/happycodex-v0.7.1-release-notes.md` from the frozen
  body above, with exactly one final newline, mode `0600`, size `847`, and
  SHA-256
  `042ceeb1030088f8ecf19afe7e17947b6080170b0a5c2f076450f676b4bcbcf6`.
  The body is now frozen and the notes file is not a repository commit input.
- Current obligation disposition: `RL-SURFACE`, `RL-PRESERVE`, `RL-VALIDATE`,
  `RL-FREEZE`, `RL-EXACT`, the candidate portion of `RL-COMMIT`, and
  `RL-ACTIVATE` are satisfied. Readiness-commit creation and immediate readback,
  publish effects, and closeout remain pending. The readiness commit identity
  will be recorded from immediate readback later because a commit cannot embed
  its own identity in its committed bytes.
- The effective phase advances to `readiness`. No push, tag, GitHub Release,
  test/provider/helper/install, manual plugin/cache/marketplace/configuration
  edit, claim release, or other network/ref write has occurred under this
  readiness grant.

## Publication receipts and final closeout acceptance

- Readiness commit `68703f75b24b402e2924f491e90a6cc4cc9cdeb9`, tree
  `10a408ed9b64c45c835690567789b8c84d53f48b`, has sole parent candidate commit
  `8dfacab289241c6af9e913b5c1546e36a843cb44`. Its exact subject is
  `docs: record HappyCodex 0.7.1 release readiness`, and its diff-tree contains
  only `docs/execplans/happycodex-0-7-1-release.md` at committed SHA-256
  `fc3cf65000687d9debb35e7afc1578f06c3f21952d2bb16751592bb4886d8328`.
  Immediate readback found an empty index and clean worktree.
- Under `HC-0.7.1-MAIN-PUSH-029`, exactly one non-force
  `git push origin main` exited `0` and reported
  `39a37b5..68703f7  main -> main`. Immediate local tracking and fresh live
  readback both resolved `main` to the exact readiness commit. No retry or
  other ref effect occurred.
- Under `HC-0.7.1-TAG-030`, exactly one non-signed annotated local tag
  `v0.7.1` was created at the readiness commit with annotation
  `HappyCodex 0.7.1`, then exactly one
  `git push origin refs/tags/v0.7.1` exited `0`. Local and fresh remote tag
  object are
  `cc2b319b35afeac163d28d963898248c0541ca84`; both peel to
  `68703f75b24b402e2924f491e90a6cc4cc9cdeb9`.
- Under `HC-0.7.1-GITHUB-RELEASE-031`, exactly one
  `gh release create v0.7.1 --repo cch96/happycodex --title 'HappyCodex 0.7.1' --notes-file /home/caichenghang/.codex/happycodex-v0.7.1-release-notes.md --verify-tag`
  exited `0`. The public Release is
  `https://github.com/cch96/happycodex/releases/tag/v0.7.1`, with exact tag
  `v0.7.1`, title `HappyCodex 0.7.1`, `publishedAt`
  `2026-08-05T16:09:12Z`, `targetCommitish` `main`, draft `false`, prerelease
  `false`, zero assets, and body byte-identical to the 847-byte frozen notes,
  SHA-256
  `042ceeb1030088f8ecf19afe7e17947b6080170b0a5c2f076450f676b4bcbcf6`.
  No retry, edit, asset upload, or recreate occurred.
- Root accepts the exact Outcome. The inherited full offline suite ran `159`
  tests with exactly two known baseline failures, `0` errors, `0` new
  failures, and no timeout; it is not green and is not represented as green.
  Focused checks and existing Skill/plugin validators passed. The admitted
  fresh Codex-native read-only neutral Exact-final returned `GO`; independent
  outer mount-level isolation was explicitly waived. Root also accepts the
  official activation's normal single-cache replacement semantics. This is a
  reviewed source release, not a maintainer-evaluator certification.
- `HC-0.7.1-CLOSEOUT-032` closes the release through one final bounded chain.
  The closeout commit input is only this plan, with exact subject
  `docs: close HappyCodex 0.7.1 release` and readiness commit
  `68703f75b24b402e2924f491e90a6cc4cc9cdeb9` as sole parent. After exact local
  readback, one non-force `git push origin main` publishes that closeout commit.
  Only after successful fresh remote readback may the original eight-claim
  receipt be released exactly once; if and only if that succeeds safely, the
  repair one-claim receipt is released exactly once. Raw release output and
  owner tokens must never be exposed or persisted; only safe status, task, and
  resource-count fields may be reported.
- The original receipt remains mode `0600`, SHA-256
  `1b6abf5363bf14468fe8a42dceb66ce3a92fef806d5f0c0b198fadb24e41c6a5`,
  and covers eight claims. The repair receipt remains mode `0600`, SHA-256
  `51ffe37b8b388577574db7f9e5cdee48bfa5bbad0d1a56707a64ce271393eac3`,
  and covers one claim. Both receipt files remain after release. Exactly `20`
  unrelated claim records must remain; their aggregate over sorted per-root
  relative `*.claim/claim` path, tab, record SHA-256, and newline is
  `2147aecaf2281ef52c4a050bfb8cf1d36e2cd3c2772cdf8f207ec5cf1c3b92e2`.
- This committed record necessarily describes its own terminal commit, push,
  and claim releases prospectively. Their exact identities and safe statuses
  are obtained by immediate readback; no later plan mutation is required. On
  successful completion of that chain, all release obligations are satisfied
  and the effective phase is `closed`.
