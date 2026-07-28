from pathlib import Path

import pandas as pd

source_files = [
    Path("preprocessing_comparison.csv"),
    Path("max_tokens_comparison.csv"),
    Path("model_comparison.csv"),
]

dataframes = []

for source_file in source_files:
    if not source_file.exists():
        print(
            f"파일 없음, 건너뜀: "
            f"{source_file}"
        )
        continue

    dataframe = pd.read_csv(source_file)
    dataframe["source_file"] = source_file.name
    dataframes.append(dataframe)

if not dataframes:
    raise FileNotFoundError(
        "통합할 측정 결과 CSV가 없다."
    )

usage_report = pd.concat(
    dataframes,
    ignore_index=True,
    sort=False,
)

required_columns = [
    "source_file",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "elapsed_seconds",
]

for column in required_columns:
    if column not in usage_report.columns:
        usage_report[column] = None

output_path = Path("usage_report.csv")

usage_report.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig",
)

print(f"저장 완료:{output_path}")

print(
    usage_report[
        required_columns
    ]
)
