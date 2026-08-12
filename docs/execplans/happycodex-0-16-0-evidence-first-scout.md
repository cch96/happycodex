# HappyCodex v0.16.0 Evidence-first Scout

## User Request

> 好的执行修改， 发布，并本地重装

## Outcome

Ship a new immutable `v0.16.0` release that makes HappyCodex use one native
read-only scout before broad architecture or design recommendations when the
answer depends on unread current implementation facts. Keep small bounded
lookups direct, keep judgment with the Primary, publish the exact reviewed
commit to `origin/main`, and reinstall that release locally through the
`personal` marketplace with a cachebuster version.

## Repository and Version

- Repository: `/home/caichenghang/projects/happycodex`
- Starting source: `origin/main` at
  `940f3ca33edf9f7d4df2c005d4ff8ee6196577c0`
- Starting immutable release: `v0.15.1`
- Candidate release: `v0.16.0`
- Local marketplace source: `/home/caichenghang/plugins/happycodex`

## Mutable Boundary

- `docs/execplans/happycodex-0-16-0-evidence-first-scout.md`
- `skills/happycodex/SKILL.md`
- `.codex-plugin/plugin.json`
- `evaluation/provider-fixtures-v1.json`
- `evaluation/hidden-oracles-v1.json`
- `evaluation/report-schemas-v1.json`
- `tests/test_attestation_contract.py`
- `README.md`
- `README.en.md`
- After publication only: the local marketplace source at
  `/home/caichenghang/plugins/happycodex`, limited to synchronizing the exact
  release tree and applying the plugin cachebuster.

## Preservation Boundary

- Do not rewrite an existing tag or release.
- Do not add a custom agent, model pin, Fable dependency, mutable ledger,
  compatibility reader, alias, migration, or dual write.
- Keep zero-configuration native-agent routing and the single-writer rule.
- Do not force a scout for one or two bounded direct lookups or for facts
  already verified in the current context.
- Scout output is factual evidence with citations, searched scope, and
  unknowns; recommendations and final judgment remain with the Primary.
- Keep the repository evaluator deterministic, stateless, and offline.

## Acceptance Checks

- Skill discovery advertises the new recommendation/current-facts trigger.
- Installed guidance states the broad-scout rule, factual-output contract, and
  bounded-lookup exception without prescribing exactly five questions.
- Provider fixtures, hidden oracles, report schemas, and tests cover both the
  broad recommendation scenario and its bounded negative control.
- All offline tests pass and the source worktree is clean after the candidate
  commit.
- A fresh exact-final reviewer returns `GO` for the immutable candidate commit.
- `origin/main`, annotated tag `v0.16.0`, and the GitHub Release resolve to the
  exact reviewed commit.
- `happycodex@personal` is enabled locally as
  `0.16.0+codex.<timestamp>` and the published source worktree remains clean.

## External Effects

1. Push the reviewed candidate once as `HEAD:refs/heads/main`; read back the
   remote branch SHA and require the exact candidate commit.
2. Push the new annotated `refs/tags/v0.16.0` once; read back both the tag object
   and peeled commit and require the exact candidate commit.
3. Create the GitHub Release for `v0.16.0` once; read back its published status,
   URL, and tag identity.
4. Reinstall `happycodex@personal` once after cachebusting its synchronized
   local source; read back enabled state, source path, and version.

Each effect has a retry cap of zero. An ambiguous or partial result stops the
sequence for read-only reconciliation. No later effect proceeds if an earlier
identity check fails.

## Review and Repair

- Freeze the candidate as a local commit after tests pass.
- Give one fresh no-history read-only exact-final reviewer the commit SHA, this
  plan, the diff, and the relevant tests. Require strict `GO` or `NOT_YET` and
  an exact echo of the candidate SHA.
- One in-boundary repair commit and one replacement exact-final review are
  authorized if the first result is `NOT_YET`; otherwise stop before publish.
