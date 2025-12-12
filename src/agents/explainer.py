from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class ExplainerConfig:
    input_csv: Path = Path("runs/detections_top.csv")
    output_json: Path = Path("runs/explanations_top.json")
    output_md: Path = Path("runs/explanations_top.md")


def explain_row(r) -> dict:
    reasons = []
    evidence = {}

    flows = int(r.get("flows", 0))
    usp = int(r.get("unique_src_ports", 0))

    # flags mező stringből dict-be
    flags = r.get("flags", {})
    if isinstance(flags, str):
        try:
            flags = json.loads(flags.replace("'", '"'))
        except Exception:
            flags = {}

    if flags.get("port_scan_suspected"):
        reasons.append("Port scan gyanú: sok különböző forrásport rövid időablakban azonos célra.")
        evidence["unique_src_ports"] = usp

    if flags.get("high_volume_suspected"):
        reasons.append("Nagy forgalom gyanú: kiugróan sok flow ugyanabban az időablakban.")
        evidence["flows"] = flows

    # kiegészítő indokok
    if flows >= 200 and "flows" not in evidence:
        reasons.append("Magas eseménysűrűség: a flow-k száma magas ebben az időablakban.")
        evidence["flows"] = flows

    if usp >= 30 and "unique_src_ports" not in evidence:
        reasons.append("Széles porttartomány: sok különböző forrásport használata.")
        evidence["unique_src_ports"] = usp

    # Top label/type/subtype mezők rövid összefoglalása (stringként jönnek a CSV-ből)
    for k in ["labels_top", "traffic_types_top", "traffic_subtypes_top"]:
        v = r.get(k, "")
        if isinstance(v, str) and v:
            evidence[k] = v

    summary = f"{r.get('src_ip')} → {r.get('dst_ip')}:{r.get('dst_port')} ({r.get('protocol')}) @ {r.get('time_bucket')}"

    return {
        "summary": summary,
        "risk_score": int(r.get("risk_score", 0)),
        "reasons": reasons or ["Gyanús mintázat a szabályok alapján (részletek az evidence mezőben)."],
        "evidence": evidence,
        "raw": {
            "time_bucket": r.get("time_bucket"),
            "src_ip": r.get("src_ip"),
            "dst_ip": r.get("dst_ip"),
            "dst_port": r.get("dst_port"),
            "protocol": r.get("protocol"),
        }
    }


def main() -> None:
    cfg = ExplainerConfig()
    cfg.output_json.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(cfg.input_csv)

    items = [explain_row(row) for _, row in df.iterrows()]

    payload = {
        "count": len(items),
        "items": items
    }

    cfg.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Markdown (gyors review-hoz)
    lines = []
    for i, it in enumerate(items, 1):
        lines.append(f"## {i}. {it['summary']}")
        lines.append(f"- risk_score: {it['risk_score']}")
        for r in it["reasons"]:
            lines.append(f"- ok: {r}")
        if it["evidence"]:
            lines.append("- evidence:")
            for k, v in it["evidence"].items():
                lines.append(f"  - {k}: {v}")
        lines.append("")
    cfg.output_md.write_text("\n".join(lines), encoding="utf-8")

    print("Explainer done.")
    print(f"Wrote: {cfg.output_json} and {cfg.output_md}")


if __name__ == "__main__":
    main()
