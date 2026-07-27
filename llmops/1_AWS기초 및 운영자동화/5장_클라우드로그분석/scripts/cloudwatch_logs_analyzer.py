import json
import os
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError

REGION = os.getenv("AWS_REGION", "ap-northeast-2")
LOG_GROUP = os.getenv("LOG_GROUP", "/training/kim/application")
OUTPUT_FILE = "cloudwatch_error_report.json"

session = boto3.Session(region_name=REGION)
client = session.client("logs")

# Logs Insights StartQuery는 초 단위 Unix timestamp를 사용한다.
end_time = int(time.time())
start_time = end_time - 3600

query = """
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
"""

try:
    response = client.start_query(
        logGroupName=LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        queryString=query,
    )

    query_id = response["queryId"]
    print(f"Query ID:{query_id}")

    while True:
        result = client.get_query_results(queryId=query_id)
        status = result["status"]

        if status == "Complete":
            break

        if status in {"Failed", "Cancelled", "Timeout"}:
            raise RuntimeError(f"Logs Insights 쿼리 실패:{status}")

        print(f"쿼리 실행 중:{status}")
        time.sleep(2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"분석 결과 저장 완료:{OUTPUT_FILE}")

except (BotoCoreError, ClientError, RuntimeError) as error:
    print(f"오류:{error}")
    raise SystemExit(1)
