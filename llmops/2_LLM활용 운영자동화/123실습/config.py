import os

from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")
STUDENT_INITIAL = os.getenv("STUDENT_INITIAL", "student")

if not BEDROCK_MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID가 설정되지 않았다.")
