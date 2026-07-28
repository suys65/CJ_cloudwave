from pydantic import ValidationError

from structured_models import IncidentAnalysis

INVALID_DATA = {
    "severity": "urgent",
    "service": 100,
    "summary": "오류",
    "facts": "Address already in use",
    "possible_causes": [],
    "recommended_checks": [
        {
            "command": "sudo systemctl restart nginx",
            "purpose": "서비스 재시작",
            "risk_level": "high",
            "approval_required": False,
        }
    ],
    "approval_required": "no",
    "additional_information": [],
    "unexpected": "허용되지 않은 필드",
}

def main() -> None:
    try:
        IncidentAnalysis.model_validate(INVALID_DATA)

    except ValidationError as error:
        print("=" * 70)
        print("Validation Error 분석")
        print("=" * 70)

        for number, item in enumerate(
            error.errors(),
            start=1,
        ):
            print(f"[오류{number}]")
            print("위치:", item["loc"])
            print("메시지:", item["msg"])
            print("유형:", item["type"])
            print("입력값:", item.get("input"))
            print("-" * 50)

if __name__ == "__main__":
    main()
