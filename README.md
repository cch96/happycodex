# Native Codex Loop

Native Codex Loop is a personal Codex plugin for long or high-risk implementation. It
keeps one root writer, treats the native plan as a live decision record, limits children
to bounded investigative packets, and requires a fresh native Codex review of the final
commit before completion.

## What it changes

- Adds the `$native-codex-loop` Skill through the plugin marketplace.
- Runs final review in a temporary clean HOME/CODEX_HOME using `gpt-5.6-sol` at max,
  read-only sandbox, approval never, restricted network, and disabled extensions.
- Keeps the root thread as the only source-code writer and requires the final HEAD to
  match the latest successful review receipt.

It does not install custom agents, modify global `AGENTS.md`/`config.toml`, use
hooks/MCP/external models, or force an ExecPlan file. Invoke the Skill explicitly when
deterministic pickup matters; normal plugin metadata remains available for implicit use.

## Review artifacts

The Skill creates a factual packet outside the candidate repository and calls
`scripts/review_runner.py`. It derives one canonical series from source CODEX_HOME,
repository identity, and frozen task baseline. `series.json` counts every started
invocation (including failures) and caps that identity at two. Each
successful `attempt-N/` contains:

- `packet.md`: the exact clone-adjusted context given to the reviewer;
- `review.md`: native review findings;
- `preflight.log`, `events.jsonl`, and `stderr.log`: isolation and execution evidence;
- `receipt.json`: base/head, actual runtime policy, CLI/binary and artifact hashes, token
  usage when reported, process containment, Git-visible source hashes, and full
  review-clone hashes.

Credentials, generated config, rollouts, Git bundle, and review clone are temporary and
are removed on success, error, or timeout. The receipt is an audit record, not a signed
attestation.

## Compatibility and limits

- Validated against Codex CLI 0.144.1; rerun real preflight after CLI upgrades.
- The runner requires Linux, an available unprivileged user/PID namespace through
  `unshare`, and `$CODEX_HOME/auth.json`; unsupported containment fails closed.
- A positive filesystem allowlist, a deterministic preflight, and an in-review canary
  restrict the reviewer to the isolated clone and minimal runtime files. Treat this as
  a checked CLI contract, not a general container boundary; historical-oracle
  experiments should still make oracle data inaccessible outside the candidate runtime.
- Every Codex subprocess runs in a disposable PID namespace, so detached descendants are
  killed by the kernel on normal exit or timeout.
- Built-in investigative children inherit the parent runtime. Their non-writing boundary
  is policy-enforced and bracketed by Git fingerprints; only the independent reviewer
  has a verified hard read-only context.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

The design and experiment protocol live under `docs/superpowers/`.
