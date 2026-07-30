from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation import live
from evaluation.core.identity import (
    PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
    PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
    canonical_sha256,
    engine_inventory,
    invocation_profile,
    package_identities,
)
from evaluation.core.impact import DEFAULT_EFFORT, DEFAULT_MODEL, DEFAULT_TIMEOUT
from evaluation.core.ledger import apply_record, ledger_sha256


ROOT = Path(__file__).resolve().parents[1]


def verify_command() -> int:
    ledger, current, _impact = live.load_state()
    inventory = engine_inventory(ROOT)
    derived = live.derived_release_state(ledger)
    payload = {
        "schema_version": 1,
        "status": "ok",
        "ledger_state": derived["state"],
        "ledger_sha256": ledger_sha256(ledger, repo=ROOT),
        "snapshot_sha256": canonical_sha256(current),
        "engine_manifest_sha256": inventory["manifest_sha256"],
        "pending_gates": derived["pending_gates"],
        "coverage": derived["coverage"],
        "receipt_tip": derived["receipt_tip"],
        "freeze_eligibility": derived["freeze_eligibility"],
        "failed": derived["failed"],
        "certified": derived["certified"],
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def impact_command(public: Path | None = None) -> int:
    ledger, current, impact = live.load_state()
    if public is not None and package_identities(public) != {
        "artifact_sha256": PUBLIC_02_PACKAGE_ARTIFACT_SHA256,
        "semantic_sha256": PUBLIC_02_PACKAGE_SEMANTIC_SHA256,
    }:
        raise ValueError("public path does not equal frozen public-0.2 archive")
    print(
        json.dumps(
            {
                "snapshot": current,
                "impact": impact,
                "candidate": ledger["candidate"],
                "plans": ledger["plans"],
                "derived": live.derived_release_state(ledger),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 2 if ledger["candidate"] is None else 0


def apply_command(args: argparse.Namespace) -> int:
    repo = args.repo.resolve()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    after = apply_record(
        repo=repo,
        ledger_path=args.ledger,
        expected_predecessor_sha256=args.expected,
        record=record,
    )
    print(
        json.dumps(
            {
                "schema_version": 1,
                "status": "applied",
                "record_type": record.get("record_type"),
                "ledger_sha256": canonical_sha256(after),
                "derived": live.derived_release_state(after),
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


def _zero_effects() -> dict[str, int]:
    return {
        "intents_created": 0,
        "units_consumed": 0,
        "fixtures_created": 0,
        "outputs_created": 0,
        "receipts_created": 0,
        "workspaces_created": 0,
        "subprocesses": 0,
        "model_calls": 0,
        "network_calls": 0,
    }


def executor_command(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise ValueError("live calibration requires Root/Host effect orchestration")
    payload = {
        "schema_generation": 6,
        "command": "executor",
        "dry_run": True,
        "calibration_route": "corpus --calibrate",
        "invocation_profile": invocation_profile(
            model=args.model,
            effort=args.effort,
            timeout_seconds=args.timeout,
            arm=args.arm,
            session_mode="fresh",
        ),
        "effects": _zero_effects(),
        "gate_plan_is_permission": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def _gate_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default=DEFAULT_EFFORT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--bind-impact")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m evaluation.cli",
        description="HappyCodex clean-break certification engine",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate the release ledger")
    impact = commands.add_parser(
        "impact",
        help="derive full-refresh impact without authorizing effects",
    )
    impact.add_argument("--public", type=Path)
    apply = commands.add_parser(
        "apply",
        help="atomically append one complete release record",
    )
    apply.add_argument("--repo", type=Path, default=Path.cwd())
    apply.add_argument(
        "--ledger",
        type=Path,
        default=Path("evaluation/results/current.json"),
    )
    apply.add_argument("--expected", required=True)
    apply.add_argument("--record", type=Path, required=True)

    executor = commands.add_parser(
        "executor",
        help="inspect the calibration route without executing it",
    )
    _gate_options(executor)
    executor.add_argument("--arm", choices=("candidate",), default="candidate")
    executor.add_argument("--plugin", type=Path, default=ROOT)
    executor.add_argument("--output", type=Path)

    corpus = commands.add_parser("corpus", help="inspect or run behavior cases")
    corpus.add_argument("--plugin", type=Path, default=ROOT)
    corpus.add_argument("--case", action="append", dest="cases")
    corpus.add_argument("--list", action="store_true")
    corpus.add_argument("--calibrate", action="store_true")
    _gate_options(corpus)
    corpus.add_argument(
        "--arm",
        choices=("candidate", "public-0.2"),
        default="candidate",
    )
    corpus.add_argument("--output", type=Path)

    holdout = commands.add_parser("holdout", help="inspect or run blinded holdouts")
    holdout.add_argument("--candidate", type=Path, default=ROOT)
    holdout.add_argument("--public", type=Path)
    holdout.add_argument("--output", type=Path)
    holdout.add_argument("--list", action="store_true")
    _gate_options(holdout)
    return parser


def run_authorized(
    args: argparse.Namespace,
    effect_intents: dict[str, dict[str, Any]],
    claim_root: Path,
) -> int:
    """Host-only dispatch; validated content is not provenance or permission."""
    from evaluation.corpus import engine as corpus_engine
    from evaluation.holdout import engine as holdout_engine

    if args.command == "executor":
        args.cases = ["subthreshold-control"]
        args.calibrate = True
        return corpus_engine.run_authorized(args, effect_intents, claim_root)
    if args.command == "corpus":
        return corpus_engine.run_authorized(args, effect_intents, claim_root)
    if args.command == "holdout":
        return holdout_engine.run_authorized(args, effect_intents, claim_root)
    raise ValueError("authorized dispatch requires a model-reaching gate")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            return verify_command()
        if args.command == "impact":
            return impact_command(args.public)
        if args.command == "apply":
            return apply_command(args)
        if args.command == "executor":
            return executor_command(args)
        if args.command in {"corpus", "holdout"}:
            if args.list or args.dry_run:
                from evaluation.corpus import engine as corpus_engine
                from evaluation.holdout import engine as holdout_engine

                return {
                    "corpus": corpus_engine.run_command,
                    "holdout": holdout_engine.run_command,
                }[args.command](args)
            raise ValueError(
                "live execution requires Root/Host EffectIntent orchestration"
            )
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
