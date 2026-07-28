import json

from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    parse_json_object,
)

EVENTS = """
09:55 버전 2.4.0에서 2.5.0으로 배포 시작
10:00 배포 완료
10:05 CPU 사용률 32%에서 94%로 증가
10:06 HTTP 500 오류율 1%에서 17%로 증가
10:07 평균 응답시간 140ms에서 1.1초로 증가
10:08 payment-api Pod 재시작 횟수 0에서 5로 증가
"""

def call_json(client, model_id: str, prompt: str, max_tokens: int) -> dict:
    output, _ = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=max_tokens,
    )
    return parse_json_object(output)

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    facts = call_json(
        client,
        model_id,
        f"""
다음 데이터에서 직접 확인되는 사실만 추출합니다.

<events>
{EVENTS}
</events>

출력:
{{"facts": []}}

JSON만 반환합니다.
""",
        700,
    )

    classification = call_json(
        client,
        model_id,
        f"""
다음 사실을 이용하여 장애를 분류합니다.

<facts>
{json.dumps(facts, ensure_ascii=False)}
</facts>

허용 category:
- application
- performance
- availability
- security
- unknown

허용 severity:
- low
- medium
- high
- unknown

출력:
{{
  "category": "",
  "severity": "",
  "reason": ""
}}

JSON만 반환합니다.
""",
        500,
    )

    ticket = call_json(
        client,
        model_id,
        f"""
다음 사실과 분류 결과를 이용하여 운영 티켓을 작성합니다.

<facts>
{json.dumps(facts, ensure_ascii=False)}
</facts>

<classification>
{json.dumps(classification, ensure_ascii=False)}
</classification>

입력에 없는 사실을 생성하지 않습니다.

출력:
{{
  "title": "",
  "severity": "",
  "category": "",
  "affected_service": "payment-api",
  "summary": "",
  "status": "open"
}}

JSON만 반환합니다.
""",
        800,
    )

    print("=" * 60)
    print("호출 1: 사실 추출")
    print("=" * 60)
    print(json.dumps(facts, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("호출 2: 장애 분류")
    print("=" * 60)
    print(json.dumps(classification, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("호출 3: 운영 티켓 생성")
    print("=" * 60)
    print(json.dumps(ticket, ensure_ascii=False, indent=2))

    required = {
        "title",
        "severity",
        "category",
        "affected_service",
        "summary",
        "status",
    }

    missing = required - ticket.keys()

    if missing:
        print("\n[검증 실패] 티켓 누락 필드:", sorted(missing))
    else:
        print("\n[검증 성공] 세 단계 호출 결과가 티켓으로 연결되었습니다.")

if __name__ == "__main__":
    main()
