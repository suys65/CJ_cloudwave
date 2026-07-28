from pydantic import ValidationError

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import NetworkIncident

PROMPT = """
다음 네트워크 장애 정보를 분석하여 JSON 객체 하나만 반환합니다.

<input>
Source: web01
Destination: db01
Destination Port: 5432
Symptom: Connection timed out
DNS resolution: success
ICMP ping: success
TCP connection to 5432: timeout
</input>

출력 형식:

{
  "source": "string",
  "destination": "string",
  "destination_port": 1,
  "symptom": "string",
  "possible_causes": ["string"],
  "recommended_checks": [
    {
      "command": "string",
      "purpose": "string",
      "layer": "application | transport | network | data_link | unknown"
    }
  ],
  "confirmed_root_cause": false,
  "additional_information": ["string"]
}

규칙:
- destination_port는 숫자로 작성합니다.
- 원인이 확정되지 않았으므로 confirmed_root_cause는 false입니다.
- possible_causes는 최대 3개입니다.
- 조회 또는 진단 명령만 작성합니다.
- JSON만 반환합니다.
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output_text, _ = converse_text(
        client=client,
        model_id=model_id,
        user_prompt=PROMPT,
        temperature=0.1,
        max_tokens=1200,
    )

    print("Bedrock 원본 응답")
    print(output_text)

    try:
        json_text = extract_json_object(output_text)
        analysis = NetworkIncident.model_validate_json(
            json_text
        )

        print("\n[검증 성공]")
        print(analysis.model_dump_json(indent=2))

    except (ValueError, ValidationError) as error:
        print("\n[검증 실패]")
        print(error)

if __name__ == "__main__":
    main()
