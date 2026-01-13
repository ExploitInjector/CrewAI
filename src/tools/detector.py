
# -*- coding: utf-8 -*-
# src/tools/detector.py
from __future__ import annotations

import os
import json
import logging
from typing import List, Dict, Any, Tuple

import pandas as pd

# --- LangChain Tool dekorátor: próbáljuk a core-ból, ha nem megy, a régi helyről ---
try:
    from langchain_core.tools import tool  # LangChain 0.2+
except ImportError:
    try:
        from langchain.tools import tool  # régebbi LangChain
    except ImportError as e:
        raise ImportError(
            "Hiányzik a 'tool' dekorátor (langchain_core.tools / langchain.tools). "
            "Telepítsd:  pip install langchain langchain-core\n"
            "Parquet olvasáshoz: pip install pyarrow"
        ) from e

# -----------------------------------------------------------------------------
# Beállítások (minimál)
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
INPUT_PATH: str = os.getenv("CORRELATION_PATH", "data/processed/correlation.parquet")
CSV_FALLBACK: str = os.getenv("CORRELATION_CSV_FALLBACK", "data/processed/correlation.csv")

# Küszöbök
BF_HIGH, BF_CRIT = 10, 20
SCAN_HIGH, SCAN_CRIT = 50, 100
HIGH_RISK_PROTOS = {"TELNET", "SMBv1", "RLOGIN"}

# -----------------------------------------------------------------------------
# Segédfüggvények
# -----------------------------------------------------------------------------
def load_correlation(path: str) -> pd.DataFrame:
    """Parquet preferált; ha nem elérhető/olvasási hiba, CSV fallback."""
    if path.lower().endswith(".parquet"):
        try:
            return pd.read_parquet(path)  # pyarrow szükséges
        except Exception:
            pass
    if os.path.exists(CSV_FALLBACK):
        return pd.read_csv(CSV_FALLBACK)
    raise FileNotFoundError(f"Input nem található: {path} (CSV fallback: {CSV_FALLBACK})")

def split_key(key: Any) -> Tuple[str, str]:
    """
    '10.0.0.5->10.0.1.10' / '10.0.0.5-&gt;10.0.1.10' / '10.0.0.5→10.0.1.10' → (src, dst)
    """
    if pd.isna(key):
        return ("", "")
    s = str(key)
    if "->" in s:
        a, b = s.split("->", 1);  return (a.strip(), b.strip())
    if "-&gt;" in s:
        a, b = s.split("-&gt;", 1);  return (a.strip(), b.strip())
    if "-&amp;gt;" in s:
        a, b = s.split("-&amp;gt;", 1);  return (a.strip(), b.strip())
    if "→" in s:
        a, b = s.split("→", 1);  return (a.strip(), b.strip())
    return (s.strip(), "")

def to_int_series(series: pd.Series) -> pd.Series:
    """
    Biztosítsuk, hogy Series maradjon:
    - to_numeric (coerce)
    - NaN → 0
    - int
    """
    s = pd.to_numeric(series, errors="coerce")
    if not isinstance(s, pd.Series):
        s = pd.Series(s, index=series.index)
    return s.fillna(0).astype(int)

