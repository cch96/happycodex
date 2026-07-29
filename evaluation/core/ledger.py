from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any

from evaluation.core.identity import (
    BLOCKER_CLASSES,
    CONVERGENCE_PHASES,
    PERMISSION_FIELDS,
    PERMISSION_VALUES,
    RECOVERY_ACTIONS,
    RECOVERY_MANIFEST_PATTERN,
    RECOVERY_PENDING_GATES,
    RECOVERY_STATE_FIELDS,
    canonical_sha256,
    sha256_bytes,
    source_archive_identity,
)
from evaluation.core.impact import validate_snapshot


LEDGER_FIELDS = {
    "schema_version",
    "engine_generation",
    "state",
    "snapshot",
    "source_anchor",
    "pending",
    "authorities",
    "calibration_history",
    "accepted_evidence",
    "receipt_head",
    "certification",
}
PENDING_FIELDS = {"gates", "corpus_cases", "holdout_pairs"}
PENDING_GATES = (
    "corpus",
    "executor_pilot",
    "holdout",
    "isolated_install",
    "receipt",
    "review",
)
AUTHORITY_SLOTS = {"executor", "corpus", "holdout"}
SOURCE_ANCHOR_FIELDS = {
    "source_commit",
    "source_tree",
    "package_artifact_sha256",
    "package_semantic_sha256",
    "engine_manifest_sha256",
    "executor_role_sha256",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_OID = re.compile(r"^[0-9a-f]{40}$")
RECOVERY_MANIFEST_PATH = "docs/execplans/recovery-manifest.json"


def _object_schema(
    properties: dict[str, Any], *, nullable: bool = False
) -> dict[str, Any]:
    return {
        "type": ["object", "null"] if nullable else "object",
        "additionalProperties": False,
        "properties": properties,
        "required": sorted(properties),
    }


def _array_schema(items: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "items": items}


OUTPUT_SCHEMA = _object_schema(
    {
        "decision": {
            "type": "string",
            "enum": ["continue", "stop_for_user", "complete", "incomplete"],
        },
        "qualifies": {"type": "boolean"},
        "execplan_condition": {
            "type": "string",
            "enum": ["not_required", "missing", "usable", "needs_amendment"],
        },
        "protocol_may_product_write": {"type": "boolean"},
        "protocol_review_mode": {
            "type": "string",
            "enum": ["none", "focused_hardening", "exact_final"],
        },
        "protocol_may_complete": {"type": "boolean"},
        "finding_classifications": _array_schema(
            _object_schema(
                {
                    "identity": {"type": "string", "minLength": 1},
                    "domain": {
                        "type": "string",
                        "enum": ["secret", "baseline_failure", "receipt", "other"],
                    },
                    "state": {
                        "type": "string",
                        "enum": [
                            "baseline_unchanged",
                            "resolved",
                            "candidate_new",
                            "unknown",
                        ],
                    },
                    "anchors": _array_schema({"type": "string"}),
                }
            )
        ),
        "blocker_classifications": _array_schema(
            _object_schema(
                {
                    "identity": {"type": "string", "minLength": 1},
                    "class": {"type": "string", "enum": sorted(BLOCKER_CLASSES)},
                    "blocking": {"type": "boolean"},
                    "reason": {"type": "string"},
                }
            )
        ),
        "open_gates": _array_schema(
            {"type": "string", "enum": list(RECOVERY_PENDING_GATES)}
        ),
        "evidence": _array_schema({"type": "string"}),
        "reason": {"type": "string"},
        "recovery_state": _object_schema(
            {
                "baseline_revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "baseline_tree": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "current_revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "current_tree": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "writer": {"type": "string", "enum": ["Root", "unknown"]},
                "milestone_phase": {
                    "type": "string",
                    "enum": list(CONVERGENCE_PHASES),
                },
                "next_action": {"type": "string", "enum": list(RECOVERY_ACTIONS)},
                "pending_gates": _array_schema(
                    {"type": "string", "enum": list(RECOVERY_PENDING_GATES)}
                ),
                "tests": _object_schema(
                    {
                        "passed": {"type": "integer", "minimum": 0},
                        "failed": {"type": "integer", "minimum": 0},
                        "accepted_failures": {"type": "integer", "minimum": 0},
                        "marker_ids": _array_schema({"type": "string"}),
                    }
                ),
                "worktree": {
                    "type": "string",
                    "enum": ["clean", "dirty", "unknown"],
                },
                "live_agents": _array_schema(
                    _object_schema(
                        {
                            "id": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "terminal", "missing"],
                            },
                            "receipt_reproduced": {"type": "boolean"},
                        }
                    )
                ),
                "marker_ids": _array_schema({"type": "string"}),
            },
            nullable=True,
        ),
    }
)


