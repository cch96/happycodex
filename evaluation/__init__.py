"""HappyCodex schema-v3 deterministic thin verifier."""

from evaluation.policy import RECORD_TYPES, SCHEMA_VERSION, UNIT_TOPOLOGY
from evaluation.records import (
    validate_attestation,
    validate_eval_spec,
    validate_product_artifact,
    validate_record,
    validate_release_receipt,
)

__version__ = "3.0.0"

__all__ = (
    "RECORD_TYPES",
    "SCHEMA_VERSION",
    "UNIT_TOPOLOGY",
    "__version__",
    "validate_attestation",
    "validate_eval_spec",
    "validate_product_artifact",
    "validate_record",
    "validate_release_receipt",
)
