from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
)

class IncidentSummary(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    severity: str
    service: str
    summary: str
    approval_required: bool

def main() -> None:
    valid_data = {
        "severity": "high",
        "service": "nginx",
        "summary": "80번 포트 충돌로 Nginx 시작 실패",
        "approval_required": False,
    }

    invalid_data = {
        "severity": "high",
        "service": 100,
        "summary": "장애",
        "approval_required": "아니오",
        "extra_field": "허용하지 않는 필드",
    }

    print("=" * 60)
    print("정상 데이터 검증")
    print("=" * 60)

    analysis = IncidentSummary.model_validate(valid_data)

    print(analysis)
    print(analysis.model_dump())
    print(analysis.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("잘못된 데이터 검증")
    print("=" * 60)

    try:
        IncidentSummary.model_validate(invalid_data)

    except ValidationError as error:
        for item in error.errors():
            print("위치:", item["loc"])
            print("오류:", item["msg"])
            print("유형:", item["type"])
            print("-" * 40)

if __name__ == "__main__":
    main()
