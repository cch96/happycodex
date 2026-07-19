from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.core.identity import canonical_sha256, engine_inventory
from evaluation.core.impact import (
    DEFAULT_EFFORT,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    build_snapshot,
    plan_impact,
)
from evaluation.core.receipt import ledger_sha256, load_ledger
from evaluation.corpus import engine as corpus_engine
from evaluation.holdout import engine as holdout_engine


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "evaluation" / "results" / "current.json"


def _settings_from_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    settings = ledger["snapshot"]["settings"]
    return {
        "model": settings["model"],
        "effort": settings["effort"],
        "timeout": settings["timeout_seconds"],
    }


def _load_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ledger = load_ledger(LEDGER_PATH)
    current = build_snapshot(ROOT, **_settings_from_ledger(ledger))
    impact = plan_impact(ledger["snapshot"], current, pending=ledger["pending"])
    return ledger, current, impact


def _approval_token(
    ledger: dict[str, Any], current: dict[str, Any], impact: dict[str, Any]
) -> str:
    return canonical_sha256(
        {
            "schema_version": 1,
            "ledger_sha256": ledger_sha256(ledger),
            "snapshot_sha256": canonical_sha256(current),
            "impact": impact,
        }
    )


def verify_command() -> int:
    ledger, current, impact = _load_state()
    inventory = engine_inventory(ROOT)
    payload = {
        "schema_version": 1,
        "status": "ok",
        "ledger_state": ledger["state"],
        "ledger_sha256": ledger_sha256(ledger),
        "snapshot_sha256": canonical_sha256(current),
        "engine_manifest_sha256": inventory["manifest_sha256"],
        "pending_gates": impact["gates"],
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def impact_command() -> int:
    ledger, current, impact = _load_state()
    payload = {
        **impact,
        "ledger_state": ledger["state"],
        "snapshot_sha256": canonical_sha256(current),
        "cost_approval_required": bool(impact["live_calls"]["maximum"]),
        "approval_token": _approval_token(ledger, current, impact),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m evaluation.cli",
        description="HappyCodex clean-break certification engine",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate identities and the evidence ledger")
    commands.add_parser("impact", help="print exact rerun gates and historical cost")

    corpus = commands.add_parser("corpus", help="inspect or run behavior cases")
    corpus.add_argument("--plugin", type=Path, default=ROOT)
    corpus.add_argument("--case", action="append", dest="cases")
    corpus.add_argument("--list", action="store_true")
    corpus.add_argument("--dry-run", action="store_true")
    corpus.add_argument("--model", default=DEFAULT_MODEL)
    corpus.add_argument("--effort", default=DEFAULT_EFFORT)
    corpus.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    corpus.add_argument(
        "--arm",
        choices=tuple(corpus_engine.EXPECTED_SKILL_ENTRIES_BY_ARM),
        default="candidate",
    )
    corpus.add_argument("--output", type=Path)
    corpus.add_argument("--approve-impact")

    holdout = commands.add_parser("holdout", help="inspect or run blinded holdouts")
    holdout.add_argument("--candidate", type=Path, default=ROOT)
    holdout.add_argument("--public", type=Path)
    holdout.add_argument("--output", type=Path)
    holdout.add_argument("--model", default=DEFAULT_MODEL)
    holdout.add_argument("--effort", default=DEFAULT_EFFORT)
    holdout.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    holdout.add_argument("--list", action="store_true")
    holdout.add_argument("--dry-run", action="store_true")
    holdout.add_argument("--approve-impact")
    return parser


def _require_live_approval(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    if args.list or args.dry_run:
        return
    ledger, current, impact = _load_state()
    expected = _approval_token(ledger, current, impact)
    if args.approve_impact != expected:
        parser.error(
            "live evaluation requires the exact approval_token from the current "
            "read-only impact receipt plus a persisted user cost approval"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "verify":
        return verify_command()
    if args.command == "impact":
        return impact_command()
    if args.command == "corpus":
        _require_live_approval(args, parser)
        return corpus_engine.run_command(args)
    if args.command == "holdout":
        _require_live_approval(args, parser)
        return holdout_engine.run_command(args)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
