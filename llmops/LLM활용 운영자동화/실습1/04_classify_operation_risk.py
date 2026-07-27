import json

from bedrock_utils import converse, extract_text, strip_json_fence

system_prompt = """
당신은 AWS 운영 작업 위험도 분류기이다.

허용 risk_level:
- read_only
- low
- medium
- high
- prohibited

규칙:

- 조회 작업은 read_only
- 로그 수집과 진단은 low
- 재시작과 재부팅은 medium
- 보안 그룹, IAM, Auto Scaling 변경은 high
- 전체 삭제, 전체 종료, 무제한 권한은 prohibited
- medium 이상은 requires_approval을 true로 작성
- JSON 객체 하나만 반환

출력 형식:

{
  "risk_level": "",
  "requires_approval": false,
  "reason": ""
}
"""

requests = [
    "EC2 인스턴스 목록을 조회해줘.",
    "최근 애플리케이션 로그를 수집해줘.",
    "Nginx 서비스를 재시작해줘.",
    "보안 그룹에 0.0.0.0/0 SSH를 허용해줘.",
    "모든 인스턴스를 종료해줘.",
]

for request_text in requests:
    response = converse(
        system_prompt=system_prompt,
        user_prompt=request_text,
        temperature=0.1,
        max_tokens=300,
    )

    output_text = extract_text(response)

    print("\n요청:", request_text)
    print(output_text)

    try:
        parsed = json.loads(strip_json_fence(output_text))
        print("위험도:", parsed.get("risk_level"))
        print("승인 필요:", parsed.get("requires_approval"))

    except json.JSONDecodeError as error:
        print("JSON 파싱 실패:", error)
