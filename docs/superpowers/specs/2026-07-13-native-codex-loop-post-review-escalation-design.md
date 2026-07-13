# Native Codex Loop Post-Review Escalation Design

## Objective

Close the five confirmed native-review findings without weakening the default two-attempt
review discipline. Add one human-authorized, non-recursive post-fix review series whose
identity is mechanically bound to the immutable original series, its final receipt, the
augmented Task Contract, and the confirmed finding IDs.

The user approved this scope on 2026-07-13. The external Task Contract preserves its
original bytes and appends the exact authorization; its current SHA256 is
`8cd6b52498bca86154c33bf9b26b617c93a74b8460ef242aac3c0da5dc57b62e`.

## Candidate comparison

1. Increase `MAX_REVIEW_ATTEMPTS` globally to three. Rejected: every normal task would
   silently receive a larger loop budget.
2. Change worktree path or baseline to obtain a fresh series. Rejected: it bypasses the
   audit identity and can be performed without human authorization.
3. Add an explicit escalation identity. Selected: normal series remain unchanged and
   capped at two; a single additional generation exists only when the runner verifies
   the user's addendum and the exhausted parent series.

## Escalation contract

The CLI adds optional `--escalate-from-series <series.json>`. Without it, behavior and
series identity are unchanged. With it, the runner requires all of the following before
creating state:

- the path is the canonical default series for the same resolved repository and base;
- the series is a private regular file with exactly two ordered attempts;
- its final attempt succeeded and its persisted receipt hash matches `series.json`;
- the final receipt is `ok`, uses the same base/repository, and its head equals the
  addendum's `Prior reviewed head`;
- the augmented Task Contract contains exactly one canonical addendum with the original
  Task Contract hash, parent series path/hash, final receipt hash, exact five finding IDs,
  and an authorization statement permitting one non-recursive post-fix series;
- the parent is a default series, never another escalation.

The escalation series key hashes repository, base, augmented Task Contract hash, parent
series hash, and parent receipt hash. It lives under a separate `escalations/` namespace,
retains the same two-attempt cap, persists parent hashes in `series.json` and every
receipt, and cannot itself be supplied to `--escalate-from-series`.

## Security fixes

### Credential exclusion before model launch

After creating the head-only clone but before generated config, preflight, version probe,
or model launch, scan both the checked-out filesystem and every Git blob reachable from
`HEAD` for exact credential byte strings extracted from source `auth.json`. Use streaming
reads with overlap so secrets spanning chunks are detected. Any match fails before the
reviewer can read the clone. Packet/log redaction remains defense in depth.

### Fail-closed network proof

Run the probe as `python3 -I -S -c <script>` so the candidate directory, `PYTHONPATH`,
user site, and `sitecustomize` cannot affect imports. An accessible listener exits 1.
Only `EPERM` or `EACCES`, whether raised or returned by `connect_ex`, exits 0. Every other
error, including `ECONNREFUSED`, timeout, missing interpreter, or import failure, exits 2
or the shell's nonzero code.

### Finding metadata binding

Require the title prefix `^[P0-3]` to match numeric priority. Before mapping clone paths
back to source paths, require every finding location to resolve under the isolated clone,
name a changed regular file, and overlap at least one new-side `-U0` hunk in
`base..head`. Out-of-clone, unchanged, nonexistent, and out-of-range locations fail.

## Skill behavior

The normal gate still stops after two attempts. When attempt two supports material fixes,
the root records dispositions and stops. Only an explicit later user instruction may
authorize escalation. The root appends, never rewrites, the Task Contract; invokes the
runner with the exact parent `series.json`; and accepts only the new escalation receipt.
One escalation generation is the maximum. A second exhausted escalation reports residual
risk and cannot recurse.

The failed Fable call remains closed evidence. After the user's recovery notice, a new
stateless Fable task may be created; it must not resume, replay, or reuse the failed
packet/session.

## Validation and release gates

- RED-to-GREEN unit tests cover each of the five findings and every escalation binding.
- Full `unittest`, Ruff, compileall, diff check, plugin validator, and Skill validator pass.
- A real Codex 0.144.1 post-fix escalation review succeeds on the exact final head.
- A new two-invocation-maximum Fable task covers the initial 1904-line implementation
  and the incremental fixes without exceeding 2000 lines per packet.
- Installation occurs only through the plugin-creator marketplace/cachebuster flow.
- Storyboard replay begins only after both reviews succeed.

## Backup and switch condition

If any parent-series binding, streaming credential scan, changed-hunk parser, real CLI
preflight, or reviewer receipt cannot be proved, fail closed and keep the plugin
uninstalled. Do not switch to a global third attempt, a changed baseline, or a worktree
identity workaround.

## Readiness

`ready`: root causes are reproduced, the user authorized the exact escalation boundary,
interfaces and validation are explicit, and no implementation decision remains hidden.
