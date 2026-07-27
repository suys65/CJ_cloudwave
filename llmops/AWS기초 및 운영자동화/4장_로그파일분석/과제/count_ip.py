from collections import Counter

ip_counter = Counter()

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        if not line:
            continue

        parts = line.split()
        ip = parts[0]
        ip_counter[ip] += 1

for ip, count in ip_counter.items():
    print(f"{ip}: {count}")
