import json

def extract_json_object(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json") :]

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```") :]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "응답에서 JSON 객체를 찾을 수 없습니다."
            )

        candidate = cleaned[start : end + 1]
        parsed = json.loads(candidate)
        cleaned = candidate

    if not isinstance(parsed, dict):
        raise ValueError(
            "최상위 JSON 값은 객체여야 합니다."
        )

    return cleaned
