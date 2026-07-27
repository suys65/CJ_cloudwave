with open("app.log", "r", encoding="utf-8") as file:
    for line in file:
        if "ERROR" in line:
            print(f"error line:{line.strip()}")
