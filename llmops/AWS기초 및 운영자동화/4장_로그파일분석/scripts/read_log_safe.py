try:
    with open("missing.log", "r", encoding="utf-8") as file:
        for line in file:
            print(line.strip())

except FileNotFoundError:
    print("파일을 찾을 수 없음")

except Exception as e:
    print("로그 처리 중 오류 발생")
    print(f"오류 내용: {e}")
