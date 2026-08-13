# HappyCodex v1.0.0 Scope-stability Release

Keep this contract static. Reconstruct live state from Git, tests, and tools.

## Request and Outcome

- Verbatim request chain: inspect recent HappyCodex sessions for overly strict
  scope handling; obtain a Fable 5 review of the confirmed P1 findings; design
  the fix; `好的执行，发布，本地重装吧`.
- Outcome: publish and locally activate an immutable HappyCodex `v1.0.0` that
  separates authorization boundary, exact consumer candidate closure, and
  incidental tool footprint. Reversible Outcome-required work inside the
  selected workspace or task-owned boundary proceeds without per-path
  reauthorization, while shared, system, trust, credential, destructive,
  remote, paid, ambiguous, and consumer-input changes remain fail-closed.
- Done evidence: the exact frozen candidate passes all required offline checks
  and one fresh blocker-only Exact-final review; `origin/main`, annotated tag
  `v1.0.0`, and the public GitHub Release resolve to that commit; the personal
  source and enabled local plugin match its runtime projection modulo one
  helper-generated `1.0.0+codex.<timestamp>` cachebuster.

## Workspace and Change Boundary

- Workspace: `/home/caichenghang/projects/happycodex-1.0.0-scope-stability`,
  branch `codex/happycodex-1.0.0-scope-stability`, based exactly on
  `origin/main` commit `735b75d01feb99108cd08c81d7b40b24e9276664` and released
  `v0.16.0`.
- Mutable repository paths:
  - `.codex-plugin/plugin.json`
  - `README.md`
  - `README.en.md`
  - `docs/execplans/happycodex-1-0-0-scope-stability.md`
  - `skills/happycodex/SKILL.md`
  - `skills/happycodex/references/execplan.md`
  - `evaluation/provider-fixtures-v1.json`
  - `evaluation/hidden-oracles-v1.json`
  - `evaluation/report-schemas-v1.json`
  - `tests/test_attestation_contract.py`
- Writer overlap: one fixed Executor owns every repository path above until
  freeze. Root remains read-only over the candidate after handoff.
- Preservation: published tags and trees; deterministic stateless evaluator;
  exact consumer input closure; one writer per overlapping semantic resource;
  external-effect target/identity/cap/readback; one-shot effect handling;
  blocker-only exact-final admission; native Goal and review authority limits;
  installed `0.16.0` source/cache until rollback evidence is durable.
- Exclusions: evaluator runtime changes; Hook changes; per-tool path allowlists;
  automatic cache cleanup; ledger, path registry, side-effect controller,
  compatibility reader, migration, alias, dual write, force push, history
  rewrite, asset upload, branch/worktree cleanup, official-directory submission,
  or mutation of unrelated worktrees and repositories.
- Supported workflows: pip/uv/npm/Hugging Face-style additive caches and
  task-owned tmp/log/compiled output; in-workspace additions; safe task-owned
  environment relocation; system/user-site/shared installs; shared-cache
  deletion; trust/credential changes; Docker shared-daemon effects; remote or
  paid jobs; consumer-native freeze and one-shot publication.

## Stability Handoff

- Outcome/change boundary/Done: fixed as above; no unresolved product choice.
- Writer/current blockers: one HappyCodex Executor; no current blocker.
- Authorized increments: clarify installed guidance and template, add paired
  closed continuation cases and public-contract assertions, update bilingual
  summaries, and set the release version to `1.0.0`.
- Revision admission: only new decision-changing evidence or a concrete failure
  against Outcome, preservation, supported workflows, checks, or release
  identity may revise the candidate brief.

## Baseline and Allowed Breaks

- Baseline: the complete offline suite, Skill/plugin validators, JSON parsing,
  evaluator verification, line budgets, and `git diff --check` at the exact
  starting commit. Record any exact pre-existing failure before implementation.
- Allowed breaks: the former interpretation that every realized mutable path is
  also an authorization boundary is intentionally replaced. No evaluator
  schema version, record topology, invocation, install layout, external-effect,
  candidate-freeze, one-writer, or review-admission compatibility break is
  allowed.

## Consumer and Candidate

- Consumer: Codex plugin installer and users invoking
  `$happycodex:happycodex`; evaluator fixtures consume the installed guidance
  contract but remain maintainer-only material.
