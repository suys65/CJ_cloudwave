from pydantic import ValidationError

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import IncidentAnalysis

MAX_RETRIES = 2

SOURCE_PROMPT = """
다음 로그를 분석하여 JSON 객체 하나만 반환합니다.

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

규칙:
- severity는 low, medium, high, critical, unknown 중 하나입니다.
- possible_causes는 1개 이상 3개 이하입니다.
- recommended_checks는 조회 명령만 작성합니다.
- recommended_checks의 risk_level은 read_only입니다.
- recommended_checks의 approval_required는 false입니다.
- JSON만 반환합니다.
"""

def call_model(client, model_id: str, prompt: str) -> str:
    output_text, _ = converse_text(
        client=client,
        model_id=model_id,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=1400,
    )
    return output_text

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    prompt = SOURCE_PROMPT

    for attempt in range(1, MAX_RETRIES + 2):
        print(f"\n[{attempt}차 호출]")

        output_text = call_model(
            client,
            model_id,
            prompt,
        )

        print(output_text)

        try:
            json_text = extract_json_object(output_text)
            analysis = IncidentAnalysis.model_validate_json(
                json_text
            )

            print("\n[검증 성공]")
            print(analysis.model_dump_json(indent=2))
            return

        except (ValueError, ValidationError) as error:
            print("\n[검증 실패]")
            print(error)

            if attempt > MAX_RETRIES:
                print(
                    "\n재시도 한도를 초과했습니다. "
                    "운영자 검토가 필요합니다."
                )
                return

            prompt = f"""
다음 응답은 JSON 또는 Schema 검증에 실패했습니다.

[원래 요청]
{SOURCE_PROMPT}

[잘못된 응답]
{output_text}

[검증 오류]
{error}

검증 오류를 수정하여 JSON 객체 하나만 다시 반환합니다.
Markdown 코드 블록과 설명 문장은 포함하지 않습니다.
"""

if __name__ == "__main__":
    main()
