from typing import Any

from aws_clients import bedrock_runtime
from config import BEDROCK_MODEL_ID


def strip_json_fence(text: str) -> str:
    """모델이 JSON을 ```json ... ``` 코드 블록으로 감싸는 경우 순수 JSON만 추출한다."""
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # 첫 줄(```json 또는 ```)과 마지막 줄(```)을 제거
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return cleaned


def extract_text(response: dict[str, Any]) -> str:
    content_blocks = response["output"]["message"]["content"]

    texts = [
        block["text"]
        for block in content_blocks
        if "text" in block
    ]

    return "\n".join(texts)


def converse(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 800,
) -> dict[str, Any]:
    return bedrock_runtime.converse(
        modelId=BEDROCK_MODEL_ID,
        system=[
            {
                "text": system_prompt
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": user_prompt
                    }
                ],
            }
        ],
        inferenceConfig={
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    )
