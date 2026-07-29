import sys
import time
import requests

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "사용법: python generate_error_requests.py <ALB_URL>"
        )

    base_url = sys.argv[1].rstrip("/")
    error_url = f"{base_url}/error"

    for index in range(30):
        try:
            response = requests.get(error_url, timeout=5)
            print(index + 1, response.status_code, response.text)
        except requests.RequestException as error:
            print(index + 1, "REQUEST_ERROR", error)

        time.sleep(1)

if __name__ == "__main__":
    main()
