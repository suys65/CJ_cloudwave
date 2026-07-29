from backend.aws_session import ec2_client
from backend.config import NAME_PREFIX

def _tag_value(tags: list[dict] | None, key: str) -> str:
    for tag in tags or []:
        if tag.get("Key") == key:
            return tag.get("Value", "")
    return ""

def get_ec2_instances() -> list[dict]:
    response = ec2_client.describe_instances(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": [f"{NAME_PREFIX}-app*"],
            }
        ]
    )

    instances = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instances.append(
                {
                    "instance_id": instance["InstanceId"],
                    "name": _tag_value(instance.get("Tags"), "Name"),
                    "state": instance["State"]["Name"],
                    "instance_type": instance["InstanceType"],
                    "availability_zone": instance["Placement"]["AvailabilityZone"],
                    "private_ip": instance.get("PrivateIpAddress"),
                    "public_ip": instance.get("PublicIpAddress"),
                    "launch_time": instance["LaunchTime"].isoformat(),
                }
            )

    return instances

def get_ec2_status_checks() -> list[dict]:
    # describe_instance_status는 tag:Name 필터를 지원하지 않으므로
    # 먼저 프로젝트 인스턴스 ID를 구해 InstanceIds로 전달한다.
    instance_ids = [
        instance["instance_id"] for instance in get_ec2_instances()
    ]

    if not instance_ids:
        return []

    response = ec2_client.describe_instance_status(
        InstanceIds=instance_ids,
        IncludeAllInstances=True,
    )

    return [
        {
            "instance_id": item["InstanceId"],
            "instance_state": item["InstanceState"]["Name"],
            "system_status": item["SystemStatus"]["Status"],
            "instance_status": item["InstanceStatus"]["Status"],
        }
        for item in response.get("InstanceStatuses", [])
    ]
