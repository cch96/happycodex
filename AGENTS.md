# HappyCodex maintainer protocol

The packaged product is frozen at the published `v0.6.5` bytes while the
maintainer evaluator is rebuilt independently. Repository evaluation files are
maintenance support and must never be linked from `skills/happycodex/SKILL.md`.

- Preserve the exact `skills/happycodex` tree
  `d9e525a267fbf36669d409ba1b4b009a6beeeea5`, external role configuration,
  active install, cache, and rollback state until separately authorized.
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
