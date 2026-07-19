from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.core.identity import (
    IdentityError,
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    package_identities,
)


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_EFFORT = "high"
DEFAULT_TIMEOUT = 300
SNAPSHOT_FIELDS = {
    "schema_version",
    "settings",
    "engine",
    "package",
    "corpus",
    "holdout",
}
ENGINE_CATEGORY_FIELDS = {"semantic", "harness", "artifact"}
ENGINE_SCOPE_FIELDS = {"corpus_harness", "holdout_harness"}
CORPUS_HARNESS_PATHS = {
    "evaluation/__init__.py",
    "evaluation/cli.py",
    "evaluation/core/__init__.py",
    "evaluation/core/identity.py",
    "evaluation/corpus/__init__.py",
    "evaluation/corpus/engine.py",
}
HOLDOUT_HARNESS_PATHS = {
    "evaluation/holdout/__init__.py",
    "evaluation/holdout/blind.py",
    "evaluation/holdout/compare.py",
    "evaluation/holdout/engine.py",
}
GATE_ORDER = ("corpus", "holdout", "receipt", "isolated_install", "review")
CORPUS_COST = {
    "authorized-rebaseline": (26015, 93.933),
    "boundary-cutover": (28776, 281.718),
    "clean-qualifying-control": (39337, 90.086),
    "compaction-recovery": (26075, 224.845),
    "goal-divergence": (22538, 87.522),
    "midflight-escalation": (24407, 130.736),
    "multi-repo-submodule": (42105, 149.799),
    "no-commit-secret": (23875, 90.357),
    "pre-freeze-compaction": (104203, 622.99),
    "receipt-mismatch": (44614, 276.224),
    "review-admin-cycle": (31325, 71.457),
    "review-inventory-gate": (22009, 107.795),
    "review-isolation": (42543, 152.363),
    "subthreshold-control": (20886, 49.584),
}
HOLDOUT_COST = {
    "authority-production-boundary": (57410, 389.038),
    "local-documentation-control": (29091, 93.427),
    "destructive-migration-fallback": (51818, 275.211),
}


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IdentityError(f"JSON object required: {path}")
    return value


def _load_cases(root: Path) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "evaluation" / "cases").glob("*.json")):
        case = _read_json(path)
        case_id = case.get("id")
        if not isinstance(case_id, str) or case_id in cases:
            raise IdentityError(f"invalid or duplicate corpus case id: {case_id!r}")
        cases[case_id] = case
    if not cases:
        raise IdentityError("empty corpus")
    return cases


