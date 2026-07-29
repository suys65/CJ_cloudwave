from datetime import datetime
from pathlib import Path
import json

from backend.bedrock_client import converse
from backend.prompts import REPORT_SYSTEM_PROMPT

REPORT_DIR = Path("reports")


def generate_incident_report(incident_data: dict) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    prompt = json.dumps(
        incident_data,
        ensure_ascii=False,
        default=str,
    )

    report = converse(
        system_prompt=REPORT_SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=2500,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = REPORT_DIR / f"incident_report_{timestamp}.md"
    output_path.write_text(report, encoding="utf-8")

    return output_path
