import json

VALID_JSON = """
{
  "severity": "high",
  "service": "nginx",
  "approval_required": false
}
"""

INVALID_JSONS = {
    "작은따옴표": "{'severity': 'high'}",
    "마지막 쉼표": """
{
  "severity": "high",
}
""",
    "설명 문장 포함": """
분석 결과입니다.
{
  "severity": "high"
}
""",
    "코드 블록 포함": """
```json
{
  "severity": "high"
}
```
""",
}

def main() -> None:
    print("=" * 60)
    print("정상 JSON 파싱")
    print("=" * 60)

    parsed = json.loads(VALID_JSON)

    print(parsed)
    print("severity:", parsed["severity"])
    print("service:", parsed["service"])

    print("\n" + "=" * 60)
    print("잘못된 JSON 파싱")
    print("=" * 60)

    for name, text in INVALID_JSONS.items():
        try:
            json.loads(text)
            print(f"[{name}] 파싱 성공")
        except json.JSONDecodeError as error:
            print(f"[{name}] 파싱 실패")
            print("오류 위치:", error.pos)
            print("오류 내용:", error.msg)
            print("-" * 40)

if __name__ == "__main__":
    main()
