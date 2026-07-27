import argparse

parser = argparse.ArgumentParser(description="로그 파일에서 특정 키워드가 포함된 줄을 검색한다.")
parser.add_argument("--file", required=True, help="분석할 로그 파일 경로")
parser.add_argument("--keyword", required=True, help="검색할 키워드")

args = parser.parse_args()

try:
    with open(args.file, "r", encoding="utf-8") as file:
        for line in file:
            if args.keyword in line:
                print(line.strip())

except FileNotFoundError:
    print(f"파일을 찾을 수 없음: {args.file}")

except Exception as e:
    print("로그 검색 중 오류 발생")
    print(f"오류 내용: {e}")
