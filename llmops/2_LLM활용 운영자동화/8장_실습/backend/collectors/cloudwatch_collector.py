from datetime import datetime, timedelta, timezone

from backend.aws_session import cloudwatch_client
from backend.config import ALARM_PREFIX

def get_alarm_status() -> list[dict]:
    response = cloudwatch_client.describe_alarms(
        AlarmNamePrefix=ALARM_PREFIX
    )

    return [
        {
            "alarm_name": alarm["AlarmName"],
            "state": alarm["StateValue"],
            "reason": alarm.get("StateReason"),
            "metric_name": alarm.get("MetricName"),
            "namespace": alarm.get("Namespace"),
            "threshold": alarm.get("Threshold"),
            "comparison_operator": alarm.get("ComparisonOperator"),
            "state_updated_timestamp": alarm["StateUpdatedTimestamp"].isoformat(),
        }
        for alarm in response.get("MetricAlarms", [])
    ]

def get_ec2_cpu(instance_id: str, minutes: int = 15) -> list[dict]:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    response = cloudwatch_client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=["Average", "Maximum"],
    )

    datapoints = sorted(
        response.get("Datapoints", []),
        key=lambda item: item["Timestamp"],
    )

    return [
        {
            "timestamp": point["Timestamp"].isoformat(),
            "average": round(point.get("Average", 0), 2),
            "maximum": round(point.get("Maximum", 0), 2),
            "unit": point.get("Unit"),
        }
        for point in datapoints
    ]
