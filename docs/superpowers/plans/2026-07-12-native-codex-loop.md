# Native Codex Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver and validate a personal Codex plugin that runs long tasks with a single root writer, evidence-driven planning, safe read-only delegation, and an independent completion review.

**Architecture:** A plugin-distributed Skill controls decisions; a transactional setup script installs a standalone read-only reviewer because plugin manifests cannot register custom agents. Native Goal, plan state, Git, and tests retain execution state; hooks and mandatory ExecPlan files stay out of V1.

**Tech Stack:** Codex plugin/Skill Markdown, TOML, Python 3 standard library, `unittest`, Git, Codex CLI 0.144.1.

## Global Constraints

- Codex root is the only writer; all subagents are read-only.
- Runtime uses no external model, MCP, hook, recursive agent, or automatic multi-writer worktree.
- Reviewer is `gpt-5.6-sol`, `model_reasoning_effort = "max"`, and `sandbox_mode = "read-only"`.
- Setup never edits `config.toml` and fails closed on collisions, malformed markers, overrides, or drift.
- Review is bounded to one initial pass and one optional fresh pass after confirmed fixes.

---

### Task 1: Freeze RED evidence and configuration contracts

**Files:**
- Create: `tests/fixtures/storyboard-red-baseline.json`
- Create: `tests/test_configure.py`
- Create: `tests/test_contracts.py`

**Interfaces:**
- Consumes: the Storyboard four-arm result and the design document.
- Produces: executable expectations for `scripts.configure` and all plugin artifacts.

- [ ] Record the immutable Storyboard RED facts: Codex-native agent calls `0`, the two missed seams, and frozen source report path.
- [ ] Write `unittest` cases for install, doctor, uninstall, idempotence, collision, override, malformed markers, and drift.
- [ ] Write artifact contract tests for manifest, Skill, packet reference, and reviewer TOML.
- [ ] Run `python3 -m unittest discover -s tests -v`; expect import/file failures because implementation does not exist.

### Task 2: Implement the transactional custom-agent setup

**Files:**
- Create: `scripts/configure.py`
- Create: `assets/agents/native-codex-reviewer.toml`

**Interfaces:**
- Produces: `install(codex_home, plugin_root, with_guidance)`, `doctor(codex_home, plugin_root)`, `uninstall(codex_home, plugin_root)`, and CLI subcommands with JSON output.

- [ ] Implement preflight validation and name scanning before writes.
- [ ] Implement atomic `0600` writes, state hashes, exact managed-block insertion/removal, and drift rejection.
- [ ] Run `python3 -m unittest tests.test_configure -v`; expect all setup tests to pass.
- [ ] Refactor only after the full test module remains green.

### Task 3: Scaffold and author the plugin Skill

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `skills/native-codex-loop/SKILL.md`
- Create: `skills/native-codex-loop/agents/openai.yaml`
- Create: `skills/native-codex-loop/references/packets.md`

**Interfaces:**
- Consumes: custom agent name `native_codex_reviewer` and the packet fields specified by the design.
- Produces: implicit/explicit Skill discovery and a complete execution/review protocol.

- [ ] Run the official plugin and Skill scaffold helpers.
- [ ] Replace placeholders with minimal trigger metadata, workflow instructions, packet contracts, and UI prompts.
- [ ] Run `python3 -m unittest tests.test_contracts -v`; expect all contract tests to pass.
- [ ] Run Skill quick validation and plugin validation; expect exit code `0` from both.

### Task 4: Isolated capability and behavior preflight

**Files:**
- Create: `scripts/preflight.py`
- Test: `tests/test_preflight.py`

**Interfaces:**
- Produces: a temporary clean-home run directory and a machine-readable receipt proving discovery, freshness, and read-only behavior.

- [ ] Test command construction, secret-safe copying, tree hashes, and receipt parsing before implementing the runner.
- [ ] Run a nonce custom-agent preflight under isolated `HOME` and `CODEX_HOME`.
- [ ] Run a behavioral Skill pressure scenario and inspect JSONL for reviewer use, no child writes, and withheld premature completion.
- [ ] If custom-agent freshness or read-only enforcement fails, stop and switch to the documented ephemeral-review backup.

### Task 5: Verify, commit, and obtain Fable review

**Files:**
- Create outside repo: task, test receipt, packet, and review receipt.

**Interfaces:**
- Produces: immutable base/head commits and dispositioned Fable findings.

- [ ] Run full unit tests and both official validators fresh.
- [ ] Commit a clean implementation head and capture base/head SHA.
- [ ] Run the bundled Fable prepare/run flow once in the foreground.
- [ ] Reproduce every finding; write regression tests before fixes; rerun full verification.
- [ ] Use the optional second Fable invocation only for confirmed fixed finding IDs.

### Task 6: Paired Storyboard replay

**Files:**
- Create under the benchmark control directory: neutral common base, A/B manifests, prompts, logs, R0/R1 SHAs, verification receipts, and result report.

**Interfaces:**
- Consumes: `base-four-arm.bundle`, unchanged `TASK.md`, original 7-test oracle, and two frozen supplemental regression oracles.
- Produces: normal Goal arm A, plugin Goal arm B, B-R0/B-R1, and comparable process/quality metrics.

- [ ] Create two independent clones from a protocol-neutral common SHA with isolated homes and equal resources.
- [ ] Preflight A cannot see the Skill/reviewer; B can discover it and cannot write from the reviewer.
- [ ] Run both arms with max planning, sol-high execution, Goal, offline tooling, and the same wall-clock limit.
- [ ] Freeze candidates before mounting hidden tests; verify full pytest, Ruff, mypy, 7 original hidden tests, and 2 supplemental oracles.
- [ ] Report overall A/B outcome and the reviewer-specific R0→R1 yield without treating historical cross-task results as causal.
