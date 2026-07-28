import os
from typing import Any

import boto3
from dotenv import load_dotenv

load_dotenv()

def get_model_id() -> str:
    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()

    if not model_id:
        raise ValueError(
            "BEDROCK_MODEL_ID가 설정되지 않았습니다. "
            ".env 파일에 사용할 모델 ID를 입력하세요."
        )

    return model_id

def create_bedrock_runtime():
    region_name = os.getenv("AWS_REGION", "ap-northeast-2").strip()
    profile_name = os.getenv("AWS_PROFILE", "").strip()

    if profile_name:
        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name,
        )
        return session.client("bedrock-runtime")

    return boto3.client(
        "bedrock-runtime",
        region_name=region_name,
    )

def extract_text(response: dict[str, Any]) -> str:
    content_blocks = response["output"]["message"]["content"]

    text = "".join(
        block.get("text", "")
        for block in content_blocks
        if "text" in block
    ).strip()

    if not text:
        raise ValueError("Bedrock 응답에서 텍스트를 찾을 수 없습니다.")

    return text

def converse_text(
    *,
    client,
    model_id: str,
    user_prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    request: dict[str, Any] = {
        "modelId": model_id,
        "messages": [
            {
                "role": "user",
                "content": [{"text": user_prompt}],
            }
        ],
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }

    if system_prompt:
        request["system"] = [{"text": system_prompt}]

    response = client.converse(**request)

    metadata = {
        "stop_reason": response.get("stopReason"),
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
    }

    return extract_text(response), metadata

def print_usage(metadata: dict[str, Any]) -> None:
    usage = metadata.get("usage", {})
    metrics = metadata.get("metrics", {})

    print("\n[호출 정보]")
    print("입력 토큰:", usage.get("inputTokens", "확인 불가"))
    print("출력 토큰:", usage.get("outputTokens", "확인 불가"))
    print("전체 토큰:", usage.get("totalTokens", "확인 불가"))
    print("지연시간(ms):", metrics.get("latencyMs", "확인 불가"))
