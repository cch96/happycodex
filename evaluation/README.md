# Stateless evaluator attestations

This maintainer-only evaluator is outside the packaged plugin. It has no active
database and accepts exactly four immutable durable records:

- `ProductArtifact` identifies product bytes and external role configuration.
- `EvalSpec` identifies evaluator components, the exact finite sample plan,
  exact behavior and exact-final profiles, previous released product, authority
  request, and total cap.
- `Attestation` freezes a behavior observation, zero-call oracle replay, or one
  neutral exact-final result with typed terminal provenance.
- `ReleaseReceipt` binds a separately authorized release to exact product,
  attestations, isolated install, destination, and rollback identities.

The command surface is deliberately read-only:

```bash
python3 -m evaluation.cli inventory
python3 -m evaluation.cli product --revision REV --external-role-config-sha256 SHA
python3 -m evaluation.cli materialize --product PRODUCT.json \
  --previous-product PREVIOUS.json --profiles PROFILES.json ...
python3 -m evaluation.cli authority-request --spec SPEC.json
python3 -m evaluation.cli validate-record RECORD.json
python3 -m evaluation.cli verify --product PRODUCT.json \
  --previous-product PREVIOUS.json --spec SPEC.json \
  --attestation ATTESTATION.json ... --mapping MAPPING.json \
  --revealed-at 2026-08-02T00:00:20Z
python3 -m evaluation.cli verify-release ...
```

`authority-request` prints only the digest and bounded invocation inventory.
An external authenticator must validate user authority before the provider or
release APIs mint a non-serializable process-local capability. Repository
content cannot authenticate itself.

`PROFILES.json` has exactly `behavior` and `exact_final`, each with the existing
`model`, `effort`, `tools`, and `timeout_seconds` fields. Core behavior and all
six holdout invocations use `behavior`; only the unique exact-final invocation
uses `exact_final`. The production target is `gpt-5.6-sol/high` for behavior
and holdouts and `gpt-5.6-sol/max` for exact-final.

Provider input is built from a closed allowlist. Expected answers, hidden
boundaries, oracle and matcher content, holdout mappings, desired verdicts, and
repair history are absent from workspace, arguments, standard input,
environment, and sanitized events. Fixed holdouts are exactly three concurrent
two-arm pairs against the previous released product; all six outputs freeze
before reveal, and aggregate token and wall ratios must each be at most 1.25.

The fixed external host is the trusted capture boundary. `EvalSpec`
binds its binary, trust domain, tool/permission/workspace configuration, and
every invocation. The raw input is native `codex exec --json`: one thread, one
turn, paired item events, one JSON agent message and one terminal usage event.
The host supplies only start/freeze timestamps, exit code and timeout status;
all terminal and usage facts are derived. Verification requires the retained
native JSONL and recomputes its digest, terminal, report and allowlisted
sanitized-projection hashes, times, claim, contract, and invocation links.
Command/tool output is excluded from the projection. This is host-observed
integrity, not cross-host cryptographic non-repudiation; the host is trusted
only for raw-to-sanitized report transformation, and no secret or raw event is
persisted in an Attestation.

Run all offline checks with:

```bash
python3 -m unittest discover -s tests -v
```
