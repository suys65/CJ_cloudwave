from typing import Any

def extract_usage(
    response: dict[str, Any],
    elapsed_time: float,
) -> dict[str, int | float]:
    """
    Bedrock Converse 응답에서 토큰 사용량과 응답시간을 추출한다.
    """
    usage = response.get("usage", {})

    return {
        "input_tokens": usage.get("inputTokens", 0),
        "output_tokens": usage.get("outputTokens", 0),
        "total_tokens": usage.get("totalTokens", 0),
        "elapsed_seconds": round(elapsed_time, 3),
    }
