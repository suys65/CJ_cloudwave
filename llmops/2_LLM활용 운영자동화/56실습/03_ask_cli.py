from bedrock_sql_generator import generate_sql_from_question
from athena_utils import run_athena_query

question = input("질문 입력: ").strip()

sql = generate_sql_from_question(question)
print("\n[생성된 SQL]")
print(sql)

df = run_athena_query(sql)
print("\n[조회 결과]")
print(df)
