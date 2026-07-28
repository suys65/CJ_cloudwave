import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    ProfileNotFound,
)
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. 환경변수 읽기
# ---------------------------------------------------------

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_PROFILE = os.getenv("AWS_PROFILE", "").strip()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID_1", "").strip()

OUTPUT_DIR = Path("output")

# ---------------------------------------------------------
# 2. 허용할 분류 값 정의
# ---------------------------------------------------------

ALLOWED_CATEGORIES = {
    "performance",
    "security",
    "availability",
    "normal",
}

ALLOWED_SEVERITIES = {
    "low",
    "medium",
    "high",
}

# ---------------------------------------------------------
# 3. 시스템 프롬프트
# ---------------------------------------------------------

SYSTEM_PROMPT = """
너는 IT 운영 메시지 분류기이다.

입력된 운영 메시지를 분석하여 반드시 다음 JSON 형식으로 출력한다.

{
  "category": "performance | security | availability | normal",
  "severity": "low | medium | high",
  "summary": "운영 메시지를 한 문장으로 요약"
}

분류 규칙:

1. category
- CPU, 메모리, 디스크, 응답 지연은 performance로 분류한다.
- 로그인 실패, 권한 거부, 비정상 접근은 security로 분류한다.
- 서버 중단, 연결 실패, HTTP 500 반복은 availability로 분류한다.
- 정상 완료, 정상 동작, 성공 메시지는 normal로 분류한다.

2. severity
- 정상 완료 메시지는 low로 분류한다.
- CPU, 메모리, 디스크 사용률이 70% 이상 90% 미만이면 medium으로 분류한다.
- CPU, 메모리, 디스크 사용률이 90% 이상이면 high로 분류한다.
- 일시적인 경고 또는 소수의 실패는 medium으로 분류한다.
- 반복되는 연결 실패, 서비스 중단, 다수의 로그인 실패는 high로 분류한다.

3. 출력 제한
- JSON 이외의 설명을 출력하지 않는다.
- 마크다운 코드 블록을 사용하지 않는다.
- 입력 메시지에서 확인되지 않는 내용을 추측하지 않는다.
"""

# ---------------------------------------------------------
# 4. 환경변수 검증
# ---------------------------------------------------------

def validate_environment() -> None:
    if not BEDROCK_MODEL_ID:
        raise ValueError(
            "BEDROCK_MODEL_ID가 설정되지 않았음. "
            ".env 파일에 사용할 모델 ID를 입력해야 함."
        )

# ---------------------------------------------------------
# 5. Bedrock Runtime 클라이언트 생성
# ---------------------------------------------------------

def create_bedrock_client():
    if AWS_PROFILE:
        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )
    else:
        session = boto3.Session(
            region_name=AWS_REGION,
        )

    return session.client("bedrock-runtime")

# ---------------------------------------------------------
# 6. LLM 응답에서 JSON 추출
# ---------------------------------------------------------

def extract_json(response_text: str) -> dict:
    cleaned_text = response_text.strip()

    try:
        return json.loads(cleaned_text)

    except json.JSONDecodeError:
        json_match = re.search(
            r"\{.*\}",
            cleaned_text,
            re.DOTALL,
        )

        if not json_match:
            raise ValueError(
                "LLM 응답에서 JSON 객체를 찾을 수 없음.\n"
                f"원본 응답: {response_text}"
            )

        return json.loads(json_match.group())

# ---------------------------------------------------------
# 7. 분류 결과 검증
# ---------------------------------------------------------

def validate_result(result: dict) -> dict:
    required_fields = {
        "category",
        "severity",
        "summary",
    }

    missing_fields = required_fields - result.keys()

    if missing_fields:
        raise ValueError(
            f"필수 필드가 누락되었음: {sorted(missing_fields)}"
        )

    category = str(result["category"]).strip().lower()
    severity = str(result["severity"]).strip().lower()
    summary = str(result["summary"]).strip()

    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"허용되지 않은 category 값임: {category}"
        )

    if severity not in ALLOWED_SEVERITIES:
        raise ValueError(
            f"허용되지 않은 severity 값임: {severity}"
        )

    if not summary:
        raise ValueError("summary 값이 비어 있음.")

    return {
        "category": category,
        "severity": severity,
        "summary": summary,
    }

# ---------------------------------------------------------
# 8. Bedrock으로 운영 메시지 분류
# ---------------------------------------------------------

