#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import tempfile
from typing import Any, Callable

try:
    from . import run_corpus
except ImportError:  # Direct invocation: python3 evaluation/run_holdouts.py
    import run_corpus  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_ROOT = ROOT / "evaluation" / "holdouts"
MANIFEST_PATH = HOLDOUT_ROOT / "manifest.json"
ALIASES = ("arm-a", "arm-b")
ACTUAL_ARMS = ("candidate", "public-0.2")
BLIND_FIELDS = frozenset(
    {
        "passed",
        "timed_out",
        "exit_code",
        "oracle_failures_count",
        "uncached_input_tokens",
        "output_tokens",
        "elapsed_seconds",
    }
)
PAIR_OUTCOMES = frozenset({"better", "equal", "regression", "uncertain"})
QUALITY_OUTCOMES = frozenset(
    {"materially_better", "equal", "regression", "inconclusive"}
)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new_json(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()
    with path.open("xb") as output:
        output.write(encoded)
        output.flush()
        os.fsync(output.fileno())
    return hashlib.sha256(encoded).hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if set(raw) != {"schema_version", "pairs"} or raw["schema_version"] != 1:
        raise ValueError("invalid holdout manifest envelope")
    pairs = raw["pairs"]
    if not isinstance(pairs, list) or len(pairs) != 3:
        raise ValueError("holdout manifest must freeze exactly three pairs")
    loaded: list[dict[str, Any]] = []
    pair_ids: set[str] = set()
    case_ids: set[str] = set()
    expected_fields = {
        "id",
        "case_path",
        "outside_diff_boundary",
        "oracle_kind",
    }
    for raw_pair in pairs:
        if not isinstance(raw_pair, dict) or set(raw_pair) != expected_fields:
            raise ValueError("invalid holdout pair envelope")
        pair_id = raw_pair["id"]
        if not isinstance(pair_id, str) or not re.fullmatch(r"[a-z0-9-]+", pair_id):
            raise ValueError(f"invalid holdout pair id: {pair_id!r}")
        if pair_id in pair_ids:
            raise ValueError(f"duplicate holdout pair id: {pair_id}")
        pair_ids.add(pair_id)
        relative = Path(raw_pair["case_path"])
        case_path = (ROOT / relative).resolve()
        if (
            relative.is_absolute()
            or not case_path.is_relative_to(HOLDOUT_ROOT.resolve())
            or case_path.suffix != ".json"
            or not case_path.is_file()
        ):
            raise ValueError(f"unsafe holdout case path: {relative}")
        case = json.loads(case_path.read_text(encoding="utf-8"))
        run_corpus.validate_case(case, case_path)
        if case["id"] in case_ids:
            raise ValueError(f"duplicate holdout case id: {case['id']}")
        case_ids.add(case["id"])
        if not isinstance(raw_pair["outside_diff_boundary"], bool):
            raise ValueError(f"invalid boundary marker: {pair_id}")
        if raw_pair["oracle_kind"] not in {"mechanical", "behavioral"}:
            raise ValueError(f"invalid oracle kind: {pair_id}")
        loaded.append(
            {
                **raw_pair,
                "case_path": case_path,
                "case": case,
                "case_sha256": file_sha256(case_path),
            }
        )
    if not any(pair["outside_diff_boundary"] for pair in loaded[:2]):
        raise ValueError("first two holdouts need an outside-diff boundary")
    if not any(
        pair["oracle_kind"] in {"mechanical", "behavioral"} for pair in loaded[:2]
    ):
        raise ValueError("first two holdouts need a mechanical or behavioral oracle")
    return {
        "schema_version": 1,
        "manifest_sha256": file_sha256(path),
        "pairs": loaded,
    }


def blind_view(metadata: dict[str, Any]) -> dict[str, Any]:
    failures = metadata.get("oracle_failures")
    usage = metadata.get("usage")
    if not isinstance(failures, list) or not isinstance(usage, dict):
        raise ValueError("raw result lacks oracle or usage telemetry")
    view = {
        "passed": metadata.get("passed"),
        "timed_out": metadata.get("timed_out"),
        "exit_code": metadata.get("exit_code"),
        "oracle_failures_count": len(failures),
        "uncached_input_tokens": metadata.get("uncached_input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "elapsed_seconds": metadata.get("elapsed_seconds"),
    }
    validate_blind_view(view)
    return view


def validate_blind_view(view: dict[str, Any]) -> None:
    if set(view) != BLIND_FIELDS:
        raise ValueError("unexpected blind receipt fields")
    if not isinstance(view["passed"], bool) or not isinstance(view["timed_out"], bool):
        raise ValueError("invalid blind receipt status")
    if not isinstance(view["exit_code"], int) or isinstance(view["exit_code"], bool):
        raise ValueError("invalid blind receipt exit code")
    for field_name in (
        "oracle_failures_count",
        "uncached_input_tokens",
        "output_tokens",
    ):
        value = view[field_name]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid blind receipt metric: {field_name}")
    elapsed = view["elapsed_seconds"]
    if (
        not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
    ):
        raise ValueError("invalid blind receipt elapsed time")


def freeze_blind_decision(views: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if set(views) != set(ALIASES):
        raise ValueError("blind decision requires exactly arm-a and arm-b")
    aliases = []
    for alias in ALIASES:
        view = views[alias]
        validate_blind_view(view)
        passed = (
            view["passed"]
            and not view["timed_out"]
            and view["exit_code"] == 0
            and view["oracle_failures_count"] == 0
        )
        aliases.append(
            {
                "alias": alias,
                "blind_view_sha256": canonical_sha256(view),
                "quality": "pass" if passed else "fail",
                "metrics": {
                    "uncached_input_tokens": view["uncached_input_tokens"],
                    "output_tokens": view["output_tokens"],
                    "elapsed_seconds": view["elapsed_seconds"],
                },
            }
        )
    return {"schema_version": 1, "aliases": aliases}


@dataclass(frozen=True)
class SealedMapping:
    pair_id: str
    mapping_commitment_sha256: str
    _mapping: dict[str, str] = field(repr=False)
    _nonce: str = field(repr=False)

    def public_receipt(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "pair_id": self.pair_id,
            "mapping_commitment_sha256": self.mapping_commitment_sha256,
        }


def seal_mapping(
    pair_id: str, *, candidate_alias: str | None = None, nonce: str | None = None
) -> SealedMapping:
    if not re.fullmatch(r"[a-z0-9-]+", pair_id):
        raise ValueError("invalid pair id")
    candidate_alias = candidate_alias or ALIASES[secrets.randbelow(len(ALIASES))]
    if candidate_alias not in ALIASES:
        raise ValueError("candidate alias must be arm-a or arm-b")
    public_alias = next(alias for alias in ALIASES if alias != candidate_alias)
    nonce = nonce or secrets.token_hex(32)
    if not isinstance(nonce, str) or len(nonce) < 16:
        raise ValueError("mapping nonce is too short")
    mapping = {"candidate": candidate_alias, "public-0.2": public_alias}
    payload = {
        "schema_version": 1,
        "pair_id": pair_id,
        "mapping": mapping,
        "nonce": nonce,
    }
    return SealedMapping(pair_id, canonical_sha256(payload), mapping, nonce)


def reveal_mapping(
    sealed: SealedMapping, *, pre_reveal_decision_sha256: str
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{64}", pre_reveal_decision_sha256):
        raise ValueError("invalid pre-reveal decision digest")
    return {
        "schema_version": 1,
        "pair_id": sealed.pair_id,
        "mapping_commitment_sha256": sealed.mapping_commitment_sha256,
        "mapping": dict(sealed._mapping),
        "nonce": sealed._nonce,
        "pre_reveal_decision_sha256": pre_reveal_decision_sha256,
    }


def validate_reveal(reveal: dict[str, Any], decision: dict[str, Any]) -> None:
    expected_fields = {
        "schema_version",
        "pair_id",
        "mapping_commitment_sha256",
        "mapping",
        "nonce",
        "pre_reveal_decision_sha256",
    }
    if set(reveal) != expected_fields or reveal["schema_version"] != 1:
        raise ValueError("invalid reveal envelope")
    mapping = reveal["mapping"]
    payload = {
        "schema_version": 1,
        "pair_id": reveal["pair_id"],
        "mapping": mapping,
        "nonce": reveal["nonce"],
    }
    if canonical_sha256(payload) != reveal["mapping_commitment_sha256"]:
        raise ValueError("mapping commitment mismatch")
    if (
        not isinstance(mapping, dict)
        or set(mapping) != set(ACTUAL_ARMS)
        or set(mapping.values()) != set(ALIASES)
    ):
        raise ValueError("invalid revealed mapping")
    if canonical_sha256(decision) != reveal["pre_reveal_decision_sha256"]:
        raise ValueError("pre-reveal decision digest mismatch")


def compare_pair(decision: dict[str, Any], reveal: dict[str, Any]) -> str:
    validate_reveal(reveal, decision)
    rows = {row["alias"]: row for row in decision["aliases"]}
    if set(rows) != set(ALIASES):
        raise ValueError("decision aliases do not match reveal")
    candidate = rows[reveal["mapping"]["candidate"]]["quality"]
    public = rows[reveal["mapping"]["public-0.2"]]["quality"]
    if candidate == "fail":
        return "regression"
    return "better" if public == "fail" else "equal"


def adaptive_next(outcomes: list[str]) -> str:
    if len(outcomes) > 3 or any(outcome not in PAIR_OUTCOMES for outcome in outcomes):
        raise ValueError("invalid adaptive holdout history")
    if "regression" in outcomes:
        return "reject"
    if not outcomes:
        return "run_first"
    if len(outcomes) == 1:
        return "run_second"
    if len(outcomes) == 2 and ("uncertain" in outcomes or outcomes[0] != outcomes[1]):
        return "run_third"
    return "stop"


def aggregate_quality(outcomes: list[str]) -> str:
    if not outcomes or any(outcome not in PAIR_OUTCOMES for outcome in outcomes):
        raise ValueError("invalid holdout outcomes")
    if "regression" in outcomes:
        return "regression"
    conclusive = [outcome for outcome in outcomes if outcome != "uncertain"]
    if len(outcomes) < 3 and "uncertain" in outcomes:
        return "inconclusive"
    if len(outcomes) == 3:
        if len(conclusive) < 2:
            return "inconclusive"
        better = conclusive.count("better")
        equal = conclusive.count("equal")
        if better == equal:
            return "inconclusive"
        return "materially_better" if better > equal else "equal"
    if len(set(conclusive)) > 1:
        return "inconclusive"
    if "better" in conclusive:
        return "materially_better"
    return "equal"


def ratio(numerator: float, denominator: float) -> float | str:
    if denominator == 0:
        return 1.0 if numerator == 0 else "infinity"
    return numerator / denominator


def exceeds_threshold(value: float | str) -> bool:
    return value == "infinity" or (isinstance(value, float) and value > 1.25)


def validate_metrics(metrics: dict[str, Any]) -> None:
    if set(metrics) != {
        "uncached_input_tokens",
        "output_tokens",
        "elapsed_seconds",
    }:
        raise ValueError("invalid cost metrics envelope")
    for field_name in ("uncached_input_tokens", "output_tokens"):
        value = metrics[field_name]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid cost metric: {field_name}")
    elapsed = metrics["elapsed_seconds"]
    if (
        not isinstance(elapsed, (int, float))
        or isinstance(elapsed, bool)
        or not math.isfinite(elapsed)
        or elapsed < 0
    ):
        raise ValueError("invalid cost metric: elapsed_seconds")


def cost_gate(
    candidate: dict[str, Any], public: dict[str, Any], *, quality: str
) -> dict[str, Any]:
    validate_metrics(candidate)
    validate_metrics(public)
    if quality not in QUALITY_OUTCOMES:
        raise ValueError("invalid aggregate quality")
    candidate_combined = candidate["uncached_input_tokens"] + candidate["output_tokens"]
    public_combined = public["uncached_input_tokens"] + public["output_tokens"]
    blocking = {
        "combined_tokens": ratio(candidate_combined, public_combined),
        "wall": ratio(candidate["elapsed_seconds"], public["elapsed_seconds"]),
    }
    diagnostics = {
        "uncached_input_tokens": ratio(
            candidate["uncached_input_tokens"], public["uncached_input_tokens"]
        ),
        "output_tokens": ratio(candidate["output_tokens"], public["output_tokens"]),
    }
    expensive = any(exceeds_threshold(value) for value in blocking.values())
    if quality in {"regression", "inconclusive"}:
        decision = "reject"
    elif expensive and quality == "equal":
        decision = "simplify_and_retest"
    elif expensive and quality == "materially_better":
        decision = "user_confirmation_required"
    else:
        decision = "pass"
    return {
        "quality": quality,
        "threshold": 1.25,
        "candidate": {**candidate, "combined_tokens": candidate_combined},
        "public_0_2": {**public, "combined_tokens": public_combined},
        "blocking_ratios": blocking,
        "diagnostic_ratios": diagnostics,
        "decision": decision,
        "release_permitted": decision == "pass",
    }


def decision_metrics(
    decision: dict[str, Any], reveal: dict[str, Any]
) -> dict[str, Any]:
    validate_reveal(reveal, decision)
    rows = {row["alias"]: row for row in decision["aliases"]}
    return {arm: dict(rows[reveal["mapping"][arm]]["metrics"]) for arm in ACTUAL_ARMS}


def sum_metrics(values: list[dict[str, Any]]) -> dict[str, Any]:
    if not values:
        raise ValueError("cannot aggregate empty metrics")
    for value in values:
        validate_metrics(value)
    return {
        "uncached_input_tokens": sum(
            value["uncached_input_tokens"] for value in values
        ),
        "output_tokens": sum(value["output_tokens"] for value in values),
        "elapsed_seconds": round(sum(value["elapsed_seconds"] for value in values), 3),
    }


def run_pair(
    pair: dict[str, Any],
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    evaluator: Callable[..., dict[str, Any]] = run_corpus.evaluate_case,
) -> dict[str, Any]:
    pair_output = output / pair["id"]
    pair_output.mkdir(parents=True, exist_ok=False)
    sealed = seal_mapping(pair["id"])
    commitment_sha = write_new_json(
        pair_output / "01-mapping-commitment.json", sealed.public_receipt()
    )
    plugins = {"candidate": candidate, "public-0.2": public}
    inverse = {alias: arm for arm, alias in sealed._mapping.items()}
    raw: dict[str, dict[str, Any]] = {}
    for alias in ALIASES:
        arm = inverse[alias]
        raw[alias] = evaluator(
            pair["case"],
            plugin=plugins[arm],
            output=pair_output / "raw" / alias,
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
        )
    views = {alias: blind_view(raw[alias]) for alias in ALIASES}
    decision = freeze_blind_decision(views)
    decision_sha = write_new_json(pair_output / "02-pre-reveal-decision.json", decision)
    reveal = reveal_mapping(
        sealed, pre_reveal_decision_sha256=canonical_sha256(decision)
    )
    validate_reveal(reveal, decision)
    reveal_sha = write_new_json(pair_output / "03-mapping-reveal.json", reveal)
    outcome = compare_pair(decision, reveal)
    metrics = decision_metrics(decision, reveal)
    sanitized: dict[str, Any] = {}
    for arm in ACTUAL_ARMS:
        alias = reveal["mapping"][arm]
        metadata_path = (
            pair_output / "raw" / alias / pair["case"]["id"] / "metadata.json"
        )
        sanitized[arm] = run_corpus.sanitized_case_receipt(
            raw[alias], metadata_sha256=file_sha256(metadata_path)
        )
    receipt = {
        "schema_version": 1,
        "id": pair["id"],
        "case_id": pair["case"]["id"],
        "case_sha256": pair["case_sha256"],
        "outside_diff_boundary": pair["outside_diff_boundary"],
        "oracle_kind": pair["oracle_kind"],
        "mapping_commitment_file_sha256": commitment_sha,
        "pre_reveal_decision_file_sha256": decision_sha,
        "mapping_reveal_file_sha256": reveal_sha,
        "pre_reveal_decision_sha256": canonical_sha256(decision),
        "mapping_commitment_sha256": reveal["mapping_commitment_sha256"],
        "outcome": outcome,
        "metrics": metrics,
        "arms": sanitized,
    }
    write_new_json(pair_output / "04-pair-receipt.json", receipt)
    return receipt


def resolve_output(requested: Path | None, *plugins: Path) -> Path:
    output = (
        requested.expanduser().resolve()
        if requested is not None
        else Path(tempfile.mkdtemp(prefix="happycodex-holdouts-")).resolve()
    )
    for protected in (ROOT.resolve(), *(plugin.resolve() for plugin in plugins)):
        if output == protected or output.is_relative_to(protected):
            raise ValueError("raw holdout output must stay outside source and plugins")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("raw holdout output directory must be empty")
    return output


def run_holdouts(
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
) -> dict[str, Any]:
    manifest = load_manifest()
    candidate_manifest = run_corpus.package_manifest_sha256(candidate)
    public_manifest = run_corpus.package_manifest_sha256(public)
    if public_manifest != run_corpus.EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256:
        raise ValueError(
            "public-0.2 package manifest mismatch: "
            f"got {public_manifest}, expected "
            f"{run_corpus.EXPECTED_PUBLIC_02_PACKAGE_MANIFEST_SHA256}"
        )
    package_manifests = {
        "candidate": candidate_manifest,
        "public-0.2": public_manifest,
    }
    run_receipt = {
        "schema_version": 1,
        "manifest_sha256": manifest["manifest_sha256"],
        "holdout_runner_sha256": file_sha256(Path(__file__).resolve()),
        "corpus_runner_sha256": file_sha256(Path(run_corpus.__file__).resolve()),
        "package_manifests": package_manifests,
        "model": model,
        "effort": effort,
        "timeout_seconds": timeout,
        "pair_ids": [pair["id"] for pair in manifest["pairs"]],
        "case_sha256": {pair["id"]: pair["case_sha256"] for pair in manifest["pairs"]},
    }
    write_new_json(output / "00-run-receipt.json", run_receipt)
    receipts: list[dict[str, Any]] = []
    outcomes: list[str] = []
    while True:
        action = adaptive_next(outcomes)
        if action in {"reject", "stop"}:
            break
        pair = manifest["pairs"][len(outcomes)]
        receipt = run_pair(
            pair,
            candidate=candidate,
            public=public,
            output=output,
            model=model,
            effort=effort,
            timeout=timeout,
        )
        receipts.append(receipt)
        outcomes.append(receipt["outcome"])
    if {
        arm: run_corpus.package_manifest_sha256(path)
        for arm, path in (("candidate", candidate), ("public-0.2", public))
    } != package_manifests:
        raise RuntimeError("evaluated package changed during holdouts")
    quality = aggregate_quality(outcomes)
    aggregate = {
        arm: sum_metrics([receipt["metrics"][arm] for receipt in receipts])
        for arm in ACTUAL_ARMS
    }
    gate = cost_gate(aggregate["candidate"], aggregate["public-0.2"], quality=quality)
    summary = {
        "schema_version": 1,
        "run_receipt_sha256": file_sha256(output / "00-run-receipt.json"),
        "adaptive_history": outcomes,
        "adaptive_terminal_action": adaptive_next(outcomes),
        "pairs_run": len(receipts),
        "pair_receipts": receipts,
        "cost_gate": gate,
    }
    write_new_json(output / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run blinded adaptive HappyCodex holdouts"
    )
    parser.add_argument("--candidate", type=Path, default=ROOT)
    parser.add_argument("--public", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest()
    if args.list:
        for pair in manifest["pairs"]:
            print(pair["id"])
        return 0
    if args.dry_run:
        print(
            json.dumps(
                {
                    "manifest_sha256": manifest["manifest_sha256"],
                    "pairs": [
                        {
                            key: pair[key]
                            for key in (
                                "id",
                                "case_sha256",
                                "outside_diff_boundary",
                                "oracle_kind",
                            )
                        }
                        for pair in manifest["pairs"]
                    ],
                    "adaptive_policy": [
                        "first regression rejects",
                        "otherwise second pair is mandatory",
                        "split or uncertainty runs the third pair",
                    ],
                },
                indent=2,
            )
        )
        return 0
    if args.public is None:
        raise SystemExit("--public is required for a live paired run")
    candidate = args.candidate.expanduser().resolve()
    public = args.public.expanduser().resolve()
    try:
        output = resolve_output(args.output, candidate, public)
        summary = run_holdouts(
            candidate=candidate,
            public=public,
            output=output,
            model=args.model,
            effort=args.effort,
            timeout=args.timeout,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(summary, indent=2))
    return 0 if summary["cost_gate"]["release_permitted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
