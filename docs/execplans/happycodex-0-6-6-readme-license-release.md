# HappyCodex 0.6.6 README, license, and public Release

## Current checkpoint

- Phase: `working` (control bootstrap only; no product candidate exists).
- Current checkpoint: `HC-RL-004/local-candidate-commit`.
- Outcome owner and decision maker: Root.
- Fixed Executor: `/root/readme_license_release_executor`, the sole
  controlled-domain writer for this task.
- Goal state: none requested; no Goal was created.
- Grant `HC-RL-001` is consumed by its terminal receipt below.
- Grant `HC-RL-002` (sequence 2) is returned by its terminal receipt below
  because the final full-suite execution produced no observable terminal
  output/exit receipt. The edited bytes remain a working candidate, not
  `candidate_frozen`; no product/effect grant is active at handoff.
- Grant `HC-RL-003` (sequence 3) consumed its one exact compact-capture
  invocation and is returned adverse by the terminal receipt below. The result
  is 158 tests, 2 expected failures, and 41 unaccepted errors; phase remains
  `working` and no grant is active at handoff.
- Active grant: `HC-RL-004` (sequence 4), exact local candidate commit plus one
  clean-source suite only. Root established that the 41 errors correctly reject
  dirty package bytes; a clean Git candidate is a prerequisite for the
  source-identity suite, not a waiver or weakened assertion.
- This grant permits one exact five-path stage and local commit, then one exact
  clean-commit `-q` suite capture. Push, tag, GitHub Release, install,
  active-state mutation, provider/model calls, product repair, amend, and a
  second suite remain forbidden.

## Verbatim request and amendments

The Root dispatch conveyed these user-authorized requests verbatim:

- `REQUEST-MIT`: `add the previously recommended MIT LICENSE`
  (SHA-256 `28368ed7acecacfcdc5fc8716d9606e58952144e3e0c0f4a780852de1ca21349`).
- `REQUEST-RELEASE`: `resolve public version mismatch by ultimately creating GitHub Release v0.6.6`
  (SHA-256 `ad5b99bfdd45191241fe7a019005db3022834d679ff08d58c9b880853b0916bf`).
- `REQUEST-README`: `make README default Chinese and inspect/fix its content`
  (SHA-256 `a6e217e54f25f6076be461b2a69c9f3a58246d3477fd0b928a6d62469f8449da`).

Root then made this exact design amendment:

> preserve English discoverability with README.en.md; batch manifest license metadata because README already creates a new ProductArtifact.

Its SHA-256 is
`169df137888383a45a0d2d9e74daa32414218839ff3f3dfc6dd2cc602523114c`.

Before product authorization, Root added these exact content and validation
amendments:

- `release v0.6.6 is a reviewed public release but MUST NOT claim evaluator certification.`
  (SHA-256 `b3e7dceda351fd302c5cc2857a3e99ceb11622f4145c2932cbbf2ec102a3234a`).
- `README semantic digest would otherwise require 12 provider calls; those calls are out of scope and must not run.`
  (SHA-256 `486611e2976c42dbd45d03d3dceca2d829235550140f88f214a148136db1ad46`).
- `Planned validation is offline suite + plugin/skill checks + fresh isolated native exact-final + bounded isolated install; active install/cache unchanged.`
  (SHA-256 `56b26c2732bfc4361e0115b3ed5d8c47a0e64192b3ab547dbba32f8662e94a85`).
- `current README fixed GPT-5.6 role matrix appears only in README, not runtime SKILL, so public docs must not present it as automatically enforced; either remove or accurately label it as a maintainer-tested profile, with portable host behavior clear.`
  (SHA-256 `9fa7a3fc8ebcb143ba57d0e8f9e25c8ea4966a27d057eeb6b18159a77a34f5b1`).
- `Codex 0.145 or newer has no source-backed minimum; current local is 0.146.0, so replace with an exact tested-version statement or remove.`
  (SHA-256 `3f0472bba40480ac78b777def3e75d0f0fa8a9da0e68c3f2133f23ed2717156c`).
- `remove the long, misordered in-README release history and point to GitHub Releases.`
  (SHA-256 `8fb3785e6065e1b1958cfb3c58157792107a97245dce0e9ae4688af0c0364a73`).

Root then corrected the landing-page contract again, superseding the
maintainer-profile option but not the preserved verbatim amendment above:

- `Candidate Design B must NOT retain long 0.3–0.6.5 release history; remove obsolete/misordered history from both landing pages, keep only concise 0.6.6 highlights and link GitHub Releases.`
  (SHA-256 `fec9c7670615007afa9ab9c0950e50f113e6b1f777b197595394e9048e519e15`).
- `Do NOT preserve or mirror the README’s fixed model/effort matrix; source audit found it is not shipped behavior. State instead that HappyCodex bundles no model matrix/custom-agent profiles and effective model/effort remains user/Codex config recorded per participant.`
  (SHA-256 `b6e891cb815b24ef834801ff82ae96d96033636277f7d4469abcb08b4dcd7041`).
- `Remove unsupported minimum Codex 0.145+; safest public copy: this release was validated with Codex CLI 0.146.0, older versions not verified, or omit version floor.`
  (SHA-256 `7b1e94eba5e035dd212929c99d44225a8245c30d1c31b5b63a8d64708a3d3d9b`).
- `Goal wording must say it is created/changed only when explicitly requested and never expands authority/replaces ExecPlan/verification.`
  (SHA-256 `cca5e6cf4ed244c9a89b9ff117c1f1755bc7dfbc8dace9f3688e2e6a4bc101ba`).
- `Package boundary must mention resource-claim helper or say core runtime guidance; explicitly not controller/daemon/scheduler/MCP server/automatic authority or retry system.`
  (SHA-256 `a430ca152286c91799739ebc23a419b73ce9c2e5d5629e12d93acb688b8f4312`).
- `replace placeholder dev commands with repo-owned offline commands.`
  (SHA-256 `6b75f9355c933aa814f8781586a2e576432e91d4c4068752f5b9005c7bf58c94`).
- `add explicit <a id="install"></a> before Chinese install heading.`
  (SHA-256 `280d859819072af717e6998a62e0d9a474966fb159bfb3a5376ff9d8e23b06b6`).
- `product grant will also authorize replacing manifest keywords cross-cutting,testing with codex-plugin,codex-skill; amend selected paths/manifest obligation from license only to exact license+those two replacements.`
  (SHA-256 `7802d56e33ebd493ce86d81f6bde5b1ce8fa1f0a0b01360aa77bb3313e739415`).

Root resolved the remaining legal text and selected publication defaults,
without granting either effect:

- `standard MIT text with Copyright (c) 2026 caichenghang`
  (SHA-256 `12e2696ba7dd4faf17a9643c74ffcd5236ff1bb40856251e015a906ea910c1ac`).
- `annotated v0.6.6 tag message HappyCodex 0.6.6; GitHub Release name HappyCodex 0.6.6, draft=false, prerelease=false, exact body frozen later.`
  (SHA-256 `037ee1ed6c47de589a7d7ab3b3d7bea7c21d9bb38568dc6c8d8ab62d6efc0d96`).

These are frozen design inputs, not active tag or GitHub authority.

