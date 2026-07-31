from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
from typing import Any

from evaluation.core.identity import (
    RECOVERY_MANIFEST_PATTERN,
    RECOVERY_STATE_FIELDS,
    canonical_sha256,
    executor_role_identity,
    package_identities,
    sha256_bytes,
    source_archive_identity,
)
from evaluation.core.schema import CONTRACTS, validate_named


LEDGER_FIELDS = frozenset({"schema_version", "candidate", "plans", "receipts"})
RECORD_TYPES = frozenset({"ReleaseCandidate", "GatePlan", "GateReceipt"})
GATE_ORDER = (
    "calibration",
    "corpus",
    "holdout",
    "receipt",
    "review",
    "isolated_install",
)
MODEL_GATES = frozenset({"calibration", "corpus", "holdout"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)
_CANDIDATE_FIELDS = frozenset(
    {
        "schema_version",
        "record_type",
        "source_commit",
        "source_tree",
        "package_artifact_sha256",
        "package_semantic_sha256",
        "executor_role_sha256",
        "created_at",
        "candidate_sha256",
    }
)
_PLAN_FIELDS = frozenset(
    {
        "schema_version",
        "record_type",
        "candidate_sha256",
        "snapshot_sha256",
        "gate",
        "created_at",
        "profile",
        "cost_ceiling",
        "units",
        "resource_digests",
        "output",
        "approval_request_sha256",
        "approval_content_sha256",
        "plan_sha256",
    }
)
_PROFILE_FIELDS = frozenset(
    {"argv", "cwd", "env", "timeout_ms", "model", "effort", "arm"}
)
_COST_FIELDS = frozenset(
    {
        "model_calls",
        "uncached_input_tokens",
        "output_tokens",
        "wall_milliseconds",
    }
)
_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "record_type",
        "candidate_sha256",
        "plan_sha256",
        "gate",
        "sequence",
        "created_at",
        "evidence_commit",
        "unit_results",
        "result",
        "output_sha256",
        "parent_receipt_sha256",
        "receipt_sha256",
    }
)
_UNIT_RESULT_FIELDS = frozenset({"unit", "status", "result_sha256"})
_RECOVERY_MANIFEST_PATH = "docs/execplans/recovery-manifest.json"


