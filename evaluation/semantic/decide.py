from __future__ import annotations

from collections.abc import Mapping

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
    SemanticError,
)


def reduce_facts(facts: Facts) -> ProgressReport:
    pending = facts.stable["pending"]
    if pending:
        chosen = min(
            pending,
            key=lambda record: (record.payload["priority"], record.primary_key.value),
        )
        payload = chosen.payload
        action = NextAction(
            ActionKind(payload["kind"]),
            Id("action_target", payload["target"]),
            Id("action_scope", payload["scope"]),
            Id("falsifier", payload["falsifier_id"]),
            Id("evidence_source", payload["evidence_source_id"]),
        )
    else:
        action = NextAction(
            ActionKind.CLOSE,
            Id("action_target", facts.task.task.value),
            Id("action_scope", "task"),
            Id("falsifier", "no-pending-work"),
            Id("evidence_source", "facts"),
        )
    return ProgressReport(facts, make_progress_key(facts), action)


def enforce_effect(
    report: ProgressReport,
    authority: AuthorityProvenance | None,
) -> EffectGate:
    if authority is None:
        return EffectGate(
            EffectDecision.REFUSE,
            report.next_action.target,
            report.next_action.scope,
            "missing",
        )
    checks = (
        (not authority._adapter_issued, "spoofed"),
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
        if authority.kind.value == "DELEGATED"
        else EffectDecision.ALLOW
    )
    return EffectGate(decision, report.next_action.target, report.next_action.scope, "delegated" if decision is EffectDecision.ASK_USER else "direct")


def replay_report(raw: object) -> ProgressReport:
    if not isinstance(raw, Mapping) or set(raw) != {
        "facts",
        "progress_key",
        "next_action",
    }:
        raise SemanticError("report is invalid")
    report = reduce_facts(parse_facts(raw["facts"]))
    if raw["progress_key"] != report.progress_key.value:
        raise SemanticError("progress key mismatch")
    if raw["next_action"] != report.next_action.to_wire():
        raise SemanticError("action mismatch")
    return report


__all__ = ("enforce_effect", "reduce_facts", "replay_report")
