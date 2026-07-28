import json
import os
from typing import Any

import boto3
from dotenv import load_dotenv

load_dotenv()

def get_model_id() -> str:
    """환경변수에서 Bedrock 모델 ID를 가져온다."""
    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()

    if not model_id:
        raise ValueError(
            "BEDROCK_MODEL_ID가 설정되지 않았습니다. "
            ".env 파일에 사용할 모델 ID를 입력하세요."
        )

    return model_id

def create_bedrock_runtime():
    """AWS 프로파일 또는 기본 자격증명으로 Bedrock Runtime 클라이언트를 생성한다."""
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
    """Converse 응답의 text content block을 하나의 문자열로 결합한다."""
    content_blocks = response["output"]["message"]["content"]

    text = "".join(
        block.get("text", "")
        for block in content_blocks
        if "text" in block
    ).strip()

    if not text:
        raise ValueError("Bedrock 응답에서 텍스트를 찾을 수 없습니다.")

    return text

def invoke_text(
    *,
    client,
    model_id: str,
    user_prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 1000,
) -> tuple[str, dict[str, Any]]:
    """Converse API를 호출하고 응답 텍스트와 사용량 정보를 반환한다."""
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

def parse_json_object(text: str) -> dict[str, Any]:
    """모델 응답에서 최상위 JSON 객체를 추출하여 파싱한다."""
    cleaned = text.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "응답에서 JSON 객체를 찾을 수 없습니다.\n"
                f"원본 응답:\n{cleaned}"
            )

        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("최상위 JSON 값은 객체여야 합니다.")

    return parsed

def normalize_label(text: str) -> str:
    """단일 라벨 응답의 공백, 코드 표시, 마침표를 정리한다."""
    return (
        text.strip()
        .replace("```text", "")
        .replace("```", "")
        .strip()
        .strip("`\"' .")
        .lower()
    )

def print_metadata(metadata: dict[str, Any]) -> None:
    """모델 호출의 토큰 사용량과 지연시간을 출력한다."""
    usage = metadata.get("usage", {})
    metrics = metadata.get("metrics", {})

    print("\n[호출 정보]")
    print("입력 토큰:", usage.get("inputTokens", "확인 불가"))
    print("출력 토큰:", usage.get("outputTokens", "확인 불가"))
    print("전체 토큰:", usage.get("totalTokens", "확인 불가"))
    print("지연시간(ms):", metrics.get("latencyMs", "확인 불가"))
