import json

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
    print_usage,
)
from json_tools import extract_json_object

PROMPT = """
다음 로그를 분석하여 JSON 객체 하나만 반환합니다.

<log>
nginx: bind() to 0.0.0.0:80 failed
nginx: Address already in use
</log>

출력 형식:

{
  "severity": "low | medium | high | critical | unknown",
  "service": "string",
  "summary": "string",
  "facts": ["string"],
  "approval_required": true
}

규칙:
- JSON 앞뒤에 설명을 추가하지 않습니다.
- Markdown 코드 블록을 사용하지 않습니다.
- 입력에 없는 사실을 생성하지 않습니다.
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output_text, metadata = converse_text(
        client=client,
        model_id=model_id,
        user_prompt=PROMPT,
        temperature=0.1,
        max_tokens=600,
    )

    print("=" * 70)
    print("Bedrock 원본 응답")
    print("=" * 70)
    print(output_text)

    json_text = extract_json_object(output_text)
    parsed = json.loads(json_text)

    print("\n[JSON 파싱 성공]")
    print("severity:", parsed.get("severity"))
    print("service:", parsed.get("service"))
    print("facts 개수:", len(parsed.get("facts", [])))

    print_usage(metadata)

if __name__ == "__main__":
    main()