def _unique_strings(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(type(item) is not str or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError(f"invalid {label}")
    return value


def _validate_recovery_manifest(native: dict[str, Any], case_id: str) -> None:
    markers = [
        item
        for item in native["recovery_oracle"].get("marker_ids", [])
        if type(item) is str and RECOVERY_MANIFEST_PATTERN.fullmatch(item)
    ]
    if len(markers) != 1:
        raise ValueError(f"invalid Recovery Manifest marker: {case_id}")
    match = RECOVERY_MANIFEST_PATTERN.fullmatch(markers[0])
    digest = match.group(1)
    content = native["post_compaction_transition"]["files"].get(
        _RECOVERY_MANIFEST_PATH
    )
    if type(content) is not str or sha256_bytes(content.encode()) != digest:
        raise ValueError(f"Recovery Manifest digest mismatch: {case_id}")
    manifest = json.loads(content)
    validate_named(CONTRACTS, "recovery_manifest", manifest)
    repositories = manifest["repositories"]
    claim = manifest["resource_claim"]
    resources = claim["resources"]
    tests = manifest["tests"]
    selected = manifest["selected_checkpoint"]
    agents = manifest["agents"]
    selected_ok = (
        (
            type(selected["ref"]) is str
            and re.fullmatch(
                r"refs/(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]*[A-Za-z0-9_-]",
                selected["ref"],
            )
            is not None
        )
        if selected["archive"] is None
        else selected["ref"] is None
        and type(selected["archive"]) is str
        and re.fullmatch(r"sha256:[0-9a-f]{64}", selected["archive"]) is not None
    )
    if (
        len({item["namespace"] for item in repositories}) != len(repositories)
        or {item.partition(":")[0] for item in resources}
        != {"worktree", "ref", "ledger", "output", "activation"}
        or not selected_ok
        or tests["accepted_failures"] > tests["failed"]
        or any(item["receipt_reproduced"] is not True for item in agents)
        or len({item["id"] for item in agents}) != len(agents)
    ):
        raise ValueError(f"invalid Recovery Manifest state: {case_id}")
    oracle = native["recovery_oracle"]
    oracle_tests = {
        field: oracle["tests"][field]
        for field in ("passed", "failed", "accepted_failures")
    }
    if (
        manifest["writer"] != oracle["writer"]
        or manifest["gates"] != oracle["pending_gates"]
        or tests != oracle_tests
        or agents != oracle["live_agents"]
    ):
        raise ValueError(f"Recovery Manifest cross-binding mismatch: {case_id}")


def validate_case_input(case: dict[str, Any], path: Path) -> None:
    """Validate immutable behavior input without promoting its prose to state."""
    validate_named(CONTRACTS, "case", case)
    if "$happycodex:happycodex" not in case["prompt"]:
        raise ValueError(f"invalid case envelope: {path}")
    fixture, oracle = case["fixture"], case["oracle"]
    if not fixture.get("commits"):
        raise ValueError(f"case needs a commit: {case['id']}")
    prompts = [case["prompt"]]
    native = fixture.get("native_compaction_resume")
    if native is not None:
        required = {
            "prepare_prompt",
            "fresh_recovery_prompt",
            "auto_compact_token_limit",
            "post_compaction_transition",
            "recovery_oracle",
        }
        if (
            not isinstance(native, dict)
            or set(native) != required
            or type(native["auto_compact_token_limit"]) is not int
            or native["auto_compact_token_limit"] <= 0
            or set(native["recovery_oracle"])
            != RECOVERY_STATE_FIELDS
            - {
                "baseline_revision",
                "baseline_tree",
                "current_revision",
                "current_tree",
            }
        ):
            raise ValueError(f"invalid native compaction: {case['id']}")
        _validate_recovery_manifest(native, case["id"])
        prompts.extend(
            [native["prepare_prompt"], native["fresh_recovery_prompt"]]
        )
    finding_ids = {
        item["id"] for item in oracle.get("required_findings", [])
    }
    anchored_blockers = {
        (canonical_sha256(item["anchor"]), tuple(item["classes"]))
        for item in oracle.get("required_anchored_blockers", [])
    }
    coverage = oracle.get("coverage_assertions")
    if coverage is not None and (
        not isinstance(coverage, list)
        or len(coverage) != len(case["covers"])
        or {item.get("tag") for item in coverage} != set(case["covers"])
        or any(
            (
                item["kind"] == "finding"
                and item["finding_id"] not in finding_ids
            )
            or (
                item["kind"] == "anchored_blocker"
                and (
                    canonical_sha256(item["anchor"]),
                    tuple(item["classes"]),
                )
                not in anchored_blockers
            )
            for item in coverage
        )
    ):
        raise ValueError(f"invalid coverage assertions: {case['id']}")
    prompt = " ".join(prompts).casefold()
    if any(
        item.casefold() in prompt
        for item in oracle.get("prompt_forbidden", [])
    ):
        raise ValueError(f"prompt leaks oracle term: {case['id']}")


validate_case = validate_case_input


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


def _exact(value: Any, fields: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"invalid {label} fields")
    return value


def _digest(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"invalid {label} digest")
    return value


def _timestamp(value: Any, label: str) -> str:
    if type(value) is not str or _TIMESTAMP.fullmatch(value) is None:
        raise ValueError(f"invalid {label} timestamp")
    return value


def _sealed(record: dict[str, Any], field: str, label: str) -> None:
    digest = _digest(record[field], label)
    payload = dict(record)
    payload.pop(field)
    if digest != canonical_sha256(payload):
        raise ValueError(f"invalid {label} seal")


def validate_release_candidate(
    value: Any, *, repo: Path | None = None
) -> dict[str, Any]:
    record = _exact(value, _CANDIDATE_FIELDS, "ReleaseCandidate")
    if record["schema_version"] != 1 or record["record_type"] != "ReleaseCandidate":
        raise ValueError("invalid ReleaseCandidate type")
    for field in ("source_commit", "source_tree"):
        if type(record[field]) is not str or _GIT_OBJECT.fullmatch(record[field]) is None:
            raise ValueError(f"invalid ReleaseCandidate {field}")
    for field in (
        "package_artifact_sha256",
        "package_semantic_sha256",
        "executor_role_sha256",
    ):
        _digest(record[field], f"ReleaseCandidate {field}")
    _timestamp(record["created_at"], "ReleaseCandidate")
    _sealed(record, "candidate_sha256", "ReleaseCandidate")
    if repo is not None:
        from evaluation.core.impact import build_snapshot

        repo = repo.resolve()
        archived = source_archive_identity(repo, record["source_commit"])
        expected = {
            "source_commit": archived["source_commit"],
            "source_tree": archived["source_tree"],
            "package_artifact_sha256": archived["package"]["artifact_sha256"],
            "package_semantic_sha256": archived["package"]["semantic_sha256"],
            "executor_role_sha256": archived["executor_role_sha256"],
        }
        if any(record[field] != expected[field] for field in expected):
            raise ValueError("ReleaseCandidate does not match Git archive")
        if (
            package_identities(repo)
            != {
                "artifact_sha256": record["package_artifact_sha256"],
                "semantic_sha256": record["package_semantic_sha256"],
            }
            or executor_role_identity(repo) != record["executor_role_sha256"]
        ):
            raise ValueError("ReleaseCandidate product inputs drifted")
        head = _git(repo, "rev-parse", "HEAD^{commit}")
        if subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor",
             record["source_commit"], head],
            check=False,
            capture_output=True,
        ).returncode:
            raise ValueError("ReleaseCandidate source is not reachable")
    return record


