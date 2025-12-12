from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd


@dataclass
class CorrelatorConfig:
    input_path: Path = Path("data/processed/tii_ssrc23_cleaned_full.csv")
    output_json: Path = Path("runs/correlated_events_full.json")
    output_csv: Path = Path("runs/correlated_events_full.csv")  # opcionális, könnyebb Excelbe
    window: str = "1min"     # 1min / 5min
    chunk_size: int = 300_000
    top_n: int = 5

    # egyszerű heurisztikák
    scan_src_port_threshold: int = 30     # ha egy (src->dst,dstport,window) alatt >=30 különböző src_port -> gyanús
    high_flow_threshold: int = 300        # ha flows >=300 -> gyanús


KEY_COLS = ["time_bucket", "Src IP", "Dst IP", "Dst Port", "Protocol"]


def main() -> None:
    cfg = CorrelatorConfig()

    cfg.output_json.parent.mkdir(parents=True, exist_ok=True)

    # Aggregációs tárolók (kulcs -> számlálók)
    flows = Counter()
    unique_src_ports: dict[tuple, set] = defaultdict(set)
    label_counts: dict[tuple, Counter] = defaultdict(Counter)
    type_counts: dict[tuple, Counter] = defaultdict(Counter)
    subtype_counts: dict[tuple, Counter] = defaultdict(Counter)

    total_in = 0

    use_cols = [
        "Flow ID", "Timestamp",
        "Src IP", "Src Port",
        "Dst IP", "Dst Port",
        "Protocol",
        "Label", "Traffic Type", "Traffic Subtype"
    ]

    for chunk in pd.read_csv(cfg.input_path, usecols=use_cols, chunksize=cfg.chunk_size):
        total_in += len(chunk)

        chunk["Timestamp"] = pd.to_datetime(chunk["Timestamp"], errors="coerce", utc=True)
        chunk = chunk.dropna(subset=["Timestamp", "Src IP", "Dst IP", "Dst Port", "Protocol"])

        # időbucket
        chunk["time_bucket"] = chunk["Timestamp"].dt.floor(cfg.window)

        # soronkénti aggregálás (memóriabarát)
        for _, row in chunk.iterrows():
            tb = row["time_bucket"]
            src = row["Src IP"]
            srcp = row["Src Port"]
            dst = row["Dst IP"]
            dstp = row["Dst Port"]
            proto = row["Protocol"]
            label = row["Label"]
            ttype = row["Traffic Type"]
            stype = row["Traffic Subtype"]



            k = (tb, src, dst, dstp, proto)

            flows[k] += 1
            unique_src_ports[k].add(srcp)
            label_counts[k].update([label])
            type_counts[k].update([ttype])
            subtype_counts[k].update([stype])

        if total_in % (cfg.chunk_size * 2) == 0:
            print(f"Correlator progress: processed rows={total_in:,} unique_groups={len(flows):,}")

    # Eseménylista előállítása
    events = []
    scan_flags = 0
    volume_flags = 0

    for k, fcount in flows.items():
        tb, src, dst, dstport, proto = k
        usp = len(unique_src_ports[k])

        flags = {
            "port_scan_suspected": bool(usp >= cfg.scan_src_port_threshold),
            "high_volume_suspected": bool(fcount >= cfg.high_flow_threshold),
        }
        if flags["port_scan_suspected"]:
            scan_flags += 1
        if flags["high_volume_suspected"]:
            volume_flags += 1

        events.append({
            "time_bucket": str(tb),
            "src_ip": src,
            "dst_ip": dst,
            "dst_port": int(dstport),
            "protocol": proto,
            "flows": int(fcount),
            "unique_src_ports": int(usp),
            "labels_top": label_counts[k].most_common(cfg.top_n),
            "traffic_types_top": type_counts[k].most_common(cfg.top_n),
            "traffic_subtypes_top": subtype_counts[k].most_common(cfg.top_n),
            "flags": flags,
        })

    # rendezés: gyanúsak elöl, majd flow szám szerint
    events.sort(key=lambda e: (e["flags"]["port_scan_suspected"] or e["flags"]["high_volume_suspected"], e["flows"]), reverse=True)

    report = {
        "input_path": str(cfg.input_path),
        "rows_processed": int(total_in),
        "groups_out": int(len(events)),
        "window": cfg.window,
        "chunk_size": cfg.chunk_size,
        "thresholds": {
            "scan_unique_src_ports": cfg.scan_src_port_threshold,
            "high_flow": cfg.high_flow_threshold,
        },
        "flag_counts": {
            "port_scan_suspected": int(scan_flags),
            "high_volume_suspected": int(volume_flags),
        }
    }

    payload = {"report": report, "events": events}

    cfg.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Correlator FULL done.")
    print(json.dumps(report, indent=2))

    # opcionális CSV export (Excel/elemzés)
    try:
        pd.DataFrame(events).to_csv(cfg.output_csv, index=False)
        print(f"Wrote CSV: {cfg.output_csv}")
    except Exception as e:
        print("CSV export skipped:", e)


if __name__ == "__main__":
    main()
