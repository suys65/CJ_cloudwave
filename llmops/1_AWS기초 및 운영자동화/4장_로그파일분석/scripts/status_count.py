import re

status_count = {}

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        match = re.search(r'" (\d{3}) ', line)

        if match:
            status_code = match.group(1)

            if status_code not in status_count:
                status_count[status_code] = 0

            status_count[status_code] += 1

    print(status_count)