def validate_gate_plan(value: Any) -> dict[str, Any]:
    record = _exact(value, _PLAN_FIELDS, "GatePlan")
    if record["schema_version"] != 1 or record["record_type"] != "GatePlan":
        raise ValueError("invalid GatePlan type")
    _digest(record["candidate_sha256"], "GatePlan candidate")
    _digest(record["snapshot_sha256"], "GatePlan snapshot")
    if record["gate"] not in GATE_ORDER:
        raise ValueError("invalid GatePlan gate")
    _timestamp(record["created_at"], "GatePlan")
    profile = _exact(record["profile"], _PROFILE_FIELDS, "GatePlan profile")
    if (
        not isinstance(profile["argv"], list)
        or not profile["argv"]
        or any(type(item) is not str or not item for item in profile["argv"])
        or type(profile["cwd"]) is not str
        or not Path(profile["cwd"]).is_absolute()
        or not isinstance(profile["env"], dict)
        or any(type(key) is not str or type(item) is not str
               for key, item in profile["env"].items())
        or type(profile["timeout_ms"]) is not int
        or profile["timeout_ms"] <= 0
        or any(type(profile[field]) is not str or not profile[field]
               for field in ("model", "effort", "arm"))
    ):
        raise ValueError("invalid GatePlan profile")
    cost = _exact(record["cost_ceiling"], _COST_FIELDS, "cost ceiling")
    if any(type(value) is not int or value < 0 for value in cost.values()):
        raise ValueError("invalid GatePlan cost ceiling")
    units = _unique_strings(record["units"], "GatePlan units")
    resources = _unique_strings(record["resource_digests"], "resource digests")
    if (
        not units
        or not resources
        or units != sorted(units)
        or resources != sorted(resources)
    ):
        raise ValueError("GatePlan units and resources must be sorted")
    if any(
        unit != unit.strip()
        or unit in {".", ".."}
        or "/" in unit
        or "\\" in unit
        or Path(unit).is_absolute()
        or len(Path(unit).parts) != 1
        or any(ord(character) < 32 or ord(character) == 127 for character in unit)
        for unit in units
    ):
        raise ValueError("GatePlan units must be safe single path components")
    for digest in resources:
        _digest(digest, "GatePlan resource")
    output = Path(record["output"]) if type(record["output"]) is str else Path()
    if (
        type(record["output"]) is not str
        or not output.is_absolute()
        or ".." in output.parts
        or output != Path(os.path.abspath(output))
    ):
        raise ValueError("invalid GatePlan output")
    _digest(record["approval_request_sha256"], "approval request")
    _digest(record["approval_content_sha256"], "approval content")
    _sealed(record, "plan_sha256", "GatePlan")
    return record


