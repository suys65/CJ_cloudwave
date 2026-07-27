import re

line = '127.0.0.1 - - [20/Apr/2026:10:01:15 +0900] "GET /api/items HTTP/1.1" 500 1234'

match = re.search(r'" (\d{3}) ', line)

if match:
    print(match.group())
    print(match.group(1))
