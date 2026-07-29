from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import (
    IdentityError,
    CORPUS_SEMANTIC_PATHS,
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    engine_paths_sha256,
    executor_role_identity,
    package_identities,
    toolchain_identity,
)


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_EFFORT = "high"
DEFAULT_TIMEOUT = 300
SNAPSHOT_FIELDS = {
    "schema_version",
    "settings",
    "engine",
    "package",
    "role",
    "corpus",
    "holdout",
}
ROLE_FIELDS = {"executor_sha256"}
ENGINE_CATEGORY_FIELDS = {"semantic", "harness", "artifact"}
ENGINE_SCOPE_FIELDS = {
    "corpus_harness",
    "corpus_semantic",
    "holdout_harness",
    "holdout_semantic",
}
ENGINE_FIELDS = {"categories", "scopes", "manifest_sha256"}
SETTINGS_FIELDS = {"model", "effort", "timeout_seconds", "toolchain"}
TOOLCHAIN_FIELDS = {"python", "codex", "git", "rg"}
TOOL_IDENTITY_FIELDS = {"path", "sha256", "version"}
IMPACT_FIELDS = {
    "schema_version",
    "reasons",
    "gates",
    "corpus_cases",
    "holdout_pairs",
    "live_calls",
    "cost",
}
CORPUS_HARNESS_PATHS = {
    "evaluation/__init__.py",
    "evaluation/cli.py",
    "evaluation/live.py",
    "evaluation/core/__init__.py",
    "evaluation/core/identity.py",
    "evaluation/core/impact.py",
    "evaluation/core/ledger.py",
    "evaluation/corpus/__init__.py",
}
HOLDOUT_HARNESS_PATHS = {
    "evaluation/holdout/__init__.py",
    "evaluation/holdout/blind.py",
    "evaluation/holdout/engine.py",
}
HOLDOUT_SEMANTIC_PATHS = {"evaluation/holdout/compare.py"}
GATE_ORDER = (
    "corpus",
    "executor_pilot",
    "holdout",
    "isolated_install",
    "receipt",
    "review",
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
    harness = {
        item["path"] for item in inventory["entries"] if item["category"] == "harness"
    }
    if harness != CORPUS_HARNESS_PATHS | HOLDOUT_HARNESS_PATHS:
        raise IdentityError("harness scope inventory is incomplete")
    package = package_identities(root)
    shared = engine_paths_sha256(inventory, CORPUS_SEMANTIC_PATHS)
    manifest, pairs = _load_holdouts(root)
    holdout_shared = canonical_sha256(
        {"corpus_contract_sha256": shared, "manifest": manifest}
    )

    def identities(
        values: dict[str, dict[str, Any]], shared_digest: str, arm: str
    ) -> dict[str, str]:
        return {
            item_id: case_semantic_sha256(
                item,
                shared_semantic_sha256=shared_digest,
                package_semantic_sha256=package["semantic_sha256"],
                model=model,
                effort=effort,
                timeout=timeout,
                arm=arm,
            )
            for item_id, item in sorted(values.items())
        }

    categories = {
        category: inventory["categories"][category]
        for category in ENGINE_CATEGORY_FIELDS
    }
    scopes = {
        "corpus_harness": engine_category_sha256(
            inventory, "harness", paths=CORPUS_HARNESS_PATHS
        ),
        "corpus_semantic": shared,
        "holdout_harness": engine_category_sha256(
            inventory, "harness", paths=HOLDOUT_HARNESS_PATHS
        ),
        "holdout_semantic": engine_category_sha256(
            inventory, "semantic", paths=HOLDOUT_SEMANTIC_PATHS
        ),
    }
    return {
        "schema_version": 1,
        "settings": {
            "model": model,
            "effort": effort,
            "timeout_seconds": timeout,
            "toolchain": toolchain_identity(),
        },
        "engine": {
            "manifest_sha256": inventory["manifest_sha256"],
            "categories": categories,
            "scopes": scopes,
        },
        "package": package,
        "role": {"executor_sha256": executor_role_identity(root)},
        "corpus": {"cases": identities(_load_cases(root), shared, "candidate")},
        "holdout": {"pairs": identities(pairs, holdout_shared, "blinded-pair")},
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
    if not isinstance(snapshot, dict) or set(snapshot) != SNAPSHOT_FIELDS:
        unknown = set(snapshot) - SNAPSHOT_FIELDS if isinstance(snapshot, dict) else set()
        label = "unknown" if unknown else "missing"
        raise IdentityError(f"{label} snapshot field")
    if snapshot["schema_version"] != 1:
        raise IdentityError("unsupported snapshot schema")
    settings = snapshot["settings"]
    if (
        not isinstance(settings, dict)
        or set(settings) != SETTINGS_FIELDS
        or any(type(settings[field]) is not str or not settings[field] for field in (
            "model", "effort"
        ))
        or type(settings["timeout_seconds"]) is not int
        or settings["timeout_seconds"] <= 0
    ):
        raise IdentityError("invalid snapshot settings")
    toolchain = settings["toolchain"]
    if not isinstance(toolchain, dict) or set(toolchain) != TOOLCHAIN_FIELDS:
        raise IdentityError("invalid snapshot toolchain")
    for name, identity in toolchain.items():
        if (
            not isinstance(identity, dict)
            or set(identity) != TOOL_IDENTITY_FIELDS
            or any(type(identity[field]) is not str or not identity[field] for field in (
                "path", "version"
            ))
            or re.fullmatch(r"[0-9a-f]{64}", identity["sha256"]) is None
        ):
            raise IdentityError(f"invalid snapshot tool identity: {name}")
    engine = snapshot["engine"]
    if (
        not isinstance(engine, dict)
        or set(engine) != ENGINE_FIELDS
        or re.fullmatch(r"[0-9a-f]{64}", engine["manifest_sha256"]) is None
        or not _digest_map(engine["categories"], ENGINE_CATEGORY_FIELDS)
        or not _digest_map(engine["scopes"], ENGINE_SCOPE_FIELDS)
    ):
        raise IdentityError("invalid engine identity")
    if (
        not _digest_map(
            snapshot["package"], {"semantic_sha256", "artifact_sha256"}
        )
        or not _digest_map(snapshot["role"], ROLE_FIELDS)
    ):
        raise IdentityError("invalid package or role identity")
    for envelope, field in (("corpus", "cases"), ("holdout", "pairs")):
        value = snapshot[envelope]
        if (
            not isinstance(value, dict)
            or set(value) != {field}
            or not _digest_map(value[field])
        ):
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
        raise IdentityError("generation-6 cost envelope is not persisted")


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
        reasons.add("engine_manifest_changed")
        gates.add("receipt")
    if before_engine["categories"]["artifact"] != after_engine["categories"]["artifact"]:
        reasons.add("engine_artifact_changed")
        gates.add("receipt")
    changes = {
        field: before_engine["scopes"][field] != after_engine["scopes"][field]
        for field in ENGINE_SCOPE_FIELDS
    }
    semantic_changed = (
        before_engine["categories"]["semantic"]
        != after_engine["categories"]["semantic"]
    )
    harness_changed = (
        before_engine["categories"]["harness"]
        != after_engine["categories"]["harness"]
    )
    if semantic_changed != (
        changes["corpus_semantic"] or changes["holdout_semantic"]
    ) or harness_changed != (
        changes["corpus_harness"] or changes["holdout_harness"]
    ):
        raise IdentityError("inconsistent aggregate and scope identities")
    if changes["corpus_harness"]:
        full_live("corpus_harness_changed")
    elif changes["holdout_harness"]:
        reasons.add("holdout_harness_changed")
        gates.add("holdout")
        holdout.update(all_pairs)
    if changes["corpus_semantic"]:
        full_live("corpus_semantic_changed")
    elif changes["holdout_semantic"]:
        reasons.add("holdout_semantic_changed")
        gates.add("holdout")
        holdout.update(all_pairs)
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
            raise IdentityError("invalid generation-6 pending envelope")
        pending_gates = pending["gates"]
        if pending_gates != [
            gate for gate in GATE_ORDER if gate in pending_gates
        ] or len(pending_gates) != len(set(pending_gates)):
            raise IdentityError("invalid generation-6 pending gates")
        pending_cases = set(pending["corpus_cases"])
        pending_pairs = set(pending["holdout_pairs"])
        if not pending_cases <= all_cases or not pending_pairs <= all_pairs:
            raise IdentityError("pending scope is absent from current snapshot")
        if ("corpus" in pending_gates) != bool(pending_cases) or (
            "holdout" in pending_gates
        ) != bool(pending_pairs):
            raise IdentityError("pending gate does not match scope")
        reasons.add("generation_6_genesis")
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
