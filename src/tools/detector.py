
# src/tools/detector.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Tuple

import pandas as pd


# ---- Beállítások ----
INPUT_PATH: str = "data/processed/correlation.parquet"  # ha CSV: "data/processed/correlation.csv"
OUT_JSON: str = "data/processed/detections.json"
OUT_MD: str = "data/processed/detector_report.md"

# Küszöbök
BF_HIGH: int = 10
BF_CRIT: int = 20
SCAN_HIGH: int = 50
SCAN_CRIT: int = 100
HIGH_RISK_PROTOS = {"TELNET", "SMBv1", "RLOGIN"}  # bővíthető


# ---- Helper: key feldarabolása src->dst ----
def split_key(key: Any) -> Tuple[str, str]:
    """
    '10.0.0.5->10.0.1.10' -> ('10.0.0.5', '10.0.1.10')
    Tolerálja a ritka formákat is: '10.0.0.5-&gt;10.0.1.10' vagy '10.0.0.5→10.0.1.10'
    """
    if pd.isna(key):
        return ("", "")
    s = str(key)
    if "->" in s:
        a, b = s.split("->", 1)
        return (a.strip(), b.strip())
    if "-&gt;" in s:  # ha HTML kódolt nyíl került a fájlba
        a, b = s.split("-&gt;", 1)
        return (a.strip(), b.strip())
    if "→" in s:
        a, b = s.split("→", 1)
        return (a.strip(), b.strip())
    # ha semmi nem illik: forrás ismeretlen, cél üres
    return (s.strip(), "")


# ---- Detektáló szabályok a sémára ----
def detect_auth_fail_cluster(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'auth_fail_cluster' → events alapján severity."""
    if "type" not in df.columns or "events" not in df.columns or "key" not in df.columns:
        return []

    sub = df[df["type"] == "auth_fail_cluster"].copy()
    if sub.empty:
        return []

    sub["events_num"] = pd.to_numeric(sub["events"], errors="coerce").fillna(0).astype(int)
    dets: List[Dict[str, Any]] = []

    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        events = int(row["events_num"])
        if events >= BF_CRIT:
            sev = "critical"
        elif events >= BF_HIGH:
            sev = "high"
        else:
            sev = "medium"

        dets.append({
            "rule_id": "auth_fail_cluster",
            "name": "Bruteforce klaszter (sikertelen bejelentkezések)",
            "severity": sev,
            "metric": events,
            "group": {
                "src_ip": src,
                "dst_ip": dst,
                "zone": str(row["zone"]) if "zone" in row and pd.notna(row["zone"]) else ""
            },
            "reason": f"Sikertelen auth események száma={events} (küszöbök: high≥{BF_HIGH}, critical≥{BF_CRIT})."
        })

    return dets


def detect_port_scan_like(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'port_scan_like' → unique_ports alapján severity."""
    needed = {"type", "unique_ports", "key"}
    if not needed.issubset(df.columns):
        return []

    sub = df[df["type"] == "port_scan_like"].copy()
    if sub.empty:
        return []

    sub["uports"] = pd.to_numeric(sub["unique_ports"], errors="coerce").fillna(0).astype(int)
    dets: List[Dict[str, Any]] = []

    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        u = int(row["uports"])
        if u >= SCAN_CRIT:
            sev = "critical"
        elif u >= SCAN_HIGH:
            sev = "high"
        else:
            sev = "medium"

        dets.append({
            "rule_id": "port_scan_like",
            "name": "Port-szkennelés jellegű viselkedés",
            "severity": sev,
            "metric": u,
            "group": {
                "src_ip": src,
                "dst_ip": dst,
                "zone": str(row["zone"]) if "zone" in row and pd.notna(row["zone"]) else ""
            },
            "reason": f"Egyedi portok száma={u} (küszöbök: high≥{SCAN_HIGH}, critical≥{SCAN_CRIT})."
        })

    return dets


def detect_forbidden_proto(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'forbidden_proto' → proto/zone alapján severity."""
    needed = {"type", "key", "proto"}
    if not needed.issubset(df.columns):
        return []

    sub = df[df["type"] == "forbidden_proto"].copy()
    if sub.empty:
        return []

    dets: List[Dict[str, Any]] = []

    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        proto = str(row["proto"]) if pd.notna(row["proto"]) else ""
        zone = str(row["zone"]) if "zone" in row and pd.notna(row["zone"]) else ""

        # Severity logika: SCADA-ban kritikus; illetve magas kockázatú proto nevekre is emeljünk
        if zone.upper() == "SCADA":
            sev = "critical"
        elif proto.upper() in HIGH_RISK_PROTOS:
            sev = "high"
        else:
            sev = "medium"

        dets.append({
            "rule_id": "forbidden_proto",
            "name": "Tiltott/érzékeny protokoll",
            "severity": sev,
            "metric": 1,
            "group": {
                "src_ip": src,
                "dst_ip": dst,
                "proto": proto,
                "zone": zone
            },
            "reason": f"Tiltott/érzékeny protokoll észlelve: {proto or 'N/A'}"
                      + (", zóna=SCADA → kritikus" if zone.upper() == "SCADA" else "")
        })

    return dets


# ---- Fő futtató ----
def run_detector(
    input_path: str = INPUT_PATH,
    out_json: str = OUT_JSON,
    out_md: str = OUT_MD
) -> None:
    # Input betöltés (Parquet preferált; CSV fallback)
    if input_path.lower().endswith(".parquet"):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    # Detekciók
    detections: List[Dict[str, Any]] = []
    detections += detect_auth_fail_cluster(df)
    detections += detect_port_scan_like(df)
    detections += detect_forbidden_proto(df)

    # Kimenetek
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(detections, f, ensure_ascii=False, indent=2)

    if out_md:
        os.makedirs(os.path.dirname(out_md), exist_ok=True)
        lines: List[str] = [
            "# Detector Report (correlator schema)",
            "",
            f"- Input: `{input_path}`",
            f"- Detections: {len(detections)}",
            "",
            "## Példa találatok (max 50)",
            ""
        ]
        for det in detections[:50]:
            lines.append(
                f"- **{det.get('name')}** | severity: `{det.get('severity')}` "
                f"| metric: `{det.get('metric')}` | group: `{det.get('group')}` "
                f"| reason: {det.get('reason')}"
            )
        with open(out_md, "w", encoding="utf-8") as f_md:
            f_md.write("\n".join(lines))


if __name__ == "__main__":
    run_detector()
