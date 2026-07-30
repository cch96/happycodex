from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import (
    IdentityError,
    PUBLIC_02_ARM,
    PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
    PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
    PUBLIC_02_SKILL_ENTRIES,
    PUBLIC_02_SOURCE_COMMIT,
    PUBLIC_02_SOURCE_TREE,
    canonical_sha256,
    case_semantic_sha256,
    engine_inventory,
    executor_role_identity,
    package_identities,
)
from evaluation.core.schema import CONTRACTS, validate_named


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_EFFORT = "high"
DEFAULT_TIMEOUT = 300
IMPACT_FIELDS = {
    "schema_version",
    "reasons",
    "gates",
    "corpus_cases",
    "holdout_pairs",
    "live_calls",
    "cost",
}
GATE_ORDER = (
    "calibration",
    "corpus",
    "holdout",
    "receipt",
    "review",
    "isolated_install",
)
CORPUS_MODEL_CALLS = {
    case_id: 3 if case_id == "pre-freeze-compaction" else 1
    for case_id in (
        "authorized-rebaseline",
        "boundary-cutover",
        "clean-qualifying-control",
        "compaction-recovery",
        "exact-final-ready",
        "goal-divergence",
        "midflight-escalation",
        "multi-repo-submodule",
        "no-commit-archive-recovery",
        "no-commit-secret",
        "no-commit-unselected",
        "pre-freeze-compaction",
        "receipt-mismatch",
        "review-admin-cycle",
        "review-inventory-gate",
        "review-isolation",
        "subthreshold-control",
    )
}


def _public_baseline() -> dict[str, Any]:
    return {
        "arm": PUBLIC_02_ARM,
        "source_commit": PUBLIC_02_SOURCE_COMMIT,
        "source_tree": PUBLIC_02_SOURCE_TREE,
        "artifact_sha256": PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
        "semantic_sha256": PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
        "skill_entries": list(PUBLIC_02_SKILL_ENTRIES),
    }


def _load_cases(root: Path) -> dict[str, dict[str, Any]]:
    from evaluation.corpus.engine import load_cases

    return load_cases(root / "evaluation" / "cases")


