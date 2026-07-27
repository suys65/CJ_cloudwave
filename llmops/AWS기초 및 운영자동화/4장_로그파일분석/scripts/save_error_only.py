with open("app.log", "r", encoding="utf-8") as file, \
     open("error_only.log", "w", encoding="utf-8") as output_file:

    for line in file:
        # 줄 바꿈 기호를 포함한 한 줄 단위로 처리
        if "ERROR" in line:
            # "ERROR" 단어가 포함된 줄만 결과 파일에 기록
            output_file.write(line)
