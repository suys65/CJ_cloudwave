import json

from security_common import create_sts_client

RUNTIME_REQUIRED_ACTIONS = [
    "bedrock:InvokeModel",
    "bedrock:ApplyGuardrail",
]

CONTROL_PLANE_ACTIONS = [
    "bedrock:GetGuardrail",
    "bedrock:ListGuardrails",
]

def main() -> None:
    sts = create_sts_client()
    identity = sts.get_caller_identity()

    print("=" * 70)
    print("현재 AWS 인증 주체")
    print("=" * 70)
    print(
        json.dumps(
            identity,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )

    print("\n[애플리케이션 런타임 권한]")
    for action in RUNTIME_REQUIRED_ACTIONS:
        print("-", action)

    print("\n[관리·조회 시 추가 권한]")
    for action in CONTROL_PLANE_ACTIONS:
        print("-", action)

    print("\n설계 원칙:")
    print("- 모델에 AWS 자격증명을 전달하지 않습니다.")
    print("- 애플리케이션 역할에 최소 권한만 부여합니다.")
    print("- 변경 권한과 조회 권한을 분리합니다.")
    print("- 이 실습은 AWS 변경 API를 호출하지 않습니다.")

if __name__ == "__main__":
    main()
