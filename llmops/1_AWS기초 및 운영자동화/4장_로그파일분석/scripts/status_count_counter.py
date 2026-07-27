import re
from collections import Counter

status_counter = Counter()

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        match = re.search(r'" (\d{3}) ', line)
        if match:
            status_code = match.group(1)
            # Counter는 키가 없어도 자동으로 0으로 처리하므로 바로 더하면 됩니다.
            status_counter[status_code] += 1

print("상태코드별 개수")

for status_code, count in sorted(status_counter.items()):
    print(f"{status_code}: {count}")
