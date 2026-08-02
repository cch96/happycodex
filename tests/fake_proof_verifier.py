#!/usr/bin/python3
from __future__ import annotations

import hashlib
import json
import sys


def canonical_sha256(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    value = json.load(sys.stdin)
    proof, challenge = value["proof"], value["challenge"]
    valid = (
        set(proof) == {"trust_domain", "challenge_sha256"}
        and proof["trust_domain"] == challenge["trust_domain"]
        and proof["challenge_sha256"] == canonical_sha256(challenge)
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
