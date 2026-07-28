from pydantic import ValidationError

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import IncidentAnalysis

SYSTEM_PROMPT = """
당신은 Linux 서비스 장애 분석가입니다.

규칙:
- 입력에서 직접 확인되는 내용만 facts에 작성합니다.
- 가능한 원인은 최대 3개입니다.
- 원인을 확정하지 않습니다.
- recommended_checks에는 조회 명령만 작성합니다.
- 조회 작업의 risk_level은 read_only입니다.
- 조회 작업의 approval_required는 false입니다.
- JSON 객체 하나만 반환합니다.
"""

USER_PROMPT = """
다음 로그를 분석합니다.

<log>
nginx: bind() to 0.0.0.0:80 failed
nginx: Address already in use
</log>

다음 JSON 구조를 정확하게 사용합니다.

{
  "severity": "low | medium | high | critical | unknown",
  "service": "string",
  "summary": "string",
  "facts": ["string"],
  "possible_causes": [
    {
      "cause": "string",
      "evidence_type": "direct | temporal | correlation | configuration | general_knowledge",
      "evidence": "string",
      "confidence": "high | medium | low",
      "verification": ["string"]
    }
  ],
  "recommended_checks": [
    {
      "command": "string",
      "purpose": "string",
      "risk_level": "read_only",
      "approval_required": false
    }
  ],
  "approval_required": false,
  "additional_information": ["string"],
  "error_code": null
}
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output_text, _ = converse_text(
        client=client,
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        temperature=0.1,
        max_tokens=1400,
    )

    print("=" * 70)
    print("Bedrock 원본 응답")
    print("=" * 70)
    print(output_text)

    json_text = extract_json_object(output_text)

    try:
        analysis = IncidentAnalysis.model_validate_json(
            json_text
        )

        print("\n[Pydantic 검증 성공]")
        print(analysis.model_dump_json(indent=2))

    except ValidationError as error:
        print("\n[Pydantic 검증 실패]")

        for item in error.errors():
            print("위치:", item["loc"])
            print("오류:", item["msg"])
            print("유형:", item["type"])
            print("-" * 50)

if __name__ == "__main__":
    main()
