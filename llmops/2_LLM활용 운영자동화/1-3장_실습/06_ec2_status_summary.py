import json

from botocore.exceptions import BotoCoreError, ClientError

from aws_clients import ec2_client
from bedrock_utils import converse, extract_text
from config import STUDENT_INITIAL


def get_name_tag(tags: list[dict] | None) -> str:
    for tag in tags or []:
        if tag.get("Key") == "Name":
            return tag.get("Value", "")

    return ""


def get_ec2_instances() -> list[dict]:
    response = ec2_client.describe_instances(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": [f"{STUDENT_INITIAL}-*"],
            }
        ]
    )

    instances = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instances.append(
                {
                    "instance_id": instance["InstanceId"],
                    "name": get_name_tag(instance.get("Tags")),
                    "state": instance["State"]["Name"],
                    "instance_type": instance["InstanceType"],
                    "availability_zone": (
                        instance["Placement"]["AvailabilityZone"]
                    ),
                    "private_ip": instance.get("PrivateIpAddress"),
                    "launch_time": instance["LaunchTime"].isoformat(),
                }
            )

    return instances


system_prompt = """
당신은 AWS 운영 상태를 설명하는 운영 엔지니어이다.

규칙:

- 제공된 EC2 조회 결과만 사용한다.
- 입력에 없는 상태를 생성하지 않는다.
- 인스턴스가 없으면 없다고 작성한다.
- 장애 원인을 추측하지 않는다.
- 변경 명령을 제안하지 않는다.
- 운영자가 빠르게 이해할 수 있도록 간결하게 작성한다.
"""

try:
    instances = get_ec2_instances()

    user_prompt = f"""
다음 EC2 조회 결과를 운영자에게 요약한다.

<ec2_instances>
{json.dumps(instances, ensure_ascii=False, indent=2)}
</ec2_instances>

다음 항목을 작성한다.

1. 전체 인스턴스 수
2. 상태별 인스턴스 수
3. 인스턴스별 이름, 상태, 가용 영역
4. 확인이 필요한 항목
"""

    response = converse(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
        max_tokens=900,
    )

    print("=" * 80)
    print("Boto3 조회 결과")
    print("=" * 80)
    print(json.dumps(instances, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("LLM 운영 요약")
    print("=" * 80)
    print(extract_text(response))

except ClientError as error:
    print("AWS API 오류")
    print("코드:", error.response["Error"]["Code"])
    print("메시지:", error.response["Error"]["Message"])

except BotoCoreError as error:
    print("AWS SDK 오류")
    print(error)