def classify_message(client, message: str) -> dict:
    response = client.converse(
        modelId=BEDROCK_MODEL_ID,
        system=[
            {
                "text": SYSTEM_PROMPT,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": message,
                    }
                ],
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.0,
        },
    )

    content_blocks = response["output"]["message"]["content"]

    response_text = "".join(
        block.get("text", "")
        for block in content_blocks
        if "text" in block
    ).strip()

    if not response_text:
        raise ValueError(
            "Bedrock 응답에서 텍스트를 찾을 수 없음."
        )

    parsed_result = extract_json(response_text)

    return validate_result(parsed_result)

# ---------------------------------------------------------
# 9. Downstream Task 선택
# ---------------------------------------------------------

def route_task(result: dict) -> dict:
    severity = result["severity"]

    if severity == "high":
        return {
            "task_name": "create_incident",
            "description": "장애 기록 생성",
            "output_file": OUTPUT_DIR / "incident.jsonl",
        }

    if severity == "medium":
        return {
            "task_name": "create_warning",
            "description": "경고 기록 생성",
            "output_file": OUTPUT_DIR / "warning.jsonl",
        }

    return {
        "task_name": "store_normal",
        "description": "정상 기록 생성",
        "output_file": OUTPUT_DIR / "normal.jsonl",
    }

# ---------------------------------------------------------
# 10. 결과 파일 저장
# ---------------------------------------------------------

def save_result(
    message: str,
    result: dict,
    task: dict,
) -> Path:
    """
    severity에 따라 선택된 JSONL 파일에 결과를 추가 저장한다.
    """

    # output 디렉터리가 없으면 자동 생성
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 파일에 저장할 최종 레코드
    record = {
        "processed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "input_message": message,
        "analysis": result,
        "downstream_task": {
            "task_name": task["task_name"],
            "description": task["description"],
        },
    }

    # route_task()에서 선택한 저장 파일
    output_file = task["output_file"]

    # "a" 모드: 기존 내용을 지우지 않고 파일 끝에 추가
    with output_file.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
        )
        file.write("\n")

    return output_file

# ---------------------------------------------------------
# 11. 분석 결과 출력
# ---------------------------------------------------------

def print_result(
    result: dict,
    task: dict,
    saved_file: Path,
) -> None:
    print()
    print("=" * 60)
    print("운영 메시지 분석 결과")
    print("=" * 60)
    print(f"유형      : {result['category']}")
    print(f"심각도    : {result['severity']}")
    print(f"요약      : {result['summary']}")

    print()
    print("[Downstream Task]")
    print(f"작업 이름 : {task['task_name']}")
    print(f"작업 설명 : {task['description']}")
    print(f"저장 파일 : {saved_file}")

# ---------------------------------------------------------
# 12. 메인 함수
# ---------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("운영 메시지 분류와 작업 분기")
    print("=" * 60)

    message = input(
        "운영 메시지를 입력하세요: "
    ).strip()

    if not message:
        print("[입력 오류] 운영 메시지가 비어 있음.")
        return

    validate_environment()

    client = create_bedrock_client()

    print()
    print("[1] Amazon Bedrock에 분석 요청 중")

    result = classify_message(
        client,
        message,
    )

    print("[2] 운영 메시지 분류 완료")

    task = route_task(result)

    print("[3] Downstream Task 선택 완료")

    saved_file = save_result(
        message,
        result,
        task,
    )

    print("[4] 결과 파일 저장 완료")

    print_result(
        result,
        task,
        saved_file,
    )

# ---------------------------------------------------------
# 13. 프로그램 시작
# ---------------------------------------------------------

if __name__ == "__main__":
    try:
        main()

    except ProfileNotFound as error:
        print()
        print("[AWS 프로파일 오류]")
        print(error)

    except NoCredentialsError:
        print()
        print("[AWS 인증 오류]")
        print("사용할 수 있는 AWS 자격증명을 찾지 못했음.")

    except ClientError as error:
        error_info = error.response.get(
            "Error",
            {},
        )

        error_code = error_info.get(
            "Code",
            "Unknown",
        )

        error_message = error_info.get(
            "Message",
            str(error),
        )

        print()
        print("[AWS API 오류]")
        print(f"오류 코드: {error_code}")
        print(f"오류 내용: {error_message}")

    except (
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        print()
        print("[처리 오류]")
        print(error)

    except KeyboardInterrupt:
        print()
        print("사용자가 실행을 중단했음.")
