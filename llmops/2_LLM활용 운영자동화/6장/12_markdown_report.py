from structured_models import IncidentAnalysis

SAMPLE_DATA = {
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

def to_markdown(
    analysis: IncidentAnalysis,
) -> str:
    lines = [
        f"#{analysis.service} 장애 분석",
        "",
        f"- 심각도: `{analysis.severity}`",
        f"- 요약:{analysis.summary}",
        "",
        "## 확인된 사실",
    ]

    for fact in analysis.facts:
        lines.append(f"-{fact}")

    lines.extend(
        [
            "",
            "## 가능한 원인",
        ]
    )

    for item in analysis.possible_causes:
        lines.append(
            f"-{item.cause} "
            f"(신뢰도:{item.confidence})"
        )
        lines.append(
            f"  - 근거:{item.evidence}"
        )

    lines.extend(
        [
            "",
            "## 권장 확인 절차",
        ]
    )

    for item in analysis.recommended_checks:
        lines.append(f"- `{item.command}`")
        lines.append(f"  - 목적:{item.purpose}")

    return "\n".join(lines)

def main() -> None:
    analysis = IncidentAnalysis.model_validate(
        SAMPLE_DATA
    )

    print(to_markdown(analysis))

if __name__ == "__main__":
    main()
