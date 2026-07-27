import json

with open("app_json_invalid.log", "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            # JSON 파싱 시도
            log = json.loads(line)
        except json.JSONDecodeError:
            # 형식이 잘못된 경우 에러 메시지 출력 후 다음 줄로 이동
            print(f"{line_number}번째 줄은 JSON 형식이 아니어서 건너뜀")
            continue

        # level이 ERROR인 경우에만 안전하게(get 메서드 사용) 필드 값 출력
        if log.get("level") == "ERROR":
            print(f"time={log.get('time')}, message={log.get('message')}")
