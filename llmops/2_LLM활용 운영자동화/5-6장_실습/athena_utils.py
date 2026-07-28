import os
import time
from io import StringIO
from dotenv import load_dotenv
import boto3
import pandas as pd

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
S3_BUCKET = os.getenv("S3_BUCKET")
ATHENA_OUTPUT_PREFIX = os.getenv("ATHENA_OUTPUT_PREFIX", "athena-results/")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "nlp_s3_analytics_db")

athena = boto3.client("athena", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

def run_athena_query(sql: str) -> pd.DataFrame:
    if not S3_BUCKET:
        raise ValueError(".env 파일에 S3_BUCKET 값을 설정해야 한다.")

    output_location = f"s3://{S3_BUCKET}/{ATHENA_OUTPUT_PREFIX.strip('/')}/"

    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": output_location}
    )

    query_execution_id = response["QueryExecutionId"]

    while True:
        status_response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        state = status_response["QueryExecution"]["Status"]["State"]

        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break

        time.sleep(1)

    if state != "SUCCEEDED":
        reason = status_response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
        raise RuntimeError(f"Athena 쿼리 실패: {state}, 원인: {reason}")

    result_key = f"{ATHENA_OUTPUT_PREFIX.strip('/')}/{query_execution_id}.csv"
    obj = s3.get_object(Bucket=S3_BUCKET, Key=result_key)
    csv_text = obj["Body"].read().decode("utf-8")

    return pd.read_csv(StringIO(csv_text))
