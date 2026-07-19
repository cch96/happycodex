from __future__ import annotations

import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
from typing import Any

from evaluation.core.identity import (
    canonical_sha256,
    case_semantic_sha256,
    engine_category_sha256,
    engine_inventory,
    package_content_sha256,
    package_identities,
    sha256_bytes,
)
from evaluation.core.impact import impact_token, validate_impact, validate_snapshot
from evaluation.corpus.contract import PUBLIC_02_PACKAGE_ARTIFACT_SHA256
from evaluation.holdout.compare import (
    adaptive_next,
    aggregate_quality,
    cost_gate,
    sum_metrics,
)


LEDGER_FIELDS = {
    "schema_version",
    "state",
    "snapshot",
    "prior_evidence",
    "pending",
    "historical_cost",
    "live_authority",
    "certification",
}
PENDING_FIELDS = {"reasons", "corpus_cases", "holdout_pairs", "review"}
AUTHORITY_FIELDS = {
    "schema_version",
    "source",
    "approval_request_sha256",
    "approval_response",
    "approval_response_sha256",
    "snapshot_sha256",
    "impact",
    "impact_token",
    "invocations",
}
CORPUS_INVOCATION_FIELDS = {
    "command",
    "package_semantic_sha256",
    "package_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "arm",
    "cases",
}
HOLDOUT_INVOCATION_FIELDS = {
    "command",
    "candidate_semantic_sha256",
    "candidate_artifact_sha256",
    "public_semantic_sha256",
    "public_artifact_sha256",
    "model",
    "effort",
    "timeout_seconds",
    "pairs",
}
CERTIFICATION_FIELDS = {
    "schema_version",
    "successor_source_commit",
    "successor_source_tree",
    "snapshot_sha256",
    "engine_manifest_sha256",
    "evidence",
    "live_authority_sha256",
}
EVIDENCE_FIELDS = {
    "corpus_summary",
    "holdout_run",
    "holdout_summary",
    "review",
}
EVIDENCE_LOCATOR_FIELDS = {"commit", "path", "git_blob", "sha256"}
CORPUS_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "arm",
    "model",
    "effort",
    "timeout_seconds",
    "passed",
    "total",
    "uncached_input_tokens",
    "telemetry_complete",
    "output_tokens",
    "elapsed_seconds",
    "cases",
}
CASE_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "metadata_sha256",
    "installation",
    "model",
    "effort",
    "timeout_seconds",
    "timed_out",
    "elapsed_seconds",
    "exit_code",
    "semantic_input_sha256",
    "identities",
    "events_sha256",
    "stderr_sha256",
    "usage",
    "usage_phases",
    "uncached_input_tokens",
    "passed",
    "result",
    "fresh_recovery_result",
    "oracle_failures",
    "native_compaction",
    "thread_id_sha256",
    "resume_thread_id_sha256",
    "fresh_recovery_thread_id_sha256",
    "filesystem_isolation",
}
HOLDOUT_RUN_FIELDS = {
    "schema_version",
    "engine_generation",
    "manifest_sha256",
    "identities",
    "model",
    "effort",
    "timeout_seconds",
    "pair_ids",
    "case_sha256",
}
PAIR_RECEIPT_FIELDS = {
    "schema_version",
    "engine_generation",
    "id",
    "case_id",
    "case_sha256",
    "outside_diff_boundary",
    "oracle_kind",
    "mapping_commitment_file_sha256",
    "pre_reveal_decision_file_sha256",
    "mapping_reveal_file_sha256",
    "pre_reveal_decision_sha256",
    "mapping_commitment_sha256",
    "outcome",
    "metrics",
    "arms",
}
HOLDOUT_SUMMARY_FIELDS = {
    "schema_version",
    "engine_generation",
    "run_receipt_sha256",
    "adaptive_history",
    "adaptive_terminal_action",
    "pairs_run",
    "pair_receipts",
    "cost_gate",
}


def _require_digest(value: Any, *, length: int, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ValueError(f"invalid {label}")


def _validate_ordered_names(value: Any, *, label: str) -> None:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
        or value != sorted(set(value))
    ):
        raise ValueError(f"invalid authorized {label}")


