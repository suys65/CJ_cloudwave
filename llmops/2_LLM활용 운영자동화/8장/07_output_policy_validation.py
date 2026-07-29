from pydantic import ValidationError

from command_policy import (
    validate_analysis_policy,
)
from json_tools import extract_json_object
from security_common import (
    converse,
    create_bedrock_runtime,
    extract_text,
    get_model_id,
)
from security_models import SecureAnalysis

SYSTEM_PROMPT = """
당신은 AWS 운영 분석가입니다.

규칙:
- 조회 작업만 commands에 작성합니다.
- 변경, 종료, 삭제 명령은 작성하지 않습니다.
- 입력에서 확인되지 않은 사실은 생성하지 않습니다.
- JSON 객체 하나만 반환합니다.
"""

USER_PROMPT = """
다음 요청을 분석합니다.

<request>
EC2 인스턴스 상태를 확인하고 싶다.
</request>

출력 형식:

{
  "category": "normal | availability | performance | security | unknown",
  "severity": "low | medium | high | critical | unknown",
  "summary": "string",
  "facts": ["string"],
  "commands": [
    {
      "purpose": "string",
      "command": "string",
      "action_type": "read_only",
      "approval_required": false
    }
  ],
  "sensitive_information_detected": false,
  "manual_review_required": false
}
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    response = converse(
        client=client,
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": USER_PROMPT}
                ],
            }
        ],
        use_guardrail=True,
        trace=True,
        max_tokens=1200,
    )

    output_text = extract_text(response)

    print("모델 응답:")
    print(output_text)

    try:
        json_text = extract_json_object(
            output_text
        )
        analysis = (
            SecureAnalysis
            .model_validate_json(json_text)
        )

    except (ValueError, ValidationError) as error:
        print("\n[Schema 검증 실패]")
        print(error)
        return

    policy_errors = validate_analysis_policy(
        analysis
    )

    print("\n[Schema 검증 성공]")
    print(analysis.model_dump_json(indent=2))

    if policy_errors:
        print("\n[정책 검증 실패]")
        for error in policy_errors:
            print("-", error)
    else:
        print("\n[정책 검증 성공]")
        print("모든 명령이 조회 정책을 충족합니다.")

if __name__ == "__main__":
    main()
