import re
from collections import Counter

path_counter = Counter()

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        # 요청 경로(Path)를 추출하기 위한 정규표현식 매칭
        match = re.search(r'"[A-Z]+ ([^ ]+) HTTP/', line)

        if match:
            path = match.group(1)
            path_counter[path] += 1

print("요청 경로별 개수")

for path, count in path_counter.items():
    print(f"{path}: {count}")
