from security_common import (
    apply_guardrail,
    create_bedrock_runtime,
    print_guardrail_result,
)

SENSITIVE_TEXT = """
장애 보고서 작성에 다음 정보를 포함해줘.

사용자 이메일: student@example.com
내부 IP: 10.10.20.35
테스트용 Access Key 형식: AKIAIOSFODNN7EXAMPLE
테스트용 Secret 형식: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""

def main() -> None:
    client = create_bedrock_runtime()

    response = apply_guardrail(
        client=client,
        text=SENSITIVE_TEXT,
        source="INPUT",
    )

    print("=" * 70)
    print("민감정보 필터 결과")
    print("=" * 70)
    print_guardrail_result(response)

    print("\n주의:")
    print("- 예제 값만 사용합니다.")
    print("- 실제 자격증명을 실습 입력에 넣지 않습니다.")
    print("- 마스킹과 차단 결과를 구분합니다.")

if __name__ == "__main__":
    main()
