import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import AWS_PROFILE, AWS_REGION

def create_session() -> boto3.Session:
    try:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )
    except (BotoCoreError, ClientError) as error:
        raise RuntimeError(f"AWS 세션 생성 실패:{error}") from error

session = create_session()

ec2_client = session.client("ec2")
autoscaling_client = session.client("autoscaling")
elbv2_client = session.client("elbv2")
cloudwatch_client = session.client("cloudwatch")
logs_client = session.client("logs")
bedrock_client = session.client("bedrock-runtime")
ssm_client = session.client("ssm")

def get_caller_identity() -> dict:
    sts = session.client("sts")
    return sts.get_caller_identity()

if __name__ == "__main__":
    import json

    print(json.dumps(get_caller_identity(), ensure_ascii=False, indent=2, default=str))
