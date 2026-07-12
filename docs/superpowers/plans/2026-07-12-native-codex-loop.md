# Native Codex Loop Implementation Plan

**Goal:** Deliver and validate a personal Codex plugin for long tasks with one root
writer, evidence-driven planning, bounded investigative delegation, and an independent
native completion review.

**Architecture:** A plugin Skill controls decisions. Goal, native plan state, Git, and
tests retain execution evidence. A temporary clean Codex process invokes the native
review harness at Sol/max/read-only and emits a verified receipt. The plugin never writes
global Codex configuration or installs custom agents.

**Tech stack:** Markdown plugin/Skill, Python standard library, `unittest`, Git, Codex CLI
0.144.1.

## Global constraints

- Root is the only writer; children are non-writing investigative advisors.
- Runtime uses no external model, MCP, hook, recursive delegation, or multi-writer flow.
- Review must prove fresh Sol/max/read-only, approval never, and restricted network.
- Final HEAD must equal the latest successful review receipt; maximum two reviews.
- No plugin workflow mutates global AGENTS, config, hook, agent, or memory files.
- Fable change packet remains within 20 files and 2,000 changed textual lines.

## Task 1: Freeze evidence and contracts — complete

**Files:** `tests/fixtures/storyboard-red-baseline.json`, configuration/contract tests.

- [x] Record immutable Storyboard agent-call count, missed seams, report path, and hash.
- [x] Write RED tests for configuration safety, plugin surfaces, packet fields, and review.
- [ ] Freeze reproducible no-Skill versus Skill behavior-pressure evidence during the
  clean-home release preflight.

## Task 2: Resolve reviewer routing experimentally — complete

**Interfaces:** clean HOME/CODEX_HOME preflights and rollout inspection.

- [x] Test the named custom-agent design for discovery, freshness, effort, and sandbox.
- [x] Observe that task naming does not apply its model/effort config under Sol
  MultiAgent V2; remove the invalid production path.
- [x] Compare generic exec, argv injection, isolated config, and profile injection.
- [x] Select isolated config plus native `codex exec review --base`, which preserves the
  native review harness without exposing the task packet in argv.

## Task 3: Minimize the global configuration surface — complete

**Files:** plugin contract tests and user-facing documentation.

- [x] Reject the optional AGENTS trigger bridge after concurrent-edit, symlink-swap, and
  crash-consistency red-team analysis showed disproportionate transactional risk.
- [x] Keep deterministic explicit Skill invocation and metadata-only implicit discovery.
- [x] Contract-test that the plugin ships no global configuration writer.

## Task 4: Implement the Skill and native review runner — in progress

**Files:** plugin manifest, Skill/packets, `scripts/review_runner.py`, runner tests.

- [x] Author Goal-aware evidence/recovery loop and dirty-worktree routing.
- [x] Define complete delegation/review/disposition packets and root-only integration.
- [x] Make post-review mutation force a second review; cap at two and require SHA match.
- [x] Reject dirty source, non-ancestor base, nested output, and non-empty output.
- [x] Use a head-only bundle clone; disable project docs and nonessential capabilities.
- [x] Keep auth/runtime temporary and verify inner review context and unchanged trees.
- [x] Add wall-clock timeout, Linux PID-namespace cleanup, runtime/artifact hashes, and tests.
- [ ] Re-run full tests, linters/compilation, official Skill/plugin validators, and a clean
  real-CLI review after final refactoring.

## Task 5: Commit and obtain independent reviews — pending

**Artifacts:** external task/test packet, immutable base/head, native review and Fable
receipts.

- [ ] Keep changed file/line counts within the Fable packet contract.
- [ ] Commit a clean implementation head and run this plugin's own native review gate.
- [ ] Reproduce every finding; add regression tests before confirmed fixes.
- [ ] Run the bundled Fable review once on the clean committed range and independently
  disposition findings. Use its second invocation only for confirmed fix IDs.
- [ ] If any fix changes task artifacts, create and review a new immutable head.

## Task 6: Install and clean-home preflight — pending

- [ ] Create/update the personal marketplace via the plugin-creator helper.
- [ ] Sync the verified source to `~/plugins/native-codex-loop` and install it.
- [ ] Under an isolated HOME/CODEX_HOME, prove Skill discovery, no custom enhancements,
  real native review, exact runtime context, secret cleanup, and final-SHA gate behavior.
- [ ] Run three fresh long-task pressure cases and require three of three review receipts.

## Task 7: Matched Storyboard replay — pending

**Inputs:** historical R0 `0d66b59`, common base `816ca31`, original seven-test oracle,
and two frozen supplemental route-seam regressions.

- [ ] Construct an R0-only candidate Git object set; keep later commits/oracles outside
  the candidate's readable OS boundary and keep tooling offline.
- [ ] Arm A freezes R0 without review. Arm B exposes only the plugin's fresh review/fix
  intervention, preserving B-R0 and B-R1.
- [ ] Reviewer and fixer cannot see historical answers, Claude output, or hidden tests.
- [ ] After freeze, run identical full pytest, Ruff, mypy, seven original hidden tests,
  and the fabricated-visible-delta and missing-storyboard-IR regressions.
- [ ] Report review discovery yield, confirmed fixes, no-regression result, token/time,
  repeated work, and limitations. Do not call this a Goal/compaction causal test.

## Stop conditions

Do not install or claim success if the real preflight cannot prove fresh/max/read-only,
credentials survive cleanup, final HEAD differs from the receipt, Fable integrity fails,
or Storyboard review finds neither known route seam. Report the failed gate and preserve
artifacts instead of silently weakening it.
