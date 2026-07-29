from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from evaluation.core.impact import (
    build_snapshot,
    impact_token as snapshot_impact_token,
    plan_impact,
)
from evaluation.core.ledger import load_ledger
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


def load_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    ledger = load_ledger(LEDGER_PATH)
    current = build_snapshot(ROOT, **_settings_from_ledger(ledger))
    impact = plan_impact(ledger["snapshot"], current, pending=ledger["pending"])
    return ledger, current, impact


def impact_token(
    ledger: dict[str, Any], current: dict[str, Any], impact: dict[str, Any]
) -> str:
    del ledger
    return snapshot_impact_token(current, impact)


def run_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    offline_runner = {
        "corpus": corpus_engine.run_command,
        "holdout": holdout_engine.run_command,
    }[args.command]
    if args.list or args.dry_run:
        return offline_runner(args)
    parser.error(
        "generation-6 live capability, gate authority, and attempt wiring "
        "are unavailable until Batch3"
    )
    raise AssertionError("argparse error must terminate")
