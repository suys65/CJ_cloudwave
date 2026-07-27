import json

with open("app_json.log", "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            log = json.loads(line)
        except json.JSONDecodeError:
            print(f"{line_number}번째 줄은 JSON 형식이 아니어서 건너뜀")
            continue

        if log.get("level") == "ERROR":
            print(f"time={log.get('time')}, message={log.get('message')}")
