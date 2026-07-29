import re
import time
from collections import Counter

from backend.aws_session import logs_client
from backend.config import LOG_GROUP_NAME

def get_recent_logs(
    minutes: int = 10,
    filter_pattern: str = "",
    limit: int = 100,
) -> list[dict]:
    end_time_ms = int(time.time() * 1000)
    start_time_ms = end_time_ms - (minutes * 60 * 1000)

    params = {
        "logGroupName": LOG_GROUP_NAME,
        "startTime": start_time_ms,
        "endTime": end_time_ms,
        "limit": limit,
        "interleaved": True,
    }

    if filter_pattern:
        params["filterPattern"] = filter_pattern

    response = logs_client.filter_log_events(**params)

    return [
        {
            "timestamp": event["timestamp"],
            "log_stream_name": event["logStreamName"],
            "message": event["message"].strip(),
        }
        for event in response.get("events", [])
    ]

def mask_sensitive_data(message: str) -> str:
    message = re.sub(
        r"AKIA[0-9A-Z]{16}",
        "[MASKED_AWS_ACCESS_KEY]",
        message,
    )
    message = re.sub(
        r"(?i)(password|passwd|token|secret)=\S+",
        r"\1=[MASKED]",
        message,
    )
    return message

def summarize_duplicate_logs(logs: list[dict]) -> list[dict]:
    counter = Counter(
        mask_sensitive_data(log["message"]) for log in logs
    )

    return [
        {"message": message, "count": count}
        for message, count in counter.most_common(20)
    ]
