from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from evaluation.semantic.canonical import _digest, make_progress_key
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
    _Record,
    _is_issued_authority,
    _is_reducer_report,
    _make_report,
    _validate_authority,
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
_GATE_POLICY = (
    ("user_selection", ActionKind.ASK_USER),
    ("contract_freeze", ActionKind.VERIFY),
    ("red_oracle", ActionKind.VERIFY),
    ("product_edit", ActionKind.IMPLEMENT_BATCH),
    ("checks", ActionKind.VERIFY),
    ("family_hardening", ActionKind.IMPLEMENT_BATCH),
    ("boundary_repair", ActionKind.IMPLEMENT_BATCH),
    ("reconciliation", ActionKind.RECONCILE),
    ("focused_review", ActionKind.FOCUSED_REVIEW),
    ("candidate_freeze", ActionKind.FREEZE_CANDIDATE),
    ("exact_final_review", ActionKind.EXACT_FINAL),
    ("release", ActionKind.VERIFY),
)
def _family_for(facts: Facts, domain: str, record: _Record) -> Id:
    if domain == "gates":
        return record.payload["family_id"]
    if domain == "families":
        return Id("family_id", record.primary_key.value)
    return Id("family_id", f"task:{facts.task.task.value}")
def _evidence_source(evidence: tuple[str, ...]) -> Id:
    return Id(
        "evidence_source",
        f"evidence:{_digest('happycodex/0.6/evidence-source', evidence)}",
    )
def _unresolved_action(facts: Facts, domain: str, record: _Record) -> NextAction:
    identity = record.primary_key.value
    state = record.payload["state"]
    if domain == "checks":
        kind = ActionKind.RECONCILE if identity == "execplan" else ActionKind.VERIFY
    elif domain == "findings" and state == "OPEN":
        kind = ActionKind.IMPLEMENT_BATCH
    elif domain == "families":
        kind = (
            ActionKind.DISCOVER
            if state == "BOUNDARY_REQUIRED"
            else ActionKind.IMPLEMENT_BATCH
        )
    else:
        kind = ActionKind.RECONCILE
    family = _family_for(facts, domain, record)
    return NextAction(
        kind,
        Id("action_target", f"{domain}:{identity}"),
        Id("action_scope", f"family:{family.value}"),
        family,
        Id("falsifier", f"unresolved:{domain}:{identity}"),
        _evidence_source(record.payload["evidence"]),
    )
def _gate_action(facts: Facts, record: _Record, kind: ActionKind) -> NextAction:
    identity = record.primary_key.value
    family = _family_for(facts, "gates", record)
    return NextAction(
        kind,
        Id("action_target", f"gate:{identity}"),
        Id("action_scope", f"family:{family.value}"),
        family,
        Id("falsifier", f"gate:{identity}:open"),
        _evidence_source(record.payload["evidence"]),
    )
def _default_close(facts: Facts) -> NextAction:
    family = Id("family_id", f"task:{facts.task.task.value}")
    return NextAction(
        ActionKind.CLOSE,
        Id("action_target", facts.task.task.value),
        Id("action_scope", "task"),
        family,
        Id("falsifier", "all-terminal"),
        _evidence_source(()),
    )

def _derive_action(facts: Facts) -> NextAction:
    unresolved = [
        (domain, record)
        for domain in ("checks", "claims", "findings", "families")
        for record in facts.stable[domain]
        if record.payload["state"] not in _TERMINAL_STATES[domain]
    ]
    active_gates = {
        record.primary_key.value: record
        for record in facts.stable["gates"]
        if record.payload["state"] not in _TERMINAL_STATES["gates"]
    }
    known = {identity for identity, _ in _GATE_POLICY}
    unknown = sorted(set(active_gates) - known)
    if unknown:
        return _gate_action(
            facts,
            active_gates[unknown[0]],
            ActionKind.RECONCILE,
        )
    gate_action = None
    for identity, kind in _GATE_POLICY:
        if identity in active_gates:
            record = active_gates[identity]
            gate_action = _gate_action(
                facts,
                record,
                (
                    kind
                    if record.payload["state"] == "OPEN"
                    or identity == "user_selection"
                    else ActionKind.RECONCILE
                ),
            )
            break
    if gate_action is not None:
        if gate_action.kind in {ActionKind.ASK_USER, ActionKind.RECONCILE}:
            return gate_action
        boundary = next(
            (
                (domain, record)
                for domain, record in unresolved
                if domain == "families"
                and record.payload["state"] == "BOUNDARY_REQUIRED"
            ),
            None,
        )
        if boundary is not None:
            return _unresolved_action(facts, *boundary)
        failed_check = next(
            ((domain, record) for domain, record in unresolved if domain == "checks"),
            None,
        )
        if failed_check is not None and gate_action.kind in {
            ActionKind.IMPLEMENT_BATCH,
            ActionKind.FOCUSED_REVIEW,
            ActionKind.EXACT_FINAL,
            ActionKind.FREEZE_CANDIDATE,
        }:
            return _unresolved_action(facts, *failed_check)
        if unresolved and gate_action.kind in {
            ActionKind.FOCUSED_REVIEW,
            ActionKind.EXACT_FINAL,
            ActionKind.FREEZE_CANDIDATE,
        }:
            return _unresolved_action(facts, *unresolved[0])
        return gate_action
    if unresolved:
        return _unresolved_action(facts, *unresolved[0])
    return _default_close(facts)

def reduce_facts(facts: Facts) -> ProgressReport:
    return _make_report(
        facts=facts,
        progress_key=make_progress_key(facts),
        next_action=_derive_action(facts),
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
    if report.next_action != _derive_action(report.facts):
        raise SemanticError("reducer report action mismatch")
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
    try:
        derived_kind = _validate_authority(
            authority.channel,
            authority.root_task,
            authority.source_task,
            authority.target_task,
            authority.executor_task,
            authority.destination,
            authority.lineage,
            authority.message_id,
            authority.turn_id,
            authority.content_digest,
            authority.target,
            authority.scope,
        )
    except (AttributeError, SemanticError):
        return EffectGate(
            EffectDecision.REFUSE,
            report.next_action.target,
            report.next_action.scope,
            "spoofed",
        )
    if authority.kind is not derived_kind:
        return EffectGate(
            EffectDecision.REFUSE,
            report.next_action.target,
            report.next_action.scope,
            "spoofed",
        )
    checks = (
        (authority.root_task != report.facts.task.root_task, "wrong_root"),
        (authority.destination != report.facts.task.destination, "wrong_destination"),
        (authority.lineage != report.facts.task.lineage, "wrong_lineage"),
        (
            authority.executor_task != report.facts.task.executor_task,
            "wrong_executor",
        ),
        (authority.target_task != report.facts.task.task, "wrong_target_task"),
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
        if authority.channel == "cross_task_user_delegation"
        else EffectDecision.ALLOW
    )
    reason = "cross_task" if decision is EffectDecision.ASK_USER else "direct"
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
