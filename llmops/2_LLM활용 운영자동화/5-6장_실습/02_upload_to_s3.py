import os
from pathlib import Path
from dotenv import load_dotenv
import boto3

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
S3_BUCKET = os.getenv("S3_BUCKET")
DATA_PREFIX = os.getenv("DATA_PREFIX", "datasets/ecommerce_sales/")

LOCAL_FILE = Path("data/ecommerce_sales.csv")

if not S3_BUCKET:
    raise ValueError(".env 파일에 S3_BUCKET 값을 설정해야 한다.")

if not LOCAL_FILE.exists():
    raise FileNotFoundError("data/ecommerce_sales.csv 파일이 없다. 먼저 01_generate_sample_data.py를 실행한다.")

s3 = boto3.client("s3", region_name=AWS_REGION)

key = f"{DATA_PREFIX.rstrip('/')}/ecommerce_sales.csv"
s3.upload_file(str(LOCAL_FILE), S3_BUCKET, key)

print("S3 업로드 완료")
print(f"s3://{S3_BUCKET}/{key}")
