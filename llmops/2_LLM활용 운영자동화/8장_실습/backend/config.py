import os
from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE", "프로필")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")
PROJECT_NAME = os.getenv("PROJECT_NAME", "llmops")
STUDENT_INITIAL = os.getenv("STUDENT_INITIAL", "이니셜")

NAME_PREFIX = f"{STUDENT_INITIAL}-{PROJECT_NAME}"
ASG_NAME = f"{NAME_PREFIX}-asg"
ALARM_PREFIX = NAME_PREFIX
LOG_GROUP_NAME = f"/training/{NAME_PREFIX}/application"