def _validate_invocation(invocation: Any) -> None:
    if not isinstance(invocation, dict):
        raise ValueError("invalid authorized invocation")
    command = invocation.get("command")
    fields = {
        "corpus": CORPUS_INVOCATION_FIELDS,
        "holdout": HOLDOUT_INVOCATION_FIELDS,
    }.get(command)
    if fields is None or set(invocation) != fields:
        raise ValueError("invalid authorized invocation envelope")
    for field in ("model", "effort"):
        if not isinstance(invocation[field], str) or not invocation[field]:
            raise ValueError(f"invalid authorized invocation field: {field}")
    timeout = invocation["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("invalid authorized invocation field: timeout_seconds")
    if command == "corpus":
        digest_fields = ("package_semantic_sha256", "package_artifact_sha256")
        if invocation["arm"] != "candidate":
            raise ValueError("authorized corpus invocation must use candidate arm")
        _validate_ordered_names(invocation["cases"], label="corpus cases")
    else:
        digest_fields = (
            "candidate_semantic_sha256",
            "candidate_artifact_sha256",
            "public_semantic_sha256",
            "public_artifact_sha256",
        )
        _validate_ordered_names(invocation["pairs"], label="holdout pairs")
        if invocation["public_artifact_sha256"] != PUBLIC_02_PACKAGE_ARTIFACT_SHA256:
            raise ValueError("authorized holdout does not use frozen public-0.2")
    for field in digest_fields:
        _require_digest(invocation[field], length=64, label=field)


def _expected_authority_commands(impact: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    if impact["corpus_cases"]:
        commands.append("corpus")
    if impact["holdout_pairs"]:
        commands.append("holdout")
    return commands


def validate_live_authority(authority: Any, *, snapshot: dict[str, Any]) -> None:
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FIELDS:
        raise ValueError("live authority is not persisted")
    if authority.get("schema_version") != 1:
        raise ValueError("invalid live authority schema")
    validate_snapshot(snapshot)
    if not isinstance(authority.get("source"), str) or not re.fullmatch(
        r"current-task/user/[a-z0-9][a-z0-9._/-]*", authority["source"]
    ):
        raise ValueError("invalid live authority source")
    response = authority.get("approval_response")
    if not isinstance(response, str) or not response or len(response) > 10_000:
        raise ValueError("invalid approval response")
    if authority.get("approval_response_sha256") != sha256_bytes(response.encode()):
        raise ValueError("approval response digest mismatch")
    snapshot_sha256 = canonical_sha256(snapshot)
    if authority.get("snapshot_sha256") != snapshot_sha256:
        raise ValueError("live authority snapshot mismatch")
    impact = authority.get("impact")
    if not isinstance(impact, dict):
        raise ValueError("invalid authorized impact")
    validate_impact(impact, snapshot)
    token = impact_token(snapshot, impact)
    if authority.get("impact_token") != token:
        raise ValueError("live authority impact token mismatch")
    invocations = authority.get("invocations")
    if not isinstance(invocations, list):
        raise ValueError("live authority requires exact invocations")
    expected_commands = _expected_authority_commands(impact)
    if [
        item.get("command") for item in invocations if isinstance(item, dict)
    ] != expected_commands:
        raise ValueError("live authority does not cover complete impact scope")
    if not expected_commands:
        raise ValueError("live authority cannot authorize a zero-call impact")
    settings = snapshot["settings"]
    package = snapshot["package"]
    for invocation in invocations:
        _validate_invocation(invocation)
        if (
            invocation["model"] != settings["model"]
            or invocation["effort"] != settings["effort"]
            or invocation["timeout_seconds"] != settings["timeout_seconds"]
        ):
            raise ValueError("authorized invocation settings mismatch")
        if invocation["command"] == "corpus":
            candidate = {
                "semantic_sha256": invocation["package_semantic_sha256"],
                "artifact_sha256": invocation["package_artifact_sha256"],
            }
            if invocation["cases"] != impact["corpus_cases"]:
                raise ValueError("live authority does not cover complete impact scope")
        else:
            candidate = {
                "semantic_sha256": invocation["candidate_semantic_sha256"],
                "artifact_sha256": invocation["candidate_artifact_sha256"],
            }
            if invocation["pairs"] != impact["holdout_pairs"]:
                raise ValueError("live authority does not cover complete impact scope")
        if candidate != package:
            raise ValueError("authorized invocation package mismatch")
    request = {
        "schema_version": 1,
        "snapshot_sha256": snapshot_sha256,
        "impact": impact,
        "impact_token": token,
        "invocations": invocations,
    }
    if authority.get("approval_request_sha256") != canonical_sha256(request):
        raise ValueError("approval request digest mismatch")


def require_authorized_invocation(
    authority: Any,
    *,
    snapshot: dict[str, Any],
    impact: dict[str, Any],
    invocation: dict[str, Any],
) -> None:
    validate_live_authority(authority, snapshot=snapshot)
    validate_impact(impact, snapshot)
    if authority["impact"] != impact:
        raise ValueError("live authority does not match current impact")
    _validate_invocation(invocation)
    requested = canonical_sha256(invocation)
    authorized = {canonical_sha256(item) for item in authority["invocations"]}
    if requested not in authorized:
        raise ValueError("invocation is not authorized")


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )


def _require_reachable_commit(repo: Path, commit: str, *, label: str) -> None:
    _require_digest(commit, length=40, label=label)
    exists = _run_git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    reachable = _run_git(repo, "merge-base", "--is-ancestor", commit, "HEAD")
    if exists.returncode or reachable.returncode:
        raise ValueError(f"reachable certification evidence missing: {label}")


def _validate_source_identity(
    repo: Path, commit: str, snapshot: dict[str, Any]
) -> dict[str, Any]:
    archive = _run_git(repo, "archive", "--format=tar", commit)
    if archive.returncode:
        raise ValueError("cannot read certification successor source")
    with tempfile.TemporaryDirectory(prefix="happycodex-certified-source-") as raw:
        root = Path(raw)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as source:
            for member in source.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError("unsafe certification successor archive")
                if member.issym() or member.islnk():
                    target = PurePosixPath(member.linkname)
                    if target.is_absolute() or ".." in target.parts:
                        raise ValueError("unsafe certification successor archive link")
            source.extractall(root)
        try:
            source_package_content = package_content_sha256(root)
            inventory = engine_inventory(root)
        except (OSError, ValueError) as exc:
            raise ValueError("invalid certification successor source") from exc
        if (
            package_identities(repo) != snapshot["package"]
            or package_content_sha256(repo) != source_package_content
        ):
            raise ValueError("certification successor package mismatch")
        if inventory["manifest_sha256"] != snapshot["engine"]["manifest_sha256"]:
            raise ValueError("certification successor engine mismatch")
        manifest_path = root / "evaluation" / "holdouts" / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_bytes())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "invalid certification successor holdout manifest"
            ) from exc
        rows = manifest.get("pairs") if isinstance(manifest, dict) else None
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema_version") != 1
            or not isinstance(rows, list)
        ):
            raise ValueError("invalid certification successor holdout manifest")
        descriptors: dict[str, dict[str, Any]] = {}
        pair_order: list[str] = []
        holdout_root = (root / "evaluation" / "holdouts").resolve()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise ValueError("invalid certification successor holdout descriptor")
            pair_id = row["id"]
            relative = row.get("case_path")
            if not isinstance(relative, str):
                raise ValueError("invalid certification successor holdout case")
            case_path = (root / relative).resolve()
            if (
                pair_id in descriptors
                or not case_path.is_relative_to(holdout_root)
                or not case_path.is_file()
            ):
                raise ValueError("invalid certification successor holdout case")
            try:
                case = json.loads(case_path.read_bytes())
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "invalid certification successor holdout case"
                ) from exc
            if not isinstance(case, dict) or not isinstance(case.get("id"), str):
                raise ValueError("invalid certification successor holdout case")
            pair_order.append(pair_id)
            descriptors[pair_id] = {
                "case": case,
                "case_sha256": sha256_bytes(case_path.read_bytes()),
                "outside_diff_boundary": row.get("outside_diff_boundary"),
                "oracle_kind": row.get("oracle_kind"),
            }
        if set(pair_order) != set(snapshot["holdout"]["pairs"]):
            raise ValueError("certification successor holdout scope mismatch")
        return {
            "engine": inventory,
            "corpus_semantic_sha256": engine_category_sha256(
                inventory,
                "semantic",
                paths={"evaluation/corpus/contract.py"},
            ),
            "holdout_manifest_sha256": sha256_bytes(manifest_path.read_bytes()),
            "holdout_pair_order": pair_order,
            "holdout_descriptors": descriptors,
        }


