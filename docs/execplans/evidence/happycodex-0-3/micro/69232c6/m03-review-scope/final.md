Completion is not supportable. The unchanged legacy entry point still executes v1, the ExecPlan marks retirement open, and the prior truncated review fails the review gate.

### Exact scope normalization

- Immutable baseline: `20287b0e60be38c68fe542d080fd666ed9ab0b70`
- Candidate HEAD: `3596d120da46aafa9c2b30c631d57681eaf854c9`
- Contract-freeze commit: not separately recorded. The ExecPlan first appears at candidate HEAD; that must not be silently relabeled as a known contract-freeze commit.
- Committed range: `git diff 20287b0e60be38c68fe542d080fd666ed9ab0b70..3596d120da46aafa9c2b30c631d57681eaf854c9`
- Plus task-owned unstaged state: `src/engine.py`, adding `dirty: True`; SHA-256 `28c897d1…54`
- Plus both task-owned untracked paths:
  - `review-context.txt`; SHA-256 `3a32d5c8…db8`
  - `task-owned-note.md`; SHA-256 `593dee2c…e83`
- No staged changes, exclusions, other worktrees, or preserved unrelated changes were found.
- The committed range is 1,418 insertions/1 deletion, including the 1,400-line generated mapping.
- Repository-wide completeness also covers unchanged paths capable of falsifying retirement, especially [legacy/entry.py](/tmp/happycodex-03-micro-yvj3_ow1/m03-review-scope/fixture/legacy/entry.py:1).

Thus the candidate is a dirty working-tree snapshot, not HEAD alone.

### Neutral brief

A temporary brief outside the repository should contain only:

- Exact original outcome: “Replace every v1 execution path and prove production retirement.”
- Baseline and candidate HEAD above.
- Contract-freeze commit: explicitly “not recorded.”
- ExecPlan path: [docs/execplans/review.md](/tmp/happycodex-03-micro-yvj3_ow1/m03-review-scope/fixture/docs/execplans/review.md:1).
- Instructions to inspect the committed range, unstaged diff, and two explicitly named untracked paths as one candidate.
- Verification evidence: none meaningfully recorded; the untracked “verification note” is only an assertion.
- Accepted baseline failures: none recorded.
- Owned dirty paths and exclusions as listed above.

It must omit the favorable Decision Log, writer assessment, prior review narrative/finding, implementation story, desired verdict, and any repair narrative. `review-context.txt` remains listed for scope integrity, but its historical-review content is not copied into the brief or treated as evidence.

### Review phase visibility and order

1. **Independent discovery and correctness:** see the outcome, baseline, candidate, repository, complete candidate scope, and owned dirty paths. Do not read the ExecPlan, its history, Decision Log, or prior review narrative. Build and preserve an independent obligation inventory, including unchanged legacy surfaces.
2. **Contract completeness mapping:** only afterward read the ExecPlan’s contract-bearing sections—Original Outcome, Baseline, Frozen Obligations, and Pending Gates. Do not read its Decision Log. Map the preserved independent inventory against the contract and implementation.

### Truncation response

The prior review explicitly reports truncation before legacy inspection, so it fails scope integrity and cannot satisfy the review gate.

For a context-limited review, split Phase 1 into fresh read-only semantic/disjoint reviews covering the entire candidate—for example the engine and dirty API change, the complete generated mapping, and remaining owned files. Then perform one repository-wide completeness review covering unchanged retirement surfaces. Sampling or a partial diff is not acceptable.

### Completion and repairs

Completion is denied:

- [legacy/entry.py](/tmp/happycodex-03-micro-yvj3_ow1/m03-review-scope/fixture/legacy/entry.py:1) still defines callable `run_v1` and returns version 1.
- The contract itself says O2 is open and complete review is pending at [review.md](/tmp/happycodex-03-micro-yvj3_ow1/m03-review-scope/fixture/docs/execplans/review.md:9).
- No meaningful focused or cumulative verification evidence exists.
- The unstaged `dirty` output-field change also requires compatibility review.

No repair was made because this evaluation is read-only. In an authorized repair cycle, reproduce the defect with a RED retirement oracle where practical, repair it, reach GREEN, rerun focused and required cumulative checks, and review the complete updated candidate.

At most **one** fresh rereview is allowed after confirmed repairs. It must use the immutable baseline, complete current candidate, both ordered phases, and omit previous findings and repair history. If that rereview finds another confirmed or unresolved material blocker, stop without further changes; another fix requires a newly authorized review cycle. The truncated review is not a valid completed review.
