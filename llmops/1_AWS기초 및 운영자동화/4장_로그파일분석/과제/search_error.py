try:
    with open("app.log", "r", encoding="utf-8") as file:
        for line in file:
            if "ERROR" in line:
                print(line.strip())

except FileNotFoundError:
    print("파일을 찾을 수 없음")
