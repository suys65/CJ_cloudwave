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

prompt = """
다음 Kubernetes 장애를 분석한다.

- Status: CrashLoopBackOff
- Last State: OOMKilled
- Exit Code: 137
- Memory Limit: 512Mi
- Restart Count: 12

출력:
- 장애 요약
- 확인된 사실
- 가능한 원인 최대 3개
- 확인 명령어
- 승인 필요 작업
"""

results = []

for max_tokens in [200, 500, 1000]:
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
            "maxTokens": max_tokens,
        },
    )

    output = extract_text(response)

    stop_reason = response.get(
        "stopReason",
        "unknown",
    )

    results.append(
        {
            "max_tokens": max_tokens,
            **usage,
            "stop_reason": stop_reason,
            "output": output,
        }
    )

    print("\n" + "=" * 80)
    print(f"maxTokens={max_tokens}")
    print("=" * 80)
    print(output)
    print("출력 토큰:", usage["output_tokens"])
    print("총 토큰:", usage["total_tokens"])
    print("응답시간:", usage["elapsed_seconds"], "초")
    print("종료 이유:", stop_reason)

dataframe = pd.DataFrame(results)

print(
    dataframe[
        [
            "max_tokens",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "elapsed_seconds",
            "stop_reason",
        ]
    ]
)

dataframe.to_csv(
    "max_tokens_comparison.csv",
    index=False,
    encoding="utf-8-sig",
)
