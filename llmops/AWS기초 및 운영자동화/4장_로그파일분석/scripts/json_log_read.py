import json

with open("app_json.log", "r", encoding="utf-8") as file:
    for line in file:
        log = json.loads(line)
        print(log)
