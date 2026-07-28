import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_json_basics.py",
    "02_bedrock_json_output.py",
    "03_basic_pydantic.py",
    "04_literal_field.py",
    "05_nested_models.py",
    "06_bedrock_pydantic_validation.py",
    "07_validation_errors.py",
    "08_retry_validation.py",
    "09_save_results.py",
    "10_kubernetes_validation.py",
    "11_network_validation.py",
    "12_markdown_report.py",
    "13_integrated_pipeline.py",
]

def main() -> None:
    project_dir = Path(__file__).resolve().parent

    print(
        "실제 Amazon Bedrock 호출이 포함됩니다. "
        "모델 사용 비용에 유의합니다.\n"
    )

    for script in SCRIPTS:
        print("=" * 72)
        print("실행:", script)
        print("=" * 72)

        completed = subprocess.run(
            [sys.executable, script],
            cwd=project_dir,
            check=False,
        )

        if completed.returncode != 0:
            print(f"\n[중단]{script} 실행에 실패했습니다.")
            raise SystemExit(completed.returncode)

    print("\n모든 실습 파일 실행을 완료했습니다.")

if __name__ == "__main__":
    main()