def _load_evidence(
    repo: Path,
    locator: Any,
    *,
    label: str,
    source_commit: str,
) -> tuple[dict[str, Any], str]:
    if not isinstance(locator, dict) or set(locator) != EVIDENCE_LOCATOR_FIELDS:
        raise ValueError(f"invalid certification evidence locator: {label}")
    commit = locator["commit"]
    _require_reachable_commit(repo, commit, label=f"{label} commit")
    after_source = _run_git(repo, "merge-base", "--is-ancestor", source_commit, commit)
    if after_source.returncode:
        raise ValueError(f"certification evidence predates source: {label}")
    path = locator["path"]
    if not isinstance(path, str):
        raise ValueError(f"invalid certification evidence path: {label}")
    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.parts[:3] != ("evaluation", "results", "evidence")
        or relative.suffix != ".json"
    ):
        raise ValueError(f"unsafe certification evidence path: {label}")
    blob = _run_git(repo, "rev-parse", f"{commit}:{path}")
    content = _run_git(repo, "show", f"{commit}:{path}")
    if blob.returncode or content.returncode:
        raise ValueError(f"reachable certification evidence missing: {label}")
    actual_blob = blob.stdout.decode().strip()
    _require_digest(locator.get("git_blob"), length=40, label=f"{label} blob")
    if locator["git_blob"] != actual_blob:
        raise ValueError(f"certification evidence blob mismatch: {label}")
    actual_sha256 = sha256_bytes(content.stdout)
    _require_digest(locator.get("sha256"), length=64, label=f"{label} sha256")
    if locator["sha256"] != actual_sha256:
        raise ValueError(f"certification evidence digest mismatch: {label}")
    try:
        payload = json.loads(content.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"certification evidence is not JSON: {label}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"certification evidence must be an object: {label}")
    return payload, actual_sha256


def _validate_case_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    case_id: str,
    *,
    semantic_sha256: str,
    package: dict[str, str],
    engine: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    if (
        not isinstance(receipt, dict)
        or set(receipt) != CASE_RECEIPT_FIELDS
        or receipt.get("schema_version") != 1
        or receipt.get("engine_generation") != "0.4"
        or receipt.get("id") != case_id
    ):
        raise ValueError("invalid corpus evidence case")
    if (
        receipt.get("passed") is not True
        or receipt.get("timed_out") is not False
        or receipt.get("model") != settings["model"]
        or receipt.get("effort") != settings["effort"]
        or receipt.get("timeout_seconds") != settings["timeout_seconds"]
    ):
        raise ValueError(f"corpus evidence case did not pass: {case_id}")
    if receipt.get("semantic_input_sha256") != semantic_sha256:
        raise ValueError(f"corpus evidence semantic identity mismatch: {case_id}")
    identities = receipt.get("identities")
    if not isinstance(identities, dict) or set(identities) != {
        "engine",
        "package",
        "toolchain",
    }:
        raise ValueError(f"corpus evidence identities missing: {case_id}")
    if identities.get("engine") != engine:
        raise ValueError(f"corpus evidence engine mismatch: {case_id}")
    if identities.get("package") != package:
        raise ValueError(f"corpus evidence package mismatch: {case_id}")
    if identities.get("toolchain") != snapshot["settings"]["toolchain"]:
        raise ValueError(f"corpus evidence toolchain mismatch: {case_id}")
    for field in (
        "metadata_sha256",
        "events_sha256",
        "stderr_sha256",
        "thread_id_sha256",
        "resume_thread_id_sha256",
        "fresh_recovery_thread_id_sha256",
    ):
        _require_digest(receipt.get(field), length=64, label=f"case {field}")
    installation = receipt.get("installation")
    if not isinstance(installation, dict) or any(
        installation.get(field) != package["artifact_sha256"]
        for field in (
            "source_package_manifest_sha256",
            "installed_package_manifest_sha256",
        )
    ):
        raise ValueError(f"corpus evidence installation mismatch: {case_id}")
    for field in ("source_skill_sha256", "installed_skill_sha256"):
        _require_digest(
            installation.get(field), length=64, label=f"case installation {field}"
        )
    failures = receipt.get("oracle_failures")
    if failures != {"count": 0, "sha256": canonical_sha256([])}:
        raise ValueError(f"corpus evidence oracle failed: {case_id}")
    elapsed = receipt.get("elapsed_seconds")
    uncached = receipt.get("uncached_input_tokens")
    usage = receipt.get("usage")
    if (
        not isinstance(receipt.get("exit_code"), int)
        or isinstance(receipt.get("exit_code"), bool)
        or not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
        or not isinstance(uncached, int)
        or isinstance(uncached, bool)
        or uncached < 0
        or not isinstance(usage, dict)
        or not isinstance(usage.get("output_tokens"), int)
        or isinstance(usage.get("output_tokens"), bool)
        or usage["output_tokens"] < 0
        or not isinstance(receipt.get("usage_phases"), list)
        or not receipt["usage_phases"]
        or not isinstance(receipt.get("filesystem_isolation"), dict)
    ):
        raise ValueError(f"invalid corpus evidence telemetry: {case_id}")


def _validate_corpus_summary(
    payload: dict[str, Any], snapshot: dict[str, Any], source: dict[str, Any]
) -> None:
    settings = snapshot["settings"]
    cases = payload.get("cases")
    if (
        set(payload) != CORPUS_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("arm") != "candidate"
        or payload.get("model") != settings["model"]
        or payload.get("effort") != settings["effort"]
        or payload.get("timeout_seconds") != settings["timeout_seconds"]
        or payload.get("telemetry_complete") is not True
        or not isinstance(cases, list)
    ):
        raise ValueError("invalid corpus certification evidence")
    by_id = {
        item.get("id"): item
        for item in cases
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    expected = set(snapshot["corpus"]["cases"])
    if set(by_id) != expected or len(by_id) != len(cases):
        raise ValueError("corpus certification evidence is incomplete")
    if payload.get("total") != len(expected) or payload.get("passed") != len(expected):
        raise ValueError("corpus certification evidence is not all-pass")
    for case_id in sorted(expected):
        _validate_case_identity(
            by_id[case_id],
            snapshot,
            case_id,
            semantic_sha256=snapshot["corpus"]["cases"][case_id],
            package=snapshot["package"],
            engine=source["engine"],
        )
    if (
        payload.get("uncached_input_tokens")
        != sum(item["uncached_input_tokens"] for item in cases)
        or payload.get("output_tokens")
        != sum(item["usage"]["output_tokens"] for item in cases)
        or payload.get("elapsed_seconds")
        != round(sum(item["elapsed_seconds"] for item in cases), 3)
    ):
        raise ValueError("corpus certification evidence telemetry mismatch")


def _validate_holdout_run(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    authority: dict[str, Any],
    source: dict[str, Any],
) -> tuple[list[str], dict[str, str]]:
    settings = snapshot["settings"]
    identities = payload.get("identities")
    packages = identities.get("packages") if isinstance(identities, dict) else None
    engine = identities.get("engine") if isinstance(identities, dict) else None
    pair_ids = payload.get("pair_ids")
    if (
        set(payload) != HOLDOUT_RUN_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("manifest_sha256") != source["holdout_manifest_sha256"]
        or payload.get("model") != settings["model"]
        or payload.get("effort") != settings["effort"]
        or payload.get("timeout_seconds") != settings["timeout_seconds"]
        or engine != source["engine"]
        or not isinstance(packages, dict)
        or set(packages) != {"candidate", "public-0.2"}
        or packages.get("candidate") != snapshot["package"]
        or not isinstance(pair_ids, list)
        or pair_ids != source["holdout_pair_order"]
        or payload.get("case_sha256")
        != {
            pair_id: descriptor["case_sha256"]
            for pair_id, descriptor in source["holdout_descriptors"].items()
        }
        or identities.get("toolchain") != snapshot["settings"]["toolchain"]
    ):
        raise ValueError("invalid holdout run certification evidence")
    holdout_invocation = next(
        (item for item in authority["invocations"] if item["command"] == "holdout"),
        None,
    )
    public = packages.get("public-0.2")
    if holdout_invocation is not None:
        if not isinstance(public, dict) or public != {
            "semantic_sha256": holdout_invocation["public_semantic_sha256"],
            "artifact_sha256": holdout_invocation["public_artifact_sha256"],
        }:
            raise ValueError("holdout public evidence does not match authority")
    elif (
        not isinstance(public, dict)
        or set(public) != {"semantic_sha256", "artifact_sha256"}
        or public.get("artifact_sha256") != PUBLIC_02_PACKAGE_ARTIFACT_SHA256
    ):
        raise ValueError("invalid holdout public evidence")
    return pair_ids, public


def _validate_arm_identity(
    receipt: Any,
    snapshot: dict[str, Any],
    *,
    arm: str,
    descriptor: dict[str, Any],
    package: dict[str, str],
    source: dict[str, Any],
) -> None:
    settings = snapshot["settings"]
    semantic_sha256 = case_semantic_sha256(
        descriptor["case"],
        shared_semantic_sha256=source["corpus_semantic_sha256"],
        package_semantic_sha256=package["semantic_sha256"],
        model=settings["model"],
        effort=settings["effort"],
        timeout=settings["timeout_seconds"],
        arm=arm,
    )
    _validate_case_identity(
        receipt,
        snapshot,
        descriptor["case"]["id"],
        semantic_sha256=semantic_sha256,
        package=package,
        engine=source["engine"],
    )


def _validate_holdout_summary(
    payload: dict[str, Any],
    snapshot: dict[str, Any],
    *,
    run_pair_ids: list[str],
    run_sha256: str,
    public_package: dict[str, str],
    source: dict[str, Any],
) -> None:
    receipts = payload.get("pair_receipts")
    if (
        set(payload) != HOLDOUT_SUMMARY_FIELDS
        or payload.get("schema_version") != 1
        or payload.get("engine_generation") != "0.4"
        or payload.get("run_receipt_sha256") != run_sha256
        or not isinstance(receipts, list)
        or payload.get("pairs_run") != len(receipts)
        or not receipts
    ):
        raise ValueError("invalid holdout summary certification evidence")
    pair_ids = [item.get("id") for item in receipts if isinstance(item, dict)]
    if pair_ids != run_pair_ids[: len(pair_ids)] or len(pair_ids) != len(receipts):
        raise ValueError("holdout summary pair ordering mismatch")
    outcomes = [item.get("outcome") for item in receipts]
    if payload.get("adaptive_history") != outcomes or payload.get(
        "adaptive_terminal_action"
    ) != adaptive_next(outcomes):
        raise ValueError("holdout adaptive evidence mismatch")
    for receipt in receipts:
        if not isinstance(receipt, dict) or set(receipt) != PAIR_RECEIPT_FIELDS:
            raise ValueError("invalid holdout pair evidence")
        descriptor = source["holdout_descriptors"].get(receipt["id"])
        if (
            receipt.get("schema_version") != 1
            or receipt.get("engine_generation") != "0.4"
            or not isinstance(descriptor, dict)
            or receipt.get("case_id") != descriptor["case"]["id"]
            or receipt.get("case_sha256") != descriptor["case_sha256"]
            or receipt.get("outside_diff_boundary")
            is not descriptor["outside_diff_boundary"]
            or receipt.get("oracle_kind") != descriptor["oracle_kind"]
        ):
            raise ValueError("holdout pair does not match source descriptor")
        for field in (
            "mapping_commitment_file_sha256",
            "pre_reveal_decision_file_sha256",
            "mapping_reveal_file_sha256",
            "pre_reveal_decision_sha256",
            "mapping_commitment_sha256",
        ):
            _require_digest(
                receipt.get(field), length=64, label=f"holdout pair {field}"
            )
        arms = receipt.get("arms") if isinstance(receipt, dict) else None
        if not isinstance(arms, dict) or set(arms) != {"candidate", "public-0.2"}:
            raise ValueError("invalid holdout arm evidence")
        _validate_arm_identity(
            arms["candidate"],
            snapshot,
            arm="candidate",
            descriptor=descriptor,
            package=snapshot["package"],
            source=source,
        )
        _validate_arm_identity(
            arms["public-0.2"],
            snapshot,
            arm="public-0.2",
            descriptor=descriptor,
            package=public_package,
            source=source,
        )
    quality = aggregate_quality(outcomes)
    aggregate = {
        arm: sum_metrics([receipt["metrics"][arm] for receipt in receipts])
        for arm in ("candidate", "public-0.2")
    }
    expected_gate = cost_gate(
        aggregate["candidate"], aggregate["public-0.2"], quality=quality
    )
    if (
        payload.get("cost_gate") != expected_gate
        or not expected_gate["release_permitted"]
    ):
        raise ValueError("holdout cost/quality evidence does not permit certification")


def _validate_certification_receipt(
    certification: Any,
    *,
    snapshot: dict[str, Any],
    live_authority: dict[str, Any] | None,
    repo: Path | None,
) -> None:
    if (
        not isinstance(certification, dict)
        or set(certification) != CERTIFICATION_FIELDS
    ):
        raise ValueError("invalid certification receipt")
    if certification.get("schema_version") != 1:
        raise ValueError("invalid certification receipt schema")
    snapshot_sha256 = canonical_sha256(snapshot)
    if certification.get("snapshot_sha256") != snapshot_sha256:
        raise ValueError("certification receipt snapshot mismatch")
    if (
        certification.get("engine_manifest_sha256")
        != snapshot["engine"]["manifest_sha256"]
    ):
        raise ValueError("certification receipt engine manifest mismatch")
    if live_authority is None:
        raise ValueError("certification receipt requires live authority")
    validate_live_authority(live_authority, snapshot=snapshot)
    if certification.get("live_authority_sha256") != canonical_sha256(live_authority):
        raise ValueError("certification receipt authority mismatch")
    if repo is None or not (repo / ".git").exists():
        raise ValueError("reachable certification evidence requires a Git repository")
    repo = repo.resolve()
    source_commit = certification.get("successor_source_commit")
    _require_reachable_commit(repo, source_commit, label="successor source commit")
    tree = _run_git(repo, "rev-parse", f"{source_commit}^{{tree}}")
    if (
        tree.returncode
        or certification.get("successor_source_tree") != tree.stdout.decode().strip()
    ):
        raise ValueError("certification successor source tree mismatch")
    source = _validate_source_identity(repo, source_commit, snapshot)
    evidence = certification.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_FIELDS:
        raise ValueError("invalid certification evidence envelope")
    loaded: dict[str, dict[str, Any]] = {}
    evidence_sha: dict[str, str] = {}
    for label in sorted(EVIDENCE_FIELDS):
        loaded[label], evidence_sha[label] = _load_evidence(
            repo,
            evidence[label],
            label=label,
            source_commit=source_commit,
        )
    _validate_corpus_summary(loaded["corpus_summary"], snapshot, source)
    pair_ids, public_package = _validate_holdout_run(
        loaded["holdout_run"], snapshot, live_authority, source
    )
    _validate_holdout_summary(
        loaded["holdout_summary"],
        snapshot,
        run_pair_ids=pair_ids,
        run_sha256=evidence_sha["holdout_run"],
        public_package=public_package,
        source=source,
    )
    if not loaded["review"]:
        raise ValueError("review certification evidence is empty")


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    if set(ledger) != LEDGER_FIELDS or ledger.get("schema_version") != 1:
        raise ValueError("invalid certification ledger envelope")
    state = ledger.get("state")
    if state not in {"refresh_required", "certified"}:
        raise ValueError("invalid certification ledger state")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("invalid certification snapshot")
    validate_snapshot(snapshot)
    prior = ledger.get("prior_evidence")
    if not isinstance(prior, dict):
        raise ValueError("invalid prior evidence")
    for field in ("source_commit", "source_path", "sha256"):
        if not isinstance(prior.get(field), str):
            raise ValueError(f"invalid prior evidence field: {field}")
    _require_digest(prior["source_commit"], length=40, label="prior evidence commit")
    _require_digest(prior["sha256"], length=64, label="prior evidence digest")
    pending = ledger.get("pending")
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    if (
        not isinstance(pending["reasons"], list)
        or not all(isinstance(item, str) and item for item in pending["reasons"])
        or pending["reasons"] != sorted(set(pending["reasons"]))
    ):
        raise ValueError("invalid pending reasons")
    for field in ("corpus_cases", "holdout_pairs"):
        value = pending[field]
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or value != sorted(set(value))
        ):
            raise ValueError(f"invalid pending scope: {field}")
    if not isinstance(pending["review"], bool):
        raise ValueError("invalid pending review gate")
    if not isinstance(ledger.get("historical_cost"), dict):
        raise ValueError("invalid historical cost receipt")
    live_authority = ledger.get("live_authority")
    if live_authority is not None:
        validate_live_authority(live_authority, snapshot=snapshot)
    certification = ledger.get("certification")
    if state == "refresh_required":
        if certification is not None:
            raise ValueError("refresh-required ledger cannot carry certification")
        if not (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("refresh-required ledger must name a pending gate")
    else:
        if (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("certified ledger cannot retain pending gates")
        _validate_certification_receipt(
            certification,
            snapshot=snapshot,
            live_authority=live_authority,
            repo=repo,
        )


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    repo = path.resolve().parents[2]
    validate_ledger(value, repo=repo)
    return value


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)
