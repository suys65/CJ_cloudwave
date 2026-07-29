import json

from backend.bedrock_client import converse
from backend.schemas import RouteDecision
from backend.prompts import ROUTER_SYSTEM_PROMPT

from backend.collectors.ec2_collector import (
    get_ec2_instances,
    get_ec2_status_checks,
)
from backend.collectors.asg_collector import (
    get_asg_status,
    get_scaling_activities,
)
from backend.collectors.alb_collector import (
    get_load_balancer,
    get_target_groups,
    get_target_health,
)
from backend.collectors.cloudwatch_collector import (
    get_alarm_status,
    get_ec2_cpu,
)
from backend.collectors.logs_collector import get_recent_logs


def _parse_json_object(raw: str) -> dict:
    """모델 응답에서 JSON 객체를 안전하게 파싱한다(코드블록 대비)."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise
        return json.loads(cleaned[start : end + 1])


def classify_question(question: str) -> RouteDecision:
    raw = converse(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_prompt=question,
        temperature=0,
        max_tokens=400,
    )

    data = _parse_json_object(raw)
    return RouteDecision.model_validate(data)


def _safe(fn, *args, **kwargs):
    """수집기 하나가 실패해도 나머지 결과를 유지한다(§18 개선 과제)."""
    try:
        return fn(*args, **kwargs)
    except Exception as error:  # noqa: BLE001
        return {"error": str(error)}


def execute_route(category: str, time_range_minutes: int) -> dict:
    if category == "ec2_status":
        return {
            "instances": _safe(get_ec2_instances),
            "status_checks": _safe(get_ec2_status_checks),
        }

    if category == "asg_status":
        return {
            "asg": _safe(get_asg_status),
            "activities": _safe(get_scaling_activities, 10),
        }

    if category == "log_analysis":
        return {
            "logs": _safe(
                get_recent_logs,
                minutes=time_range_minutes,
                filter_pattern='"ERROR"',
                limit=100,
            )
        }

    if category == "alb_status":
        load_balancer = _safe(get_load_balancer)
        target_groups = []
        target_health = []

        if isinstance(load_balancer, dict) and load_balancer.get("exists"):
            target_groups = _safe(get_target_groups, load_balancer["arn"])
            if isinstance(target_groups, list) and target_groups:
                target_health = _safe(
                    get_target_health,
                    target_groups[0]["target_group_arn"],
                )

        return {
            "load_balancer": load_balancer,
            "target_groups": target_groups,
            "target_health": target_health,
        }

    if category == "metric_analysis":
        instances = _safe(get_ec2_instances)
        instance_list = instances if isinstance(instances, list) else []

        return {
            "instances": instance_list,
            "cpu_metrics": {
                instance["instance_id"]: _safe(
                    get_ec2_cpu,
                    instance["instance_id"],
                    minutes=time_range_minutes,
                )
                for instance in instance_list
            },
            "asg": _safe(get_asg_status),
            "alarms": _safe(get_alarm_status),
        }

    if category in {"overall_status", "incident_analysis"}:
        return {
            "instances": _safe(get_ec2_instances),
            "status_checks": _safe(get_ec2_status_checks),
            "asg": _safe(get_asg_status),
            "activities": _safe(get_scaling_activities, 5),
            "alarms": _safe(get_alarm_status),
            "logs": _safe(
                get_recent_logs,
                minutes=time_range_minutes,
                filter_pattern='"ERROR"',
                limit=50,
            ),
        }

    return {"message": "지원하지 않는 질문 유형입니다."}