def validate_gate_receipt(value: Any) -> dict[str, Any]:
    record = _exact(value, _RECEIPT_FIELDS, "GateReceipt")
    if record["schema_version"] != 1 or record["record_type"] != "GateReceipt":
        raise ValueError("invalid GateReceipt type")
    _digest(record["candidate_sha256"], "GateReceipt candidate")
    _digest(record["plan_sha256"], "GateReceipt plan")
    if record["gate"] not in GATE_ORDER:
        raise ValueError("invalid GateReceipt gate")
    if type(record["sequence"]) is not int or record["sequence"] < 0:
        raise ValueError("invalid GateReceipt sequence")
    _timestamp(record["created_at"], "GateReceipt")
    if (
        type(record["evidence_commit"]) is not str
        or _GIT_OBJECT.fullmatch(record["evidence_commit"]) is None
    ):
        raise ValueError("invalid GateReceipt evidence commit")
    if record["result"] not in {"succeeded", "failed"}:
        raise ValueError("invalid GateReceipt result")
    _digest(record["output_sha256"], "GateReceipt output", nullable=True)
    _digest(
        record["parent_receipt_sha256"],
        "GateReceipt parent",
        nullable=True,
    )
    if not isinstance(record["unit_results"], list) or not record["unit_results"]:
        raise ValueError("invalid GateReceipt unit results")
    units = []
    for raw in record["unit_results"]:
        item = _exact(raw, _UNIT_RESULT_FIELDS, "unit result")
        if (
            type(item["unit"]) is not str
            or not item["unit"]
            or item["status"] not in {"succeeded", "failed"}
        ):
            raise ValueError("invalid GateReceipt unit result")
        _digest(item["result_sha256"], "unit result")
        units.append(item["unit"])
    if units != sorted(set(units)):
        raise ValueError("GateReceipt units must be sorted and unique")
    if record["result"] == "succeeded":
        if record["output_sha256"] is None:
            raise ValueError("successful GateReceipt needs an output digest")
        if any(
            item["status"] != "succeeded" for item in record["unit_results"]
        ):
            raise ValueError("successful GateReceipt contains a failed unit")
    elif all(
        item["status"] == "succeeded" for item in record["unit_results"]
    ):
        raise ValueError("failed GateReceipt needs a failed unit")
    _sealed(record, "receipt_sha256", "GateReceipt")
    return record


def validate_evidence_commit(
    repo: Path, *, source_commit: str, evidence_commit: str
) -> None:
    source = _git(repo, "rev-parse", "--verify", f"{source_commit}^{{commit}}")
    evidence = _git(repo, "rev-parse", "--verify", f"{evidence_commit}^{{commit}}")
    head = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if source == evidence:
        raise ValueError("evidence commit must strictly postdate source")
    for ancestor, descendant, message in (
        (source, evidence, "evidence commit does not descend from source"),
        (evidence, head, "evidence commit is not reachable from HEAD"),
    ):
        if subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor",
             ancestor, descendant],
            check=False,
            capture_output=True,
        ).returncode:
            raise ValueError(message)