During `HC-RL-002`, Root amended discovery and removed the public development
check after reviewing the first candidate:

- `Open-source OpenAI Codex skill and plugin for reliable long-running, high-risk engineering tasks.`
  (SHA-256 `eb22fd08d3788295d14ec2a51cf87c97933e5867254458f81fa0c416d1054819`).
- `HappyCodex 是面向 Codex 长流程、高风险工程任务的可靠性工作流。它用仓库内的 ExecPlan 固化完成条件，由一个固定 Executor 执行受控写入，Root 负责决策、授权、复核与最终验证；它不替代 Codex 原生的 Plan、Git、测试或 review。`
  (SHA-256 `ea959e97d8b9a785b019bdf3e568dbf13bd4f7c3e654c53bcc2e95cf058e0791`).
- `Remove the public Development section and unittest command from both READMEs.`
  (SHA-256 `5490706a8c76db96dcc93124dcc6c16f58f1bad00b31a26b0d4d7e06423bc403`).

The English opening must be fact-equivalent and explicitly identify an
open-source OpenAI Codex skill/plugin. Maintainer validation remains private
release evidence in this ExecPlan; it is not copied into public landing pages.

Root's final landing-page amendment supersedes that ownership-ambiguous
tagline and removes validation/certification evidence from evergreen copy:

- `Open-source skill and plugin for reliable long-running, high-risk engineering work in OpenAI Codex.`
  (SHA-256 `951da1061feb9bb3e8251761d1417cb246a64b358c37ad7053abd0c2cc03744d`).
- `HappyCodex 是面向 OpenAI Codex 长流程、高风险工程任务的开源可靠性工作流。它用仓库内的 ExecPlan 固化完成条件，由一个固定 Executor 执行受控写入，Root 负责决策、授权、复核与最终验证；它不替代 Codex 原生的 Plan、Git、测试或 review。`
  (SHA-256 `fe5d1f006982013b8a5eec4df18c2c4157bfc449cacb3d5ebefae35247d58ffb`).
- `完整发布历史与验证状态请查看 GitHub Releases`
  (SHA-256 `16c10a62879cd7ec9cb5b43f151c96a3f34c1529d670f8d3b84134bed9e99b36`).
- `See GitHub Releases for full release history and validation status.`
  (SHA-256 `e3379cde3326ba3226202125cd088b30079bfc5b3c12d5b570cfe95a50ea7d9c`).

Both install sections now state only that marketplace support is required.
Neither README exposes the local `0.146.0` validation fact, an older-version
statement, or certification disclaimer. The later GitHub Release body—not the
landing pages—must disclose reviewed-but-not-evaluator-certified status and
the unrun native-compaction certification.

The exact current grant is:

> Initial grant HC-RL-001 ONLY: inspect current state; acquire exact resource claims for the worktree, refs/heads/main, and refs/tags/v0.6.6 using the installed HappyCodex resource_claim.py, keeping raw receipt outside tracked files; create and persist docs/execplans/happycodex-0-6-6-readme-license-release.md as the current ExecPlan with verbatim request/amendments, Outcome, preservation/exclusions, two candidate designs (Chinese-only vs Chinese-default+English mirror), selected design, paths, baseline, roles, grants, effects, obligations, checks, and stop conditions. You may write ONLY that ExecPlan and resource-claim control state in this turn. Do not modify README.md, create README.en.md/LICENSE, edit manifest/tests, stage, commit, push, tag, release, install, or invoke providers.

No sentence above grants any later operation by implication.

## Outcome

Publish one honest 0.6.6 source/release state in which:

1. GitHub renders an accurate Simplified Chinese `README.md` by default, led by
   Root's final exact Chinese positioning sentence and final exact shared
   English discovery tagline above.
2. `README.en.md` preserves an equally discoverable, fact-equivalent English
   presentation with reciprocal language links.
3. The README content defects found at baseline are fixed: English-only
   default, missing language navigation, missing license disclosure, a long
   misordered embedded release history, an unsupported minimum Codex version,
   and a README-only fixed GPT-5.6 matrix presented as enforced behavior. Both
   landing pages instead keep only concise 0.6.6 highlights and link GitHub
   Releases.
4. A standard MIT license exists at `LICENSE`, and the plugin manifest remains
   version `0.6.6`, adds supported SPDX value `"license": "MIT"`, replaces
   keyword `cross-cutting` with `codex-plugin`, and replaces `testing` with
   `codex-skill`, with no other metadata change.
5. The exact validated release commit is pushed to `refs/heads/main`, an exact
   `refs/tags/v0.6.6` is created and pushed, and GitHub exposes a non-ambiguous
   Release for that exact tag only after separate release authority.
6. The Release is explicitly a reviewed public release, not an evaluator-
   certified release. The twelve provider calls that a new README semantic
   digest would require are not run and must not be implied.
7. The published v0.6.5 product, HappyCodex Runtime, evaluator, external role
   configuration, active install/cache, marketplace/config, and rollback state
   remain unchanged.

Completion is a Root decision after it reproduces the final local and remote
receipts. This plan never decides completion.

## Preservation, exclusions, and allowed changes

Preserve exactly:

