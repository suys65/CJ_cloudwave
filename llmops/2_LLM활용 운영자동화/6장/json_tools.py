import json
from typing import Any

def remove_code_fence(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json") :]

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```") :]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return cleaned.strip()

def extract_json_object(text: str) -> str:
    cleaned = remove_code_fence(text)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "응답에서 JSON 객체를 찾을 수 없습니다.\n"
                f"원본 응답:\n{cleaned}"
            )

        candidate = cleaned[start : end + 1]
        json.loads(candidate)
        return candidate

    if not isinstance(parsed, dict):
        raise ValueError("최상위 JSON 값은 객체여야 합니다.")

    return cleaned

def to_pretty_json(data: Any) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )
