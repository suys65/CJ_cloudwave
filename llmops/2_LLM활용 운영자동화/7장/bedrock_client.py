"""
[보충 파일] 교안 02·03·04에서 import하지만 코드가 제공되지 않은 모듈.
Bedrock Runtime 클라이언트를 생성하는 헬퍼를 제공한다.
"""

import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def create_bedrock_runtime():
    """AWS 프로파일과 리전으로 Bedrock Runtime 클라이언트를 생성한다."""
    profile_name = os.getenv("AWS_PROFILE")
    region_name = os.getenv("AWS_REGION", "ap-northeast-2")

    session = boto3.Session(
        profile_name=profile_name or None,
        region_name=region_name,
    )

    return session.client("bedrock-runtime")
