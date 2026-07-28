from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    normalize_label,
)

ALLOWED_CATEGORIES = {
    "authentication",
    "network",
    "storage",
    "application",
    "resource",
    "unknown",
}

NEW_LOG = "java.lang.OutOfMemoryError: Java heap space"

def classify(client, model_id: str, prompt: str) -> str:
    output, _ = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=30,
    )
    return normalize_label(output)

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()
# 예시 7 입력: OutOfMemoryError 출력: resource 를 넣은 경우와 뺀 경우를 비교

    zero_shot_prompt = f"""
다음 로그를 authentication, network, storage,
application, resource, unknown 중 하나로 분류합니다.

로그:
{NEW_LOG}

출력은 category 이름 하나만 작성합니다.
"""

    few_shot_prompt = f"""
다음 기준과 예시를 참고하여 로그를 분류합니다.

허용 category:
- authentication
- network
- storage
- application
- resource
- unknown

예시 1
입력: Failed password for invalid user root
출력: authentication

예시 2
입력: Connection refused to 10.0.2.20:5432
출력: network

예시 3
입력: No space left on device
출력: storage

예시 4
입력: NullPointerException in PaymentService
출력: application

예시 5
입력: CPU throttling detected
출력: resource

예시 6
입력: ERROR operation failed
출력: unknown

예시 7
입력: OutOfMemoryError
출력: resource

새 입력:
{NEW_LOG}

출력은 category 이름 하나만 작성합니다.
"""

    zero_result = classify(client, model_id, zero_shot_prompt)
    few_result = classify(client, model_id, few_shot_prompt)

    print("=" * 60)
    print("Zero-shot과 Few-shot 비교")
    print("=" * 60)
    print("입력:", NEW_LOG)
    print("Zero-shot 결과:", zero_result)
    print("Few-shot 결과:", few_result)
    print("기대 결과: resource")

    for name, result in (
        ("Zero-shot", zero_result),
        ("Few-shot", few_result),
    ):
        if result in ALLOWED_CATEGORIES:
            print(f"[{name}] 형식 검증 성공")
        else:
            print(f"[{name}] 형식 검증 실패")

    if few_result == "resource":
        print("[비교 결과] Few-shot이 기대 분류 기준을 적용했습니다.")
    else:
        print("[비교 결과] 예시 또는 분류 기준을 다시 검토해야 합니다.")

if __name__ == "__main__":
    main()
