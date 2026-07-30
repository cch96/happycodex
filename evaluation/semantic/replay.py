from __future__ import annotations

from .codec import parse_report, semantic_digest
from .model import CanonicalReport, SemanticError


def replay(records: object) -> tuple[CanonicalReport, ...]:
    if type(records) not in (list, tuple):
        raise SemanticError("receipt chain must be an exact list or tuple")
    previous: str | None = None
    consumed: set[str] = set()
    reports: list[CanonicalReport] = []
    for expected_sequence, value in enumerate(records):
        if type(value) is not dict or set(value) != {
            "sequence",
            "previous_hash",
            "report",
            "consumed_action",
        }:
            raise SemanticError("receipt link has an invalid shape")
        if (
            type(value["sequence"]) is not int
            or value["sequence"] != expected_sequence
        ):
            raise SemanticError("receipt sequence is non-monotonic")
        if value["previous_hash"] != previous:
            raise SemanticError("receipt previous hash mismatch")
        if type(value["consumed_action"]) is not bool:
            raise SemanticError("receipt consumption flag must be an exact boolean")
        report = parse_report(value["report"])
        if value["consumed_action"]:
            if report.action_key in consumed:
                raise SemanticError("ActionKey was consumed more than once")
            consumed.add(report.action_key)
        reports.append(report)
        previous = semantic_digest("receipt-link", value)
    return tuple(reports)


__all__ = ("replay",)