- Input closure: all changed repository paths listed above plus their modes and
  deletions; runtime projection is the manifest, both READMEs, the complete
  `skills/` tree, and `hooks/` tree selected by repository identity code.
- Native freeze: one clean Git commit over the baseline. Mutable worktree
  digests are not candidates.
- Terminal admission: one fresh no-history `happycodex_exact_final` over the
  complete readable baseline, candidate commit, this plan, diff, and check
  evidence; strict `GO` or `NOT_YET` with exact candidate SHA echo.
- Repair budget: one in-boundary repair and one replacement Exact-final if the
  first terminal result is `NOT_YET`; otherwise stop before publication.

## External Effects

All effects have a retry cap of zero. A partial, ambiguous, or unknown result
stops later mutation pending read-only reconciliation.

1. Push the frozen candidate once to `origin:refs/heads/main` after proving the
   remote still equals the baseline; read back the exact SHA.
2. Fast-forward the clean local `main` worktree once to the published commit;
   read back branch, HEAD, index, and worktree state.
3. Create one local annotated `refs/tags/v1.0.0` with title
   `HappyCodex v1.0.0`, push it once, and require local and remote tag objects to
   peel to the frozen commit.
4. Create one public, non-draft, non-prerelease GitHub Release for `v1.0.0`,
   with zero assets, title `HappyCodex v1.0.0`, and the exact notes below; read
   back tag, title, body, state, target, assets, and URL.
5. Before local source mutation, create exactly one rollback directory at
   `/home/caichenghang/.codex/happycodex-release-installs/happycodex-1.0.0-preinstall`
   containing the pre-mutation personal source and enabled `0.16.0` cache;
   verify inventories and byte hashes and retain it.
6. Materialize the release runtime projection in one task-owned temporary
   directory, synchronize it once to `/home/caichenghang/plugins/happycodex`,
   invoke the official plugin-creator cachebuster helper there exactly once,
   validate it, and prove cachebuster-normalized equality to the release. Do not
   edit marketplace or Codex configuration files.
7. Read the marketplace name from
   `/home/caichenghang/.agents/plugins/marketplace.json`, invoke
   `codex plugin add happycodex@personal --json` exactly once, and read back
   enabled state, local source path, generated version, source/cache equality,
   and cachebuster-normalized release equality.

## Exact GitHub Release Notes

HappyCodex v1.0.0 establishes the stable Codex-native reliability contract for
high-risk and long-running engineering work.

Highlights:
- Separates the workspace/task authorization boundary from the exact frozen
  consumer input closure and one-writer overlap.
- Treats bounded additive tool caches and task-owned temporary, log, and
  compiled output as reportable incidental footprint rather than scope drift.
- Keeps system or shared installs, destructive shared-cache changes, trust and
  credential state, remote or paid resources, ambiguous effects, and omitted
  consumer inputs fail-closed.
- Preserves stateless evaluation, consumer-native freeze, one-shot external
  effects, evidence-based convergence, and fresh blocker-only terminal review.

## Checks

- JSON parse all maintained JSON files and verify fixture/oracle/schema closure.
- Run focused public-contract and continuation tests, then
  `python3 -m unittest discover -s tests -v`.
- Run `python3 -m evaluation.cli verify` and report its exact disposition.
- Run Skill quick validation, plugin validation, Python compile/import checks,
  `git diff --check`, version/line-budget checks, and exact Git/index/path diff.
- Require paired assertions for: in-workspace/task-owned extension continues;
  additive incidental cache/tmp continues; system/user/shared install stops;
  destructive shared-cache change stops; uncertain classification stops.
- Verify no Hook/evaluator runtime change, no per-tool allowlist, and no new
  controller/ledger/registry mechanism.
- After commit, repeat candidate-bound checks against the immutable commit and
  require a clean source worktree before Exact-final.

## Stops and Recovery

Stop on candidate, source, scope, identity, index, writer, trust, version, tag,
remote, Release, marketplace, source/cache, or effect drift; any new failure; a
required unknown; or a partial/ambiguous external result. Retry only after
authentic zero-effect proof and only where this plan explicitly grants recovery;
this plan grants no external-effect retry.
