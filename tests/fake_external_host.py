from __future__ import annotations

import json
import sys


def main() -> int:
    request = json.load(sys.stdin)
    for event in (
        {"type": "thread.started", "thread_id": "fake-thread"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"id": "fake-message", "type": "agent_message", "text": json.dumps(request["report"], sort_keys=True)}},
        {"type": "turn.completed", "usage": request["usage"]},
    ):
        print(json.dumps(event, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
