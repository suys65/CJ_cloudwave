import re
from collections import Counter

status_counter = Counter()

try:
    with open("access.log", "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(r'" (\d{3}) ', line)
            if match:
                status_code = match.group(1)
                status_counter[status_code] += 1

    for status_code, count in sorted(status_counter.items()):
        print(f"{status_code}: {count}")

except FileNotFoundError:
    print("파일을 찾을 수 없음")
