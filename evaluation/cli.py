from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.identity import evaluator_components, load_json, product_artifact_from_git
from evaluation.records import RECORD_TYPES, validate_eval_spec, validate_record
from evaluation.verify import verify_evaluation, verify_release


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


def _records(paths: list[Path]) -> list[dict[str, Any]]:
    return [validate_record(load_json(path.resolve())) for path in paths]


def inventory_command(args: argparse.Namespace) -> int:
    _print(
        {
            "durable_record_types": sorted(RECORD_TYPES),
            "components": evaluator_components(args.repo.resolve()),
            "active_ledger": False,
        }
    )
    return 0


def product_command(args: argparse.Namespace) -> int:
    _print(
        product_artifact_from_git(
            args.repo.resolve(), args.revision,
            external_role_config_sha256=args.external_role_config_sha256,
        )
    )
    return 0


def request_command(args: argparse.Namespace) -> int:
    spec = validate_eval_spec(load_json(args.spec.resolve()))
    # This is deliberately only a request digest. It cannot mint approval text,
    # signatures, capabilities, plans, or receipts.
    _print(
        {
            "scope": "evaluation",
            "authority_request_sha256": spec["authority_request_sha256"],
            "eval_spec_sha256": spec["record_sha256"],
            "total_cap": spec["total_cap"],
            "invocations": [
                {"unit_id": unit["unit_id"], "invocation_sha256": unit["invocation_sha256"]}
                for unit in spec["units"]
            ],
        }
    )
    return 0


def verify_command(args: argparse.Namespace) -> int:
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    spec = validate_record(load_json(args.spec.resolve()))
    attestations = _records(args.attestation)
    mapping = load_json(args.mapping.resolve()) if args.mapping else None
    result = verify_evaluation(
        product=product, spec=spec, attestations=attestations,
        previous_product=previous_product,
        holdout_mapping=mapping, mapping_revealed_at=args.revealed_at,
    )
    _print(result)
    return 0 if result["verified"] else 2


def release_command(args: argparse.Namespace) -> int:
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    spec = validate_record(load_json(args.spec.resolve()))
    attestations = _records(args.attestation)
    mapping = load_json(args.mapping.resolve())
    evaluation = verify_evaluation(
        product=product, spec=spec, attestations=attestations,
        previous_product=previous_product,
        holdout_mapping=mapping, mapping_revealed_at=args.revealed_at,
    )
    receipt = validate_record(load_json(args.release_receipt.resolve()))
    destination = load_json(args.destination.resolve())
    rollback = load_json(args.rollback.resolve())
    result = verify_release(
        product=product, evaluation=evaluation, receipt=receipt,
        destination=destination, rollback=rollback,
    )
    _print(result)
    return 0


def record_command(args: argparse.Namespace) -> int:
    record = validate_record(load_json(args.path.resolve()))
    _print({"valid": True, "record_type": record["record_type"], "record_sha256": record["record_sha256"]})
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Stateless HappyCodex evaluator attestation tools")
    sub = result.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory")
    inventory.add_argument("--repo", type=Path, default=Path.cwd())
    inventory.set_defaults(handler=inventory_command)

    product = sub.add_parser("product")
    product.add_argument("--repo", type=Path, default=Path.cwd())
    product.add_argument("--revision", required=True)
    product.add_argument("--external-role-config-sha256", required=True)
    product.set_defaults(handler=product_command)

    request = sub.add_parser("authority-request")
    request.add_argument("--spec", type=Path, required=True)
    request.set_defaults(handler=request_command)

    verify = sub.add_parser("verify")
    verify.add_argument("--product", type=Path, required=True)
    verify.add_argument("--previous-product", type=Path, required=True)
    verify.add_argument("--spec", type=Path, required=True)
    verify.add_argument("--attestation", type=Path, action="append", required=True)
    verify.add_argument("--mapping", type=Path)
    verify.add_argument("--revealed-at")
    verify.set_defaults(handler=verify_command)

    release = sub.add_parser("verify-release")
    release.add_argument("--product", type=Path, required=True)
    release.add_argument("--previous-product", type=Path, required=True)
    release.add_argument("--spec", type=Path, required=True)
    release.add_argument("--attestation", type=Path, action="append", required=True)
    release.add_argument("--mapping", type=Path, required=True)
    release.add_argument("--revealed-at", required=True)
    release.add_argument("--release-receipt", type=Path, required=True)
    release.add_argument("--destination", type=Path, required=True)
    release.add_argument("--rollback", type=Path, required=True)
    release.set_defaults(handler=release_command)

    record = sub.add_parser("validate-record")
    record.add_argument("path", type=Path)
    record.set_defaults(handler=record_command)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
