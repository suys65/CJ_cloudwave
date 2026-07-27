import json

with open("app_json.log", "r", encoding="utf-8") as file:
    for line in file:
        # JSON 형식의 문자열을 파이썬 딕셔너리로 변환
        log = json.loads(line)

        # 로그 레벨이 ERROR인 경우에만 특정 필드 출력
        if log["level"] == "ERROR":
            print(f"time={log['time']}, message={log['message']}")
