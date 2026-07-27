import boto3
from botocore.exceptions import BotoCoreError, ClientError

PROFILE_NAME = "bedrock-training"
REGION_NAME = "ap-northeast-2"

try:
    session = boto3.Session(
        profile_name=PROFILE_NAME,
        region_name=REGION_NAME,
    )

    client = session.client("bedrock-runtime")

    print("Bedrock Runtime 클라이언트 생성 성공")
    print("Profile:", PROFILE_NAME)
    print("리전:", client.meta.region_name)

except (BotoCoreError, ClientError) as error:
    print("Bedrock Runtime 클라이언트 생성 실패")
    print(error)
