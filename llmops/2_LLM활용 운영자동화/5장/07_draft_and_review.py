import json

from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    parse_json_object,
)

SOURCE_DATA = """
10:00 신규 버전 배포
10:05 CPU 사용률 95%
10:06 HTTP 500 오류율 18%
10:08 payment-api Pod 재시작 5회
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    draft_prompt = f"""
다음 운영 데이터를 분석하여 초안을 JSON으로 작성합니다.

<events>
{SOURCE_DATA}
</events>

출력 형식:

{{
  "summary": "",
  "facts": [],
  "possible_causes": [
{{
      "cause": "",
      "evidence": "",
      "confidence": ""
}}
  ]
}}

규칙:
- 입력에서 확인되는 사실과 가능한 원인을 구분합니다.
- 원인을 확정하지 않습니다.
- 가능한 원인은 최대 3개입니다.
- JSON만 반환합니다.
"""

    draft_text, _ = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=draft_prompt,
        temperature=0.1,
        max_tokens=1800,
    )
    draft = parse_json_object(draft_text)

    review_prompt = f"""
다음 원본 데이터와 분석 초안을 비교하여 초안을 검토합니다.

<source>
{SOURCE_DATA}
</source>

<draft>
{json.dumps(draft, ensure_ascii=False)}
</draft>

검토 항목:
- 입력에 없는 사실을 단정했는가
- facts와 possible_causes가 혼합되었는가
- 원인 후보에 근거가 있는가
- confidence가 high, medium, low 중 하나인가
- 필요한 출력 필드가 누락되었는가

문제가 없더라도 revised_result에 최종 결과를 작성합니다.

출력 형식:

{{
  "valid": true,
  "problems": [],
  "revised_result":{{
    "summary": "",
    "facts": [],
    "possible_causes": []
}}
}}

JSON만 반환합니다.
"""

    review_text, _ = invoke_text(
        client=client,
        model_id=model_id,
        user_prompt=review_prompt,
        temperature=0.1,
        max_tokens=2000,
    )
    review = parse_json_object(review_text)

    print("=" * 60)
    print("1차 초안")
    print("=" * 60)
    print(json.dumps(draft, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("검토 결과")
    print("=" * 60)
    print(json.dumps(review, ensure_ascii=False, indent=2))

    if review.get("valid") is True:
        print("\n[검토 결과] 초안이 검토 기준을 충족했습니다.")
    else:
        print("\n[검토 결과] problems와 revised_result를 확인합니다.")

if __name__ == "__main__":
    main()
