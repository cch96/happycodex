# Pair 01 Oracle Correction

## Why correction was required

The frozen hidden-oracle output in each arm shows the same invalid first check:
`Request.__init__()` rejected `planexecution_phase`. Retirement of that field was
itself a required outcome, so constructing it could not test post-cutover route
compatibility. The result did not discriminate between arms and was not used for
the release decision.

Both worktrees had already frozen their status and content hashes before any
oracle was revealed. The first mirrored correction invocation had identical
shell-quoting `SyntaxError` failures in both arms and changed no repository
state. A valid mirrored invocation then used this exact matrix:

- `domain_context`: `None`, `{}`, `{"tenant": "acme"}`, `"persisted"`
- `run_mode`: `None`, `"execute"`, `"tool"`, `"cancel"`, `"reconcile"`,
  `"read"`
- expected result: Authority `v2`, with `None` normalized to `execute` and every
  other mode preserved

## Corrected result

```text
ARM=amber
passed=24/24
ARM=sable
passed=20/24
{'domain_context': None, 'run_mode': 'read', 'error': 'ValueError: read'}
{'domain_context': {}, 'run_mode': 'read', 'error': 'ValueError: read'}
{'domain_context': {'tenant': 'acme'}, 'run_mode': 'read', 'error': 'ValueError: read'}
{'domain_context': 'persisted', 'run_mode': 'read', 'error': 'ValueError: read'}
```

Root reproduced this result from each metadata-recorded frozen repository path.
The metadata records `status_unchanged_after_oracle: true` for both arms. The
blind evaluator independently reproduced the same matrix before reveal.
