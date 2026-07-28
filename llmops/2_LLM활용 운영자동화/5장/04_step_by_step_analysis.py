import json

from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    parse_json_object,
    print_metadata,
)

SYSTEM_PROMPT = """
당신은 웹 애플리케이션 장애 분석가입니다.

규칙:
- 입력에서 직접 확인되는 사실만 facts에 작성합니다.
- 시간 순서만으로 인과관계를 확정하지 않습니다.
- 가능한 원인은 최대 3개로 제한합니다.
- 각 원인에는 evidence와 verification을 작성합니다.
- 입력에 없는 시스템 상태를 생성하지 않습니다.
- 출력은 JSON만 반환합니다.
"""

USER_PROMPT = """
다음 운영 이벤트를 분석합니다.

<events>
10:00 신규 버전 배포 완료
10:05 CPU 사용률 32%에서 94%로 증가
10:06 HTTP 500 오류율 1%에서 17%로 증가
10:07 평균 응답시간 140ms에서 1.1초로 증가
10:08 payment-api Pod 재시작 횟수 0에서 5로 증가
</events>

다음 순서로 결과를 작성합니다.

1. 입력에서 확인된 사실을 facts에 작성합니다.
2. 사건의 시간 관계를 timeline에 작성합니다.
3. 장애 category를 분류합니다.
4. 가능한 원인을 최대 3개 작성합니다.
5. 각 원인의 근거와 확인 방법을 작성합니다.
6. 추가로 필요한 정보를 additional_information에 작성합니다.
7. 전체 상황을 summary에 작성합니다.

출력 형식:

{
  "facts": [],
  "timeline": [],
  "category": "",
  "possible_causes": [
    {
      "cause": "",
      "evidence": "",
      "verification": []
    }
  ],
  "additional_information": [],
  "summary": ""
}
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output, metadata = invoke_text(
        client=client,
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        temperature=0.1,
        max_tokens=3000,
    )

    print("모델 원본 응답")
    print(output)

    parsed = parse_json_object(output)

    required_fields = {
        "facts",
        "timeline",
        "category",
        "possible_causes",
        "additional_information",
        "summary",
    }

    missing = required_fields - parsed.keys()
    cause_count = len(parsed.get("possible_causes", []))

    print("\n[구조 확인]")
    print("누락 필드:", sorted(missing) if missing else "없음")
    print("사실 개수:", len(parsed.get("facts", [])))
    print("시간 항목 개수:", len(parsed.get("timeline", [])))
    print("원인 후보 개수:", cause_count)

    if not missing and cause_count <= 3:
        print("[검증 성공] 단계별 분석 구조를 충족했습니다.")
    else:
        print("[검증 실패] 프롬프트 또는 출력 구조를 조정해야 합니다.")

    print("\n[정리된 JSON]")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    print_metadata(metadata)

if __name__ == "__main__":
    main()
