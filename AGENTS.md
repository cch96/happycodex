# HappyCodex maintainer guidance

Keep this file limited to stable repository-wide constraints. Detailed evaluator
schemas, topology, budgets, and release-specific facts belong in code, tests,
or the task ExecPlan.

- Treat every published tag and its reachable tree as immutable. Publish changes
  through a new commit and tag; never rewrite an existing release.
- Keep maintainer evaluator and evidence material out of
  `skills/happycodex/SKILL.md` and other installed product guidance.
- Treat the user, maintainer, workspace, and selected configuration as
  non-adversarial but fallible. Verify relevant identity and state
  proportionately.
- Keep the repository evaluator deterministic and stateless. Do not add an
  active mutable ledger, general evidence graph, compatibility reader,
  migration, alias, or dual write without an explicitly authorized redesign.
- Repository code may construct requests and validate externally supplied
  authority. It cannot manufacture user authority.
- After the exact candidate, repository, and version are established, a direct
  user request to publish authorizes the standard release sequence to the
  configured `origin/main`, the matching annotated version tag, and the GitHub
  Release. Installation, activation, provider/model calls, and other
  destinations remain separate unless requested.
- Attempt each external effect once. On an ambiguous or partial result, stop and
  inspect read-only state. Retry only after proving that the previous attempt
  had no effect.
- Use offline standard-library tests by default. Network access is permitted
  only for an explicitly requested external effect and its readback.
