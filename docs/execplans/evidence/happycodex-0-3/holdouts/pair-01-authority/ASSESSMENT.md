# Pair 01 Assessment: Authority v2 Cutover

## Controlled protocol

- Fixture baseline: `0635866d4de3acf9e19a3251d549cba513536386`
- Same implementation prompt and SHA-256 for both arms
- Same model `gpt-5.6-sol`, `high` reasoning effort, 900-second budget,
  workspace-write sandbox, and approval policy
- No implementation prompts after launch
- Predeclared out-of-diff seam: `workflow/gateway.py`
- Predeclared hidden behavior: route matrix, all four intent lifecycles, gateway
  commands, production validation/readiness, and legacy retirement
- Blind labels remained sealed until the read-only evaluator returned its
  independent obligations, arm assessment, blockers, and ranking

Each `worktree.patch.gz` is a deterministic gzip encoding of the frozen tracked
Git diff; `gzip -cd` restores it byte-for-byte. The decompressed SHA-256 values
are `34e96d8beb2d9239d64bfb9b3f3529e2ad73dc4bccf1246e20d6046d1d40bec1`
for amber and
`1b4b0550b7dbcb6d0152df6028230f3d6b390e650294a0a41ebb748961b2e60b`
for sable. The controller's separate `worktree_diff_sha256` snapshot field and
per-untracked-file hashes remain verbatim in arm metadata; they are not
repurposed as archive hashes. JSONL event streams remain unmodified.

The original route check was invalid because it constructed a retired field.
`oracle-correction.md` records the mirrored post-freeze correction and Root
reproduction. All other hidden checks passed for both arms.

## Blind result and reveal

The evaluator ranked sable above amber on system completeness: sable connected
the full route-to-worker path and had stronger production and malformed-input
coverage, while amber left the gateway disconnected. Neither was complete.

After that verdict was frozen, `reveal.json` mapped amber to current 0.2 and
sable to the candidate. The corrected route matrix therefore proves that the
candidate introduced a completion-blocking regression: all four baseline `read`
contexts raise `ValueError("read")`, while current 0.2 preserves them.

## Cost and completion accounting

| Arm | Outcome | Wall time | Measured uncached input | Output |
| --- | --- | ---: | ---: | ---: |
| Current / amber | exited incomplete | 429.737 s | 61,171 | 17,883 |
| Candidate / sable | timed out before turn completion | 900.044 s | unavailable | unavailable |

No nested-session usage was present in either arm's captured metadata. The
candidate exceeded current wall time by approximately 109.45 percent and did
not emit final usage accounting because it timed out. Both arms faced the same
Git sandbox restriction; neither could create the requested commits. Candidate
events show it had repaired review findings and reached 20 passing tests, but it
was still refreshing the full oracles before its one allowed rereview when the
budget expired.

## Release decision

**Reject the candidate at Pair 1.** The frozen adaptive rule requires immediate
rejection on the candidate's first completion-blocking regression. Consequently:

- Pair 2 and Pair 3 are not run.
- The cost tradeoff confirmation rule does not apply; it cannot override a
  quality regression.
- The pending anonymous rereview is not run for a rejected candidate.
- No 0.3 version is minted, installed, or made active.
- Public and active defaults remain 0.2.

This is a successful fail-closed evaluation outcome, not a successful 0.3
release.
