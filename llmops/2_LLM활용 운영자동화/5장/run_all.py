"""01~10 실습 스크립트를 순서대로 실행한다."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_zero_shot.py",
    "02_few_shot.py",
    "03_boundary_cases.py",
    "04_step_by_step_analysis.py",
    "05_evidence_based_output.py",
    "06_safe_actions.py",
    "07_draft_and_review.py",
    "08_multi_call_pipeline.py",
    "09_batch_evaluation.py",
    "10_integrated_ticket.py",
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

    if failures:
        print("실패한 스크립트:")
        for script in failures:
            print("-", script)
    else:
        print("모든 스크립트가 정상 종료되었습니다.")

if __name__ == "__main__":
    main()
