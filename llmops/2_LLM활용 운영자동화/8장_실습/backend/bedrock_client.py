from botocore.exceptions import BotoCoreError, ClientError

from backend.aws_session import bedrock_client
from backend.config import BEDROCK_MODEL_ID

def converse(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1500,
) -> str:
    if not BEDROCK_MODEL_ID:
        raise RuntimeError("BEDROCK_MODEL_ID가 설정되지 않았습니다.")

    try:
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": system_prompt}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_prompt}],
                }
            ],
            inferenceConfig={
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
        )
    except (BotoCoreError, ClientError) as error:
        raise RuntimeError(f"Bedrock 호출 실패:{error}") from error

    output = response["output"]["message"]["content"]
    return "".join(item.get("text", "") for item in output)
