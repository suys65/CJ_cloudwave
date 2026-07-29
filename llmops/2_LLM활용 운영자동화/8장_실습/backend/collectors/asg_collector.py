from backend.aws_session import autoscaling_client
from backend.config import ASG_NAME

def get_asg_status() -> dict:
    response = autoscaling_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ASG_NAME]
    )

    groups = response.get("AutoScalingGroups", [])

    if not groups:
        return {"exists": False, "name": ASG_NAME}

    group = groups[0]

    return {
        "exists": True,
        "name": group["AutoScalingGroupName"],
        "min_size": group["MinSize"],
        "desired_capacity": group["DesiredCapacity"],
        "max_size": group["MaxSize"],
        "health_check_type": group["HealthCheckType"],
        "instances": [
            {
                "instance_id": item["InstanceId"],
                "availability_zone": item["AvailabilityZone"],
                "lifecycle_state": item["LifecycleState"],
                "health_status": item["HealthStatus"],
            }
            for item in group.get("Instances", [])
        ],
    }

def get_scaling_activities(max_records: int = 10) -> list[dict]:
    response = autoscaling_client.describe_scaling_activities(
        AutoScalingGroupName=ASG_NAME,
        MaxRecords=max_records,
    )

    return [
        {
            "activity_id": item["ActivityId"],
            "description": item.get("Description"),
            "cause": item.get("Cause"),
            "status_code": item.get("StatusCode"),
            "start_time": item["StartTime"].isoformat(),
            "end_time": item["EndTime"].isoformat() if item.get("EndTime") else None,
        }
        for item in response.get("Activities", [])
    ]
