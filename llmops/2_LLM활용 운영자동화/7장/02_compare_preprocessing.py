import os

import pandas as pd
from dotenv import load_dotenv

from bedrock_client import create_bedrock_runtime
from measured_converse import converse_with_usage
from response_utils import extract_text

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

if not MODEL_ID:
    raise ValueError(
        "BEDROCK_MODEL_ID가 설정되지 않았다."
    )

client = create_bedrock_runtime()

raw_log = """
2026-07-15T10:21:31.011Z ERROR request_id=001
service=payment-api status=500 message="database timeout"

2026-07-15T10:21:32.012Z ERROR request_id=002
service=payment-api status=500 message="database timeout"

2026-07-15T10:21:33.013Z ERROR request_id=003
service=payment-api status=500 message="database timeout"

2026-07-15T10:21:34.014Z WARN request_id=004
service=payment-api pool_usage=95
message="connection pool usage high"
"""

processed_log = """
service: payment-api
period: 10:21:31~10:21:34
events:
- database timeout, 3회
- connection pool usage high, 1회
- pool_usage: 95%
"""

results = []

for label, log_text in [
    ("원본", raw_log),
    ("전처리", processed_log),
]:
    prompt = f"""
다음 운영 로그를 분석한다.

<log>
{log_text}
</log>

다음 내용을 작성한다.
- 장애 요약
- 확인된 사실
- 가능한 원인 최대 3개
- 추가 확인 항목
"""

    response, usage = converse_with_usage(
        client=client,
        model_id=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ],
            }
        ],
        inference_config={
            "temperature": 0.1,
            "maxTokens": 500,
        },
    )

    output = extract_text(response)

    results.append(
        {
            "label": label,
            **usage,
            "output": output,
        }
    )

    print("\n" + "=" * 80)
    print(label)
    print("=" * 80)
    print(output)
    print("입력 토큰:", usage["input_tokens"])
    print("출력 토큰:", usage["output_tokens"])
    print("총 토큰:", usage["total_tokens"])
    print("응답시간:", usage["elapsed_seconds"], "초")

dataframe = pd.DataFrame(results)

print("\n[측정 결과]")
print(
    dataframe[
        [
            "label",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "elapsed_seconds",
        ]
    ]
)

dataframe.to_csv(
    "preprocessing_comparison.csv",
    index=False,
    encoding="utf-8-sig",
)

raw_tokens = results[0]["input_tokens"]
processed_tokens = results[1]["input_tokens"]

if raw_tokens > 0:
    reduction_rate = (
        (raw_tokens - processed_tokens)
        / raw_tokens
        * 100
    )

    print(
        f"\n입력 토큰 감소율: "
        f"{reduction_rate:.2f}%"
    )
