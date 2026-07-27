from collections import Counter

ip_counter = Counter()

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        parts = line.split()

        if parts:
            ip = parts[0]
            ip_counter[ip] += 1

print("IP별 요청 수")

for ip, count in ip_counter.items():
    print(f"{ip}: {count}")
