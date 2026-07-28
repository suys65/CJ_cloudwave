from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)

class IncidentRule(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
        "unknown",
    ]
    summary: str = Field(
        min_length=5,
        max_length=100,
    )
    possible_causes: list[str] = Field(
        min_length=1,
        max_length=3,
    )

def validate_case(name: str, data: dict) -> None:
    print(f"\n[{name}]")

    try:
        result = IncidentRule.model_validate(data)
        print("검증 성공")
        print(result.model_dump())

    except ValidationError as error:
        print("검증 실패")
        for item in error.errors():
            print(
                f"- 위치={item['loc']}, "
                f"오류={item['msg']}"
            )

def main() -> None:
    validate_case(
        "정상 데이터",
        {
            "severity": "high",
            "summary": "Nginx 포트 충돌로 서비스 시작 실패",
            "possible_causes": [
                "다른 프로세스가 80번 포트를 사용 중",
            ],
        },
    )

    validate_case(
        "허용되지 않은 심각도",
        {
            "severity": "urgent",
            "summary": "Nginx 포트 충돌로 서비스 시작 실패",
            "possible_causes": [
                "다른 프로세스가 80번 포트를 사용 중",
            ],
        },
    )

    validate_case(
        "원인 개수 초과",
        {
            "severity": "high",
            "summary": "Nginx 포트 충돌로 서비스 시작 실패",
            "possible_causes": [
                "원인 1",
                "원인 2",
                "원인 3",
                "원인 4",
            ],
        },
    )

if __name__ == "__main__":
    main()
