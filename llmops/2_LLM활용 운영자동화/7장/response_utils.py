from typing import Any

def extract_text(
    response: dict[str, Any],
) -> str:
    """
    Bedrock Converse 응답에서 모든 text 블록을 결합한다.
    """
    content = (
        response
        .get("output", {})
        .get("message", {})
        .get("content", [])
    )

    text_blocks = [
        block["text"]
        for block in content
        if isinstance(block, dict)
        and isinstance(block.get("text"), str)
    ]

    return "\n".join(text_blocks).strip()
