hour_count = {}

with open("app.log", "r", encoding="utf-8") as file:
    for line in file:
        # 시간대 키 추출 (예: 2026-05-04 12)
        hour_key = line[:13]

        if hour_key not in hour_count:
            hour_count[hour_key] = 0

        # 1을 더하는 로직은 if문 밖에 있어야 누적됨
        hour_count[hour_key] += 1

# 모든 로그 처리가 끝난 후 한 번만 출력
for hour, count in hour_count.items():
    print(f"{hour}: {count}")