def _unique_strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(type(item) is not str or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"invalid {label}")
    return value


def _permission_failures(expected: dict[str, Any]) -> bool:
    for field, allowed in PERMISSION_VALUES.items():
        raw = expected.get(field)
        values = raw if isinstance(raw, list) else [raw]
        expected_type = type(next(iter(allowed)))
        if (
            not values
            or len({(type(item), item) for item in values}) != len(values)
            or any(type(item) is not expected_type or item not in allowed for item in values)
        ):
            return True
    return False


def _validate_recovery_manifest(native: dict[str, Any], case_id: str) -> None:
    markers = [
        item
        for item in native["recovery_oracle"].get("marker_ids", [])
        if type(item) is str and RECOVERY_MANIFEST_PATTERN.fullmatch(item)
    ]
    if len(markers) != 1:
        raise ValueError(f"invalid Recovery Manifest marker: {case_id}")
    digest = RECOVERY_MANIFEST_PATTERN.fullmatch(markers[0]).group(1)
    content = native["post_compaction_transition"]["files"].get(
        RECOVERY_MANIFEST_PATH
    )
    if type(content) is not str or sha256_bytes(content.encode()) != digest:
        raise ValueError(f"Recovery Manifest digest mismatch: {case_id}")
    manifest = json.loads(content)
    fields = {
        "schema_version",
        "repositories",
        "resource_claim",
        "selected_checkpoint",
        "convergence",
        "writer",
        "tests",
        "agents",
        "gates",
    }
    if not isinstance(manifest, dict) or set(manifest) != fields:
        raise ValueError(f"invalid Recovery Manifest: {case_id}")
    repositories = manifest["repositories"]
    claim = manifest["resource_claim"]
    resources = claim.get("resources", []) if isinstance(claim, dict) else []
    convergence = manifest["convergence"]
    families = convergence.get("families", []) if isinstance(convergence, dict) else []
    tests = manifest["tests"]
    selected = manifest["selected_checkpoint"]
    agents = manifest["agents"]
    if (
        manifest["schema_version"] != 1
        or manifest["writer"] != "Root"
        or not isinstance(repositories, list)
        or not repositories
        or any(
            set(item) != {"namespace", "revision", "tree"}
            or type(item["namespace"]) is not str
            or not item["namespace"]
            or any(
                type(item[key]) is not str
                or re.fullmatch(r"[0-9a-f]{40}", item[key]) is None
                for key in ("revision", "tree")
            )
            for item in repositories
        )
        or len({item["namespace"] for item in repositories}) != len(repositories)
        or not isinstance(claim, dict)
        or set(claim) != {"owner", "owner_token_sha256", "resources"}
        or claim.get("owner") != "Root"
        or re.fullmatch(r"[0-9a-f]{64}", claim.get("owner_token_sha256", "")) is None
        or not isinstance(resources, list)
        or len(resources) != 5
        or any(
            type(item) is not str
            or re.fullmatch(
                r"(?:worktree|ref|ledger|output|activation):.+", item
            ) is None
            for item in resources
        )
        or len(resources) != len(set(resources))
        or {item.partition(":")[0] for item in resources}
        != {"worktree", "ref", "ledger", "output", "activation"}
        or not isinstance(selected, dict)
        or set(selected) != {"ref", "archive"}
        or (
            (
                type(selected["ref"]) is not str
                or re.fullmatch(
                    r"refs/(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]*"
                    r"[A-Za-z0-9_-]",
                    selected["ref"],
                )
                is None
            )
            if selected["archive"] is None
            else (
                selected["ref"] is not None
                or type(selected["archive"]) is not str
                or re.fullmatch(r"sha256:[0-9a-f]{64}", selected["archive"]) is None
            )
        )
        or not isinstance(convergence, dict)
        or set(convergence) != {"phase", "families"}
        or convergence.get("phase") not in CONVERGENCE_PHASES
        or not isinstance(families, list)
        or not families
        or any(
            not isinstance(item, dict)
            or set(item) != {"family_id", "status", "repair_batch", "recurrence"}
            or type(item["family_id"]) is not str
            or not item["family_id"].strip()
            or item["status"] not in {"open", "boundary_required", "closed"}
            or re.fullmatch(r".+/(?:instance|boundary)", item["repair_batch"]) is None
            or type(item["recurrence"]) is not int
            or item["recurrence"] < 0
            for item in families
        )
        or len({item["family_id"] for item in families}) != len(families)
        or not isinstance(tests, dict)
        or set(tests) != {"passed", "failed", "accepted_failures"}
        or any(type(tests[field]) is not int or tests[field] < 0 for field in tests)
        or tests["accepted_failures"] > tests["failed"]
        or not isinstance(agents, list)
        or any(
            not isinstance(item, dict)
            or set(item) != {"id", "status", "receipt_reproduced"}
            or type(item["id"]) is not str
            or not item["id"].strip()
            or item["status"] != "terminal"
            or item["receipt_reproduced"] is not True
            for item in agents
        )
        or len({item["id"] for item in agents}) != len(agents)
        or any(
            (item["recurrence"] == 0 and not item["repair_batch"].endswith("/instance"))
            or (
                item["recurrence"] > 0
                and not item["repair_batch"].endswith("/boundary")
            )
            or (
                item["status"] == "boundary_required"
                and item["recurrence"] != 1
            )
            or (
                item["recurrence"] >= 2
                and (
                    item["status"] != "open"
                    or convergence["phase"] != "focused_hardening"
                    or "user_selection" not in manifest["gates"]
                )
            )
            for item in families
        )
        or not _unique_strings(manifest["gates"], "Recovery Manifest gates")
    ):
        raise ValueError(f"invalid Recovery Manifest state: {case_id}")


