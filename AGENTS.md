# HappyCodex maintainer protocol

The published `v0.6.5` tag and product tree remain immutable while the
maintainer evaluator is rebuilt independently. Repository evaluation files are
maintenance support and must never be linked from `skills/happycodex/SKILL.md`.

- Preserve the exact published `v0.6.5:skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`, external role configuration,
  active install, cache, and rollback state. This exact user authorization
  permits only the local 0.8.1 source-release candidate surfaces named in
  `docs/execplans/happycodex-0-8-1-release.md`.
- Unless the request or source establishes otherwise, treat the user,
  maintainer, workspace, and selected configuration as non-adversarial but
  fallible. Verify state and identity, prefer the smallest sufficient control,
  and require explicit user authority to expand scope or trust boundaries.
- The evaluator has exactly four durable record types: `ProductArtifact`,
  `EvalSpec`, `Attestation`, and `ReleaseReceipt`. Unknown types fail closed.
- Product identity never includes evaluator bytes. Evaluator identity separates
  provider input, oracle, and harness components so invalidation causes only
  necessary work.
- Verification is stateless over caller-supplied immutable records. Do not add
  an active mutable ledger, general evidence graph, compatibility reader,
  migration, alias, or dual write.
- Provider input is allowlisted and mechanically excludes expected answers,
  hidden boundaries, oracle/matcher/mapping content, desired verdicts, and
  history. Raw events remain external; repository records contain digests and
  sanitized projections only.
- Repository code may construct an authority request digest and validate
  externally supplied authority. It cannot manufacture user authority. One
  bounded evaluation authority normally covers the exact behavior plan and one
  neutral exact-final. Release authority is separate.
- Every provider invocation is one-shot. Only a proven pre-provider
  infrastructure no-effect terminal may recover within an already authorized
  recovery cap. Ambiguous or partial effects stop without retry.
- Holdouts are exactly three fixed concurrent pairs against the previous
  released product. Freeze all six outputs before revealing mappings; aggregate
  candidate total input plus output tokens must be no more than 1.25 times
  baseline. The corresponding relative wall ratio is retained as a diagnostic;
  per-unit timeouts and the absolute cumulative wall cap remain hard.
- Persist an adverse exact-final attestation and reject a friendlier rerun for
  unchanged artifact bytes. Product mutation requires a new exact-final.
- Keep evaluator Python at most 3,200 lines where practical; 3,600 is a hard
  stop and no production module may exceed 600 lines.
- Use only offline standard-library tests unless a later exact authority names
  every model/network/install/release effect, identity, destination, and cap.
