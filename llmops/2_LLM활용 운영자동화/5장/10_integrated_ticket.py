import json

from bedrock_common import (
    create_bedrock_runtime,
    get_model_id,
    invoke_text,
    parse_json_object,
)

SYSTEM_PROMPT = """
당신은 AWS와 Kubernetes 운영 장애 분석가입니다.

분석 규칙:
1. 입력 데이터에 직접 존재하는 사실과 가능한 원인을 구분합니다.
2. 장애 원인을 확정하지 않습니다.
3. 가능한 원인은 최대 3개입니다.
4. 각 원인에 evidence_type, evidence, confidence,
   verification을 작성합니다.
5. 시간 순서만으로 인과관계를 확정하지 않습니다.
6. 정보가 부족하면 additional_information에 작성합니다.
7. 실제 조회하지 않은 시스템 상태를 생성하지 않습니다.

안전 규칙:
1. recommended_checks에는 조회와 진단 작업만 작성합니다.
2. 변경, 재시작, 롤백, 삭제 명령은 작성하지 않습니다.
3. 변경 검토 사항은 proposed_actions에 작성합니다.
4. proposed_actions의 command는 null입니다.
5. proposed_actions의 approval_required는 true입니다.

출력은 JSON만 반환합니다.
"""

USER_PROMPT = """
다음 운영 상황을 분석합니다.

<service>
payment-api
</service>

<events>
09:55 버전 2.4.0에서 2.5.0으로 배포 시작
10:00 배포 완료
10:05 CPU 사용률 32%에서 94%로 증가
10:06 HTTP 500 오류율 1%에서 17%로 증가
10:07 평균 응답시간 140ms에서 1.1초로 증가
10:08 payment-api Pod 재시작 횟수 0에서 5로 증가
10:10 CloudWatch HighCPU 알람 발생
</events>

<context>
데이터베이스 CPU는 정상 범위
ALB Target 상태는 unhealthy
Kubernetes Node 상태는 Ready
</context>

출력 형식:

{
  "ticket": {
    "title": "",
    "severity": "",
    "category": "",
    "affected_service": "",
    "summary": "",
    "status": "open"
  },
  "facts": [],
  "timeline": [],
  "possible_causes": [
    {
      "cause": "",
      "evidence_type": "",
      "evidence": "",
      "confidence": "",
      "verification": []
    }
  ],
  "recommended_checks": [
    {
      "description": "",
      "command": "",
      "purpose": "",
      "approval_required": false
    }
  ],
  "proposed_actions": [
    {
      "description": "",
      "action_type": "",
      "command": null,
      "risk_level": "",
      "approval_required": true
    }
  ],
  "additional_information": []
}
"""

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    output, _ = invoke_text(
        client=client,
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        temperature=0.1,
        max_tokens=4000,
    )

    parsed = parse_json_object(output)
    ticket = parsed.get("ticket", {})

    print("모델 원본 응답")
    print(output)

    print("\n[결과 확인]")
    print("티켓 제목:", ticket.get("title"))
    print("심각도:", ticket.get("severity"))
    print("분류:", ticket.get("category"))
    print("사실 개수:", len(parsed.get("facts", [])))
    print("원인 후보 개수:", len(parsed.get("possible_causes", [])))
    print("조회 작업 개수:", len(parsed.get("recommended_checks", [])))
    print("승인 작업 개수:", len(parsed.get("proposed_actions", [])))

    errors: list[str] = []

    if len(parsed.get("possible_causes", [])) > 3:
        errors.append("원인 후보가 3개를 초과했습니다.")

    for action in parsed.get("proposed_actions", []):
        if action.get("command") is not None:
            errors.append("승인 작업의 command는 null이어야 합니다.")
        if action.get("approval_required") is not True:
            errors.append("승인 작업의 approval_required는 true여야 합니다.")

    if errors:
        print("\n[검증 실패]")
        for error in errors:
            print("-", error)
    else:
        print("\n[검증 성공] 종합 출력 구조와 승인 규칙을 충족했습니다.")

    print("\n[정리된 JSON]")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
