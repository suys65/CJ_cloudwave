import time
from typing import Any
import os

import boto3
from dotenv import load_dotenv

from usage_utils import extract_usage

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-northeast-2",
)
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

session = boto3.Session(
    profile_name=AWS_PROFILE or None,
    region_name=AWS_REGION,
)

client = session.client(
    "bedrock-runtime"
)

def converse_with_usage(
    *,
    client: Any,
    model_id: str,
    messages: list[dict[str, Any]],
    inference_config: dict[str, Any],
    system: list[dict[str, str]] | None = None,
) -> tuple[dict[str, Any], dict[str, int | float]]:
    """
    Bedrock Converse API를 호출하고 응답과 사용량 정보를 함께 반환한다.
    """
    request: dict[str, Any] = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": inference_config,
    }

    if system:
        request["system"] = system

    start_time = time.perf_counter()

    response = client.converse(**request)

    elapsed_time = time.perf_counter() - start_time

    usage = extract_usage(
        response=response,
        elapsed_time=elapsed_time,
    )

    return response, usage
