"""End-to-end verification for the Week 1 temporal retrieval pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from loader import load_dataset
from retriever import retrieve

DATASET_PATH = PROJECT_ROOT / "data" / "sample_dataset.json"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "week1_verification_output.json"


def main() -> None:
    subprocess.run([sys.executable, "-m", "pytest"], cwd=PROJECT_ROOT, check=True)

    first_pass = [retrieve(record) for record in load_dataset(DATASET_PATH)]
    second_pass = [retrieve(record) for record in load_dataset(DATASET_PATH)]

    if first_pass != second_pass:
        raise AssertionError("Pipeline output is not deterministic for repeated runs.")

    valid_count = sum(len(item["valid_news"]) for item in first_pass)
    invalid_count = sum(len(item["invalid_future_news"]) for item in first_pass)
    warning_count = sum(len(item["warnings"]) for item in first_pass)

    if valid_count == 0 or invalid_count == 0:
        raise AssertionError("Expected both valid and invalid temporal results in the sample run.")
    if warning_count == 0:
        raise AssertionError("Expected warnings to be produced for malformed or invalid records.")

    OUTPUT_PATH.write_text(json.dumps({
        "valid_news_items": valid_count,
        "invalid_future_news_items": invalid_count,
        "warning_items": warning_count,
        "records": first_pass,
    }, indent=2), encoding="utf-8")

    print("Verified Week 1 pipeline:")
    print(f"  valid_news items: {valid_count}")
    print(f"  invalid_future_news items: {invalid_count}")
    print(f"  total warnings: {warning_count}")
    print(f"  output written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
