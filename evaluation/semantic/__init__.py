"""HappyCodex generation-7 provider-neutral semantic boundary."""

from .codec import (
    canonical_bytes,
    corpus_case_to_raw,
    parse_corpus_case,
    parse_machine_facts,
    parse_model_observation,
    parse_report,
    report_to_raw,
    semantic_digest,
)
from .model import (
    CanonicalReport,
    ControlBlocker,
    CorpusCase,
    Finding,
    MachineFacts,
    ModelObservation,
    NextAction,
    SemanticError,
)
from .reducer import build_report, reduce, validate_report
from .replay import replay


__all__ = (
    "SemanticError",
    "MachineFacts",
    "ModelObservation",
    "Finding",
    "ControlBlocker",
    "NextAction",
    "CanonicalReport",
    "CorpusCase",
    "parse_machine_facts",
    "parse_model_observation",
    "parse_corpus_case",
    "parse_report",
    "corpus_case_to_raw",
    "report_to_raw",
    "canonical_bytes",
    "semantic_digest",
    "reduce",
    "build_report",
    "validate_report",
    "replay",
)
