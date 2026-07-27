import json

from bedrock_utils import converse, extract_text, strip_json_fence
from config import AWS_PROFILE, AWS_REGION

system_prompt = """
당신은 AWS CLI 조회 명령 생성기이다.

허용 operation_type:
- read_only
- change
- security_change
- destructive
- unsupported

규칙:

1. 읽기 전용 조회 명령만 생성한다.
2. 조회 작업의 operation_type은 반드시 read_only로 작성한다.
3. 생성, 수정, 삭제, 재시작, 종료 명령은 생성하지 않는다.
4. 조회가 아닌 작업은 command를 null로 작성하고 operation_type을 change, security_change, destructive 중 하나로 작성한다.
5. 지원하지 않는 요청은 command를 null, operation_type을 unsupported로 작성한다.
6. AWS Profile과 리전을 반드시 포함한다.
7. JSON 객체 하나만 반환한다.
8. Markdown 코드 블록을 사용하지 않는다.
9. 실제 실행 결과를 생성하지 않는다.

출력 형식:

{
  "service": "",
  "intent": "",
  "operation_type": "",
  "command": "",
  "approval_required": false,
  "description": ""
}
"""

requests = [
    "현재 EC2 인스턴스 목록을 확인하는 명령을 작성해줘.",
    "최근 CloudWatch Alarm을 조회하는 명령을 작성해줘.",
    "Auto Scaling Group 상태를 조회하는 명령을 작성해줘.",
    "EC2 인스턴스를 재부팅하는 명령을 작성해줘.",
]

for request_text in requests:
    user_prompt = f"""
사용자 요청:
{request_text}

환경:
- AWS Profile:{AWS_PROFILE}
- AWS Region:{AWS_REGION}
"""

    response = converse(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
        max_tokens=600,
    )

    output_text = extract_text(response)

    print("\n" + "=" * 80)
    print("요청:", request_text)
    print("=" * 80)
    print(output_text)

    try:
        parsed = json.loads(strip_json_fence(output_text))

        command = parsed.get("command")
        operation_type = parsed.get("operation_type")

        if operation_type == "read_only" and command:
            print("읽기 전용 명령 생성 완료")
        else:
            print("변경 작업이므로 명령 실행 대상에서 제외")

    except json.JSONDecodeError as error:
        print("JSON 파싱 실패:", error)
