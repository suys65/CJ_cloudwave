from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    normalize_label,
    print_metadata,
)

ALLOWED_CATEGORIES = {
    "authentication",
    "network",
    "storage",
    "application",
    "resource",
    "unknown",
}

LOG_MESSAGE = "java.lang.OutOfMemoryError: Java heap space"

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    prompt = f"""
다음 로그를 아래 category 중 하나로 분류합니다.

허용 category:
- authentication
- network
- storage
- application
- resource
- unknown

로그:
{LOG_MESSAGE}

출력은 category 이름 하나만 작성합니다.
"""

    output, metadata = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=30,
    )

    category = normalize_label(output)

    print("=" * 60)
    print("Zero-shot 로그 분류")
    print("=" * 60)
    print("입력:", LOG_MESSAGE)
    print("모델 원본 응답:", output)
    print("정리된 category:", category)

    if category in ALLOWED_CATEGORIES:
        print("[검증 성공] 허용된 category입니다.")
    else:
        print("[검증 실패] 허용되지 않은 출력입니다.")

    print_metadata(metadata)

if __name__ == "__main__":
    main()