# -----------------------------------------------------------------------------
# Detektáló szabályok
# -----------------------------------------------------------------------------
def detect_auth_fail_cluster(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'auth_fail_cluster' → events alapján severity."""
    need = {"type", "events", "key"}
    if not need.issubset(df.columns):
        return []
    sub = df[df["type"] == "auth_fail_cluster"].copy()
    if sub.empty:
        return []

    sub["events_num"] = to_int_series(sub["events"])
    dets: List[Dict[str, Any]] = []
    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        events = int(row["events_num"])
        severity = "critical" if events >= BF_CRIT else "high" if events >= BF_HIGH else "medium"
        dets.append({
            "rule_id": "auth_fail_cluster",
            "name": "Bruteforce klaszter (sikertelen bejelentkezések)",
            "severity": severity,
            "metric": events,
            "group": {
                "src_ip": src,
                "dst_ip": dst,
                "zone": str(row["zone"]) if "zone" in sub.columns and pd.notna(row.get("zone")) else ""
            },
            "reason": f"Sikertelen auth események: {events} (küszöb: high≥{BF_HIGH}, critical≥{BF_CRIT})"
        })
    return dets

def detect_port_scan_like(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'port_scan_like' → unique_ports alapján severity."""
    need = {"type", "unique_ports", "key"}
    if not need.issubset(df.columns):
        return []
    sub = df[df["type"] == "port_scan_like"].copy()
    if sub.empty:
        return []

    sub["uports"] = to_int_series(sub["unique_ports"])
    dets: List[Dict[str, Any]] = []
    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        u = int(row["uports"])
        severity = "critical" if u >= SCAN_CRIT else "high" if u >= SCAN_HIGH else "medium"
        dets.append({
            "rule_id": "port_scan_like",
            "name": "Port-szkennelés jellegű viselkedés",
            "severity": severity,
            "metric": u,
            "group": {
                "src_ip": src,
                "dst_ip": dst,
                "zone": str(row["zone"]) if "zone" in sub.columns and pd.notna(row.get("zone")) else ""
            },
            "reason": f"Egyedi portok: {u} (küszöb: high≥{SCAN_HIGH}, critical≥{SCAN_CRIT})"
        })
    return dets

def detect_forbidden_proto(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """type == 'forbidden_proto' → proto/zone alapján severity."""
    need = {"type", "key", "proto"}
    if not need.issubset(df.columns):
        return []
    sub = df[df["type"] == "forbidden_proto"].copy()
    if sub.empty:
        return []

    dets: List[Dict[str, Any]] = []
    for _, row in sub.iterrows():
        src, dst = split_key(row["key"])
        proto = str(row["proto"]) if pd.notna(row.get("proto")) else ""
        zone = str(row["zone"]) if "zone" in sub.columns and pd.notna(row.get("zone")) else ""
        severity = "critical" if zone.upper() == "SCADA" else ("high" if proto.upper() in HIGH_RISK_PROTOS else "medium")
        dets.append({
            "rule_id": "forbidden_proto",
            "name": "Tiltott/érzékeny protokoll",
            "severity": severity,
            "metric": 1,
            "group": {"src_ip": src, "dst_ip": dst, "proto": proto, "zone": zone},
            "reason": f"Tiltott/érzékeny protokoll: {proto or 'N/A'}" + (", zóna=SCADA → kritikus" if zone.upper() == "SCADA" else "")
        })
    return dets

# -----------------------------------------------------------------------------
# Fő futtató
# -----------------------------------------------------------------------------
def run_detector(input_path: str = INPUT_PATH) -> List[Dict[str, Any]]:
    df = load_correlation(input_path)
    detections: List[Dict[str, Any]] = []
    detections += detect_auth_fail_cluster(df)
    detections += detect_port_scan_like(df)
    detections += detect_forbidden_proto(df)
    return detections

# -----------------------------------------------------------------------------
# CrewAI Tool
# -----------------------------------------------------------------------------


@tool("detect_attacks")
def detect_attacks(input_text: str = "") -> Dict[str, Any]:
    """
    IDS támadásdetektáló Tool (CrewAI / LangChain).

    Paraméterek
    ----------
    input_text : str, opcionális
        Opcionális input-útvonal a korrelátor kimenethez (pl. "data/processed/correlation.parquet").
        Ha üres, a modul konstansa/környezeti változója (INPUT_PATH) lesz használva.

    Visszatérés
    ----------
    Dict[str, Any]
        JSON-kompatibilis eredmény az Explainer számára:
        {
          "detections": List[Dict[str, Any]],  # részletes találatok (name, severity, reason, group, metric)
          "detection_labels": List[str],       # egyedi rule_id-k
          "summary": {
            "total": int                       # összes találat
          }
        }
    """
    # Ha adtál be override útvonalat, használd; különben a default INPUT_PATH-et.
    input_path = (input_text or "").strip() or INPUT_PATH

    detections = run_detector(input_path)
    labels = sorted({d["rule_id"] for d in detections}) if detections else []
    summary = {"total": len(detections)}

    return {"detections": detections, "detection_labels": labels, "summary": summary}



# -----------------------------------------------------------------------------
# Kézi teszt (modul futtatása): python -m src.tools.detector
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Bármelyik jó:
    res = detect_attacks.invoke({})           # üres dict → default param érvényesül
    # res = detect_attacks.invoke("")         # 1 db string is ok (egyetlen param esetén)
    # res = detect_attacks.invoke({"input_text": ""})  # explicit kulcsnév
    print(json.dumps(res, ensure_ascii=False, indent=2))

