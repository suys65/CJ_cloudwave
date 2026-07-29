import shlex

from security_models import SecureAnalysis

ALLOWED_SERVICES = {
    "aws",
    "kubectl",
    "systemctl",
    "journalctl",
    "ss",
}

ALLOWED_AWS_OPERATIONS = {
    "describe-instances",
    "describe-instance-status",
    "describe-volumes",
    "describe-security-groups",
    "get-caller-identity",
    "get-log-events",
    "filter-log-events",
    "list-buckets",
    "list-objects-v2",
}

FORBIDDEN_TOKENS = {
    "create",
    "delete",
    "terminate",
    "stop",
    "reboot",
    "modify",
    "update",
    "put",
    "attach",
    "detach",
    "rollout",
    "restart",
    "rm",
    "shutdown",
    "poweroff",
}

def tokenize(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()

def validate_command(command: str) -> list[str]:
    errors: list[str] = []
    tokens = tokenize(command)

    if not tokens:
        return ["명령어가 비어 있습니다."]

    executable = tokens[0].lower()

    if executable == "sudo" and len(tokens) > 1:
        executable = tokens[1].lower()

    if executable not in ALLOWED_SERVICES:
        errors.append(
            f"허용되지 않은 실행 파일:{executable}"
        )

    lowered_tokens = {
        token.lower().lstrip("-")
        for token in tokens
    }

    matched_forbidden = (
        lowered_tokens & FORBIDDEN_TOKENS
    )

    if matched_forbidden:
        errors.append(
            "금지 토큰 포함: "
            + ", ".join(
                sorted(matched_forbidden)
            )
        )

    if executable == "aws":
        if len(tokens) < 3:
            errors.append(
                "AWS CLI 서비스와 작업이 부족합니다."
            )
        else:
            operation = tokens[2].lower()

            if operation not in ALLOWED_AWS_OPERATIONS:
                errors.append(
                    f"허용되지 않은 AWS 작업:{operation}"
                )

    return errors

def validate_analysis_policy(
    analysis: SecureAnalysis,
) -> list[str]:
    errors: list[str] = []

    for index, item in enumerate(
        analysis.commands,
        start=1,
    ):
        command_errors = validate_command(
            item.command
        )

        for error in command_errors:
            errors.append(
                f"{index}번 명령:{error}"
            )

        if item.action_type != "read_only":
            errors.append(
                f"{index}번 명령의 action_type은 "
                "read_only여야 합니다."
            )

        if item.approval_required is not False:
            errors.append(
                f"{index}번 조회 명령의 "
                "approval_required는 false여야 합니다."
            )

    return errors
