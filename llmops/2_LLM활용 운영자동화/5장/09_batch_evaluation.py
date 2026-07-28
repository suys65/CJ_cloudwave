from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    normalize_label,
)

TEST_DATA = [
    ("Failed password for invalid user admin", "authentication"),
    ("Connection timed out while connecting to database", "network"),
    ("No space left on device", "storage"),
    ("NullPointerException in PaymentService", "application"),
    ("CPU throttling detected", "resource"),
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
- 로그인, 자격증명, 권한 실패는 authentication
- 연결, 타임아웃, DNS, 라우팅 문제는 network
- 디스크 공간과 파일시스템 문제는 storage
- 애플리케이션 예외와 코드 오류는 application
- CPU, 메모리, 스레드, 자원 부족은 resource
- 정보가 부족하면 unknown

출력은 category 이름 하나만 작성합니다.
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    results: list[tuple[str, str, str, bool]] = []

    for message, expected in TEST_DATA:
        output, _ = invoke_text(
            client=client,
            model_id=model_id,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"로그:\n{message}",
            temperature=0.1,
            max_tokens=30,
        )

        predicted = normalize_label(output)
        results.append(
            (message, expected, predicted, expected == predicted)
        )

    correct = sum(1 for *_, matched in results if matched)
    accuracy = correct / len(results)

    print("=" * 90)
    print("테스트 데이터 기반 분류 평가")
    print("=" * 90)
    print(f"{'입력':48}{'정답':16}{'예측':16} 결과")
    print("-" * 90)

    for message, expected, predicted, matched in results:
        status = "PASS" if matched else "FAIL"
        print(
            f"{message[:46]:48} "
            f"{expected:16} "
            f"{predicted:16} "
            f"{status}"
        )

    print("-" * 90)
    print(f"정확도:{correct}/{len(results)} ={accuracy:.1%}")

    failed = [item for item in results if not item[3]]

    if failed:
        print("\n[오분류 분석 대상]")
        for message, expected, predicted, _ in failed:
            print(
                f"- 입력={message!r}, 정답={expected}, 예측={predicted}"
            )
    else:
        print("\n[평가 결과] 모든 테스트 데이터가 정답과 일치했습니다.")

if __name__ == "__main__":
    main()
