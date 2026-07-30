from __future__ import annotations

from .codec import semantic_digest
from .model import (
    CanonicalReport,
    ControlBlocker,
    Finding,
    MachineFacts,
    ModelObservation,
    NextAction,
    Reduction,
    SemanticError,
)


_GATE_ACTION = {
    "contract_freeze": "FREEZE",
    "red_oracle": "CHECK",
    "product_edit": "IMPLEMENT",
    "checks": "CHECK",
    "candidate_freeze": "FREEZE",
    "exact_final_review": "EXACT_FINAL",
    "release": "RELEASE",
}


def _unresolved(
    facts: MachineFacts,
    finding: Finding,
) -> bool:
    if finding.blocker_class is not None:
        return True
    if finding.status in {"candidate_new", "unknown"}:
        return True
    return (
        finding.status == "baseline_unchanged"
        and finding.finding_id not in facts.accepted_baseline_failures
    )


def _blockers(
    facts: MachineFacts,
    findings: tuple[Finding, ...],
) -> tuple[ControlBlocker, ...]:
    blockers: list[ControlBlocker] = []
    for finding in findings:
        unresolved = _unresolved(facts, finding)
        if unresolved and finding.blocker_class is None:
            raise SemanticError("unresolved finding requires an embedded blocker")
        if finding.blocker_class is not None:
            blockers.append(
                ControlBlocker(
                    finding_id=finding.finding_id,
                    blocker_class=finding.blocker_class,
                    anchors=finding.anchors,
                )
            )
    return tuple(
        sorted(
            blockers,
            key=lambda item: (
                item.finding_id,
                item.blocker_class,
                item.anchors,
            ),
        )
    )


def _next_action(
    facts: MachineFacts,
    observation: ModelObservation,
    blockers: tuple[ControlBlocker, ...],
) -> NextAction:
    gates = observation.open_gates
    selected = gates[0] if gates else None
    blocked_finding = blockers[0].finding_id if blockers else None
    if selected == "user_selection":
        kind, target = "ASK_USER", "gate:user_selection"
    elif selected == "reconciliation":
        kind, target = "RECONCILE", "gate:reconciliation"
    elif (
        observation.execplan_condition in {"missing", "needs_amendment"}
        and selected
        in {"product_edit", "candidate_freeze", "exact_final_review", "release"}
    ):
        kind, target = "RECONCILE", f"execplan:{observation.execplan_condition}"
    elif blockers and selected in {
        None,
        "candidate_freeze",
        "exact_final_review",
        "release",
    }:
        kind, target = "IMPLEMENT", f"finding:{blocked_finding}"
    elif selected is None:
        if blockers:
            kind, target = "IMPLEMENT", f"finding:{blocked_finding}"
        else:
            kind, target = "CLOSE", "goal:complete"
    else:
        kind, target = _GATE_ACTION[selected], f"gate:{selected}"
    structural = {
        "kind": kind,
        "target": target,
        "gates": gates,
        "blocker": (
            None if not blockers else blockers[0].semantic_value()
        ),
    }
    falsifier = semantic_digest("falsifier", structural)
    evidence_source = semantic_digest(
        "evidence-source",
        {
            "repository": facts.task_binding["repository_digest"],
            "outcome": facts.task_binding["outcome_digest"],
            "infrastructure": facts.infrastructure_generation,
            "anchors": (
                () if not blockers else blockers[0].anchors
            ),
        },
    )
    return NextAction(
        kind=kind,
        target=target,
        scope=facts.scope,
        falsifier_id=falsifier,
        evidence_source_id=evidence_source,
    )


def reduce(
    facts: MachineFacts,
    observation: ModelObservation,
) -> Reduction:
    if type(facts) is not MachineFacts:
        raise SemanticError("reducer requires exact MachineFacts")
    if type(observation) is not ModelObservation:
        raise SemanticError("reducer requires exact ModelObservation")
    blockers = _blockers(facts, observation.findings)
    return Reduction(
        findings=observation.findings,
        blockers=blockers,
        next_action=_next_action(facts, observation, blockers),
    )


def _state_value(
    facts: MachineFacts,
    observation: ModelObservation,
    reduced: Reduction,
) -> dict[str, object]:
    return {
        "facts": facts.semantic_value(),
        "observation": {
            "qualifies": observation.qualifies,
            "execplan_condition": observation.execplan_condition,
            "findings": tuple(
                item.semantic_value() for item in reduced.findings
            ),
            "open_gates": observation.open_gates,
            "recovery": observation.recovery,
        },
        "control_blockers": tuple(
            item.semantic_value() for item in reduced.blockers
        ),
        "required_decision_inputs": {
            "destination": facts.scope,
            "accepted_baseline_failures": facts.accepted_baseline_failures,
        },
    }


def build_report(
    facts: MachineFacts,
    observation: ModelObservation,
) -> CanonicalReport:
    reduced = reduce(facts, observation)
    state_key = semantic_digest(
        "state-key",
        _state_value(facts, observation, reduced),
    )
    action_key = semantic_digest(
        "action-key",
        {
            "state_key": state_key,
            "next_action": reduced.next_action,
        },
    )
    return CanonicalReport(
        facts=facts,
        observation=observation,
        findings=reduced.findings,
        blockers=reduced.blockers,
        next_action=reduced.next_action,
        state_key=state_key,
        action_key=action_key,
    )


def validate_report(report: CanonicalReport) -> None:
    if type(report) is not CanonicalReport:
        raise SemanticError("exact CanonicalReport required")
    if report != build_report(report.facts, report.observation):
        raise SemanticError("CanonicalReport differs from pure reduction")


__all__ = ("build_report", "reduce", "validate_report")
