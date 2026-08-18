"""Immutable topology and fixed policy for the thin verifier."""
from __future__ import annotations

from typing import NamedTuple


SCHEMA_VERSION = 3
RECORD_TYPES = ("ProductArtifact", "EvalSpec", "Attestation", "ReleaseReceipt")
STAGES = ("behavior", "holdout", "exact_final")
EFFECT_OUTCOMES = ("landed", "not_landed", "unknown")
DECISIONS = ("GO", "NOT_YET")
FINDING_TYPES = (
    "obligation_failure",
    "preservation_failure",
    "candidate_new_material_regression",
)
BEHAVIOR_ROLE_IDS = (
    "qualification-routing",
    "context-isolation",
    "writer-continuity",
    "candidate-review",
    "effect-closure",
)
HOLDOUT_SAMPLE_IDS = ("recovery", "safety", "scope")
HOLDOUT_ROLE_ID = "fixed-holdout"
EXACT_FINAL_ROLE_ID = "exact-final"


class UnitTopology(NamedTuple):
    unit_id: str
    stage: str
    role_id: str
    sample_id: str | None
    arm: str | None


UNIT_TOPOLOGY = (
    *(UnitTopology(role, "behavior", role, None, None) for role in BEHAVIOR_ROLE_IDS),
    *(
        UnitTopology(f"holdout-{sample}-{arm}", "holdout", HOLDOUT_ROLE_ID, sample, arm)
        for sample in HOLDOUT_SAMPLE_IDS
        for arm in ("a", "b")
    ),
    UnitTopology(EXACT_FINAL_ROLE_ID, "exact_final", EXACT_FINAL_ROLE_ID, None, None),
)
HOLDOUT_PAIR_TOPOLOGY = tuple(
    (
        f"holdout-{sample}",
        sample,
        (f"holdout-{sample}-a", f"holdout-{sample}-b"),
    )
    for sample in HOLDOUT_SAMPLE_IDS
)

PROJECTION_NAMES = (
    "source_distribution",
    "marketplace_locator",
    "plugin_runtime",
    "public_docs",
    "provider_guidance",
)
PRIVATE_ORACLE_PATH = "evaluation/hidden-oracles-v1.json"
PRODUCTION_INPUT_PATHS = (
    "evaluation/manifest-v1.json",
    "evaluation/provider-fixtures-v1.json",
    PRIVATE_ORACLE_PATH,
    "evaluation/report-schemas-v1.json",
)
REVIEW_POLICY_CONTRACT_ID = "happycodex.exact-final.blocker-only.v3"


def exact_final_review_policy() -> dict[str, object]:
    """Return the fixed provider-visible review policy value."""
    return {
        "policy_id": REVIEW_POLICY_CONTRACT_ID,
        "mode": "neutral_read_only_blocker_only",
        "terminal": True,
        "decisions": list(DECISIONS),
        "admissible_findings": list(FINDING_TYPES),
        "go_requires": {
            "coverage_complete": True,
            "unverified_empty": True,
            "findings_empty": True,
        },
        "review_rule": (
            "Before admitting a blocker or required coverage item, state three links: "
            "the normal supported path; the final source in a direct user or Outcome requirement, "
            "preservation of pre-change reachable behavior, data, or identity, a required supported "
            "workflow, or candidate-new material safety or correctness; and the material falsification. "
            "A missing link is advisory, not blocking, and priority labels grant no admission. "
            "Plan text may relay a real source but cannot create its own authority. Apply this same "
            "test to Root concerns and reviewer findings. Plan wording, reviewer preference, stricter "
            "local invariants, optional or incidental checks, and unsupported-path manual artifact injection cannot manufacture blockers; required robustness or adversarial behavior remains in scope."
        ),
    }


__all__ = tuple(name for name in globals() if name.isupper()) + (
    "UnitTopology",
    "exact_final_review_policy",
)
