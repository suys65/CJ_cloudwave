import json

from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    parse_json_object,
)

EVIDENCE_TYPES = {
    "direct",
    "temporal",
    "correlation",
    "configuration",
    "general_knowledge",
}

CONFIDENCE_LEVELS = {
    "high",
    "medium",
    "low",
}

PROMPT = """
다음 운영 상황을 분석하여 JSON만 반환합니다.

<events>
10:00 신규 버전 배포
10:05 CPU 사용률 95%
10:06 HTTP 500 오류율 18%
10:08 payment-api Pod 재시작 5회
</events>

출력 형식:

{
  "facts": [],
  "possible_causes": [
    {
      "cause": "",
      "evidence_type": "",
      "evidence": "",
      "confidence": "",
      "verification": []
    }
  ],
  "additional_information": []
}

규칙:
- facts에는 입력에서 직접 확인되는 내용만 작성합니다.
- possible_causes는 최대 3개입니다.
- 원인을 확정하지 않습니다.
- evidence_type은 direct, temporal, correlation,
  configuration, general_knowledge 중 하나입니다.
- confidence는 high, medium, low 중 하나입니다.
- verification에는 원인을 확인하기 위한 조회 절차를 작성합니다.
- 입력에 없는 사실을 생성하지 않습니다.
- JSON 이외의 설명은 작성하지 않습니다.
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output, _ = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=PROMPT,
        temperature=0.1,
        max_tokens=2000,
    )

    print("모델 원본 응답")
    print(output)

    parsed = parse_json_object(output)
    causes = parsed.get("possible_causes", [])

    validation_errors: list[str] = []

    if len(causes) > 3:
        validation_errors.append("possible_causes가 3개를 초과했습니다.")

    for index, item in enumerate(causes, start=1):
        evidence_type = item.get("evidence_type")
        confidence = item.get("confidence")
        verification = item.get("verification")

        if evidence_type not in EVIDENCE_TYPES:
            validation_errors.append(
                f"{index}번 원인의 evidence_type이 허용값이 아닙니다."
            )

        if confidence not in CONFIDENCE_LEVELS:
            validation_errors.append(
                f"{index}번 원인의 confidence가 허용값이 아닙니다."
            )

        if not isinstance(verification, list) or not verification:
            validation_errors.append(
                f"{index}번 원인에 verification이 없습니다."
            )

    print("\n[검증 결과]")
    if validation_errors:
        for error in validation_errors:
            print("-", error)
    else:
        print("[검증 성공] 근거 유형, 신뢰 수준, 확인 방법이 유효합니다.")

    print("\n[정리된 JSON]")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
