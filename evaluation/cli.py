from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.host import load_proof_verifier, reserve_claim
from evaluation.identity import evaluator_components, load_json, product_artifact_from_git
from evaluation.manifest import materialize_eval_spec
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
            "host_contract": spec["host_contract"],
            "host_contract_sha256": spec["host_contract_sha256"],
            "total_cap": spec["total_cap"],
            "invocations": [
                {"unit_id": unit["unit_id"], "invocation_sha256": unit["invocation_sha256"]}
                for unit in spec["units"]
            ],
        }
    )
    return 0


def materialize_command(args: argparse.Namespace) -> int:
    _print(
        materialize_eval_spec(
            root=args.repo.resolve(), candidate=validate_record(load_json(args.product.resolve())),
            previous=validate_record(load_json(args.previous_product.resolve())),
            profile=load_json(args.profile.resolve()), total_cap=load_json(args.total_cap.resolve()),
            holdout_mapping=load_json(args.mapping.resolve()),
            review_brief=load_json(args.review_brief.resolve()),
            host_contract=load_json(args.host_contract.resolve()),
        )
    )
    return 0


def _named_paths(values: list[str], label: str) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        unit_id, separator, raw_path = value.partition("=")
        if not separator or not unit_id or not raw_path or unit_id in result:
            raise ValueError(f"{label} must be unique UNIT=PATH values")
        result[unit_id] = Path(raw_path).resolve()
    return result


def _evidence(args: argparse.Namespace, spec: dict[str, Any]):
    raw_paths = _named_paths(args.raw, "raw")
    proof_paths = _named_paths(args.proof, "proof")
    return (
        {unit_id: path.read_bytes() for unit_id, path in raw_paths.items()},
        {unit_id: load_json(path) for unit_id, path in proof_paths.items()},
        load_proof_verifier(args.proof_verifier_command, spec["host_contract"]),
    )


def verify_command(args: argparse.Namespace) -> int:
    product = validate_record(load_json(args.product.resolve()))
    previous_product = validate_record(load_json(args.previous_product.resolve()))
    spec = validate_record(load_json(args.spec.resolve()))
    attestations = _records(args.attestation)
    mapping = load_json(args.mapping.resolve()) if args.mapping else None
    raw_streams, host_proofs, proof_verifier = _evidence(args, spec)
    result = verify_evaluation(
        root=args.repo.resolve(), product=product, spec=spec, attestations=attestations,
        raw_streams=raw_streams, host_proofs=host_proofs,
        proof_verifier=proof_verifier,
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
    raw_streams, host_proofs, proof_verifier = _evidence(args, spec)
    evaluation = verify_evaluation(
        root=args.repo.resolve(), product=product, spec=spec, attestations=attestations,
        raw_streams=raw_streams, host_proofs=host_proofs,
        proof_verifier=proof_verifier,
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


def claim_command(args: argparse.Namespace) -> int:
    previous_spec = validate_record(load_json(args.previous_spec.resolve())) if args.previous_spec else None
    _print(
        reserve_claim(
            root=args.claim_root.resolve(), claim_key=args.claim_key,
            invocation_sha256=args.invocation_sha256,
            recovery_index=args.recovery_index, recovery_cap=args.recovery_cap,
            previous_raw=args.previous_raw.read_bytes() if args.previous_raw else None,
            previous_attestation=(validate_record(load_json(args.previous_attestation.resolve())) if args.previous_attestation else None),
            previous_spec=previous_spec,
            previous_proof=(load_json(args.previous_proof.resolve()) if args.previous_proof else None),
            proof_verifier=(load_proof_verifier(args.proof_verifier_command, previous_spec["host_contract"]) if args.proof_verifier_command and previous_spec else None),
        )
    )
    return 0


def _add_evidence_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--raw", action="append", required=True, help="UNIT=PATH")
    command.add_argument("--proof", action="append", required=True, help="UNIT=PATH")
    command.add_argument("--proof-verifier-command", type=Path, required=True)


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

    materialize = sub.add_parser("materialize")
    materialize.add_argument("--repo", type=Path, default=Path.cwd())
    materialize.add_argument("--product", type=Path, required=True)
    materialize.add_argument("--previous-product", type=Path, required=True)
    materialize.add_argument("--profile", type=Path, required=True)
    materialize.add_argument("--total-cap", type=Path, required=True)
    materialize.add_argument("--mapping", type=Path, required=True)
    materialize.add_argument("--review-brief", type=Path, required=True)
    materialize.add_argument("--host-contract", type=Path, required=True)
    materialize.set_defaults(handler=materialize_command)

    verify = sub.add_parser("verify")
    verify.add_argument("--product", type=Path, required=True)
    verify.add_argument("--previous-product", type=Path, required=True)
    verify.add_argument("--spec", type=Path, required=True)
    verify.add_argument("--attestation", type=Path, action="append", required=True)
    verify.add_argument("--mapping", type=Path)
    verify.add_argument("--revealed-at")
    _add_evidence_arguments(verify)
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
    _add_evidence_arguments(release)
    release.set_defaults(handler=release_command)

    record = sub.add_parser("validate-record")
    record.add_argument("path", type=Path)
    record.set_defaults(handler=record_command)

    claim = sub.add_parser("claim")
    claim.add_argument("--claim-root", type=Path, required=True)
    claim.add_argument("--claim-key", required=True)
    claim.add_argument("--invocation-sha256", required=True)
    claim.add_argument("--recovery-index", type=int, default=0)
    claim.add_argument("--recovery-cap", type=int, default=0)
    claim.add_argument("--previous-raw", type=Path)
    claim.add_argument("--previous-attestation", type=Path)
    claim.add_argument("--previous-spec", type=Path)
    claim.add_argument("--previous-proof", type=Path)
    claim.add_argument("--proof-verifier-command", type=Path)
    claim.set_defaults(handler=claim_command)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
