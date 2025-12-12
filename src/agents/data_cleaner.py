from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
from collections import Counter

INPUT = Path("data/raw/csv/data.csv")
OUTPUT = Path("data/processed/tii_ssrc23_cleaned_full.csv")
REPORT = Path("runs/data_cleaner_report.json")

REQUIRED_COLUMNS = [
    "Flow ID", "Src IP", "Src Port",
    "Dst IP", "Dst Port", "Protocol",
    "Timestamp", "Label", "Traffic Type", "Traffic Subtype"
]

CHUNK_SIZE = 200_000  # emeld 500k–1M-re, ha bírja a gép


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    total_in = 0
    total_out = 0
    dropped_na = 0
    dropped_dup = 0
    label_counter = Counter()

    first_chunk = True

    for chunk in pd.read_csv(INPUT, chunksize=CHUNK_SIZE):
        total_in += len(chunk)

        # oszlopellenőrzés (csak egyszer)
        if first_chunk:
            missing = [c for c in REQUIRED_COLUMNS if c not in chunk.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

        # timestamp
        chunk["Timestamp"] = pd.to_datetime(
            chunk["Timestamp"], errors="coerce", utc=True
        )

        before = len(chunk)
        chunk = chunk.dropna(subset=REQUIRED_COLUMNS)
        dropped_na += before - len(chunk)

        for c in ["Src IP", "Dst IP", "Label", "Traffic Type", "Traffic Subtype"]:
            chunk[c] = chunk[c].astype(str).str.strip()

        before = len(chunk)
        chunk = chunk.drop_duplicates(subset=[
            "Flow ID", "Timestamp",
            "Src IP", "Src Port",
            "Dst IP", "Dst Port",
            "Protocol",
            "Label", "Traffic Type", "Traffic Subtype"
        ])
        dropped_dup += before - len(chunk)

        label_counter.update(chunk["Label"])

        chunk.to_csv(
            OUTPUT,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )

        total_out += len(chunk)
        first_chunk = False

        print(f"Processed chunk: in={total_in:,} out={total_out:,}")

    report = {
        "rows_in": total_in,
        "rows_out": total_out,
        "dropped_missing_required": dropped_na,
        "dropped_duplicates": dropped_dup,
        "label_counts": dict(label_counter),
        "chunk_size": CHUNK_SIZE
    }

    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\nDataCleaner FULL run completed")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
