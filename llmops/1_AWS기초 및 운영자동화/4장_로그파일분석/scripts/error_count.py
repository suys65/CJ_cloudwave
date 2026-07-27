error_count = 0

with open("app.log", "r", encoding="utf-8") as file:
    for line in file:
        if "ERROR" in line:
            error_count += 1

    print(f"error count:{error_count}")
