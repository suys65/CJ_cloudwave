import re

with open("access.log", "r", encoding="utf-8") as file:
    for line in file:
        match = re.search(r'" (\d{3}) ', line)

        if match:
            status_code = match.group(1)

        if status_code.startswith("4") or status_code.startswith("5"):
            print(line.strip())
