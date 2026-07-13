# Native Codex Loop

Native Codex Loop is a personal Codex plugin for long or high-risk implementation. It
keeps one root writer, anchors scope in an immutable Task Contract, treats the native
plan as a live decision record, limits children to bounded isolated investigations, and
requires a fresh native Codex review of the final commit before completion.

## What it changes

- Adds the `$native-codex-loop` Skill through the plugin marketplace.
- Runs final review in a temporary clean HOME/CODEX_HOME using `gpt-5.6-sol` at max,
  read-only sandbox, approval never, restricted network, and disabled extensions.
- Keeps the root thread as the only source-code writer and requires the final HEAD to
  match the final succeeded review attempt's receipt.
- Policy-routes investigative children to disposable head-only clones and brackets the
  candidate with fingerprints; built-in children remain able to address inherited host
  paths, so this is not a hard read-isolation boundary.

It does not install custom agents, modify global `AGENTS.md`/`config.toml`, use
hooks/MCP/external models, or force an ExecPlan file. Invoke the Skill explicitly when
deterministic pickup matters; normal plugin metadata remains available for implicit use.

## Review artifacts

The Skill creates an immutable mode-`0600` Task Contract plus private mode-`0600` factual packet outside the
candidate repository and calls `scripts/review_runner.py --task-contract ...`. The
runner hashes and verifies the exact inlined contract, then derives one canonical series from source CODEX_HOME,
repository identity, and frozen task baseline. `series.json` counts every started
invocation (including failures) and enforces the default two-attempt cap. A later
explicitly user-authorized, append-only Task Contract addendum can create one distinct,
non-recursive post-fix series with the same two-attempt cap; its identity and receipts
bind the parent series and final receipt hashes. A private parent-level authority
reservation prevents alternate addendum bytes from creating another series, and the
post-fix head must differ in content from the parent-reviewed head. Each
successful `attempt-N/` contains:

- `packet.md`: the exact source packet given to the reviewer; its repository path is
  provenance only, while inspection is confined to the reviewer's current clone;
- `review.md`: native review findings;
- `preflight.log`, `events.jsonl`, and `stderr.log`: isolation and execution evidence;
- `receipt.json`: base/head, Task Contract and runner hashes, actual runtime policy,
  CLI/binary and artifact hashes, token usage when reported, process containment,
  Git-visible source hashes, and full review-clone hashes.

Credentials and their canary live only in the user's private runtime tmpfs. Generated
config, rollouts, Git bundle, and review clone are temporary and are removed on success,
error, or timeout. Before any Codex command runs, the runner scans the checkout and every
Git blob reachable from `HEAD` for exact credential strings. It also rejects reviewer
findings whose priority metadata disagrees or whose location does not overlap a changed
new-side hunk. The receipt is an audit record, not a signed attestation.

## Compatibility and limits

- Validated against Codex CLI 0.144.1; rerun real preflight after CLI upgrades.
- The runner requires Linux, `/usr/bin/unshare`, a private tmpfs at `/run/user/<uid>`,
  and `$CODEX_HOME/auth.json`; unsupported containment fails closed.
- A positive filesystem allowlist, a deterministic preflight, and an in-review canary
  restrict the reviewer to the isolated clone and minimal runtime files. Treat this as
  a checked CLI contract, not a general container boundary; historical-oracle
  experiments should still make oracle data inaccessible outside the candidate runtime.
- Every Codex subprocess runs in a disposable PID namespace, so detached descendants are
  killed by the kernel on normal exit or timeout.
- Parent Codex and Git processes receive a minimal fixed environment: ambient API keys,
  proxies, dynamic-loader/Python injection, Git config, and lazy fetch are not inherited.
- Built-in investigative children inherit the parent runtime. Their non-writing boundary
  is policy-enforced and bracketed by Git fingerprints; only the independent reviewer
  has a verified hard read-only context.

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

The design and experiment protocol live under `docs/superpowers/`.