def validate_ledger(ledger: dict[str, Any], *, repo: Path | None = None) -> None:
    _exact(ledger, LEDGER_FIELDS, "ledger")
    if ledger["schema_version"] != 1:
        raise ValueError("invalid ledger schema version")
    candidate = ledger["candidate"]
    if candidate is not None:
        validate_release_candidate(candidate, repo=repo)
    if not isinstance(ledger["plans"], list) or not isinstance(ledger["receipts"], list):
        raise ValueError("ledger containers must be arrays")
    plans: dict[str, dict[str, Any]] = {}
    for plan in ledger["plans"]:
        validate_gate_plan(plan)
        if candidate is None or plan["candidate_sha256"] != candidate["candidate_sha256"]:
            raise ValueError("GatePlan does not bind the candidate")
        if plan["gate"] in plans:
            raise ValueError("duplicate GatePlan gate")
        plans[plan["gate"]] = plan
    if [gate for gate in GATE_ORDER if gate in plans] != [
        plan["gate"] for plan in ledger["plans"]
    ]:
        raise ValueError("GatePlans are not in canonical gate order")
    plan_gates = [plan["gate"] for plan in ledger["plans"]]
    if plan_gates != list(GATE_ORDER[:len(plan_gates)]):
        raise ValueError("GatePlans must form a canonical prefix")
    receipt_count = len(ledger["receipts"])
    if len(ledger["plans"]) not in {receipt_count, receipt_count + 1}:
        raise ValueError("ledger must have at most one open GatePlan")
    if repo is not None and candidate is not None:
        from evaluation.core.impact import build_snapshot

        snapshot = build_snapshot(repo)
        snapshot_sha256 = canonical_sha256(snapshot)
        expected_units = {
            "calibration": ["subthreshold-control"],
            "corpus": sorted(snapshot["corpus"]["cases"]),
            "holdout": sorted(snapshot["holdout"]["pairs"]),
        }
        expected_arms = {
            "calibration": "candidate",
            "corpus": "candidate",
            "holdout": "blinded-pair",
        }
        settings = snapshot["settings"]
        for plan in plans.values():
            if plan["snapshot_sha256"] != snapshot_sha256:
                raise ValueError(
                    f"GatePlan {plan['gate']} does not bind the current snapshot"
                )
        for gate in MODEL_GATES & plans.keys():
            plan = plans[gate]
            profile = plan["profile"]
            if (
                plan["units"] != expected_units[gate]
                or profile["model"] != settings["model"]
                or profile["effort"] != settings["effort"]
                or profile["timeout_ms"] != settings["timeout_seconds"] * 1000
                or profile["arm"] != expected_arms[gate]
            ):
                raise ValueError(
                    f"GatePlan {gate} does not match snapshot scope and settings"
                )
    parent = None
    seen_gates = set()
    previous_created_at = candidate["created_at"] if candidate is not None else None
    for sequence, receipt in enumerate(ledger["receipts"]):
        validate_gate_receipt(receipt)
        plan = plans.get(receipt["gate"])
        if plan is None or receipt["plan_sha256"] != plan["plan_sha256"]:
            raise ValueError("GateReceipt does not bind an exact GatePlan")
        if candidate is None or receipt["candidate_sha256"] != candidate["candidate_sha256"]:
            raise ValueError("GateReceipt does not bind the candidate")
        if (
            receipt["sequence"] != sequence
            or receipt["parent_receipt_sha256"] != parent
            or receipt["gate"] in seen_gates
        ):
            raise ValueError("GateReceipt chain is not append-only and exact")
        if (
            previous_created_at is None
            or plan["created_at"] <= previous_created_at
            or receipt["created_at"] <= previous_created_at
            or receipt["created_at"] <= plan["created_at"]
        ):
            raise ValueError("GateReceipt chronology is not strictly increasing")
        receipt_units = [item["unit"] for item in receipt["unit_results"]]
        if receipt["gate"] == "holdout" and repo is not None:
            from evaluation.holdout.engine import load_manifest

            manifest = load_manifest(
                repo / "evaluation" / "holdouts" / "manifest.json"
            )
            execution_order = [pair["id"] for pair in manifest["pairs"]]
            valid_length = (
                len(receipt_units) in {1, 2, 3}
                if receipt["result"] == "failed"
                else len(receipt_units) in {2, 3}
            )
            if (
                sorted(execution_order) != plan["units"]
                or not valid_length
                or receipt_units
                != sorted(execution_order[:len(receipt_units)])
            ):
                raise ValueError(
                    "GateReceipt units do not equal an adaptive holdout prefix"
                )
        elif (
            receipt["gate"] == "corpus"
            and receipt["result"] == "failed"
        ):
            if receipt_units != plan["units"][:len(receipt_units)]:
                raise ValueError(
                    "failed corpus GateReceipt units do not equal "
                    "the execution prefix"
                )
        elif receipt_units != plan["units"]:
            raise ValueError("GateReceipt units do not equal the GatePlan")
        if repo is not None:
            validate_evidence_commit(
                repo,
                source_commit=candidate["source_commit"],
                evidence_commit=receipt["evidence_commit"],
            )
        parent = receipt["receipt_sha256"]
        previous_created_at = receipt["created_at"]
        seen_gates.add(receipt["gate"])
    if [gate for gate in GATE_ORDER if gate in seen_gates] != [
        receipt["gate"] for receipt in ledger["receipts"]
    ]:
        raise ValueError("GateReceipts are not in canonical gate order")
    failed_receipts = [
        receipt["gate"]
        for receipt in ledger["receipts"]
        if receipt["result"] == "failed"
    ]
    if failed_receipts:
        if (
            len(failed_receipts) != 1
            or ledger["receipts"][-1]["gate"] != failed_receipts[0]
            or len(ledger["plans"]) != len(ledger["receipts"])
        ):
            raise ValueError("a failed GateReceipt is terminal")
    if len(ledger["plans"]) == receipt_count + 1:
        open_plan = ledger["plans"][-1]
        if (
            previous_created_at is None
            or open_plan["created_at"] <= previous_created_at
        ):
            raise ValueError("open GatePlan chronology is not strictly increasing")


