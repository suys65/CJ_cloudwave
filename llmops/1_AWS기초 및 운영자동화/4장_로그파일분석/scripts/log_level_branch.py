with open("app.log", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        # 빈 줄은 처리하지 않고 건너뛴다.
        if not line:
            continue

        if "ERROR" in line:
            print(f"[ERROR] {line}")
        elif "WARN" in line:
            print(f"[WARN] {line}")
        elif "INFO" in line:
            print(f"[INFO] {line}")
        else:
            print(f"[OTHER] {line}")
