from pydantic import ValidationError

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import KubernetesIncident

PROMPT = """
다음 Kubernetes 상태를 분석하여 JSON 객체 하나만 반환합니다.

<input>
Namespace: production
Pod: payment-api-7c89d6c8b9-k2m4p
Status: CrashLoopBackOff
Last State: OOMKilled
Exit Code: 137
Restart Count: 9
Memory Limit: 512Mi
</input>

출력 형식:

{
  "namespace": "string",
  "pod_name": "string",
  "status": "Running | Pending | CrashLoopBackOff | ImagePullBackOff | Failed | Unknown",
  "severity": "low | medium | high | critical | unknown",
  "summary": "string",
  "facts": ["string"],
  "possible_causes": ["string"],
  "recommended_checks": [
    {
      "command": "string",
      "purpose": "string"
    }
  ],
  "change_required": true,
  "approval_required": true
}

규칙:
- facts에는 입력에서 직접 확인되는 내용만 작성합니다.
- possible_causes는 최대 3개입니다.
- recommended_checks에는 조회 명령만 작성합니다.
- 메모리 제한 변경과 Pod 재시작은 변경 작업이므로 승인 필요로 표시합니다.
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
        analysis = KubernetesIncident.model_validate_json(
            json_text
        )

        print("\n[검증 성공]")
        print(analysis.model_dump_json(indent=2))

    except (ValueError, ValidationError) as error:
        print("\n[검증 실패]")
        print(error)

if __name__ == "__main__":
    main()
