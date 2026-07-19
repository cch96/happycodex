from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from evaluation.core.identity import canonical_json_bytes, sha256_bytes


LEDGER_FIELDS = {
    "schema_version",
    "state",
    "snapshot",
    "prior_evidence",
    "pending",
    "historical_cost",
    "certification",
}
PENDING_FIELDS = {"reasons", "corpus_cases", "holdout_pairs", "review"}


def validate_ledger(ledger: dict[str, Any]) -> None:
    if set(ledger) != LEDGER_FIELDS or ledger.get("schema_version") != 1:
        raise ValueError("invalid certification ledger envelope")
    state = ledger.get("state")
    if state not in {"refresh_required", "certified"}:
        raise ValueError("invalid certification ledger state")
    snapshot = ledger.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError("invalid certification snapshot")
    prior = ledger.get("prior_evidence")
    if not isinstance(prior, dict):
        raise ValueError("invalid prior evidence")
    for field in ("source_commit", "source_path", "sha256"):
        if not isinstance(prior.get(field), str):
            raise ValueError(f"invalid prior evidence field: {field}")
    if not re.fullmatch(r"[0-9a-f]{40}", prior["source_commit"]):
        raise ValueError("invalid prior evidence commit")
    if not re.fullmatch(r"[0-9a-f]{64}", prior["sha256"]):
        raise ValueError("invalid prior evidence digest")
    pending = ledger.get("pending")
    if not isinstance(pending, dict) or set(pending) != PENDING_FIELDS:
        raise ValueError("invalid pending refresh envelope")
    if not isinstance(pending["reasons"], list) or not all(
        isinstance(item, str) and item for item in pending["reasons"]
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
        if not isinstance(certification, dict):
            raise ValueError("certified ledger requires a certification receipt")
        if (
            pending["reasons"]
            or pending["corpus_cases"]
            or pending["holdout_pairs"]
            or pending["review"]
        ):
            raise ValueError("certified ledger cannot retain pending gates")


def load_ledger(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("certification ledger must be an object")
    validate_ledger(value)
    return value


def ledger_sha256(ledger: dict[str, Any]) -> str:
    validate_ledger(ledger)
    return sha256_bytes(canonical_json_bytes(ledger))


def write_new_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode()
    with path.open("xb") as output:
        output.write(encoded)
        output.flush()
        os.fsync(output.fileno())
    return sha256_bytes(encoded)