def validate_case_input(case: dict[str, Any], path: Path) -> None:
    fields = {"schema_version", "id", "covers", "prompt", "fixture", "oracle"}
    if (
        not isinstance(case, dict)
        or set(case) != fields
        or case["schema_version"] != 1
        or re.fullmatch(r"[a-z0-9-]+", case["id"]) is None
        or "$happycodex:happycodex" not in case["prompt"]
    ):
        raise ValueError(f"invalid case envelope: {path}")
    fixture, oracle = case["fixture"], case["oracle"]
    if not fixture.get("commits"):
        raise ValueError(f"case needs a commit: {case['id']}")
    expected = oracle.get("expected", {})
    if set(expected) != PERMISSION_FIELDS or _permission_failures(expected):
        raise ValueError(f"invalid permission state: {case['id']}")
    accepted = _unique_strings(
        oracle.get("accepted_baseline_failures", []), "accepted baseline failures"
    )
    if len(accepted) != len(set(accepted)):
        raise ValueError(f"ambiguous accepted baseline failures: {case['id']}")
    prompts = [case["prompt"]]
    native = fixture.get("native_compaction_resume")
    if native is not None:
        native_fields = {
            "prepare_prompt",
            "fresh_recovery_prompt",
            "auto_compact_token_limit",
            "post_compaction_transition",
            "recovery_oracle",
        }
        if (
            not isinstance(native, dict)
            or set(native) != native_fields
            or type(native["auto_compact_token_limit"]) is not int
            or native["auto_compact_token_limit"] <= 0
            or set(native["recovery_oracle"])
            != RECOVERY_STATE_FIELDS
            - {"baseline_revision", "baseline_tree", "current_revision", "current_tree"}
        ):
            raise ValueError(f"invalid native compaction: {case['id']}")
        _validate_recovery_manifest(native, case["id"])
        prompts += [native["prepare_prompt"], native["fresh_recovery_prompt"]]
    identities = set()
    for key, item_fields, identity_field in (
        ("required_classifications", {"identity", "domain", "state"}, "identity"),
        ("required_blocker_classifications", {"identity", "class"}, "identity"),
        ("required_anchored_blockers", {"anchor", "class"}, "anchor"),
        ("required_anchored_classifications", {"anchor", "domain", "state"}, "anchor"),
    ):
        values = oracle.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"invalid {key}: {case['id']}")
        for item in values:
            identity = item.get(identity_field) if isinstance(item, dict) else None
            if (
                not isinstance(item, dict)
                or set(item) != item_fields
                or type(identity) is not str
                or not identity.strip()
            ):
                raise ValueError(f"invalid {key}: {case['id']}")
            identities.add(identity)
    classes = oracle.get("required_blocker_classes", [])
    if not isinstance(classes, list) or any(item not in BLOCKER_CLASSES for item in classes):
        raise ValueError(f"invalid blocker class: {case['id']}")
    coverage = oracle.get("coverage_assertions")
    if coverage is not None and (
        not isinstance(coverage, list)
        or len(coverage) != len(case["covers"])
        or {item.get("tag") for item in coverage} != set(case["covers"])
        or any(
            item.get("kind") != "recovery"
            and item.get("identity", item.get("anchor")) not in identities
            for item in coverage
        )
    ):
        raise ValueError(f"invalid coverage assertions: {case['id']}")
    prompt = " ".join(prompts).casefold()
    if any(item.casefold() in prompt for item in oracle.get("prompt_forbidden", [])):
        raise ValueError(f"prompt leaks oracle term: {case['id']}")


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def validate_evidence_commit(
    repo: Path, *, source_commit: str, evidence_commit: str
) -> None:
    """Require evidence to be a strict, HEAD-reachable descendant of source."""
    source = _git(repo, "rev-parse", "--verify", f"{source_commit}^{{commit}}")
    evidence = _git(repo, "rev-parse", "--verify", f"{evidence_commit}^{{commit}}")
    head = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if source == evidence:
        raise ValueError("evidence commit must strictly postdate source")
    for ancestor, descendant, message in (
        (source, evidence, "evidence commit does not descend from source"),
        (evidence, head, "evidence commit is not reachable from HEAD"),
    ):
        result = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant],
            check=False,
            capture_output=True,
        )
        if result.returncode:
            raise ValueError(message)


