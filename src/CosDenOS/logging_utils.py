from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


def log_event(
    event: str,
    level: str = "INFO",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Minimal structured logger.
    Writes a JSON line to stdout so that containers / gateways
    can parse logs easily.
    """
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": level.upper(),
        "event": event,
    }
    if extra:
        record.update(extra)

    sys.stdout.write(json.dumps(record) + "\n")
    sys.stdout.flush()
