from botocore.exceptions import BotoCoreError, ClientError

from bedrock_utils import converse, extract_text

system_prompt = """
당신은 Linux 서버 운영 분석가이다.

규칙:

- 제공된 로그만 직접 근거로 사용한다.
- 장애 원인을 확정하지 않는다.
- 존재하지 않는 명령어를 생성하지 않는다.
- 변경, 삭제, 재시작 명령을 제안하지 않는다.
- 조회와 진단 명령만 작성한다.
"""

user_prompt = """
다음 로그를 분석한다.

<log>
nginx: bind() to 0.0.0.0:80 failed
nginx: Address already in use
</log>

다음 내용을 작성한다.

1. 장애 요약
2. 로그에서 확인된 사실
3. 가능한 원인
4. 조회 중심 확인 명령어
5. 각 명령어의 목적
"""

try:
    response = converse(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.1,
        max_tokens=800,
    )

    usage = response.get("usage", {})
    stop_reason = response.get("stopReason")

    print("=" * 80)
    print("모델 응답")
    print("=" * 80)
    print(extract_text(response))

    print("\n" + "=" * 80)
    print("응답 정보")
    print("=" * 80)
    print("입력 토큰:", usage.get("inputTokens", 0))
    print("출력 토큰:", usage.get("outputTokens", 0))
    print("전체 토큰:", usage.get("totalTokens", 0))
    print("종료 이유:", stop_reason)

except ClientError as error:
    print("AWS API 오류")
    print("코드:", error.response["Error"]["Code"])
    print("메시지:", error.response["Error"]["Message"])

except BotoCoreError as error:
    print("AWS SDK 오류")
    print(error)