def ledger_sha256(ledger: dict[str, Any], *, repo: Path | None = None) -> str:
    validate_ledger(ledger, repo=repo)
    return canonical_sha256(ledger)


def derive_receipt_tip(ledger: dict[str, Any]) -> str | None:
    validate_ledger(ledger)
    return (
        ledger["receipts"][-1]["receipt_sha256"]
        if ledger["receipts"]
        else None
    )


def derive_coverage(ledger: dict[str, Any]) -> dict[str, list[str]]:
    validate_ledger(ledger)
    return {
        receipt["gate"]: [item["unit"] for item in receipt["unit_results"]]
        for receipt in ledger["receipts"]
        if receipt["result"] == "succeeded"
    }


def derive_failed(ledger: dict[str, Any]) -> list[str]:
    validate_ledger(ledger)
    return [
        receipt["gate"]
        for receipt in ledger["receipts"]
        if receipt["result"] == "failed"
    ]


def derive_pending(ledger: dict[str, Any]) -> dict[str, Any]:
    validate_ledger(ledger)
    completed = {
        receipt["gate"]
        for receipt in ledger["receipts"]
        if receipt["result"] == "succeeded"
    }
    plans = {plan["gate"]: plan for plan in ledger["plans"]}
    return {
        "gates": [gate for gate in GATE_ORDER if gate not in completed],
        "corpus_cases": plans.get("corpus", {}).get("units", []),
        "holdout_pairs": plans.get("holdout", {}).get("units", []),
    }


def derive_freeze_eligibility(
    ledger: dict[str, Any], *, repo: Path | None = None
) -> bool:
    validate_ledger(ledger, repo=repo)
    if repo is None:
        return False
    completed = set(derive_coverage(ledger))
    return (
        ledger["candidate"] is not None
        and not derive_failed(ledger)
        and {"calibration", "corpus", "holdout", "receipt"} <= completed
    )


def derive_certified(
    ledger: dict[str, Any], *, repo: Path | None = None
) -> bool:
    validate_ledger(ledger, repo=repo)
    return (
        repo is not None
        and derive_freeze_eligibility(ledger, repo=repo)
        and set(derive_coverage(ledger)) == set(GATE_ORDER)
    )


def derive_status(
    ledger: dict[str, Any], *, repo: Path | None = None
) -> str:
    return (
        "certified"
        if derive_certified(ledger, repo=repo)
        else "refresh_required"
    )


def validate_successor(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    repo: Path | None = None,
) -> None:
    validate_ledger(before, repo=repo)
    validate_ledger(after, repo=repo)
    if before == after:
        raise ValueError("ledger transition must append one record")
    if before["candidate"] is None:
        if (
            after["candidate"] is None
            or before["plans"] != after["plans"]
            or before["receipts"] != after["receipts"]
        ):
            raise ValueError("first transition must append ReleaseCandidate only")
        return
    if before["candidate"] != after["candidate"]:
        raise ValueError("ReleaseCandidate is immutable")
    if before["receipts"] != after["receipts"]:
        if before["plans"] != after["plans"]:
            raise ValueError("receipt transition cannot change plans")
        if after["receipts"][:-1] != before["receipts"]:
            raise ValueError("GateReceipt must append exactly once")
        return
    if after["plans"][:-1] != before["plans"]:
        raise ValueError("GatePlan must append exactly once")
    if derive_failed(before):
        raise ValueError("GatePlan cannot append after a failed receipt")
    if len(before["plans"]) != len(before["receipts"]):
        raise ValueError("GatePlan requires the prior receipt")


