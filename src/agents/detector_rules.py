from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class DetectorConfig:
    input_csv: Path = Path("runs/correlated_events_full.csv")
    output_csv: Path = Path("runs/detections_top.csv")
    output_json: Path = Path("runs/detections_top.json")

    # küszöbök (később hangoljuk)
    min_flows: int = 50
    min_unique_src_ports: int = 10

    score_port_scan: int = 60
    score_high_volume: int = 50
    score_many_flows: int = 25
    score_many_ports: int = 20

    top_n: int = 200


def score_row(r) -> int:
    s = 0
    flags = r.get("flags", {})

    if isinstance(flags, str):
        # CSV-be dict-ként stringként került; egyszerű parse
        try:
            flags = json.loads(flags.replace("'", '"'))
        except Exception:
            flags = {}

    if flags.get("port_scan_suspected"):
        s += 60
    if flags.get("high_volume_suspected"):
        s += 50

    flows = int(r["flows"])
    usp = int(r["unique_src_ports"])

    if flows >= 200:
        s += 25
    if usp >= 30:
        s += 20

    return s


def main() -> None:
    cfg = DetectorConfig()
    cfg.output_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(cfg.input_csv)

    # pontszám
    df["risk_score"] = df.apply(score_row, axis=1)

    # minimális szűrés: ne öntsük tele a listát
    df = df[(df["flows"] >= cfg.min_flows) | (df["unique_src_ports"] >= cfg.min_unique_src_ports) | (df["risk_score"] >= 50)]

    # rendezés: legkockázatosabb elöl
    df = df.sort_values(["risk_score", "flows", "unique_src_ports"], ascending=[False, False, False])

    top = df.head(cfg.top_n).copy()

    top.to_csv(cfg.output_csv, index=False)

    payload = {
        "summary": {
            "rows_in": int(len(pd.read_csv(cfg.input_csv))),
            "rows_after_filter": int(len(df)),
            "top_n": int(len(top)),
        },
        "top_detections": top.to_dict(orient="records"),
    }

    cfg.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Detector (rules) done.")
    print(json.dumps(payload["summary"], indent=2))
    print("Wrote:", cfg.output_csv, "and", cfg.output_json)


if __name__ == "__main__":
    main()
