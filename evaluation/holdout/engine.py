#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import tempfile
from typing import Any, Callable

from evaluation.core.identity import (
    canonical_sha256,
    invocation_profile,
    sha256_bytes,
)
from evaluation.core.receipt import sanitized_case_receipt, write_new_json
from evaluation.corpus import engine as corpus_engine
from evaluation.holdout.blind import (
    ACTUAL_ARMS,
    ALIASES,
    blind_view,
    freeze_blind_decision,
    reveal_mapping,
    seal_mapping,
    validate_reveal,
)
from evaluation.holdout.compare import (
    compare_pair,
    decision_metrics,
)


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_ROOT = ROOT / "evaluation" / "holdouts"
MANIFEST_PATH = HOLDOUT_ROOT / "manifest.json"
HOLDOUT_ARM_WORKERS = 2


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    path = path.resolve()
    holdout_root = path.parent
    repo_root = holdout_root.parents[1]
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
        case_path = (repo_root / relative).resolve()
        if (
            relative.is_absolute()
            or not case_path.is_relative_to(holdout_root)
            or case_path.suffix != ".json"
            or not case_path.is_file()
        ):
            raise ValueError(f"unsafe holdout case path: {relative}")
        case = json.loads(case_path.read_text(encoding="utf-8"))
        corpus_engine.validate_case(case, case_path)
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


def _validate_pair_capability(
    authorization: Any,
    *,
    pair: dict[str, Any],
    candidate: Path,
    public: Path,
    model: str,
    effort: str,
    timeout: int,
) -> None:
    del authorization, pair, candidate, public, model, effort, timeout
    raise ValueError("generation-6 live capability is unavailable until Batch3")


def _evaluate_pair_arms(
    evaluate_alias: Callable[[str], dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Evaluate each arm once; exceptions abort, completed failures remain evidence."""
    with ThreadPoolExecutor(max_workers=HOLDOUT_ARM_WORKERS) as executor:
        results = executor.map(evaluate_alias, ALIASES)
        return dict(zip(ALIASES, results, strict=True))


def run_pair(
    pair: dict[str, Any],
    *,
    candidate: Path,
    public: Path,
    output: Path,
    model: str,
    effort: str,
    timeout: int,
    authorization: Any = None,
    evaluator: Callable[..., dict[str, Any]] = corpus_engine.evaluate_case,
) -> dict[str, Any]:
    _validate_pair_capability(
        authorization,
        pair=pair,
        candidate=candidate,
        public=public,
        model=model,
        effort=effort,
        timeout=timeout,
    )
    pair_output = output / pair["id"]
    pair_output.mkdir(parents=True, exist_ok=False)
    sealed = seal_mapping(pair["id"])
    commitment_sha = write_new_json(
        pair_output / "01-mapping-commitment.json", sealed.public_receipt()
    )
    plugins = {"candidate": candidate, "public-0.4.0": public}
    inverse = {alias: arm for arm, alias in sealed._mapping.items()}

    def evaluate_alias(alias: str) -> dict[str, Any]:
        arm = inverse[alias]
        return evaluator(
            pair["case"],
            plugin=plugins[arm],
            output=pair_output / "raw" / alias,
            model=model,
            effort=effort,
            timeout=timeout,
            arm=arm,
            authorization=authorization,
            authorization_unit=pair["id"],
        )

    raw = _evaluate_pair_arms(evaluate_alias)
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
        sanitized[arm] = sanitized_case_receipt(
            raw[alias], metadata_sha256=file_sha256(metadata_path)
        )
    receipt = {
        "schema_version": 1,
        "engine_generation": "0.6",
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
    authorization: Any,
) -> dict[str, Any]:
    del candidate, public, output, model, effort, timeout, authorization
    raise ValueError("generation-6 live capability is unavailable until Batch3")


def run_command(args: Any) -> int:
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
                    "invocation_profile": invocation_profile(
                        model=args.model,
                        effort=args.effort,
                        timeout_seconds=args.timeout,
                        arm="blinded-pair",
                    ),
                },
                indent=2,
            )
        )
        return 0
    raise SystemExit("live holdout execution is available only through evaluation.cli")


def run_authorized(args: Any, authorization: Any) -> int:
    del args, authorization
    raise SystemExit("generation-6 live capability is unavailable until Batch3")
