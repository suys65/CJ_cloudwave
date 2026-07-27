import json

from bedrock_utils import converse, extract_text, strip_json_fence

system_prompt = """
당신은 AWS 운영 요청 분석기이다.

사용자의 요청을 분석하여 JSON 객체 하나만 반환한다.

허용 service:
- ec2
- cloudwatch
- logs
- autoscaling
- elbv2
- unknown

허용 operation_type:
- read_only
- change
- security_change
- destructive
- unsupported

규칙:

1. JSON 외의 설명을 작성하지 않는다.
2. 조회 작업은 read_only로 분류한다.
3. 생성, 수정, 재시작은 change로 분류한다.
4. IAM, 보안 그룹, 방화벽 변경은 security_change로 분류한다.
5. 삭제와 종료는 destructive로 분류한다.
6. 변경 작업은 approval_required를 true로 작성한다.
7. 정보가 부족하면 service를 unknown으로 작성한다.

출력 형식:

{
  "service": "",
  "intent": "",
  "operation_type": "",
  "approval_required": false,
  "reason": ""
}
"""

requests = [
    "현재 실행 중인 EC2 인스턴스를 확인해줘.",
    "최근 CloudWatch Alarm을 조회해줘.",
    "EC2 인스턴스를 재부팅해줘.",
    "보안 그룹에 22번 포트를 열어줘.",
    "모든 EC2 인스턴스를 종료해줘.",
]

for request_text in requests:
    response = converse(
        system_prompt=system_prompt,
        user_prompt=request_text,
        temperature=0.1,
        max_tokens=400,
    )

    output_text = extract_text(response)

    print("\n" + "=" * 80)
    print("사용자 요청:", request_text)
    print("=" * 80)
    print(output_text)

    try:
        parsed = json.loads(strip_json_fence(output_text))

        print("서비스:", parsed.get("service"))
        print("작업 유형:", parsed.get("operation_type"))
        print("승인 필요:", parsed.get("approval_required"))

    except json.JSONDecodeError as error:
        print("JSON 파싱 실패:", error)
