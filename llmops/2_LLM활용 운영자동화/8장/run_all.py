"""01~11 실습 스크립트를 순서대로 실행한다."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_prompt_injection_baseline.py",
    "02_apply_guardrail_input.py",
    "03_converse_with_guardrail.py",
    "04_sensitive_information.py",
    "05_denied_topic_word_filter.py",
    "06_selective_guard_content.py",
    "07_output_policy_validation.py",
    "08_identity_least_privilege.py",
    "09_guardrail_audit.py",
    "10_secure_pipeline.py",
    "11_security_test_suite.py",
]

def main() -> None:
    base_dir = Path(__file__).resolve().parent
    failures: list[str] = []

    for script in SCRIPTS:
        print("\n" + "#" * 76)
        print(f"# 실행: {script}")
        print("#" * 76)

        result = subprocess.run(
            [sys.executable, str(base_dir / script)],
            cwd=str(base_dir),
        )

        if result.returncode != 0:
            failures.append(script)
            print(f"[실패] {script} (returncode={result.returncode})")

    print("\n" + "=" * 76)
    print("전체 실행 요약")
    print("=" * 76)
    print("실패:", failures if failures else "없음")

if __name__ == "__main__":
    main()
