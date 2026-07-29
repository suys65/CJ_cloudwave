import json
import os
from typing import Any, Literal

import boto3
from dotenv import load_dotenv

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise ValueError(
            f"{name} 환경변수가 설정되지 않았습니다."
        )

    return value

def get_model_id() -> str:
    return require_env("BEDROCK_MODEL_ID")

def get_guardrail_config() -> tuple[str, str]:
    guardrail_id = require_env("GUARDRAIL_ID")
    guardrail_version = os.getenv(
        "GUARDRAIL_VERSION",
        "DRAFT",
    ).strip()

    if not guardrail_version:
        guardrail_version = "DRAFT"

    return guardrail_id, guardrail_version

def create_session() -> boto3.Session:
    region_name = os.getenv(
        "AWS_REGION",
        "ap-northeast-2",
    ).strip()
    profile_name = os.getenv(
        "AWS_PROFILE",
        "",
    ).strip()

    if profile_name:
        return boto3.Session(
            profile_name=profile_name,
            region_name=region_name,
        )

    return boto3.Session(
        region_name=region_name,
    )

def create_bedrock_runtime():
    return create_session().client(
        "bedrock-runtime"
    )

def create_sts_client():
    return create_session().client("sts")

def extract_text(response: dict[str, Any]) -> str:
    content_blocks = (
        response
        .get("output", {})
        .get("message", {})
        .get("content", [])
    )

    text = "".join(
        block.get("text", "")
        for block in content_blocks
        if "text" in block
    ).strip()

    if not text:
        raise ValueError(
            "Bedrock 응답에서 텍스트를 찾을 수 없습니다."
        )

    return text

def converse(
    *,
    client,
    model_id: str,
    messages: list[dict[str, Any]],
    system_prompt: str | None = None,
    use_guardrail: bool = False,
    trace: bool = True,
    temperature: float = 0.1,
    max_tokens: int = 1000,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }

    if system_prompt:
        request["system"] = [
            {"text": system_prompt}
        ]

    if use_guardrail:
        guardrail_id, guardrail_version = (
            get_guardrail_config()
        )

        request["guardrailConfig"] = {
            "guardrailIdentifier": guardrail_id,
            "guardrailVersion": guardrail_version,
            "trace": (
                "enabled"
                if trace
                else "disabled"
            ),
        }

    return client.converse(**request)

def apply_guardrail(
    *,
    client,
    text: str,
    source: Literal["INPUT", "OUTPUT"],
    output_scope: str = "FULL",
) -> dict[str, Any]:
    guardrail_id, guardrail_version = (
        get_guardrail_config()
    )

    return client.apply_guardrail(
        guardrailIdentifier=guardrail_id,
        guardrailVersion=guardrail_version,
        source=source,
        content=[
            {
                "text": {
                    "text": text,
                }
            }
        ],
        outputScope=output_scope,
    )

def print_guardrail_result(
    response: dict[str, Any],
) -> None:
    print("action:", response.get("action"))
    print(
        "actionReason:",
        response.get("actionReason"),
    )

    outputs = response.get("outputs", [])

    if outputs:
        print("outputs:")
        for item in outputs:
            print("-", item.get("text"))

    print("assessments:")
    print(
        json.dumps(
            response.get("assessments", []),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

def print_converse_result(
    response: dict[str, Any],
) -> None:
    print("stopReason:", response.get("stopReason"))
    print("output:", extract_text(response))

    if "trace" in response:
        print("\n[Guardrail Trace]")
        print(
            json.dumps(
                response["trace"],
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
