"""Test-only authenticated, cross-root one-shot external boundary."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import hmac
from typing import Any

from evaluation.canonical import canonical_json, canonical_sha256


class FakeBoundaryError(ValueError):
    pass


class FakeExternalBoundary:
    authenticator_id = "test-only-hmac-terminal-v3"

    def __init__(self, *, recovery_cap: int = 1, secret: bytes = b"offline-test-key"):
        self.recovery_cap = recovery_cap
        self._secret = secret
        self._authorities: dict[str, dict[str, Any]] = {}
        self._effects: dict[str, list[tuple[str, str]]] = {}

    def _signature(self, domain: str, body: bytes) -> str:
        return hmac.new(self._secret, domain.encode() + b":" + body, hashlib.sha256).hexdigest()

    def issue_authority(self, request: dict[str, Any], *, kind: str) -> dict[str, Any]:
        purpose = {"evaluation": "happycodex-evaluation-v3", "release": "happycodex-release-v3"}
        if kind not in purpose or request.get("purpose") != purpose[kind]:
            raise FakeBoundaryError("authority kind and request purpose differ")
        request_sha = request.get("request_sha256")
        if request_sha != canonical_sha256({key: value for key, value in request.items() if key != "request_sha256"}):
            raise FakeBoundaryError("authority request identity differs")
        body = {
            "authority_identity": f"test-{kind}-authority",
            "request_sha256": request_sha,
            "signature": self._signature(f"authority-{kind}", request_sha.encode()),
        }
        authority = {**body, "authority_sha256": canonical_sha256(body)}
        self._authorities[request_sha] = deepcopy(authority)
        return authority

    def validate(self, request_sha256: str, authority: dict[str, Any]) -> bool:
        return authority == self._authorities.get(request_sha256)

    def verify(self, statement: bytes, signature: str) -> bool:
        return hmac.compare_digest(signature, self._signature("terminal", statement))

    def sign_terminal(self, statement: dict[str, Any], *, execution_root: str) -> dict[str, Any]:
        kind = statement.get("kind")
        if kind not in {"provider_terminal", "release_terminal"}:
            raise FakeBoundaryError("terminal kind differs")
        effect_key = "effect_subject_sha256" if kind == "provider_terminal" else "release_effect_subject_sha256"
        outcome_key = "effect_outcome" if kind == "provider_terminal" else "outcome"
        effect, attempt, outcome = statement[effect_key], statement["attempt"], statement[outcome_key]
        history = self._effects.setdefault(effect, [])
        if attempt != len(history) or attempt > self.recovery_cap:
            raise FakeBoundaryError("attempt is not contiguous or exceeds recovery cap")
        if history and history[-1][0] != "not_landed":
            raise FakeBoundaryError("landed or unknown effect is one-shot across roots")
        observation = statement["observation"]
        if outcome == "not_landed":
            reached = observation["provider_reached"] if kind == "provider_terminal" else observation["effect_reached"]
            complete = observation["response_complete"] if kind == "provider_terminal" else observation["readback_complete"]
            usage = () if kind == "release_terminal" else (
                observation["model_calls"], observation["input_tokens"], observation["output_tokens"],
            )
            if reached or complete or any(usage):
                raise FakeBoundaryError("recovery is not a proven pre-effect zero-use terminal")
        history.append((outcome, execution_root))
        payload = canonical_json(statement)
        return {
            "authenticator_id": self.authenticator_id,
            "evidence_sha256": canonical_sha256(statement),
            "signature": self._signature("terminal", payload),
        }

    def attempts(self, effect_subject_sha256: str) -> tuple[tuple[str, str], ...]:
        return tuple(self._effects.get(effect_subject_sha256, ()))


__all__ = ("FakeBoundaryError", "FakeExternalBoundary")
