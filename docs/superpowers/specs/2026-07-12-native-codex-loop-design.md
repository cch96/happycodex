# Native Codex Loop Design

## Objective

Build a personal Codex plugin that makes long, high-risk implementation work less likely to omit requirements while keeping Codex as the only runtime model. The root thread remains the only writer. Native Goal and plan state provide continuity; narrowly scoped read-only agents provide independent evidence; a fresh `gpt-5.6-sol` reviewer gates completion.

## Evidence and scope

The Storyboard four-arm experiment is the RED baseline. Its Codex-native arm was allowed multi-agent capability but invoked no subagent and missed two reproducible route seams. The Claude-native arm's measurable advantage came from one fresh reviewer, not broad fan-out. This design therefore optimizes reviewer uptake, plan fidelity, and safe delegation rather than agent count.

V1 includes:

- one installable plugin and one implicitly discoverable workflow Skill;
- one explicitly installed personal custom reviewer agent;
- Goal-aware execution, evidence-driven plan changes, complete task packets, and a bounded review/fix gate;
- setup, doctor, and uninstall operations that preserve unrelated user configuration;
- isolated capability and behavior preflights plus a paired Storyboard replay.

V1 excludes hooks, MCP, external models, recursive delegation, multiple writers, automatic worktree orchestration, Best-of-N, a scheduler, and a mandatory ExecPlan file. Fable is used only to audit this plugin's committed implementation.

## Candidate comparison

1. **Skill only.** Smallest, but cannot pin a reviewer model, fresh context, or read-only sandbox. Rejected.
2. **Plugin + Skill + standalone custom reviewer.** Uses native Goal, plan, and multi-agent surfaces while isolating the one agent role supported by experiment evidence. Selected.
3. **Hook-enforced reviewer.** More mechanical, but current hook handlers cannot directly launch an agent, plugin hook trust is stateful, and Stop blocking can loop. Reserved as the only backup if forward tests show repeated review skipping.
4. **External CLI orchestrator.** Deterministic but rebuilds Codex session management and weakens interactive recovery. Rejected unless custom-agent freshness or read-only isolation fails.

## Architecture

The source repository lives under `~/projects/native-codex-loop`. A validated install mirror lives under `~/plugins/native-codex-loop` and is exposed through the personal marketplace.

The plugin contains:

- `.codex-plugin/plugin.json`: versioned discovery metadata and Skill entrypoint;
- `skills/native-codex-loop/SKILL.md`: the execution decision loop;
- `skills/native-codex-loop/references/packets.md`: exact delegation and review packet contracts;
- `assets/agents/native-codex-reviewer.toml`: a read-only, max-effort reviewer template;
- `scripts/configure.py`: transactional `install`, `doctor`, and `uninstall` for the standalone agent and optional global trigger bridge;
- tests that enforce packaging, configuration safety, and workflow invariants.

The plugin manifest cannot register custom agents. Setup copies the reviewed template into `$CODEX_HOME/agents/`. It does not modify `config.toml`. An optional, minimal managed block in `$CODEX_HOME/AGENTS.md` tells future long-task sessions to load the Skill; explicit `$native-codex-loop` invocation remains the deterministic entrypoint.

## Runtime behavior

1. Freeze the task objective, acceptance criteria, baseline state, and validation commands. Use Goal only when the user explicitly requests Goal-backed execution.
2. Keep the root thread as the sole source-code writer. Use native plan state as a live decision record, not a fixed script.
3. Delegate only read-only work that is independent and can be expressed as a complete packet. Parallelize only packets without shared mutable output.
4. After every material result, compare evidence with acceptance criteria. Update the plan when evidence changes the next best action; never silently lower acceptance.
5. Before completion, run required verification and freeze a clean candidate commit. Spawn `native_codex_reviewer` with no parent-turn inheritance and a factual review packet.
6. The root independently reproduces every finding. It alone fixes confirmed findings and reruns focused plus final verification. One fresh re-review is allowed after material fixes; two review invocations is the hard limit.
7. Mark Goal complete only after verification, finding disposition, clean state, and acceptance coverage are all evidenced.

## Installation safety

`configure.py` validates every precondition before writing. It scans all agent TOMLs by `name`, rejects collisions, writes atomically with mode `0600`, and records version and hashes in `$CODEX_HOME/native-codex-loop/install.json`.

The optional guidance bridge uses unique start/end markers, preserves every unrelated byte, is idempotent, and fails closed on malformed markers or a non-empty `AGENTS.override.md`. Uninstall removes only content whose recorded hash still matches; user-modified managed files are preserved and reported as conflicts.

## Failure handling and backup

Capability preflight must prove custom-agent discovery, fresh context, and actual read-only write blocking. Failure does not silently fall back. The sole backup is an isolated, ephemeral `codex exec review` process pinned to the same model and effort. Hooks are reconsidered only if three forward-test pressure scenarios show that Skill plus guidance repeatedly skips the review gate.

A durable ExecPlan or checkpoint ledger is added only if a natural compaction/resume test shows that Goal + native plan + Git cannot recover the objective, current step, unfinished acceptance criteria, and latest evidence.

## Verification

- Unit tests: empty install, preservation, idempotence, name collision, malformed marker, override, drifted uninstall, and exact restoration.
- Contract tests: manifest, Skill metadata, reviewer model/effort/sandbox, no hooks/MCP, and required workflow invariants.
- Official validators: plugin validator and Skill quick validator.
- Isolated preflight: clean `HOME` and `CODEX_HOME`; reviewer discovers a child-only nonce, cannot write, and exposes no custom MCP/plugin/external model.
- Behavioral forward test: a fresh root uses the Skill, remains the only writer, invokes the reviewer, and withholds completion until findings are dispositioned.
- Fable review: immutable base/head, clean tree, fresh required-check receipt, at most two invocations.
- Storyboard A/B: same neutralized base, task, resources, model routing, Goal, time limit, and hidden tests; treatment differs only by this plugin and reviewer. Preserve treatment R0 (pre-review) and R1 (post-fix).

## Readiness

`ready_with_assumptions`: implementation may proceed. Installation is blocked until preflight proves custom-agent discovery, fresh-context isolation, and hard read-only behavior.
