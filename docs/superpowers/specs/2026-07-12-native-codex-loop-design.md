# Native Codex Loop Design

## Objective

Build a personal Codex plugin that reduces omissions in long, high-risk implementation
without introducing another runtime model. The root thread remains the only writer.
Goal, native plan state, Git, tests, bounded investigative delegation, and a fresh
`gpt-5.6-sol` max review address different failure modes.

## Evidence and scope

The Storyboard four-arm experiment is the RED baseline. Codex-native was allowed
multi-agent capability but invoked no child and missed two reproducible route seams.
Claude-native's measurable advantage came from one fresh reviewer rather than broad
fan-out. An exploratory, non-frozen pressure sample suggested that loading the Skill
improves review uptake; release evidence will come from the reproducible clean-home
pressure cases in the implementation plan.

V1 therefore optimizes reviewer uptake, plan fidelity, and single-writer recovery. It
includes one plugin Skill, complete packet contracts, and an isolated native-review
adapter. It excludes global configuration writes, hooks,
MCP, external models,
recursive or implementation delegation, multi-writer worktrees, Best-of-N, a scheduler,
and mandatory ExecPlan files. Fable audits the committed plugin but is not a dependency.

## Empirical architecture pivot

The first design used a custom agent TOML to pin a fresh max/read-only reviewer. A clean
preflight disproved the key assumption on Codex CLI 0.144.1: `task_name` named the child
but did not load the named agent config; the child was fresh and read-only only because
it inherited the root context, and its effort remained `high`. This matches the current
Sol MultiAgent V2 reports in OpenAI Codex issues 31814, 31893, and 32031.

The predefined switch condition therefore fired. V1 does not ship a custom agent or
claim named-agent routing. It uses a narrow adapter around the native
`codex exec review` harness. Real CLI preflight proved that this harness creates one
outer exec rollout and one fresh inner `{subagent: "review"}` rollout whose actual
context is Sol/max/read-only, approval never, network restricted, and multi-agent off.

## Candidate comparison

1. **Skill only:** cannot mechanically pin review freshness, effort, sandbox, or network.
2. **Skill + named custom agent:** preferred in theory, rejected by the runtime preflight.
3. **Skill + isolated native review adapter:** selected; retains Codex's review prompt and
   makes the critical runtime properties observable.
4. **Generic `codex exec` reviewer:** viable fallback, but loses the native review harness.
5. **Hook-enforced loop:** deferred because Stop blocking can loop and hooks cannot prove
   that the final reviewed SHA is current.

## Artifacts

The source repository is `~/projects/native-codex-loop`; the validated install mirror is
`~/plugins/native-codex-loop` and is exposed through the personal marketplace.

- `.codex-plugin/plugin.json`: discovery metadata and Skill entrypoint.
- `skills/native-codex-loop/SKILL.md`: Goal-aware execution, replanning, delegation, and
  completion gates.
- `skills/native-codex-loop/references/packets.md`: complete delegation, review, and
  finding-disposition contracts.
- `scripts/review_runner.py`: isolated native review plus verified audit receipt.
- `tests/`: packaging, global-boundary contracts, runner isolation, and frozen RED evidence.

## Runtime behavior

1. Freeze objective, criteria, exclusions, baseline, Goal identity, and verification in
   an immutable external Task Contract whose path/hash remains in native plan state.
   Preserve user changes and use a root-owned worktree when needed.
2. Use Goal only when explicitly requested. Keep the native plan live and evidence-led;
   it is a decision record rather than a fixed screenplay.
3. Root alone edits. A direct `fork_turns="none"` child receives only a disposable
   head-only clone and a complete independent investigative packet; source and Git
   common-dir fingerprints bracket the call. Child output never becomes evidence until
   root verification.
4. Reconcile every material result with acceptance criteria and update the plan without
   silently lowering the target.
5. Run checks and freeze a clean candidate commit. Send only factual context to a fresh
   native review process. Root reproduces every finding and alone applies fixes.
6. Any post-review task change requires a second fresh review. Two invocations are the
   maximum; completion requires current `HEAD` to equal the latest successful receipt.
7. Complete an active Goal only after criteria, checks, findings, Git state, and delegated
   work are all accounted for.

## Review isolation

The runner fails closed unless base is an ancestor of the requested clean HEAD and the
output is outside the source repository. It creates a head-only Git bundle so unrelated
refs and unreachable oracle objects do not enter the review clone. An empty temporary
HOME/CODEX_HOME receives only auth, optional model cache, and a generated
`developer_instructions` packet; `project_doc_max_bytes=0` prevents repository AGENTS
injection. Plugins, apps, hooks, multi-agent, browser, image, computer, and web features
are disabled. Runtime rollout evidence must confirm Sol/max/read-only/never/restricted.

The runner reads a private immutable Task Contract, verifies its exact inlined packet
block and hash, and binds one durable review series to the canonical repository and frozen task
base. It records attempts before execution and refuses a third call or an empty review
range. Credentials, config, sessions, and clone exist only in a temporary directory that is
deleted on success, error, or timeout. Persisted artifacts are the reviewed packet,
native review, JSONL events, stderr, and a receipt with runtime values and hashes. Source
and clone HEAD/full content plus source HEAD/Git-visible content are checked before and
after review. Clone paths in findings are mapped back to the canonical source path.

The receipt is an auditable run record, not a cryptographic signature. Read-only Codex
uses a positive filesystem allowlist. Credentials/canary live in private user-runtime
tmpfs while helper/config/clone remain in the CLI-compatible temporary path. Before model
launch a native sandbox preflight proves source, packet, contract, credentials/config are
unreadable, network is denied, and only the clone/helper are readable;
the reviewer must repeat an exact credential canary before an exact base-to-head diff.
Turn context rejects unknown host grants. Every Codex process is wrapped in an
unprivileged Linux user/PID/mount namespace so detached descendants die on normal exit
or timeout. Historical-oracle experiments still make oracle repositories inaccessible
outside the candidate runtime. V1 requires Linux `/usr/bin/unshare`, private
`/run/user/<uid>` tmpfs, a readable `auth.json`, and
the tested CLI contract; real preflight must be rerun after Codex CLI upgrades.

## Global configuration boundary

The plugin never writes global `AGENTS.md`, `config.toml`, hooks, agents, or memory.
Explicit `$native-codex-loop` invocation is the deterministic activation path; implicit
activation relies only on installed Skill metadata. This removes a cross-file transaction
and concurrent-user-edit surface from the trusted implementation.

## Recovery and verification

Task Contract + Goal + plan + Git + test/review receipts are the recovery surfaces.
Resume verifies the contract hash and Goal thread/objective before inspecting live
agents and continuing; it never reconstructs missing criteria from context memory.

Verification consists of unit and contract tests, official plugin/Skill validators, a
real isolated CLI review, three fresh behavior-pressure scenarios, a committed Fable
review, and a matched Storyboard replay. The replay compares the same historical R0 with
and without the review intervention, freezes pre/post-review SHAs, keeps oracle data
offline and inaccessible until freeze, and runs the original seven plus two supplemental
route-seam regressions.

## Readiness

`ready_for_committed_review`: unit tests and a real native-review smoke run pass. Release
still requires final validators, immutable commit, Fable disposition, installation
preflight, and the Storyboard matched replay.
