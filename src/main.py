"""Simple entry point for running the Week 1 loader and retriever pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from loader import DEFAULT_DATASET, load_dataset
from retriever import retrieve


def main() -> None:
    dataset_path = DEFAULT_DATASET
    results = []

    for raw_record in load_dataset(dataset_path):
        results.append(retrieve(raw_record))

    outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    output_path = outputs_dir / "week1_pipeline_output.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} normalized records to {output_path}")


if __name__ == "__main__":
    main()
