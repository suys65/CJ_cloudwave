with open("app.log", "r", encoding="utf-8") as file:
    for line in file:
        print(line.strip())
