import os

import pandas as pd
from dotenv import load_dotenv

from bedrock_client import create_bedrock_runtime
from measured_converse import converse_with_usage
from response_utils import extract_text

load_dotenv()

model_ids = {
    "small": os.getenv(
        "BEDROCK_MODEL_ID_SMALL"
    ),
    "large": os.getenv(
        "BEDROCK_MODEL_ID_LARGE"
    ),
}

if not all(model_ids.values()):
    raise ValueError(
        "소형 모델과 대형 모델 ID를 모두 설정한다."
    )

client = create_bedrock_runtime()

prompt = """
다음 운영 데이터를 분석한다.

- 10:00 신규 버전 배포
- 10:05 CPU 사용률 95%
- 10:06 HTTP 500 오류율 18%
- 10:08 payment-api Pod 재시작 5회
- Last State: OOMKilled
- Memory Limit: 512Mi

출력:
1. 장애 요약
2. 확인된 사실
3. 가능한 원인 최대 3개
4. 각 원인의 근거
5. 확인 명령어
"""

results = []

for model_type, model_id in model_ids.items():
    response, usage = converse_with_usage(
        client=client,
        model_id=model_id,
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
            "maxTokens": 900,
        },
    )

    output = extract_text(response)

    results.append(
        {
            "model_type": model_type,
            "model_id": model_id,
            **usage,
            "stop_reason": response.get(
                "stopReason",
                "unknown",
            ),
            "output": output,
        }
    )

dataframe = pd.DataFrame(results)

print(
    dataframe[
        [
            "model_type",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "elapsed_seconds",
            "stop_reason",
        ]
    ]
)

dataframe.to_csv(
    "model_comparison.csv",
    index=False,
    encoding="utf-8-sig",
)
