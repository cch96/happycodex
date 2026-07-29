from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from evaluation.semantic.canonical import make_progress_key
from evaluation.semantic.parse import parse_facts
from evaluation.semantic.types import (
    ActionKind,
    AuthorityProvenance,
    EffectDecision,
    EffectGate,
    Facts,
    Id,
    NextAction,
    ProgressReport,
    ProvenanceKind,
    SemanticError,
    _Record,
    _is_issued_authority,
    _is_reducer_report,
    _make_report,
)


_TERMINAL_STATES = MappingProxyType(
    {
        "checks": frozenset({"PASS", "BASELINE_ACCEPTED"}),
        "claims": frozenset({"VERIFIED", "N/A"}),
        "findings": frozenset({"RESOLVED", "BASELINE_ACCEPTED"}),
        "families": frozenset({"CLOSED", "N/A"}),
        "gates": frozenset({"SATISFIED", "WAIVED"}),
    }
)
_UNRESOLVED_ORDER = ("checks", "claims", "findings", "families", "gates")


def _pending_action(record: _Record) -> NextAction:
    payload = record.payload
    return NextAction(
        ActionKind(payload["kind"]),
        payload["target"],
        payload["scope"],
        payload["falsifier_id"],
        payload["evidence_source_id"],
    )


def _first_unresolved(facts: Facts) -> tuple[str, _Record] | None:
    for domain in _UNRESOLVED_ORDER:
        for record in facts.stable[domain]:
            if record.payload["state"] not in _TERMINAL_STATES[domain]:
                return domain, record
    return None


def _reconcile_action(domain: str, record: _Record) -> NextAction:
    identity = record.primary_key.value
    return NextAction(
        ActionKind.RECONCILE,
        Id("action_target", f"{domain}:{identity}"),
        Id("action_scope", domain),
        Id("falsifier", f"unresolved:{domain}:{identity}"),
        Id("evidence_source", "stable-facts"),
    )


def _default_close(facts: Facts) -> NextAction:
    return NextAction(
        ActionKind.CLOSE,
        Id("action_target", facts.task.task.value),
        Id("action_scope", "task"),
        Id("falsifier", "all-terminal"),
        Id("evidence_source", "facts"),
    )


def reduce_facts(facts: Facts) -> ProgressReport:
    progress_key = make_progress_key(facts)
    pending = facts.stable["pending"]
    non_close = tuple(
        record for record in pending if record.payload["kind"] != ActionKind.CLOSE.value
    )
    if non_close:
        chosen = min(
            non_close,
            key=lambda record: (record.payload["priority"], record.primary_key.value),
        )
        action = _pending_action(chosen)
    else:
        unresolved = _first_unresolved(facts)
        if unresolved is not None:
            action = _reconcile_action(*unresolved)
        elif pending:
            chosen = min(
                pending,
                key=lambda record: (
                    record.payload["priority"],
                    record.primary_key.value,
                ),
            )
            action = _pending_action(chosen)
        else:
            action = _default_close(facts)
    return _make_report(
        facts=facts,
        progress_key=progress_key,
        next_action=action,
    )


def enforce_effect(
    report: ProgressReport,
    authority: AuthorityProvenance | None,
) -> EffectGate:
    if (
        not _is_reducer_report(report)
        or report.progress_key != make_progress_key(report.facts)
    ):
        raise SemanticError("effect enforcement requires a reducer report")
    if authority is None:
        return EffectGate(
            EffectDecision.REFUSE,
            report.next_action.target,
            report.next_action.scope,
            "missing",
        )
    if not _is_issued_authority(authority):
        return EffectGate(
            EffectDecision.REFUSE,
            report.next_action.target,
            report.next_action.scope,
            "spoofed",
        )
    checks = (
        (authority.issuer != report.facts.task.root_task, "wrong_issuer"),
        (authority.destination != report.facts.task.destination, "wrong_destination"),
        (authority.lineage != report.facts.task.lineage, "wrong_lineage"),
        (authority.target != report.next_action.target, "wrong_target"),
        (authority.scope != report.next_action.scope, "wrong_scope"),
    )
    for failed, reason in checks:
        if failed:
            return EffectGate(
                EffectDecision.REFUSE,
                report.next_action.target,
                report.next_action.scope,
                reason,
            )
    decision = (
        EffectDecision.ASK_USER
        if authority.kind is ProvenanceKind.DELEGATED
        else EffectDecision.ALLOW
    )
    reason = "delegated" if decision is EffectDecision.ASK_USER else "direct"
    return EffectGate(
        decision,
        report.next_action.target,
        report.next_action.scope,
        reason,
    )


def replay_report(raw: object) -> ProgressReport:
    if not isinstance(raw, Mapping) or any(type(key) is not str for key in raw):
        raise SemanticError("report is invalid")
    if set(raw) != {"facts", "progress_key", "next_action"}:
        raise SemanticError("report is invalid")
    report = reduce_facts(parse_facts(raw["facts"]))
    if type(raw["progress_key"]) is not str:
        raise SemanticError("progress key mismatch")
    if raw["progress_key"] != report.progress_key.value:
        raise SemanticError("progress key mismatch")
    if raw["next_action"] != report.next_action.to_wire():
        raise SemanticError("action mismatch")
    return report

__all__ = ("enforce_effect", "reduce_facts", "replay_report")