def _load_holdouts(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    from evaluation.holdout.engine import load_manifest

    manifest_path = root / "evaluation" / "holdouts" / "manifest.json"
    loaded = load_manifest(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_by_id = {pair["id"]: pair for pair in manifest["pairs"]}
    pairs = {
        pair["id"]: {
            "descriptor": raw_by_id[pair["id"]],
            "case": pair["case"],
        }
        for pair in loaded["pairs"]
    }
    return manifest, pairs


def build_snapshot(
    root: Path,
    *,
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    root = root.resolve()
    inventory = engine_inventory(root)
    package = package_identities(root)
    _manifest, pairs = _load_holdouts(root)
    bundle = inventory["manifest_sha256"]

    def identities(
        values: dict[str, dict[str, Any]], arm: str
    ) -> dict[str, str]:
        return {
            item_id: case_semantic_sha256(
                item,
                evaluator_bundle_sha256=bundle,
                package_semantic_sha256=package["semantic_sha256"],
                model=model,
                effort=effort,
                timeout=timeout,
                arm=arm,
            )
            for item_id, item in sorted(values.items())
        }

    return {
        "schema_version": 1,
        "settings": {
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
        },
        "engine": {"manifest_sha256": bundle},
        "package": package,
        "role": {"executor_sha256": executor_role_identity(root)},
        "public_baseline": _public_baseline(),
        "corpus": {"cases": identities(_load_cases(root), "candidate")},
        "holdout": {"pairs": identities(pairs, "blinded-pair")},
    }


def _digest_map(value: Any, fields: set[str] | None = None) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and (fields is None or set(value) == fields)
        and all(
            type(name) is str
            and bool(name)
            and type(digest) is str
            and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
            for name, digest in value.items()
        )
    )


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    validate_named(CONTRACTS, "snapshot", snapshot)
    settings = snapshot["settings"]
    engine = snapshot["engine"]
    if (
        not isinstance(settings, dict)
        or set(settings) != {"model", "effort", "timeout_seconds"}
        or any(
            type(settings[field]) is not str or not settings[field]
            for field in ("model", "effort")
        )
        or type(settings["timeout_seconds"]) is not int
        or settings["timeout_seconds"] <= 0
        or not isinstance(engine, dict)
        or set(engine) != {"manifest_sha256"}
        or re.fullmatch(r"[0-9a-f]{64}", engine["manifest_sha256"]) is None
    ):
        raise IdentityError("invalid snapshot settings or evaluator identity")
    if snapshot["public_baseline"] != _public_baseline():
        raise IdentityError("public-0.2 baseline identity is not exact")
    for envelope, field in (("corpus", "cases"), ("holdout", "pairs")):
        if not _digest_map(snapshot[envelope][field]):
            raise IdentityError(f"invalid {envelope} identities")
    if len(snapshot["holdout"]["pairs"]) != 3:
        raise IdentityError("holdout identity requires exactly three pairs")


def _changed_keys(before: dict[str, str], after: dict[str, str]) -> set[str]:
    return {key for key in set(before) | set(after) if before.get(key) != after.get(key)}


def validate_impact(impact: dict[str, Any], snapshot: dict[str, Any]) -> None:
    validate_snapshot(snapshot)
    if (
        not isinstance(impact, dict)
        or set(impact) != IMPACT_FIELDS
        or impact["schema_version"] != 1
    ):
        raise IdentityError("invalid impact envelope")
    if (
        impact["reasons"] != sorted(set(impact["reasons"]))
        or impact["gates"] != [
            gate for gate in GATE_ORDER if gate in impact["gates"]
        ]
        or len(impact["gates"]) != len(set(impact["gates"]))
    ):
        raise IdentityError("invalid impact reasons or gates")
    for field, available in (
        ("corpus_cases", set(snapshot["corpus"]["cases"])),
        ("holdout_pairs", set(snapshot["holdout"]["pairs"])),
    ):
        scope = impact[field]
        if (
            not isinstance(scope, list)
            or scope != sorted(set(scope))
            or not set(scope) <= available
        ):
            raise IdentityError(f"invalid impact scope: {field}")
    corpus = bool(impact["corpus_cases"])
    holdout = bool(impact["holdout_pairs"])
    if (
        corpus != ("corpus" in impact["gates"])
        or holdout != ("holdout" in impact["gates"])
        or (
            holdout
            and set(impact["holdout_pairs"]) != set(snapshot["holdout"]["pairs"])
        )
    ):
        raise IdentityError("impact gate does not match executable scope")
    if impact["live_calls"] is not None or impact["cost"] is not None:
        raise IdentityError("generation-7 cost envelope is not persisted")


def impact_token(snapshot: dict[str, Any], impact: dict[str, Any]) -> str:
    validate_impact(impact, snapshot)
    return canonical_sha256(
        {
            "schema_version": 1,
            "snapshot_sha256": canonical_sha256(snapshot),
            "impact": impact,
        }
    )


def plan_impact(
    baseline: dict[str, Any],
    current: dict[str, Any],
    *,
    pending: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_snapshot(baseline)
    validate_snapshot(current)
    reasons: set[str] = set()
    gates: set[str] = set()
    corpus: set[str] = set()
    holdout: set[str] = set()
    all_cases = set(current["corpus"]["cases"])
    all_pairs = set(current["holdout"]["pairs"])
    for label, before, after in (
        ("corpus case", set(baseline["corpus"]["cases"]), all_cases),
        ("holdout pair", set(baseline["holdout"]["pairs"]), all_pairs),
    ):
        removed = before - after
        if removed:
            raise IdentityError(
                f"removed {label} requires explicit rebaseline: {sorted(removed)}"
            )

    def full_live(reason: str) -> None:
        reasons.add(reason)
        gates.update({"corpus", "holdout"})
        corpus.update(all_cases)
        holdout.update(all_pairs)

    if baseline["settings"] != current["settings"]:
        full_live("settings_changed")
    before_engine, after_engine = baseline["engine"], current["engine"]
    if before_engine["manifest_sha256"] != after_engine["manifest_sha256"]:
        full_live("evaluator_bundle_changed")
        gates.add("receipt")
    before_package, after_package = baseline["package"], current["package"]
    if before_package["semantic_sha256"] != after_package["semantic_sha256"]:
        full_live("package_semantic_changed")
    elif before_package["artifact_sha256"] != after_package["artifact_sha256"]:
        reasons.add("package_artifact_changed")
        gates.add("isolated_install")
    if baseline["role"] != current["role"]:
        reasons.add("executor_role_changed")
        gates.add("receipt")
    changed_cases = _changed_keys(
        baseline["corpus"]["cases"], current["corpus"]["cases"]
    )
    if changed_cases:
        reasons.add("corpus_cases_changed")
        gates.add("corpus")
        corpus.update(changed_cases & all_cases)
    if _changed_keys(baseline["holdout"]["pairs"], current["holdout"]["pairs"]):
        reasons.add("holdout_pairs_changed")
        gates.add("holdout")
        holdout.update(all_pairs)
    if pending is not None:
        if set(pending) != {"gates", "corpus_cases", "holdout_pairs"}:
            raise IdentityError("invalid generation-7 pending envelope")
        pending_gates = pending["gates"]
        if pending_gates != [
            gate for gate in GATE_ORDER if gate in pending_gates
        ] or len(pending_gates) != len(set(pending_gates)):
            raise IdentityError("invalid generation-7 pending gates")
        pending_cases = set(pending["corpus_cases"])
        pending_pairs = set(pending["holdout_pairs"])
        if not pending_cases <= all_cases or not pending_pairs <= all_pairs:
            raise IdentityError("pending scope is absent from current snapshot")
        if ("corpus" in pending_gates) != bool(pending_cases) or (
            "holdout" in pending_gates
        ) != bool(pending_pairs):
            raise IdentityError("pending gate does not match scope")
        reasons.add("generation_7_genesis")
        gates.update(pending_gates)
        corpus.update(pending_cases)
        if pending_pairs:
            holdout.update(all_pairs)
    result = {
        "schema_version": 1,
        "reasons": sorted(reasons),
        "gates": [gate for gate in GATE_ORDER if gate in gates],
        "corpus_cases": sorted(corpus),
        "holdout_pairs": sorted(holdout),
        "live_calls": None,
        "cost": None,
    }
    validate_impact(result, current)
    return result


def validate_successor(before: dict[str, Any], after: dict[str, Any],
                       *, repo: Path | None = None) -> None:
    from evaluation.core.ledger import validate_successor as validate_release_successor

    validate_release_successor(before, after, repo=repo)
