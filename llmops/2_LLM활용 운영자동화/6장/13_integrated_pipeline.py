import csv
from pathlib import Path

from pydantic import ValidationError

from bedrock_common import (
    converse_text,
    create_bedrock_runtime,
    get_model_id,
)
from json_tools import extract_json_object
from structured_models import IncidentAnalysis

MAX_RETRIES = 2

SOURCE_PROMPT = """
다음 Linux 로그를 분석하여 IncidentAnalysis JSON을 반환합니다.

<log>
nginx: bind() to 0.0.0.0:80 failed
nginx: Address already in use
</log>

규칙:
- JSON 객체 하나만 반환합니다.
- 입력에서 직접 확인되는 사실만 facts에 작성합니다.
- 가능한 원인은 1개 이상 3개 이하입니다.
- 각 원인에는 evidence_type, evidence, confidence,
  verification을 작성합니다.
- recommended_checks에는 조회 명령만 작성합니다.
- risk_level은 read_only입니다.
- recommended_checks의 approval_required는 false입니다.
- error_code가 없으면 null을 사용합니다.
"""

def call_bedrock(
    client,
    model_id: str,
    prompt: str,
) -> str:
    output_text, _ = converse_text(
        client=client,
        model_id=model_id,
        user_prompt=prompt,
        temperature=0.1,
        max_tokens=1600,
    )
    return output_text

def validate_with_retry(
    client,
    model_id: str,
) -> IncidentAnalysis:
    prompt = SOURCE_PROMPT

    for attempt in range(1, MAX_RETRIES + 2):
        output_text = call_bedrock(
            client,
            model_id,
            prompt,
        )

        print(f"\n[{attempt}차 모델 응답]")
        print(output_text)

        try:
            json_text = extract_json_object(output_text)
            return IncidentAnalysis.model_validate_json(
                json_text
            )

        except (ValueError, ValidationError) as error:
            if attempt > MAX_RETRIES:
                raise RuntimeError(
                    "재시도 후에도 검증에 실패했습니다."
                ) from error

            prompt = f"""
다음 응답은 JSON 또는 Schema 검증에 실패했습니다.

[원래 요청]
{SOURCE_PROMPT}

[응답]
{output_text}

[검증 오류]
{error}

오류를 수정하여 JSON 객체 하나만 반환합니다.
"""

def save_results(
    analysis: IncidentAnalysis,
) -> None:
    result_dir = Path("results")
    result_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = result_dir / "final_analysis.json"
    csv_path = result_dir / "final_summary.csv"

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

    print("\n[저장 완료]")
    print(json_path)
    print(csv_path)

def main() -> None:
    client = create_bedrock_runtime()
    model_id = get_model_id()

    analysis = validate_with_retry(
        client,
        model_id,
    )

    print("\n[최종 검증 결과]")
    print(analysis.model_dump_json(indent=2))

    save_results(analysis)

if __name__ == "__main__":
    main()
