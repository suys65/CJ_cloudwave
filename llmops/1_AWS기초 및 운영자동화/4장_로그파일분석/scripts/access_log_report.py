import re
import argparse
from collections import Counter

def parse_access_log_line(line):
    """
    access.log 한 줄에서 IP, 요청 경로, 상태코드를 추출한다.
    정상적으로 추출하면 딕셔너리를 반환한다.
    형식이 맞지 않으면 None을 반환한다.
    """

    pattern = r'^([^ ]+) .* "\w+ ([^ ]+) HTTP/[^"]+" (\d{3}) '
    match = re.search(pattern, line)

    if not match:
        return None

    return {
        "ip": match.group(1),
        "path": match.group(2),
        "status_code": match.group(3)
    }

def analyze_access_log(filename):
    """
    access.log 파일 전체를 읽고 주요 항목을 집계한다.
    """

    total_count = 0
    status_counter = Counter()
    ip_counter = Counter()
    path_counter = Counter()
    client_error_count = 0
    server_error_count = 0
    invalid_line_count = 0

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            parsed = parse_access_log_line(line)

            if parsed is None:
                invalid_line_count += 1
                continue

            total_count += 1

            ip = parsed["ip"]
            path = parsed["path"]
            status_code = parsed["status_code"]

            status_counter[status_code] += 1
            ip_counter[ip] += 1
            path_counter[path] += 1

            if status_code.startswith("4"):
                client_error_count += 1
            elif status_code.startswith("5"):
                server_error_count += 1

    return {
        "total_count": total_count,
        "status_counter": status_counter,
        "ip_counter": ip_counter,
        "path_counter": path_counter,
        "client_error_count": client_error_count,
        "server_error_count": server_error_count,
        "invalid_line_count": invalid_line_count
    }

def print_report(result):
    """
    분석 결과를 보기 좋은 형식으로 출력한다.
    """

    print("===== Access Log Summary =====")
    print(f"전체 요청 수: {result['total_count']}")
    print(f"4xx 요청 수: {result['client_error_count']}")
    print(f"5xx 요청 수: {result['server_error_count']}")
    print(f"형식 오류 줄 수: {result['invalid_line_count']}")
    print()

    print("[상태코드별 요청 수]")
    for status_code, count in result["status_counter"].items():
        print(f"{status_code}: {count}")

    print()
    print("[IP별 요청 수]")
    for ip, count in result["ip_counter"].items():
        print(f"{ip}: {count}")

    print()
    print("[요청 경로별 요청 수]")
    for path, count in result["path_counter"].items():
        print(f"{path}: {count}")

def main():
    parser = argparse.ArgumentParser(
        description="access.log 파일을 분석해서 요약 리포트를 출력한다."
    )

    parser.add_argument(
        "--file",
        required=True,
        help="분석할 access.log 파일 경로"
    )

    args = parser.parse_args()

    try:
        result = analyze_access_log(args.file)
        print_report(result)

    except FileNotFoundError:
        print(f"파일을 찾을 수 없음: {args.file}")

    except Exception as e:
        print("로그 분석 중 오류 발생")
        print(f"오류 내용: {e}")

if __name__ == "__main__":
    main()