def append_record(
    before: dict[str, Any],
    record: dict[str, Any],
    *,
    repo: Path | None = None,
) -> dict[str, Any]:
    validate_ledger(before, repo=repo)
    record_type = record.get("record_type") if isinstance(record, dict) else None
    if record_type not in RECORD_TYPES:
        raise ValueError("unknown release record type")
    after = json.loads(json.dumps(before))
    if record_type == "ReleaseCandidate":
        if after["candidate"] is not None:
            raise ValueError("ReleaseCandidate already exists")
        after["candidate"] = record
    elif record_type == "GatePlan":
        after["plans"].append(record)
    else:
        after["receipts"].append(record)
    validate_successor(before, after, repo=repo)
    return after


def _read_nofollow(path: Path) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        mode = os.fstat(descriptor).st_mode
        if not stat.S_ISREG(mode):
            raise ValueError("ledger path is not a regular file")
        chunks = []
        while chunk := os.read(descriptor, 65536):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode()
        + b"\n"
    )


def apply_record(
    *,
    repo: Path,
    ledger_path: Path,
    expected_predecessor_sha256: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    repo = repo.resolve()
    candidate = ledger_path if ledger_path.is_absolute() else repo / ledger_path
    candidate = candidate.absolute()
    try:
        relative = candidate.relative_to(repo).as_posix()
    except ValueError as exc:
        raise ValueError("ledger path must stay inside the repository") from exc
    if candidate.is_symlink() or candidate.resolve() != candidate:
        raise ValueError("ledger path drift or symlink refused")
    raw = _read_nofollow(candidate)
    prior_git = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
        check=False,
        capture_output=True,
    )
    if prior_git.returncode or prior_git.stdout != raw:
        raise ValueError("worktree ledger differs from prior Git ledger")
    before = json.loads(raw)
    if canonical_sha256(before) != expected_predecessor_sha256:
        raise ValueError("stale ledger predecessor digest")
    after = append_record(before, record, repo=repo)
    data = _canonical_bytes(after)
    current = _read_nofollow(candidate)
    if current != raw:
        raise ValueError("ledger changed during transition")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{candidate.name}.",
        dir=candidate.parent,
    )
    try:
        os.fchmod(descriptor, stat.S_IMODE(candidate.stat().st_mode))
        os.write(descriptor, data)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        if _read_nofollow(candidate) != raw:
            raise ValueError("ledger changed before atomic replace")
        os.replace(temporary, candidate)
        directory = os.open(
            candidate.parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return after


def load_ledger(path: Path) -> dict[str, Any]:
    candidate = path.absolute()
    if (
        ".." in candidate.parts
        or candidate != Path(os.path.abspath(candidate))
    ):
        raise ValueError("ledger path alias or drift refused")
    chain = [candidate, *candidate.parents[:-1]]
    for component in chain:
        mode = component.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError("ledger path symlink or alias refused")
    repo = candidate.parents[2]
    raw = _read_nofollow(candidate)
    ledger = json.loads(raw)
    validate_ledger(ledger, repo=repo)
    relative = candidate.relative_to(repo).as_posix()
    prior = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
        check=False,
        capture_output=True,
    )
    if prior.returncode or prior.stdout != raw:
        raise ValueError("worktree ledger differs from prior Git ledger")
    return ledger


def replay_planned_lifecycle(
    ledger: dict[str, Any], *, repo: Path | None = None
) -> dict[str, Any]:
    validate_ledger(ledger, repo=repo)
    if ledger["candidate"] is None:
        raise ValueError("refresh-required genesis has no ReleaseCandidate")
    return {
        "candidate": ledger["candidate"],
        "plans": ledger["plans"],
        "receipts": ledger["receipts"],
    }


__all__ = (
    "GATE_ORDER",
    "MODEL_GATES",
    "append_record",
    "apply_record",
    "derive_certified",
    "derive_coverage",
    "derive_failed",
    "derive_freeze_eligibility",
    "derive_pending",
    "derive_receipt_tip",
    "derive_status",
    "ledger_sha256",
    "load_ledger",
    "replay_planned_lifecycle",
    "validate_case",
    "validate_case_input",
    "validate_evidence_commit",
    "validate_gate_plan",
    "validate_gate_receipt",
    "validate_ledger",
    "validate_release_candidate",
    "validate_successor",
)
