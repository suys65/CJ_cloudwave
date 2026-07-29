import json

from backend.bedrock_client import converse
from backend.schemas import IncidentAnalysis
from backend.prompts import INCIDENT_SYSTEM_PROMPT
from backend.router import _parse_json_object


def analyze_incident(
    question: str,
    operational_data: dict,
) -> IncidentAnalysis:
    user_prompt = json.dumps(
        {
            "question": question,
            "operational_data": operational_data,
        },
        ensure_ascii=False,
        default=str,
    )

    raw = converse(
        system_prompt=INCIDENT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
        max_tokens=1800,
    )

    data = _parse_json_object(raw)
    return IncidentAnalysis.model_validate(data)


def calculate_basic_health(
    targets: list[dict],
    alarms: list[dict],
) -> dict:
    """명확한 계산은 Python이 처리하고, LLM은 의미 해석을 담당한다."""
    unhealthy_targets = [
        target for target in targets
        if target.get("state") != "healthy"
    ]

    alarm_items = [
        alarm for alarm in alarms
        if alarm.get("state") == "ALARM"
    ]

    return {
        "healthy_target_count": len(targets) - len(unhealthy_targets),
        "unhealthy_target_count": len(unhealthy_targets),
        "alarm_count": len(alarm_items),
        "service_degraded": bool(unhealthy_targets or alarm_items),
    }


READ_ONLY_PREFIXES = {
    "aws ec2 describe-",
    "aws autoscaling describe-",
    "aws elbv2 describe-",
    "aws cloudwatch describe-",
    "aws cloudwatch get-",
    "aws logs describe-",
    "aws logs get-",
    "aws logs filter-",
}


def is_read_only_command(command: str) -> bool:
    normalized = " ".join(command.strip().split()).lower()
    return any(
        normalized.startswith(prefix)
        for prefix in READ_ONLY_PREFIXES
    )
