# HappyCodex 0.12 external-review routing ExecPlan

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome
- Verbatim request: `好的执行吧`, authorizing the immediately preceding clean-break proposal and its final omission check: preserve boundary-routed native readers and workers, but make an external model/tool challenge or review a direct Primary tool call rather than work relayed through a native subagent.
- Outcome: a local HappyCodex 0.12 candidate based exactly on published `v0.11.0` has one closed routing rule: native read-only agents handle bounded supporting evidence, one native worker handles stable substantial implementation, and an external challenge or review is invoked and observed directly by the Primary without a native-agent relay; the matching personal plugin is activated locally.
- Done evidence: product guidance, bilingual summaries, evaluator fixtures/oracles/schemas, and regression tests agree on the routing split; version is 0.12.0; required offline checks pass; the complete candidate is frozen as a Git tree and receives one fresh blocker-only `GO`; `happycodex@personal` is enabled at the matching cachebuster version and its installed runtime files match the frozen candidate apart from the manifest cachebuster.

## Workspace and change boundary
- Workspace: `/home/caichenghang/projects/happycodex-0.12-external-review-routing`, branch `codex/happycodex-0.12-external-review-routing`, source `v0.11.0` commit `6edcffd309fa733215a17a6eed56ce21064c2e9c`.
- Mutable paths/resources: `.codex-plugin/plugin.json`; `README.md`; `README.en.md`; `skills/happycodex/SKILL.md`; this ExecPlan; `evaluation/provider-fixtures-v1.json`; `evaluation/hidden-oracles-v1.json`; `evaluation/report-schemas-v1.json`; `tests/attestation_fixtures.py`; `tests/test_attestation_contract.py`; after terminal `GO` only, the corresponding runtime-package files under `/home/caichenghang/plugins/happycodex`, its manifest cachebuster, and the `happycodex@personal` local installation/cache selected by `/home/caichenghang/.agents/plugins/marketplace.json`.
- Preservation: every published tag and reachable tree; `/home/caichenghang/projects/happycodex` and its dirty 0.10 state; all other worktrees, branches, indexes, active plugins, marketplace entries, external role configuration, and rollback state; Primary judgment ownership, one writer per overlapping mutable resource, conditional challenge/review behavior, stateless evaluator design, fixed evaluator topology, and zero-config/model-agnostic installation.
- Exclusions: compatibility readers, migration, alias, dual wording, fixed waves, fixed agent counts, role state machines, magic thresholds, custom-agent installation, pinned models or efforts, native relay agents for external calls, live Fable/provider/model calls, push, tag, GitHub Release, remote publication, marketplace editing, or mutation of any path not named above.
- Supported workflows: automatic Skill triggering; Primary judgment and focused verification; one bounded native evidence reader; independent native readers only when concurrency materially helps; one stable substantial native worker; small direct corrections; direct external tool-backed challenge/review; distinct conditional native exact-final review; candidate freezing; truthful one-shot local activation.

## Baseline and allowed breaks
- Baseline: exact `v0.11.0` ran `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` with 83 tests, zero failures, and zero errors; Skill Creator and plugin validators also passed.
- Allowed breaks: callers that previously wrapped an external challenge/review inside a native relay agent are intentionally redirected to a direct Primary tool call. Native evidence readers, native implementation workers, and the distinct native blocker-only terminal reviewer remain supported. No evaluator topology, record type, install layout, or other public behavior break is allowed.

Never call an accepted failing baseline green or accept a new failure silently.

## Consumer and candidate
- Consumer: a fresh Codex task loading the packaged HappyCodex Skill, the repository evaluator and tests, and the personal local plugin loader.
- Input closure: `.codex-plugin/plugin.json`, both README files, the complete `skills/` tree, this ExecPlan, all changed evaluator fixtures/oracles/schemas and tests, plus the seven-file personal runtime package projection and cachebuster-normalized installed projection.
- Native freeze: a temporary-index Git tree containing only the exact candidate closure over `v0.11.0`; the real index remains untouched.

## External effects

- Effect: refresh and reinstall the local personal plugin after terminal `GO`; target: `/home/caichenghang/plugins/happycodex` and `happycodex@personal`; identity source: frozen Git tree plus the personal marketplace source path; cap: one exact runtime-package projection update, one cachebuster helper invocation, and one `codex plugin add happycodex@personal` attempt; observation predicate: plugin list reports enabled matching 0.12 cachebuster and installed runtime bytes equal the candidate with only the expected manifest version suffix; recovery cap: none after an ambiguous or partial effect.

## Checks

- Required checks: focused routing contract test; full offline unittest suite; Skill Creator `quick_validate.py`; plugin validator; JSON parsing through tests; version and prohibited-design searches; `git diff --check`; branch, HEAD, real-index, worktree, candidate-tree, published-tag, unrelated-worktree, personal-source, and installed-cache identity checks.
- Terminal review trigger/brief: public Skill/evaluator routing semantics plus local activation. Review the frozen tree blocker-only against Done, preservation, supported workflows, direct external-call separation, distinct native exact-final behavior, no overdesign regressions, zero-config installation, and exact candidate closure.

## Stops and recovery

Stop on scope, identity, index, trust, or source drift; a new failure; a required unknown; reviewer `NOT_YET`; or a partial/ambiguous install effect. Retry only after authentic proof of no effect and only within the recorded recovery cap.

After a continuity break, confirm the old writer cannot resume, reread this plan, inspect Git/index/candidate/effect state, and rederive current facts.
