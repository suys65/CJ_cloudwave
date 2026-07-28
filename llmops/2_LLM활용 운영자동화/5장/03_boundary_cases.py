from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    normalize_label,
)

TEST_CASES = [
    ("Connection refused to database host", "network"),
    ("Database authentication failed for user app", "authentication"),
    ("java.lang.OutOfMemoryError: Java heap space", "resource"),
    ("NullPointerException in OrderService", "application"),
    ("ERROR operation failed", "unknown"),
]

SYSTEM_PROMPT = """
당신은 운영 로그 분류기입니다.

허용 category:
- authentication
- network
- storage
- application
- resource
- unknown

분류 기준:
- 자격증명, 로그인, 권한 실패는 authentication
- 연결 거부, 타임아웃, DNS, 라우팅 문제는 network
- 디스크 공간, 파일시스템 문제는 storage
- 애플리케이션 예외와 코드 오류는 application
- CPU, 메모리, 스레드, 자원 부족은 resource
- 정보가 부족하면 unknown

출력은 category 이름 하나만 작성합니다.
"""

def classify(client, model_id: str, message: str) -> str:
    user_prompt = f"""
다음 로그를 분류합니다.

로그:
{message}
"""

    output, _ = invoke_text(
        client=client,
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
        max_tokens=30,
    )

    return normalize_label(output)

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    correct = 0

    print("=" * 76)
    print("경계 사례와 unknown 처리")
    print("=" * 76)
    print(f"{'입력':45}{'예상':15}{'결과':15}")
    print("-" * 76)

    for message, expected in TEST_CASES:
        predicted = classify(client, model_id, message)
        matched = predicted == expected

        if matched:
            correct += 1

        print(f"{message[:43]:45}{expected:15}{predicted:15}")

    accuracy = correct / len(TEST_CASES)

    print("-" * 76)
    print(f"정확도:{correct}/{len(TEST_CASES)} ={accuracy:.1%}")

    if correct == len(TEST_CASES):
        print("[검증 성공] 모든 경계 사례가 기대 결과와 일치했습니다.")
    else:
        print("[검토 필요] 오분류 사례를 Few-shot 예시에 추가해 봅니다.")

if __name__ == "__main__":
    main()
