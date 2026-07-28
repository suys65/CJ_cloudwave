import os
import re
from dotenv import load_dotenv
import boto3

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "nlp_s3_analytics_db")
ATHENA_TABLE = os.getenv("ATHENA_TABLE", "ecommerce_sales")

if not BEDROCK_MODEL_ID:
    raise ValueError(".env 파일에 BEDROCK_MODEL_ID 값을 설정해야 한다.")

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

TABLE_SCHEMA = f"""
데이터베이스: {ATHENA_DATABASE}
테이블: {ATHENA_TABLE}

컬럼:
- order_id string: 주문 ID
- order_date date: 주문일
- customer_id string: 고객 ID
- region string: 지역
- category string: 상품 카테고리
- product_name string: 상품명
- channel string: 판매 채널. web, mobile, store
- quantity int: 주문 수량
- unit_price int: 상품 단가
- discount_amount int: 할인 금액
- payment_method string: 결제 방식
- is_returned boolean: 반품 여부

매출 계산식:
(quantity * unit_price - discount_amount)

주의:
- Athena SQL 문법을 사용한다.
- 비율이나 반품률을 계산할 때는 정수 나눗셈을 피하기 위해 100.0을 곱하거나 CAST(... AS double)을 사용한다.
- SELECT 문만 생성한다.
- INSERT, UPDATE, DELETE, DROP, ALTER, CREATE 문은 절대 생성하지 않는다.
- 결과 행 수가 많을 수 있으면 LIMIT 100을 추가한다.
- SQL 외의 설명은 출력하지 않는다.
"""

def extract_sql(text: str) -> str:
    code_block = re.search(r"```sql\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if code_block:
        return code_block.group(1).strip()

    generic_block = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if generic_block:
        return generic_block.group(1).strip()

    return text.strip()

def validate_sql(sql: str) -> None:
    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        raise ValueError("SELECT 문만 실행할 수 있다.")

    forbidden_keywords = [
        "insert", "update", "delete", "drop", "alter", "create",
        "truncate", "merge", "grant", "revoke", "unload"
    ]

    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", normalized):
            raise ValueError(f"허용되지 않은 SQL 키워드가 포함되어 있다: {keyword}")

    if ATHENA_TABLE.lower() not in normalized:
        raise ValueError(f"허용된 테이블만 조회할 수 있다: {ATHENA_TABLE}")

def generate_sql_from_question(question: str) -> str:
    system_text = f"""
너는 AWS Athena SQL 생성기이다.
사용자의 한국어 질문을 보고 Athena에서 실행 가능한 SQL 하나만 생성한다.

{TABLE_SCHEMA}
"""

    user_text = f"""
사용자 질문:
{question}

SQL만 출력한다.
"""

    response = bedrock.converse(
        modelId=BEDROCK_MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": user_text}]
            }
        ],
        system=[
            {"text": system_text}
        ],
        inferenceConfig={
            "maxTokens": 800,
            "temperature": 0.0
        }
    )

    output_text = response["output"]["message"]["content"][0]["text"]
    sql = extract_sql(output_text)
    validate_sql(sql)

    return sql