- Published `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; no existing tag byte or ref may
  be moved.
- `skills/happycodex/**`, including Runtime, role configuration, ExecPlan
  reference, and claim helper.
- `.agents/**`, `evaluation/**`, all existing test/evaluator semantics, and the
  four durable record types `ProductArtifact`, `EvalSpec`, `Attestation`, and
  `ReleaseReceipt`.
- Active source `/home/caichenghang/plugins/happycodex`, installed cache,
  `/home/caichenghang/.agents/plugins/marketplace.json`,
  `/home/caichenghang/.codex/config.toml`, and rollback sources. No activation
  or reinstall is part of this Outcome.
- Existing public install command, invocation string, supported workflow
  boundaries, and version `0.6.6` unless current source evidence falsifies one.
  The fixed GPT-5.6 matrix is not preserved as a Runtime claim because the
  Runtime does not contain or enforce it.

The only candidate source paths are:

- `README.md` — rewritten as the default Simplified Chinese README.
- `README.en.md` — English mirror derived from the corrected content.
- `LICENSE` — standard MIT license text with exact line
  `Copyright (c) 2026 caichenghang`.
- `.codex-plugin/plugin.json` — add top-level `"license": "MIT"` and perform
  exactly two keyword replacements: `cross-cutting` to `codex-plugin`, and
  `testing` to `codex-skill`.
- `docs/execplans/happycodex-0-6-6-readme-license-release.md` — current plan
  and receipts.
- At most one narrowly necessary offline metadata/README contract test, only
  if a later grant names its exact path. No test path is presently authorized.

Excluded without a later explicit user amendment:

- Any Runtime, evaluator, oracle, provider, holdout, corpus, role, marketplace,
  configuration, active install, activation, active cache, or rollback
  mutation. One later separately authorized bounded isolated install may write
  only its disposable isolated roots and receipt.
- Any link from `skills/happycodex/SKILL.md` to this or another repository
  evaluation/maintenance file.
- Compatibility readers, migrations, aliases, ledgers, evidence graphs,
  release automation, dependency installation, model/provider calls, or
  network write other than the later exact Git/GitHub publication effects.
- PRs, branches, force pushes, moving or replacing any existing tag, deleting
  releases, and publishing any tag or Release other than `v0.6.6`.

`README.md` and `.codex-plugin/plugin.json` are already in `PACKAGE_PATHS`, so
their later edit deliberately creates a new `ProductArtifact`. `README.en.md`
and `LICENSE` are source/release files outside the evaluator's current package
identity; this task will validate and publish them without widening
`evaluation/identity.py` or pretending they are included in that artifact.

## Candidate designs

### Design A: Chinese-only README

Replace `README.md` with corrected Chinese content, add MIT metadata, and omit
an English mirror. This minimizes file count and bilingual drift, but removes
the current English discovery path, makes external linking less useful, and
does not satisfy Root's discoverability amendment. Rejected.

### Design B: Chinese default plus English mirror

Make `README.md` the authoritative Simplified Chinese entry page, create
`README.en.md` as a corrected English mirror, and put reciprocal language links
at the top of both. Lead both with Root's final exact shared open-source
discovery tagline; use Root's final exact Chinese opening and a fact-equivalent
English opening that describes an open-source reliability workflow distributed
as a Skill/plugin for OpenAI Codex without implying OpenAI ownership. Keep
commands, identifiers, and other public facts aligned.
Remove the embedded 0.3–0.6.5 chronology, keep only concise 0.6.6 highlights,
and end both with the exact GitHub Releases validation-status sentence above.
Remove all CLI compatibility/version evidence and all certification-disclaimer
prose from the landing pages. Remove the fixed GPT-5.6 model/effort matrix
entirely. State the shipped portable contract:
HappyCodex bundles no model matrix or custom-agent profiles; user/Codex
configuration selects effective model/effort, which is recorded for each
participant. State Goal's exact boundary: it is created or changed only when
explicitly requested and never expands authority or replaces the ExecPlan or
verification. Describe the package as core Runtime guidance plus the
resource-claim helper, explicitly not a controller, daemon, scheduler, MCP
server, automatic authority system, or retry system. Put literal
`<a id="install"></a>` immediately before the Chinese install heading. Add a
license section linking `LICENSE`; apply the exact license and keyword manifest
metadata in the same candidate.

Neither public README contains a Development section or check command. The
full offline suite and installed-system validators remain private release
evidence here because the suite intentionally exits nonzero with two accepted
baseline failures.

Selected. It satisfies the explicit default-language request without reducing
English discoverability. The additional drift surface is bounded by structural
and fact-parity checks rather than by changing Runtime or adding a translation
system.

## Baseline and source identity

Baseline inspection on 2026-08-04 UTC established:

- Worktree: `/home/caichenghang/projects/happycodex`.
- Branch/ref: `refs/heads/main`.
- `HEAD`, local `main`, and local `origin/main`:
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`.
- Remote `refs/heads/main`, read with `git ls-remote`:
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`.
- HEAD tree: `880b6c250eebca078474960bcabc63fa98639e85`.
- Worktree status: clean (`## main...origin/main`).
- Current product-changing commit:
  `78073665beea058e4add59c0e48cac77bc562f43`; source tree
  `1575aa6619ec1298785d887edce333460dd58ad0`; Skill tree
  `c0fe3daba16699390b07eb80ed1d1023da236f6a`.
- Current ProductArtifact: artifact
  `455d394f23f074aa55abe1ca4398ec26c1a4456c18457b3c88e45e49e3f8872a`,
  semantic
  `528c042483c5912cbe0a0128fa1a22b9b23921147a52ccd7a906bbc1f6aaf05b`,
  record
  `85285a177e2a7ce449737ee8b3d3dafea3e00b96fafc365decbcbb3e3d3b8d07`.
- `README.md` SHA-256:
  `9bdfb46b83980bf2639a6db953dd9f572424ad85d62224eca1379329c6063c12`;
  it is English-only and contains the inconsistent release-note order
  `0.4, 0.4.1, 0.4.2, 0.5, 0.6, 0.6.6, 0.6.5, 0.3`. It also claims a fixed
  GPT-5.6 role matrix and Codex `0.145 or newer`; neither statement appears as
  an enforced matrix/minimum in `skills/happycodex/SKILL.md`.
- `README.en.md` and `LICENSE`: absent.
- `.codex-plugin/plugin.json` SHA-256:
  `6a7ed9aa91d88a3c02385e16bc5228fcf6cd978842ab3add7abb3f9aba98a63f`;
  version is `0.6.6` and top-level `license` is absent.
- Plugin-creator's current manifest specification explicitly supports a
  top-level SPDX-style `license` field; `MIT` is its canonical example.
- `v0.6.5` annotated tag object:
  `6920a968bbf8f5106c7bd8f84d585fddde84b2a6`; peeled commit:
  `e60166414d721d150a7ef3c66a316245c9c1e95d`; preserved Skill tree:
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- `refs/tags/v0.6.6` is absent locally and from `git ls-remote`; `gh release
  view v0.6.6 --repo cch96/happycodex` returned `release not found`, exit 1.
- The existing `v0.6.5` GitHub Release is public, non-draft, non-prerelease,
  named `HappyCodex 0.6.5`, and was published at
  `2026-07-31T05:33:45Z`.
- Toolchain observed: `codex-cli 0.146.0`, Python `3.10.12`.

Protected live state at baseline:

- `codex plugin list`: `happycodex@personal` installed and enabled at
  `0.6.6+codex.20260804155233` from
  `/home/caichenghang/plugins/happycodex`.
- Active source and installed-cache file-inventory digest, computed as the
  SHA-256 of sorted relative-path/file-SHA-256 lines:
  `925550c00a1ec75ef8bba23d1686bd3417c5d156ce67f1c5d0e92262a03f5a26`.
- Active/cache Skill SHA-256:
  `a1fbee68caf2d87481bfa06c1db6cdf34f7695c350c57c52e60ca98021ca28c9`;
  README SHA-256:
  `9bdfb46b83980bf2639a6db953dd9f572424ad85d62224eca1379329c6063c12`;
  cachebuster manifest SHA-256:
  `6c0773ff8bbb88e1636d71dcbb7479eec5818878f77dbe2ac69f82c7df0192ca`.
- Repository, active source, and cache role configuration
  `skills/happycodex/agents/openai.yaml` all have SHA-256
  `bc87f1506ef30893f44fb297792e17ea9df7ebfc463f9fb79fb9d43302251bc1`.
- Marketplace SHA-256:
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`;
  Codex config SHA-256:
  `0d4d88dab9263078ad0bb53cef52ae9c54b904f75900ad30a32609edc2b28802`.
- Rollback remains the immutable published v0.6.5 tag/tree above. The active
  cache root currently contains exactly one version directory,
  `0.6.6+codex.20260804155233`; this task must not add, remove, or rewrite one.

The prior recorded full-suite baseline at the same product bytes was 158 tests
with exactly two accepted failures and zero errors:
`test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
(`mutation='old-source'`) and
`test_old_source_components_cannot_back_a_new_dirty_evalspec`. `HC-RL-001`
does not authorize generating test caches or rerunning that suite, so later
validation must reproduce rather than assume this receipt.

## Roles, sessions, and resource ownership

| Role | Identity | Effective model/effort | Authority and state |
| --- | --- | --- | --- |
| Root | `/root`; exact runtime session not exposed to Executor | not exposed | Decides, grants, reproduces, and verifies; read-only in the controlled domain. |
| Fixed Executor | task `/root/readme_license_release_executor`; session `019fcd9d-129a-75c1-a560-91a8270e83b4` | runtime did not expose a trustworthy model/effort pin; no value is claimed | Sole writer; active only under one exact grant; delegation forbidden. |
| Explorer/Challenger/Reviewer | none dispatched | N/A | No agent or provider was invoked under `HC-RL-001`. |

The effective role is the fixed HappyCodex Executor. Model/effort identity is
an open provenance fact, not guessed from role defaults. It must be resolved by
Root before any later grant that requires model identity as evidence.

The installed `skills/happycodex/scripts/resource_claim.py` acquired these
resources atomically for owner `/root/readme_license_release_executor` and task
`HC-RL-001: happycodex-0.6.6-readme-license-release`:

| Resource | Canonical key | Claim SHA-256 |
| --- | --- | --- |
| `worktree=/home/caichenghang/projects/happycodex` | `fs:/home/caichenghang/projects/happycodex` | `1c58a7f5d1b885606ecf1b6060b2e7dafe42d682e66df21a273833cea007229d` |
| `ref=/home/caichenghang/projects/happycodex::refs/heads/main` | `ref:/home/caichenghang/projects/happycodex/.git:refs/heads/main` | `f35b0790e3e8ad22758216b31ad9a79ea5cd46231f32145c90376d66c9656e1c` |
| `ref=/home/caichenghang/projects/happycodex::refs/tags/v0.6.6` | `ref:/home/caichenghang/projects/happycodex/.git:refs/tags/v0.6.6` | `bb6b24ca4dd03bec717e4502f3571431a67fcf36002d3a527cca6323d1293357` |

- Raw mode-0600 receipt outside tracked files:
  `/home/caichenghang/.codex/happycodex-0.6.6-readme-license-release-HC-RL-001.claim.json`.
- Raw receipt SHA-256:
  `a8764af6bf128653da8bd64ab1b92f68ab6bf8ad5d17ba9d805219aaa59f6e19`.
- Owner-token SHA-256 (the token itself stays external):
  `d983b5f6c0e117a8c6f500bb657669fdba43cc84e341a0067928920aca8f1934`.
- First post-acquisition verification: status `verified`, resource count 3.

Claims remain held for this fixed Executor across later exact grants. Any
missing claim, owner mismatch, or token mismatch returns control to Root; it is
not repaired or reacquired automatically.

## Grant ledger

### `HC-RL-001` — bootstrap control only

- Sequence: 1.
- Executor: `/root/readme_license_release_executor`.
- Exact prestate: clean `main`/`origin/main`/remote `main` at
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`; `v0.6.6` absent.
- Closed writes: this ExecPlan and resource-claim control state only.
- Allowed reads: repository/source/config/install state, local and remote refs,
  GitHub Release metadata, installed claim helper/specification, and prior
  receipts needed to bind baseline.
- Forbidden effects: product/test edit, staging, commit, push, tag, Release,
  install, activation, provider, or delegation.
- Acceptance: three claims verify; this plan records the complete current
  contract; the only tracked diff is this plan; prestate remains unchanged.
- Stop: any prestate drift, claim conflict/mismatch, unknown write, or missing
  decision-changing fact.
- State: `consumed` by the terminal receipt below.

### `HC-RL-002` — product candidate and offline validation only

- Sequence: 2.
- Executor: `/root/readme_license_release_executor`; no delegation.
- Exact prestate: held receipt verifies all three claims; `HEAD`, local
  `main`, local `origin/main`, and live remote `main` are
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`; local/remote tag and GitHub
  Release `v0.6.6` are absent; owned status contains only this untracked
  ExecPlan.
- Closed writes: `README.md`, new `README.en.md`, new `LICENSE`,
  `.codex-plugin/plugin.json`, and this ExecPlan. `apply_patch` is the only
  authorized source-edit mechanism.
- Exact manifest delta: add top-level `"license": "MIT"`; replace keyword
  `cross-cutting` with `codex-plugin` and `testing` with `codex-skill`; retain
  every other value and ordering.
- Allowed operations: edit the closed paths; run offline structural/factual,
  canonical-license, JSON-delta, plugin/Skill validator, Git-diff, product
  identity, protected-hash, and `python3 -B` unit-test checks; persist the full
  receipt here.
- Forbidden effects: any other source/test write, staging, commit, push, tag,
  GitHub Release, install, activation, active cache/config/marketplace change,
  provider/model invocation, or delegation.
- Acceptance: exact five-path owned inventory; bilingual requirements and
  boundaries verified; canonical MIT and exact manifest delta verified;
  `skills/happycodex` byte identity preserved; validators green; full suite is
  exactly 158 tests, failures 2, errors 0 with only the two accepted baseline
  identities; ProductArtifact/diff/inventory and protected post-hashes bound.
- Stop: any claim/prestate drift, ungranted path, validator failure, different
  test count/failure/error, protected-state drift, or missing/ambiguous fact.
- State: `returned` by the terminal receipt below; acceptance is not claimed.

### `HC-RL-003` — one exact compact-capture recovery

- Sequence: 3.
- Executor: `/root/readme_license_release_executor`; no delegation.
- Exact prestate: all three HC-RL-001 claims verify; exact HC-RL-002 five-path
  inventory, candidate file hashes, ExecPlan hash
  `87ba70cf65f59058dbbe7610b459bdb2b3d2fef8b1d742f30d574c26c1d4e188`,
  aggregate product diff
  `95c35fa3edb1a825900a6084bf535d00c850597263f0ed3f276445b09ece5511`,
  refs, absent v0.6.6 tag/Release, active plugin, marketplace/config, v0.6.5,
  and Skill identities all reverified exact.
- Closed repository write: this ExecPlan only. Product/test edits and index
  writes are forbidden.
- Closed external writes: one fresh directory matching
  `/home/caichenghang/.codex/happycodex-0.6.6-readme-license-suite.XXXXXX`,
  mode 0700; one mode-0600 combined stdout/stderr capture and one mode-0600
  decimal process-exit receipt within it.
- Exact invocation, once:
  `python3 -B -m unittest discover -s tests -q`.
- Acceptance: retained raw capture proves `Ran 158 tests`, `failures=2`,
  `errors=0`, and only
  `test_exact_final_source_rejects_self_selected_projection_and_fake_diff`
  with `mutation='old-source'` plus
  `test_old_source_components_cannot_back_a_new_dirty_evalspec`; process exit
  is captured separately and equals the expected unittest nonzero exit 1.
- If accepted: hash/mode/path the raw and exit receipts; bind working snapshot,
  package artifact/semantic identities, diff and inventory, protected state,
  remaining dirt/gates; enter `candidate_frozen`; consume this grant.
- Stop: any different count, failure/subtest, error, exit, capture/mode/path,
  state drift, product mutation, or missing terminal evidence. No retry.
- State: `consumed and returned adverse`; suite invocation budget 1/1 used,
  with no retry.

### `HC-RL-004` — local candidate commit and clean-source suite

- Sequence: 4.
- Executor: `/root/readme_license_release_executor`; no delegation.
- Source-boundary amendment: `HC-RL-003 proved all 41 errors are the evaluator
  correctly rejecting dirty package bytes (frozen source package identity
  differs); deterministic product checks are green. A clean Git candidate is
  therefore a prerequisite for the source-identity suite, not a waiver or
  weakened assertion.`
- Exact prestate: held claims verify; parent/HEAD/local main/local origin/main/
  live remote main are
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`; exact HC-RL-003 candidate hashes,
  aggregate product diff, five-path status, empty index, and absent v0.6.6
  tag/Release reverified.
- Closed pre-commit writes: this ExecPlan only, then exact index entries for
  `.codex-plugin/plugin.json`, `LICENSE`, `README.en.md`, `README.md`, and this
  ExecPlan. No other path may be staged.
- Cheap dirty-source checks only: exact hashes/inventory, diff check, manifest
  delta, canonical MIT, and bilingual invariants. The full suite is forbidden
  before the commit.
- Exact commit message: `docs: publish Chinese README and MIT license`.
  Create one local commit on `main`; no amend.
- Post-commit pre-suite gate: parent, commit/tree, exact five-path inventory,
  clean product state, HEAD/local main, unchanged origin/remote main, absent
  tag/Release, claims, and protected state all verify. A later terminal receipt
  may be the only post-commit dirt and is outside package/review identity.
- Exact suite invocation after that gate, once:
  `python3 -B -m unittest discover -s tests -q`, with one fresh external
  mode-0700 directory, mode-0600 combined capture, and mode-0600 separate exit
  receipt.
- Acceptance: `Ran 158 tests`, failures 2, errors 0, exact two baseline failure
  headers including `mutation='old-source'`, and process exit 1.
- If accepted: derive ProductArtifact from the exact candidate commit; bind
  package/semantic/record hashes, complete commit inventory and diff hashes,
  protected poststate, checks, dirt, and remaining gates; enter
  `candidate_frozen`. Do not stage the later ExecPlan receipt.
- Stop: any changed byte/path/ref/protected state, cached-path mismatch, commit
  mismatch, suite mismatch, capture failure, or ungranted effect. No repair,
  amend, retry, or second suite.
- State: `active`; local commit budget 0/1 and clean-source suite budget 0/1.

The first formal candidate check wave before Root's discovery amendment
produced `git diff --check`, manifest-delta, canonical-MIT, and Skill-identity
GREEN. The initial `bilingual-structural-factual-invariants` harness terminated
with an unnamed `AssertionError` at line 40. A read-only diagnostic found all
named headings, tagline, command, boundary, Goal, model-portability, highlight,
certification-disclosure, and Chinese-content predicates true. Root then
changed the affected README content, so the superseded check is not retried
unchanged; one corrected named-predicate check will run against the amended
candidate before freeze.

The first full-suite invocation ran after that corrected invariant gate but
before Root's final landing-page amendment. Its captured prefix already showed
unexpected `ERROR` results and the tool output truncated before `Ran ...` /
`FAILED ...` / command exit lines, so it is not qualifying evidence and was not
reinvoked against unchanged bytes. Root's final amendment changes both README
identities and explicitly calls for one final validation wave; that final wave
must use compact terminal capture and is the only suite result eligible for
candidate freeze.

The following are required future boundaries, not grants:

1. Product-edit grant: exact source paths and frozen MIT line above; only
   offline edits/checks; no staging or external effect.
2. Candidate/commit grant: exact clean diff and checks, candidate ProductArtifact,
   commit message, and commit/ref prestate.
3. Fresh isolated native exact-final grant: one read-only reviewer invocation
   over the frozen candidate, with exact model/effort/session/isolation and
   cost/time cap. This is not the twelve-call evaluator certification path.
4. Bounded isolated-install grant: one install into exact disposable roots,
   with active source/config/cache excluded and pre/post protected hashes.
5. Push grant: one fast-forward of `refs/heads/main` to the exact candidate.
6. Tag grant: annotated `v0.6.6`, message `HappyCodex 0.6.6`, exact later
   frozen target, and one push after proving the ref remains absent.
7. GitHub Release grant: exact repo/tag/target, name `HappyCodex 0.6.6`, exact
   later frozen body, `draft=false`, `prerelease=false`, and one invocation
   after proving no existing Release; partial or ambiguous effect stops
   without retry.

Release authority is separate even though it serves the same user Outcome.

## Effects and ordering

`HC-RL-001` effects are limited to atomic resource-claim records, their
external raw receipt, and this tracked ExecPlan. The remote operations in the
baseline were read-only. No provider, install, Git ref, GitHub, or product
effect has occurred.

Later work must follow this order, each behind its own current grant and fresh
claim/prestate verification:

1. Resolve the open legal/release facts.
2. Edit the four selected product/source files and this plan; run offline
   checks; freeze the exact diff and identity inputs.
3. Commit only the exact granted paths, verify the commit/tree/status, and
   derive and freeze the new ProductArtifact from that commit.
4. Run one separately authorized fresh isolated native exact-final review. A
   product correction returns to step 2 and produces a new commit/artifact; the twelve-call
   evaluator certification path remains out of scope.
5. Run one separately authorized bounded isolated install from the reviewed
   commit and prove the active
   source/cache/config/marketplace stayed byte-identical.
6. Fast-forward remote `refs/heads/main` to the exact reviewed commit.
7. Revalidate remote `main` and tag absence; create/push one exact `v0.6.6` tag.
8. Revalidate GitHub Release absence; create one exact Release; immediately
   read back tag, commit, name, flags, URL, and body digest.
9. Persist the terminal receipt and return to Root for completion decision.

No automatic retry is allowed after any provider-reaching, push, tag, or
GitHub Release invocation. A proven pre-invocation no-effect failure returns to
Root unless its exact grant already names a bounded recovery.

## Obligations

| Obligation | Type | Observable contract and falsifier | Evidence/check | State |
| --- | --- | --- | --- | --- |
| `O-ZH-DEFAULT` | outcome | `README.md` is accurate Simplified Chinese, not an English wrapper, with literal `<a id="install"></a>` immediately before its install heading; falsified by untranslated prose, missing anchor, or changed command semantics. | Human inspection plus heading/code/link inventory. | offline verified |
| `O-EN-MIRROR` | outcome | `README.en.md` preserves corrected English discovery and reciprocal language navigation; falsified by fact/version/command drift. | Bilingual structure and invariant-value comparison. | offline verified |
| `O-DISCOVERY` | outcome | Both pages use exact final tagline `Open-source skill and plugin for reliable long-running, high-risk engineering work in OpenAI Codex.`; Chinese uses Root's final exact opening and English is fact-equivalent, explicitly an open-source reliability workflow distributed as a Skill/plugin for OpenAI Codex without implying official ownership. | Exact text and positioning-fact inventory. | offline verified |
| `O-CONTENT` | outcome | Both pages keep only concise 0.6.6 highlights and end with the exact GitHub Releases history/validation-status sentence; install requires marketplace support and exposes no local CLI-version evidence; no minimum or fixed model matrix remains. | README diff review against Runtime and public-fact inventory. | offline verified |
| `O-MODEL-PORTABILITY` | outcome | Public docs say HappyCodex bundles no model matrix/custom-agent profiles and user/Codex configuration selects effective model/effort, recorded per participant. | README parity and source comparison to Runtime/agent files. | offline verified |
| `O-GOAL-BOUNDARY` | outcome | Goal is created/changed only on explicit request and never expands authority or replaces ExecPlan/verification. | Exact bilingual text check. | offline verified |
| `O-PACKAGE-BOUNDARY` | outcome | Package is core Runtime guidance plus resource-claim helper, not controller/daemon/scheduler/MCP server/automatic authority/retry system. | Exact bilingual boundary inventory and source tree. | offline verified |
| `O-NO-BROKEN-DEV-COMMAND` | outcome | Neither public README contains a Development section, placeholder, maintainer path, or misleading check command; offline maintenance commands remain receipt-only. | Heading/code-block/text inventory. | offline verified |
| `O-MIT` | outcome | `LICENSE` is the standard MIT text with exact `Copyright (c) 2026 caichenghang`, and both READMEs link it; falsified by any altered term or notice. | Exact text/hash check. | offline verified |
| `O-MANIFEST` | outcome | Manifest remains strict semver `0.6.6`, adds supported top-level `license: MIT`, replaces only `cross-cutting`/`testing` with `codex-plugin`/`codex-skill`, and changes no other metadata. | JSON baseline/candidate comparison and plugin validator. | offline verified |
| `O-RELEASE` | outcome | Remote `main`, exact `v0.6.6` tag, and one GitHub Release resolve to the frozen commit with exact approved flags/body. | `git ls-remote`, `git rev-parse`, and `gh release view` receipt. | open |
| `O-NO-CERT-CLAIM` | exclusion | READMEs contain no certification assertion or disclaimer; the later Release body must separately disclose reviewed-but-not-evaluator-certified status and unrun native-compaction certification; no twelve-call semantic evaluator path runs. | README text search, invocation inventory, and later Release-body review. | README verified; Release open |
| `O-NATIVE-REVIEW` | outcome | One fresh isolated native exact-final covers the frozen diff and obligations without becoming evaluator certification. | Exact reviewer identity/isolation/coverage receipt and Root reproduction. | open |
| `O-ISOLATED-INSTALL` | outcome | One bounded isolated install validates the frozen package while active source/cache/config remain exact. | Isolated root/install receipt plus protected pre/post hashes. | open |
| `O-V065` | preservation | Existing v0.6.5 tag/commit/Skill tree remain exact. | Pre/post ref and tree checks. | baseline verified |
| `O-RUNTIME` | preservation | `skills/happycodex/**`, role config, evaluator, and record families do not change. | Exact scoped Git diff and hashes. | baseline verified |
| `O-LIVE-STATE` | preservation | Active source/cache, marketplace/config, install status, and rollback inventory remain exact. | Pre/post hashes and `codex plugin list`. | baseline verified |
| `O-NO-SKILL-LINK` | exclusion | No repository evaluator/maintenance file is linked from `skills/happycodex/SKILL.md`. | Skill byte identity. | baseline verified |
| `O-SCOPE` | exclusion | Candidate and commits contain only later granted exact paths; no untracked or staged bystander. | `git status`, cached diff, commit inventory. | working candidate verified |
| `O-IDENTITY` | premise | README/manifest mutation yields a fresh ProductArtifact; README.en/LICENSE stay source-bound without evaluator widening. | `product_artifact_from_git` plus full commit inventory. | blocked before freeze |
| `O-ONE-SHOT` | premise | Push/tag/Release effects are invoked at most once each; ambiguous/partial outcomes stop. | External command and read-back receipts. | open |

## Checks and acceptance gates

Before every later mutation or effect:

- Verify the external claim receipt with the installed helper.
- Verify worktree, `HEAD`, `refs/heads/main`, remote `main`, and relevant tag
  state against the exact active grant.
- Verify owned status contains no unclassified path.

Candidate checks, once separately granted:

- `git diff --check` is clean.
- Exact changed-path inventory equals the active grant.
- `README.md` is Chinese-default; both README files have reciprocal language
  and MIT-license links; code blocks, invocation strings, install commands,
  versions, and other factual invariants match. Role/model/effort matrix parity
  is intentionally not preserved.
- Both README files contain Root's final exact shared discovery tagline;
  Chinese contains Root's final exact opening; English states the same
  ExecPlan, fixed-Executor, Root, and native-tool boundary facts and describes
  an open-source reliability workflow distributed as a Skill/plugin for OpenAI
  Codex without implying official ownership.
- Literal `<a id="install"></a>` immediately precedes the Chinese install
  heading.
- Neither README contains the long 0.3–0.6.5 heading history; both contain only
  concise 0.6.6 highlights and point to the repository's GitHub Releases page.
- Both install sections require marketplace support but contain no CLI version,
  older-version, or minimum-version statement.
- Neither README contains the fixed GPT-5.6 matrix. Both say HappyCodex bundles
  no model matrix/custom-agent profiles and effective model/effort comes from
  user/Codex configuration and is recorded per participant.
- Goal, package boundary, and excluded controller/daemon/scheduler/MCP/
  automatic-authority/retry-system wording satisfy the exact obligations.
- Neither public README contains a Development heading, unit-test command,
  `/path/to/...` placeholder, or absolute maintainer path.
- Neither public README contains certification assertion/disclaimer prose; the
  highlight section ends with Root's exact language-specific GitHub Releases
  history/validation-status sentence.
- `LICENSE` matches the standard MIT template and approved copyright line.
- JSON parsing proves manifest `name == "happycodex"`, `version == "0.6.6"`,
  and `license == "MIT"`; the keyword array replaces exactly
  `cross-cutting`/`testing` with `codex-plugin`/`codex-skill`; all other fields
  match baseline.
- Plugin validation:
  `python3 /home/caichenghang/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`.
- Existing HappyCodex Skill validator remains green without changing Skill
  bytes.
- Focused offline metadata/README tests pass; then the full standard-library
  suite is rerun and has no new failure/error beyond the two exact accepted
  baseline identities. No dependency install or network test is allowed.
- `v0.6.5:skills/happycodex` remains
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Active source/cache/config/marketplace hashes and plugin-list state remain
  exactly at baseline.
- Text and invocation inventories prove no evaluator-certification claim and
  no twelve-call evaluator run.

Candidate freeze must record source commit/tree, package tree, ProductArtifact
digests, exact diff digest, changed paths, checks/exits/failures, external
preservation hashes, remaining dirt, and open gates. Publication preflight must
then bind the exact commit/tag/Release parameters and remote state. The native
exact-final receipt and isolated-install receipt are mandatory publication
inputs but are not evaluator certification.

## Open facts and stop conditions

Decision-changing facts that Root must resolve before their affected grant:

- Exact GitHub Release body and the exact frozen commit/tag target. Tag form
  and message, Release name, and false draft/prerelease flags are selected
  design inputs but still require an exact publication grant.
- Exact model/effort, isolation, time/token cap, and source projection for the
  required fresh native exact-final. No invocation is authorized now.
- Exact disposable roots, source package, command, cap, and cleanup/retention
  behavior for the required bounded isolated install. Active installation
  paths can never be selected.
- Effective Executor model/effort provenance if a later gate requires it.

Stop and return to Root, without widening scope or retrying, if any of these
occurs:

- claim verification fails, owner/session identity drifts, or another writer
  touches an owned resource;
- worktree, local/remote `main`, active install/config/cache, v0.6.5, or
  v0.6.6 prestate differs from the exact active grant;
- an ungranted path must change, README truth cannot be source-verified, the
  plugin validator rejects `license`, or a new/unknown test failure appears;
- README or Release wording implies evaluator certification, an evaluator
  semantic run is proposed, or the planned invocation count reaches the
  prohibited twelve-call path;
- the frozen commit/tag target or Release body remains ambiguous when its
  effect is next;
- a push, tag, or GitHub operation has a partial or ambiguous effect;
- any operation would require a provider, network/install effect, release
  mutation, compatibility mechanism, or authority expansion not named by the
  current grant.

## `HC-RL-001` terminal receipt

- Receipt finalized: `2026-08-04T16:43:29Z` UTC.
- Fixed Executor/task/session remained
  `/root/readme_license_release_executor` /
  `019fcd9d-129a-75c1-a560-91a8270e83b4`; no delegate or second writer was
  created.
- External raw claim receipt remains mode `0600`, SHA-256
  `a8764af6bf128653da8bd64ab1b92f68ab6bf8ad5d17ba9d805219aaa59f6e19`.
  Installed-helper verification returned `verified`, owner and task exact,
  resource count 3.
- Local `HEAD`, `refs/heads/main`, local `origin/main`, and live remote `main`
  remained `0893092ae2febcccfc4b2ade2e78a3e17a588d60`; HEAD tree remained
  `880b6c250eebca078474960bcabc63fa98639e85`.
- Local and remote `refs/tags/v0.6.6` remained absent. Live
  `gh release view v0.6.6 --repo cch96/happycodex` returned `release not
  found`, exit 1. No tag or Release write was invoked.
- Published v0.6.5 Skill tree remained
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`.
- Product baselines remained byte-identical: `README.md`
  `9bdfb46b83980bf2639a6db953dd9f572424ad85d62224eca1379329c6063c12`,
  manifest
  `6a7ed9aa91d88a3c02385e16bc5228fcf6cd978842ab3add7abb3f9aba98a63f`,
  and role configuration
  `bc87f1506ef30893f44fb297792e17ea9df7ebfc463f9fb79fb9d43302251bc1`.
- Marketplace/config hashes remained
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`
  and
  `0d4d88dab9263078ad0bb53cef52ae9c54b904f75900ad30a32609edc2b28802`.
  `codex plugin list` still reported `happycodex@personal` installed and
  enabled at `0.6.6+codex.20260804155233` from the same active source.
- Owned status contained exactly one untracked path, this ExecPlan. The staged
  and tracked-unstaged diffs were empty. New-file `git diff --no-index --check`
  emitted no whitespace error (exit 1 only because the file differs from
  `/dev/null`).
- The exact tracked-source effect is one newly persisted plan:
  `docs/execplans/happycodex-0-6-6-readme-license-release.md`. No `README.md`,
  `README.en.md`, `LICENSE`, manifest, test, Runtime, evaluator, install,
  staging area, commit, ref, remote, cache, configuration, provider, or GitHub
  mutation occurred.
- Root fixed the MIT line, annotated tag/message, and Release name/flags as
  recorded above. Remaining decision-changing facts are the exact frozen
  commit/tag target, Release body, exact native exact-final and isolated-install
  parameters, and trustworthy effective Executor model/effort if a later gate
  requires it.
- `HC-RL-001` is consumed. Claims stay held by this fixed Executor; control is
  returned to Root for a new exact grant. This receipt does not decide task
  completion.

## `HC-RL-002` terminal receipt

- Receipt finalized: `2026-08-04T16:59:10Z` UTC. Phase remains `working`;
  candidate freeze and completion are not claimed.
- The held external receipt again verified the exact fixed Executor/task and
  all three worktree/main/tag claims. No delegation or provider invocation
  occurred.
- Exact working product inventory is `.codex-plugin/plugin.json`, `LICENSE`,
  `README.en.md`, and `README.md`. The fifth owned path is this ExecPlan. No
  test, Runtime, evaluator, `.agents`, or external active-state path changed;
  the index remained untouched.
- Working file SHA-256 values are:
  - `README.md`:
    `5a584cf132187554ce3e2f466584f49bd700089915972b13cf17e9614a2ee336`
  - `README.en.md`:
    `11f45423198a2af6269d1d18cf0c0dded10e9b1408801236dfddad76d4f442ad`
  - `LICENSE`:
    `c8bd13985408f8a5357006c849ff1b42e196e580a71883d2337f7b1eeb0e43e1`
  - `.codex-plugin/plugin.json`:
    `2c5c0af5e0864b467fa67a40cad7303c6cff250920674e303b755fb3f691e8a5`
- Binary/full-index/no-renames aggregate product diff SHA-256, ordered as
  tracked manifest/README then new `README.en.md`/`LICENSE`, is
  `95c35fa3edb1a825900a6084bf535d00c850597263f0ed3f276445b09ece5511`.
- Final deterministic wave evidence:
  - held claim: verified, resource count 3;
  - tracked and untracked `git diff --check`: GREEN;
  - manifest: exact `license: MIT`, exact two keyword replacements, every
    other field and top-level order unchanged;
  - final named bilingual invariant set: all predicates GREEN, including exact
    tagline/openings, section order, anchors, commands, four phases, model and
    Goal boundaries, package exclusions, 0.6.6 highlights, release links, no
    CLI-version/certification/development prose, and 641 CJK characters in the
    Chinese primary page;
  - canonical MIT text: GREEN;
  - system plugin validator: `Plugin validation passed`;
  - system Skill validator: `Skill is valid!`;
  - unchanged Skill SHA-256:
    `a1fbee68caf2d87481bfa06c1db6cdf34f7695c350c57c52e60ca98021ca28c9`;
    unchanged Skill tree:
    `c0fe3daba16699390b07eb80ed1d1023da236f6a`.
- Full-suite evidence is not acceptable:
  - the pre-final-amendment invocation's visible prefix contained unexpected
    `ERROR` results, then output truncated before terminal counts and exit;
  - after Root changed both README identities and requested one final wave, the
    exact `python3 -B -m unittest discover -s tests -v` process completed in
    execution cell 60, but the compact filter and shell yielded no observable
    output at all—not the failure identities, `Ran`, `FAILED`, or exit lines;
  - therefore the required 158 tests / failures 2 / errors 0 receipt is unknown,
    not inferred or relabeled. No unchanged-byte retry was attempted.
- Because full-suite evidence is missing and staging/commit is forbidden, no
  valid commit-bound `ProductArtifact` was constructed. The working diff and
  hashes above are a proposal only, not a frozen artifact.
- Protected poststate remained exact: `HEAD`, local `main`, and local
  `origin/main` are
  `0893092ae2febcccfc4b2ade2e78a3e17a588d60`; v0.6.5 Skill tree is
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`; marketplace SHA-256 is
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`;
  config SHA-256 is
  `0d4d88dab9263078ad0bb53cef52ae9c54b904f75900ad30a32609edc2b28802`;
  `happycodex@personal` remains installed/enabled at
  `0.6.6+codex.20260804155233` from the same source.
- No staging, commit, push, tag, GitHub Release, install, activation, active
  cache/config/marketplace mutation, provider call, or retry occurred.
- `HC-RL-002` is returned to Root with one blocker: missing full-suite terminal
  evidence. Claims remain held by this fixed Executor. Root must decide whether
  to authorize one exact compact-capture recovery; this receipt does not decide
  candidate acceptance or task completion.

## `HC-RL-003` terminal receipt

- Receipt finalized: `2026-08-04T17:05:21Z` UTC. Phase remains `working`;
  `candidate_frozen` is rejected by the exact acceptance rule.
- Preflight reverified all three held claims and the exact HC-RL-002 poststate:
  five owned paths only, empty index, product hashes unchanged, ExecPlan
  `87ba70cf65f59058dbbe7610b459bdb2b3d2fef8b1d742f30d574c26c1d4e188`,
  product diff
  `95c35fa3edb1a825900a6084bf535d00c850597263f0ed3f276445b09ece5511`,
  all local/remote refs exact, v0.6.6 tag/Release absent, and protected active
  state exact. An initial read-only absent-tag shell probe stopped on expected
  exit 1 under `set -e`; corrected explicit exit handling proved absence before
  any mutation or suite dispatch.
- One fresh external directory was created and retained:
  `/home/caichenghang/.codex/happycodex-0.6.6-readme-license-suite.MZSx68`,
  mode 0700.
- Exact suite invocation count: 1/1. Command:
  `python3 -B -m unittest discover -s tests -q`.
- Combined stdout/stderr capture:
  `/home/caichenghang/.codex/happycodex-0.6.6-readme-license-suite.MZSx68/unittest-combined.txt`;
  mode 0600; 65,982 bytes; SHA-256
  `bb55886311658010274782e361ecebf8346eb538b78bc7f635b69db0a9be5039`.
- Separate true process-exit receipt:
  `/home/caichenghang/.codex/happycodex-0.6.6-readme-license-suite.MZSx68/unittest-exit.txt`;
  mode 0600; 2 bytes; value `1`; SHA-256
  `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`.
- Exact terminal lines are `Ran 158 tests in 38.279s` and
  `FAILED (failures=2, errors=41)`.
- The two failure headers exactly preserve the accepted baseline identities:
  - `test_exact_final_source_rejects_self_selected_projection_and_fake_diff
    (test_fixed_host_transaction_v2.FixedHostTransactionTests)
    (mutation='old-source')`
  - `test_old_source_components_cannot_back_a_new_dirty_evalspec
    (test_fixed_host_transaction_v2.FixedHostTransactionTests)`
- The additional error count is 41, not accepted 0. Every error terminates in
  `evaluation.provider.ProviderError: frozen source package identity differs`.
  The retained raw capture contains all exact headers and tracebacks. Compact
  error-header inventory is:

```text
test_cli_exact_request_rejects_bad_prerequisites_caps_and_collisions
test_cli_prepares_exact_only_request_equal_to_pure_contract
test_auth_staging_failure_precedes_durable_claim_and_raw
test_baseline_fatal_still_reveals_all_six_for_unified_judgment
test_behavior_transaction_is_exclusive_private_and_role_bound
test_capability_precedes_preparation_and_mapping_read
test_claim_directory_lock_is_cross_process
test_concurrent_selected_timeouts_share_remaining_wall
test_cross_filesystem_sandbox_alias_fails_before_effect
test_current_cap_overrun_is_persisted_before_stop
test_effect_marker_is_cross_process_one_shot
test_exact_diff_ignores_source_repo_external_diff_config
test_exact_final_returns_authoritative_reveal_timestamp
test_exact_final_source_is_clean_fully_bound_and_relocation_invariant
test_exact_final_source_rejects_untracked_support_and_hidden_oracle
test_exact_launcher_binding_changes_only_exact_host_identity
test_exact_launcher_link_failure_stops_before_provider_reach
test_exact_private_launcher_tamper_and_path_drift_fail_closed (tamper='replacement')
test_exact_private_launcher_tamper_and_path_drift_fail_closed (tamper='path-drift')
test_exact_source_projection_includes_managed_root_blob
test_failed_unified_holdout_judgment_blocks_exact_provider
test_fake_host_exact_only_refresh_composes_without_importing_prefix
test_forged_prefix_raw_and_known_failure_or_cap_block_launch (mode='forged')
test_forged_prefix_raw_and_known_failure_or_cap_block_launch (mode='failure')
test_forged_prefix_raw_and_known_failure_or_cap_block_launch (mode='cap')
test_host_policy_rejects_fixed_permission_drift_before_effect (mutation='filesystem')
test_host_policy_rejects_fixed_permission_drift_before_effect (mutation='network')
test_host_policy_rejects_fixed_permission_drift_before_effect (mutation='approval')
test_host_policy_rejects_fixed_permission_drift_before_effect (mutation='environment')
test_host_policy_rejects_fixed_tool_surface_drift_before_effect
test_only_same_stage_paired_inflight_prefix_is_legal
test_post_policy_source_or_git_config_mutation_stops_before_effect (relative='README.md')
test_post_policy_source_or_git_config_mutation_stops_before_effect (relative='.git/config')
test_private_sandbox_alias_tamper_fails_closed (tamper='template')
test_private_sandbox_alias_tamper_fails_closed (tamper='directory-mode')
test_private_sandbox_alias_tamper_fails_closed (tamper='replacement')
test_same_authority_invocation_cannot_run_in_two_execution_roots
test_spawn_error_persists_no_effect_attestation
test_timeout_kills_descendant_process_group
test_wall_cap_bounds_runner_timeout_before_effect
test_path_relocation_preserves_all_invocation_identities
```

- Accepted-baseline classification: `false`. Required shape was 158/2/0;
  actual shape is 158/2/41. The exact two baseline failures do not waive the 41
  new errors.
- Post-run claims and working inventory reverified exact. Candidate product
  bytes remain:
  `README.md` `5a584cf132187554ce3e2f466584f49bd700089915972b13cf17e9614a2ee336`,
  `README.en.md` `11f45423198a2af6269d1d18cf0c0dded10e9b1408801236dfddad76d4f442ad`,
  `LICENSE` `c8bd13985408f8a5357006c849ff1b42e196e580a71883d2337f7b1eeb0e43e1`,
  manifest `2c5c0af5e0864b467fa67a40cad7303c6cff250920674e303b755fb3f691e8a5`,
  and Skill `a1fbee68caf2d87481bfa06c1db6cdf34f7695c350c57c52e60ca98021ca28c9`.
  Marketplace/config hashes remain
  `752de5a68116a69025e6ac46e32e8e0a7512cf8e2f87078d53b719c4362dcbfe`
  and
  `0d4d88dab9263078ad0bb53cef52ae9c54b904f75900ad30a32609edc2b28802`.
- No candidate identity/freeze receipt was manufactured after the adverse
  result. No product edit, staging, commit, push, tag, GitHub Release, install,
  provider call, active-state mutation, cleanup, or retry occurred.
- `HC-RL-003` is consumed and returned adverse. Claims and raw capture remain
  held. Root must decide the next source/validation boundary; this receipt does
  not decide acceptance or task completion.
