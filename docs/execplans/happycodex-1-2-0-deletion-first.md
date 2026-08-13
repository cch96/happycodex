# HappyCodex v1.2.0 Deletion-first Candidate

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: explain why one session said read-only delegation was
  prohibited; assess whether HappyCodex should be optimized; obtain a Fable 5
  review; remove rules whose absence is better than their presence when both
  reviews agree; `好的执行`.
- Outcome: produce, but do not publish or install, a local `1.2.0` candidate
  that preserves HappyCodex's decision-bearing safety contract while deleting
  duplicated host guidance and compressing repeated routing, convergence,
  candidate, review, and effect prose. Correct the delegation ambiguity so a
  Skill-directed scout or worker counts as an explicit request under a host
  rule that only prohibits proactive delegation, without overriding a real
  host denial.
- Done evidence: the candidate is materially shorter than `v1.1.0`, the public
  overview points to the Skill instead of restating it, scenario-to-decision
  tests cover the delegation bridge and advisory-pass stopping behavior, all
  offline checks pass, and one fresh blocker-only Exact-final review returns
  `GO` for the exact frozen candidate tree.

## Workspace and Change Boundary

- Workspace: `/home/caichenghang/projects/happycodex`, branch
  `codex/happycodex-1.2-deletion-first`, based exactly on commit
  `88cfa23118e860b344759f92f0bebf760c52da12`, released tag `v1.1.0`.
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `docs/execplans/happycodex-1-2-0-deletion-first.md`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `evaluation/provider-fixtures-v1.json`
  - `evaluation/hidden-oracles-v1.json`
  - `evaluation/report-schemas-v1.json`
  - `tests/attestation_fixtures.py`
  - `tests/test_attestation_contract.py`
- Writer overlap: one fixed HappyCodex Executor owns every product or test path
  above except this already-frozen plan. Root remains read-only over those paths
  after handoff and may only return a concrete blocker to that same writer.
- Preservation: published tags and reachable trees; deterministic stateless
  evaluator and fixed five/six/one topology; existing scenario decisions;
  exact consumer input closure; one writer per overlapping resource; fresh
  blocker-only terminal admission; one-shot effects; truthful closure; no
  manufactured authority.
- Exclusions: Hook or evaluator-runtime redesign; a new agent, ledger, graph,
  registry, controller, migration, compatibility reader, alias, or dual write;
  Fable as a default gate; installation, activation, provider/model calls,
  commit, stage, push, tag, Release, branch cleanup, or unrelated worktree
  mutation.

## Agreed Deletion-first Contract

- Keep the sharp deltas: ExecPlan trigger and task facts; authorization boundary
  distinct from realized paths; exact compatibility-break authorization;
  incidental footprint and stop classes; advisory evidence adds no authority;
  one writer per overlap; consumer-native immutable closure; fresh no-history
  blocker-only Exact-final; one repair plus one replacement review; one-shot
  effects; truthful closure; behavior-tested Goal/advisory-pass renewal.
- Merge scouting, supporting-body delegation, worker routing, and fallback into
  one routing clause. A Skill-directed delegation is an explicit Skill request
  when the host allows delegation requested by an applicable Skill. This bridge
  cannot defeat an explicit host denial. Fallback requires a spawn failure,
  concrete missing capability/tool, explicit denial, or a body that cannot be
  bounded without transferring primary judgment.
- Merge stability handoff, advisory-pass admission, concrete-failure revision,
  and focused verification into one convergence clause; merge freeze and
  terminal identity into one candidate clause; merge terminal review and its
  single repair cycle into one review clause; merge effects and truthful closure
  into one closure clause.
- Delete duplicated generic host rules, Hook implementation prose, exact worker
  payloads, typed-reader preference, redundant review-suppression enumeration,
  detailed Goal continuity prose, and README copies of the full contract.
- Tests must assert scenario inputs and required decisions, not lock the rewrite
  to long exact phrases. Existing scenario outcomes must remain green.

## Baseline, Consumer, and Candidate

- Baseline: `python3 -B -m unittest discover -s tests -v` passed 101 tests at
  the exact starting commit before product edits. The real index and worktree
  were clean.
- Allowed break: public wording and fixture prose may change, and the candidate
  version becomes `1.2.0`. No evaluator schema version, topology, record,
  invocation, runtime, installation-layout, or effect compatibility break is
  allowed.
- Consumer: Codex plugin installer and users invoking
  `$happycodex:happycodex`; evaluator evidence stays maintainer-only.
- Input closure: every changed path above, including modes and deletions. Freeze
  with a temporary Git index into one immutable tree object without changing
  the real index, branch ref, or worktree. A mutable worktree digest is invalid.
- Terminal admission: one fresh no-history `happycodex_exact_final` receives
  the exact baseline commit, frozen candidate tree, readable diff, this plan,
  and check evidence. It must return strict `GO` or `NOT_YET` and echo the exact
  candidate tree identity. One in-boundary repair and one replacement review
  are available after a concrete `NOT_YET`; otherwise stop.

## Checks

- Parse all maintained JSON through the existing suite and preserve the fixed
  five/six/one evaluator topology and all existing behavior decisions.
- Add behavior scenarios proving: an applicable Skill plus exposed native
  capability under a proactive-only restriction attempts delegation; a real
  host denial does not; proven unavailable/failed delegation permits direct
  fallback; a completed advisory pass without renewal stops and is not `GO`.
- Run focused public-contract tests, then
  `python3 -B -m unittest discover -s tests -v`.
- Run Skill Creator `quick_validate.py`, plugin `validate_plugin.py`,
  `python3 -B -m evaluation.cli verify`, `git diff --check`, version and line
  budgets, prohibited-design searches, exact path diff, real-index identity,
  branch/HEAD/tag identity, and candidate-tree reconstruction checks.
- Verify no Hook/evaluator runtime change and no maintainer evidence leaks into
  installed product guidance.

## Effects, Stops, and Closure

- This task authorizes no external effect. Do not commit, stage, push, tag,
  publish, install, activate, or call another external model/provider.
- Stop on scope, writer, source, index, candidate, version, topology, schema,
  trust, or test drift; any new failure; any unresolved required unknown; or a
  terminal `NOT_YET` after the single repair cycle.
- Report the exact branch, baseline, changed paths, test results, frozen tree,
  terminal decision, and dirty/uncommitted status. Say explicitly that no
  publication or installation occurred.
