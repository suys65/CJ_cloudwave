import json
import os
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError

REGION = os.getenv("AWS_REGION", "ap-northeast-2")
DATABASE = os.getenv("ATHENA_DB", "kim_log_analysis")
WORKGROUP = os.getenv("ATHENA_WORKGROUP", "kim-log-analysis-wg")
OUTPUT_FILE = "athena_s3_error_report.json"

QUERY = """
SELECT
  parse_datetime(requestdatetime, 'dd/MMM/yyyy:HH:mm:ss Z') AS event_time,
  remoteip,
  requester,
  operation,
  key,
  httpstatus,
  errorcode
FROM s3_access_logs
WHERE TRY_CAST(httpstatus AS INTEGER) >= 400
ORDER BY event_time DESC
LIMIT 100
"""

session = boto3.Session(region_name=REGION)
athena = session.client("athena")

try:
    response = athena.start_query_execution(
        QueryString=QUERY,
        QueryExecutionContext={"Database": DATABASE},
        WorkGroup=WORKGROUP,
    )

    query_execution_id = response["QueryExecutionId"]
    print(f"QueryExecutionId:{query_execution_id}")

    while True:
        execution = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )

        status_info = execution["QueryExecution"]["Status"]
        state = status_info["State"]

        if state == "SUCCEEDED":
            break

        if state in {"FAILED", "CANCELLED"}:
            reason = status_info.get("StateChangeReason", "원인 정보 없음")
            raise RuntimeError(f"Athena 쿼리 실패:{state} -{reason}")

        print(f"쿼리 실행 중:{state}")
        time.sleep(2)

    result = athena.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=1000,
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2, default=str)

    print(f"Athena 분석 결과 저장 완료:{OUTPUT_FILE}")

except (BotoCoreError, ClientError, RuntimeError) as error:
    print(f"오류:{error}")
    raise SystemExit(1)
