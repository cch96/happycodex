# Shared and consequential operations

Apply these checks to the next operation whose completion or repetition has
material consequences. Ordinary task-owned reversible edits use the main Skill.

## Establish the operation

Resolve the actual destination and relevant state from the user's request and
native repository or service configuration. Include automatic downstream writes.
Check existing authorization before asking: a direct request for an established
candidate and destination may already authorize the standard operation.
Publication, installation, activation, destructive cleanup, and paid calls have
distinct consequences; advice or a plan does not authorize an additional one.

For a release or another candidate-sensitive operation, identify the exact
consumer inputs, including generated/transitive files, modes, and deletions.
Use the consumer's native immutable identity, such as a Git tree, package, image,
or revision, and confirm the artifact actually derives from the checked inputs.
Preserve the material premises behind relied-on checks and review. A digest of
unretained mutable files does not make them a recoverable candidate.

Read current target state when it matters. Check Git command statuses separately;
predicate exit 1 means false, while greater than 1 means error. Cached
remote-tracking refs do not prove live remote state. Account for shared refs,
branch checkout owners, and unrelated staged or uncommitted work.

Before proceeding, resolve conflicts with another writer, excluded scope,
preservation requirements, or the actual target. Check authorized cost or usage
limits for metered work; an explicit unlimited budget is valid. Verify a viable
recovery path where the operation needs one. These facts can come from native
records and tools; they do not require a new approval form or a frozen plan.

## Attempt and observe

Attempt each material operation once, then read authoritative state to determine
whether it landed, did not land, or remains unknown. A command returning, a lost
connection, or a local timeout cannot alone prove remote success or no effect.
Keep the native receipt and necessary observations reachable for continuation.

For an ambiguous or partial result, inspect the actual destination first and
stop the affected operation while its state remains unresolved. Do not repeat
it, change its identity, or start a new task to bypass that uncertainty.

A retry needs authoritative proof of no effect, a causal fix, and unchanged or
already authorized scope, target, relevant identity, cost, and observation.
After a completed low-cost metered read loses only its local output, one causal
recovery is acceptable if duplicate durable effects are ruled out and cost stays
authorized. Unlimited cost does not make an unexplained retry useful or safe.

If code or required review premises changed, refresh the affected checks and
review before the operation. If only the operation's target information changed,
verify its existing authority and current state; do not repeat an otherwise
valid code review. A saved review claim must match its original result and
candidate. Keep unresolved findings visible until evidence resolves them.

Before deleting a worktree, branch, old artifact, or other recovery surface,
confirm cleanup authority, actual ownership/use, and durable recovery evidence.
Do not retire resources still needed by active tasks. Report each operation's
observed result, and identify any required acceptance that remains unverified.