def _load_holdouts(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest_path = root / "evaluation" / "holdouts" / "manifest.json"
    manifest = _read_json(manifest_path)
    raw_pairs = manifest.get("pairs")
    if manifest.get("schema_version") != 1 or not isinstance(raw_pairs, list):
        raise IdentityError("invalid holdout manifest")
    pairs: dict[str, dict[str, Any]] = {}
    for row in raw_pairs:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise IdentityError("invalid holdout pair")
        pair_id = row["id"]
        if pair_id in pairs:
            raise IdentityError(f"duplicate holdout pair id: {pair_id}")
        relative = row.get("case_path")
        if not isinstance(relative, str):
            raise IdentityError(f"invalid holdout case path: {pair_id}")
        path = (root / relative).resolve()
        holdout_root = (root / "evaluation" / "holdouts").resolve()
        if not path.is_relative_to(holdout_root) or not path.is_file():
            raise IdentityError(f"unsafe holdout case path: {relative}")
        pairs[pair_id] = {"descriptor": row, "case": _read_json(path)}
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
    harness_paths = {
        item["path"] for item in inventory["entries"] if item["category"] == "harness"
    }
    scoped_harness_paths = CORPUS_HARNESS_PATHS | HOLDOUT_HARNESS_PATHS
    if harness_paths != scoped_harness_paths:
        raise IdentityError("harness scope inventory is incomplete")
    package = package_identities(root)
    shared_semantic = engine_category_sha256(
        inventory,
        "semantic",
        paths={"evaluation/corpus/contract.py"},
    )
    cases = _load_cases(root)
    case_ids = {
        case_id: case_semantic_sha256(
            case,
            shared_semantic_sha256=shared_semantic,
            package_semantic_sha256=package["semantic_sha256"],
            model=model,
            effort=effort,
            timeout=timeout,
            arm="candidate",
        )
        for case_id, case in sorted(cases.items())
    }
    manifest, pairs = _load_holdouts(root)
    holdout_shared = canonical_sha256(
        {
            "corpus_contract_sha256": shared_semantic,
            "manifest": manifest,
        }
    )
    pair_ids = {
        pair_id: case_semantic_sha256(
            pair,
            shared_semantic_sha256=holdout_shared,
            package_semantic_sha256=package["semantic_sha256"],
            model=model,
            effort=effort,
            timeout=timeout,
            arm="blinded-pair",
        )
        for pair_id, pair in sorted(pairs.items())
    }
    return {
        "schema_version": 1,
        "settings": {
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
        },
        "engine": {
            "categories": {
                "semantic": shared_semantic,
                "harness": inventory["categories"]["harness"],
                "artifact": inventory["categories"]["artifact"],
            },
            "scopes": {
                "corpus_harness": engine_category_sha256(
                    inventory, "harness", paths=CORPUS_HARNESS_PATHS
                ),
                "holdout_harness": engine_category_sha256(
                    inventory, "harness", paths=HOLDOUT_HARNESS_PATHS
                ),
            },
        },
        "package": package,
        "corpus": {"cases": case_ids},
        "holdout": {"pairs": pair_ids},
    }


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    unknown = set(snapshot) - SNAPSHOT_FIELDS
    missing = SNAPSHOT_FIELDS - set(snapshot)
    if unknown:
        raise IdentityError(f"unknown snapshot field: {', '.join(sorted(unknown))}")
    if missing:
        raise IdentityError(f"missing snapshot field: {', '.join(sorted(missing))}")
    if snapshot.get("schema_version") != 1:
        raise IdentityError("unsupported snapshot schema")
    categories = snapshot.get("engine", {}).get("categories")
    if not isinstance(categories, dict) or set(categories) != ENGINE_CATEGORY_FIELDS:
        raise IdentityError("invalid engine categories")
    scopes = snapshot.get("engine", {}).get("scopes")
    if not isinstance(scopes, dict) or set(scopes) != ENGINE_SCOPE_FIELDS:
        raise IdentityError("invalid engine scopes")
    if set(snapshot.get("package", {})) != {"semantic_sha256", "artifact_sha256"}:
        raise IdentityError("invalid package identities")
    if not isinstance(snapshot.get("corpus", {}).get("cases"), dict):
        raise IdentityError("invalid corpus identities")
    if not isinstance(snapshot.get("holdout", {}).get("pairs"), dict):
        raise IdentityError("invalid holdout identities")


def _changed_keys(before: dict[str, str], after: dict[str, str]) -> set[str]:
    return {
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    }


def _cost(corpus_cases: set[str], holdout: bool) -> dict[str, Any]:
    unknown_cases = corpus_cases - set(CORPUS_COST)
    if unknown_cases:
        raise IdentityError(
            "missing historical corpus cost: " + ", ".join(sorted(unknown_cases))
        )
    corpus_tokens = sum(CORPUS_COST[case][0] for case in corpus_cases)
    corpus_wall = sum(CORPUS_COST[case][1] for case in corpus_cases)
    holdout_order = list(HOLDOUT_COST)
    minimum_pairs = holdout_order[:2] if holdout else []
    maximum_pairs = holdout_order if holdout else []
    minimum_tokens = corpus_tokens + sum(
        HOLDOUT_COST[pair][0] for pair in minimum_pairs
    )
    maximum_tokens = corpus_tokens + sum(
        HOLDOUT_COST[pair][0] for pair in maximum_pairs
    )
    minimum_wall = corpus_wall + sum(HOLDOUT_COST[pair][1] for pair in minimum_pairs)
    maximum_wall = corpus_wall + sum(HOLDOUT_COST[pair][1] for pair in maximum_pairs)
    return {
        "basis": "0.3 v21 corpus and v23 holdout observed combined-token/wall receipts",
        "combined_tokens": {
            "minimum": minimum_tokens,
            "maximum": maximum_tokens,
        },
        "wall_seconds": {
            "minimum": round(minimum_wall, 3),
            "maximum": round(maximum_wall, 3),
        },
    }


def plan_impact(
    baseline: dict[str, Any],
    current: dict[str, Any],
    *,
    pending: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _validate_snapshot(baseline)
    _validate_snapshot(current)
    reasons: set[str] = set()
    gates: set[str] = set()
    corpus_cases: set[str] = set()
    holdout_pairs: set[str] = set()
    all_cases = set(current["corpus"]["cases"])
    all_pairs = set(current["holdout"]["pairs"])

    def full_live(reason: str) -> None:
        reasons.add(reason)
        gates.update({"corpus", "holdout"})
        corpus_cases.update(all_cases)
        holdout_pairs.update(all_pairs)

    if baseline["settings"] != current["settings"]:
        full_live("settings_changed")
    if (
        baseline["engine"]["categories"]["semantic"]
        != current["engine"]["categories"]["semantic"]
    ):
        full_live("engine_semantic_changed")
    if (
        baseline["engine"]["categories"]["artifact"]
        != current["engine"]["categories"]["artifact"]
    ):
        reasons.add("engine_artifact_changed")
        gates.add("receipt")
    harness_changed = (
        baseline["engine"]["categories"]["harness"]
        != current["engine"]["categories"]["harness"]
    )
    corpus_harness_changed = (
        baseline["engine"]["scopes"]["corpus_harness"]
        != current["engine"]["scopes"]["corpus_harness"]
    )
    holdout_harness_changed = (
        baseline["engine"]["scopes"]["holdout_harness"]
        != current["engine"]["scopes"]["holdout_harness"]
    )
    if harness_changed != (corpus_harness_changed or holdout_harness_changed):
        raise IdentityError("inconsistent harness aggregate and scope identities")
    if corpus_harness_changed:
        full_live("corpus_harness_changed")
    elif holdout_harness_changed:
        reasons.add("holdout_harness_changed")
        gates.add("holdout")
        holdout_pairs.update(all_pairs)
    if baseline["package"]["semantic_sha256"] != current["package"]["semantic_sha256"]:
        full_live("package_semantic_changed")
    elif (
        baseline["package"]["artifact_sha256"] != current["package"]["artifact_sha256"]
    ):
        reasons.add("package_artifact_changed")
        gates.add("isolated_install")

    changed_cases = _changed_keys(
        baseline["corpus"]["cases"], current["corpus"]["cases"]
    )
    if changed_cases:
        reasons.add("corpus_cases_changed")
        gates.add("corpus")
        corpus_cases.update(changed_cases & all_cases)
    changed_pairs = _changed_keys(
        baseline["holdout"]["pairs"], current["holdout"]["pairs"]
    )
    if changed_pairs:
        reasons.add("holdout_pairs_changed")
        gates.add("holdout")
        holdout_pairs.update(all_pairs)

    if pending:
        allowed_pending = {"reasons", "corpus_cases", "holdout_pairs", "review"}
        unknown_pending = set(pending) - allowed_pending
        if unknown_pending:
            raise IdentityError(
                "unknown pending field: " + ", ".join(sorted(unknown_pending))
            )
        reasons.update(pending.get("reasons", []))
        pending_cases = set(pending.get("corpus_cases", []))
        pending_pairs = set(pending.get("holdout_pairs", []))
        if not pending_cases <= all_cases or not pending_pairs <= all_pairs:
            raise IdentityError("pending scope is not present in current snapshot")
        if pending_cases:
            gates.add("corpus")
            corpus_cases.update(pending_cases)
        if pending_pairs:
            gates.add("holdout")
            holdout_pairs.update(pending_pairs)
        if pending.get("review"):
            gates.add("review")

    holdout_live = bool(holdout_pairs)
    minimum_calls = len(corpus_cases) + (4 if holdout_live else 0)
    maximum_calls = len(corpus_cases) + (6 if holdout_live else 0)
    return {
        "schema_version": 1,
        "reasons": sorted(reasons),
        "gates": [gate for gate in GATE_ORDER if gate in gates],
        "corpus_cases": sorted(corpus_cases),
        "holdout_pairs": sorted(holdout_pairs),
        "live_calls": {"minimum": minimum_calls, "maximum": maximum_calls},
        "cost": _cost(corpus_cases, holdout_live),
    }
