import csv
from pathlib import Path

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import IncidentAnalysis

PROMPT = """
다음 로그를 분석하여 IncidentAnalysis 형식의 JSON을 반환합니다.

<log>
nginx: bind() to 0.0.0.0:80 failed
nginx: Address already in use
</log>

다음 JSON 구조를 정확하게 사용합니다.

{
  "severity": "low | medium | high | critical | unknown",
  "service": "string",
  "summary": "string",
  "facts": ["string"],
  "possible_causes": [
    {
      "cause": "string",
      "evidence_type": "direct | temporal | correlation | configuration | general_knowledge",
      "evidence": "string",
      "confidence": "high | medium | low",
      "verification": ["string"]
    }
  ],
  "recommended_checks": [
    {
      "command": "string",
      "purpose": "string",
      "risk_level": "read_only",
      "approval_required": false
    }
  ],
  "approval_required": false,
  "additional_information": ["string"],
  "error_code": null
}

필수 규칙:
- severity는 low, medium, high, critical, unknown 중 하나입니다.
- possible_causes는 1개 이상 3개 이하입니다.
- recommended_checks는 조회 명령만 작성합니다.
- risk_level은 read_only입니다.
- approval_required는 false입니다.
- error_code가 없으면 null을 사용합니다.
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
        max_tokens=1400,
    )

    json_text = extract_json_object(output_text)
    analysis = IncidentAnalysis.model_validate_json(
        json_text
    )

    result_dir = Path("results")
    result_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = result_dir / "incident_analysis.json"
    csv_path = result_dir / "incident_summary.csv"

    json_path.write_text(
        analysis.model_dump_json(indent=2),
        encoding="utf-8",
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "severity",
                "service",
                "summary",
                "approval_required",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "severity": analysis.severity,
                "service": analysis.service,
                "summary": analysis.summary,
                "approval_required": (
                    analysis.approval_required
                ),
            }
        )

    print("JSON 저장:", json_path)
    print("CSV 저장:", csv_path)

if __name__ == "__main__":
    main()
