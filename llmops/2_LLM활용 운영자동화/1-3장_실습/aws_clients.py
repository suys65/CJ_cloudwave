import boto3

from config import AWS_PROFILE, AWS_REGION


def create_session() -> boto3.Session:
    if AWS_PROFILE:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )

    return boto3.Session(
        region_name=AWS_REGION,
    )


session = create_session()

sts_client = session.client("sts")
ec2_client = session.client("ec2")
bedrock_runtime = session.client("bedrock-runtime")
