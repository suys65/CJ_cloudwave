from backend.aws_session import elbv2_client
from backend.config import NAME_PREFIX

def get_load_balancer() -> dict:
    response = elbv2_client.describe_load_balancers(
        Names=[f"{NAME_PREFIX}-alb"]
    )

    items = response.get("LoadBalancers", [])
    if not items:
        return {"exists": False}

    alb = items[0]
    return {
        "exists": True,
        "arn": alb["LoadBalancerArn"],
        "dns_name": alb["DNSName"],
        "state": alb["State"]["Code"],
        "scheme": alb["Scheme"],
        "type": alb["Type"],
        "availability_zones": [
            az["ZoneName"] for az in alb.get("AvailabilityZones", [])
        ],
    }

def get_target_groups(load_balancer_arn: str) -> list[dict]:
    response = elbv2_client.describe_target_groups(
        LoadBalancerArn=load_balancer_arn
    )

    return [
        {
            "target_group_arn": group["TargetGroupArn"],
            "target_group_name": group["TargetGroupName"],
            "port": group["Port"],
            "protocol": group["Protocol"],
            "health_check_path": group.get("HealthCheckPath"),
        }
        for group in response.get("TargetGroups", [])
    ]

def get_target_health(target_group_arn: str) -> list[dict]:
    response = elbv2_client.describe_target_health(
        TargetGroupArn=target_group_arn
    )

    result = []

    for item in response.get("TargetHealthDescriptions", []):
        target = item["Target"]
        health = item["TargetHealth"]

        result.append(
            {
                "instance_id": target["Id"],
                "port": target.get("Port"),
                "state": health["State"],
                "reason": health.get("Reason"),
                "description": health.get("Description"),
            }
        )

    return result
