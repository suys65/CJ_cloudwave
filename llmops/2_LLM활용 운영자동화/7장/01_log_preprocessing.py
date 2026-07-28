from collections import Counter

logs = [
    "ERROR database timeout",
    "ERROR database timeout",
    "INFO request completed",
    "ERROR database timeout",
    "WARN connection pool usage 95%",
    "INFO request completed",
]

counter = Counter(logs)

for message, count in counter.most_common():
    print(f"{message} ×{count}")

print("\n[로그 레벨 필터링]")

allowed_levels = (
    "WARN",
    "ERROR",
    "CRITICAL",
)

filtered_logs = [
    log
    for log in logs
    if log.startswith(allowed_levels)
]

for log in filtered_logs:
    print(log)
