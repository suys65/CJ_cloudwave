import re

line = "status=500"

match = re.search(r"\d+", line)

if match:
    print(match.group())
