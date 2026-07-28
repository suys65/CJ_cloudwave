from pydantic import ValidationError

from structured_models import IncidentAnalysis

VALID_DATA = {
    "severity": "high",
    "service": "nginx",
    "summary": "80번 포트 충돌로 Nginx가 시작되지 않음",
    "facts": [
        "0.0.0.0:80 바인딩에 실패함",
        "Address already in use 메시지가 존재함",
    ],
    "possible_causes": [
        {
            "cause": "다른 프로세스가 80번 포트를 사용 중일 가능성",
            "evidence_type": "direct",
            "evidence": "Address already in use",
            "confidence": "high",
            "verification": [
                "ss 명령으로 80번 포트 점유 프로세스를 확인",
            ],
        }
    ],
    "recommended_checks": [
        {
            "command": "sudo ss -lntp | grep ':80'",
            "purpose": "80번 포트 점유 프로세스 확인",
            "risk_level": "read_only",
            "approval_required": False,
        }
    ],
    "approval_required": False,
    "additional_information": [],
    "error_code": None,
}

def main() -> None:
    try:
        analysis = IncidentAnalysis.model_validate(VALID_DATA)

        print("검증 성공")
        print(analysis.model_dump_json(indent=2))

        print("\n첫 번째 원인:")
        print(analysis.possible_causes[0].cause)

        print("\n첫 번째 조회 명령:")
        print(analysis.recommended_checks[0].command)

    except ValidationError as error:
        print("검증 실패")
        print(error)

if __name__ == "__main__":
    main()
