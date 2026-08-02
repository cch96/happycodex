"""Closed routing policy for caller-supplied evaluation specifications."""

MODEL_ROLE_IDS = (
    "goal-divergence",
    "no-commit-secret",
    "no-summary-reconstruction",
    "qualification-high-risk",
    "qualification-low-risk",
    "qualification-midflight",
    "same-task-compaction",
)
HOLDOUT_ROLE_ID = "fixed-holdout"
EXACT_FINAL_ROLE_ID = "exact-final"
DETERMINISTIC_DOMAINS = frozenset(
    {
        "receipt", "claim", "schema", "parser", "invalidation",
        "review-truncation", "install", "rollback",
    }
)

__all__ = (
    "DETERMINISTIC_DOMAINS", "EXACT_FINAL_ROLE_ID", "HOLDOUT_ROLE_ID",
    "MODEL_ROLE_IDS",
)
