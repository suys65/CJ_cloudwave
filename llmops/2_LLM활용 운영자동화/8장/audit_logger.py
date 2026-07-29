import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def hash_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

def save_audit_event(
    *,
    event: dict[str, Any],
) -> Path:
    output_dir = Path(
        os.getenv(
            "AUDIT_LOG_DIR",
            "audit_logs",
        )
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    output_path = (
        output_dir
        / f"security_event_{timestamp}.json"
    )

    event_with_time = {
        "recorded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        **event,
    }

    output_path.write_text(
        json.dumps(
            event_with_time,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    return output_path
