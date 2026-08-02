from __future__ import annotations

import json
import sys


def main() -> int:
    request = json.load(sys.stdin)
    for event in (
        {"type": "started", "at": request["started_at"]},
        {"type": "report", "report": request["report"]},
        {"type": "usage", **request["usage"]},
        {"type": "terminal", **request["terminal"], "at": request["frozen_at"]},
    ):
        print(json.dumps(event, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