def validate_source_anchor(
    value: Any, *, repo: Path | None = None
) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != SOURCE_ANCHOR_FIELDS:
        raise ValueError("invalid source anchor")
    for field in SOURCE_ANCHOR_FIELDS:
        pattern = _GIT_OID if field in {"source_commit", "source_tree"} else _SHA256
        if not isinstance(value[field], str) or pattern.fullmatch(value[field]) is None:
            raise ValueError(f"invalid source anchor field: {field}")
    if repo is not None:
        archived = source_archive_identity(repo, value["source_commit"])
        expected = {
            "source_commit": archived["source_commit"],
            "source_tree": archived["source_tree"],
            "package_artifact_sha256": archived["package"]["artifact_sha256"],
            "package_semantic_sha256": archived["package"]["semantic_sha256"],
            "engine_manifest_sha256": archived["engine_manifest_sha256"],
            "executor_role_sha256": archived["executor_role_sha256"],
        }
        if value != expected:
            raise ValueError("source anchor does not match Git archive")
    return value


def _validate_pending(pending: Any, snapshot: dict[str, Any]) -> None:
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    if pending["gates"] != list(PENDING_GATES):
        raise ValueError("invalid generation-6 pending gates")
    expected = {
        "corpus_cases": sorted(snapshot["corpus"]["cases"]),
        "holdout_pairs": sorted(snapshot["holdout"]["pairs"]),
    }
    for field, identities in expected.items():
        value = pending[field]
        if value != identities or value != sorted(set(value)):
            raise ValueError(f"invalid pending scope: {field}")
    if len(expected["corpus_cases"]) != 17 or len(expected["holdout_pairs"]) != 3:
        raise ValueError("invalid generation-6 genesis cardinality")


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    if (
        set(ledger) != LEDGER_FIELDS
        or ledger.get("schema_version") != 1
        or ledger.get("engine_generation") != "0.6"
        or ledger.get("state") != "refresh_required"
    ):
        raise ValueError("invalid certification ledger envelope")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("invalid certification snapshot")
    validate_snapshot(snapshot)
    _validate_pending(ledger.get("pending"), snapshot)
    authorities = ledger.get("authorities")
    if (
        not isinstance(authorities, dict)
        or set(authorities) != AUTHORITY_SLOTS
        or any(value is not None for value in authorities.values())
    ):
        raise ValueError("generation-6 genesis authorities must be null")
    if ledger.get("calibration_history") != [] or ledger.get("accepted_evidence") != []:
        raise ValueError("generation-6 genesis must not retain prior evidence")
    if ledger.get("receipt_head") is not None:
        raise ValueError("generation-6 genesis receipt head must be null")
    if ledger.get("certification") is not None:
        raise ValueError("refresh-required ledger cannot carry certification")
    anchor = ledger.get("source_anchor")
    if anchor is not None:
        validated = validate_source_anchor(anchor, repo=repo)
        expected = {
            "package_artifact_sha256": snapshot["package"]["artifact_sha256"],
            "package_semantic_sha256": snapshot["package"]["semantic_sha256"],
            "engine_manifest_sha256": snapshot["engine"]["manifest_sha256"],
            "executor_role_sha256": snapshot["role"]["executor_sha256"],
        }
        if any(validated[field] != digest for field, digest in expected.items()):
            raise ValueError("source anchor does not match snapshot")


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    validate_ledger(value, repo=path.resolve().parents[2])
    return value


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)
