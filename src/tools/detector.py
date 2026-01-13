import pandas as pd
import json
import os
import logging
from crewai.tools import tool
from datetime import datetime

# Naplózás beállítása
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@tool("detect_incidents")
def detect_incidents(input_path: str = "data/processed/cleaned.csv") -> str:
    """
    Biztonsági incidensek detektálása a tisztított CSV adatok alapján.
    JSON és Markdown jelentést generál a data/processed mappába.
    """
    try:
        # 1. Bemeneti útvonal ellenőrzése
        path = input_path if input_path else "data/processed/cleaned.csv"
        if not os.path.exists(path):
            return f"HIBA: A bemeneti fájl nem található: {path}. Andrásnak (DataCleaner) futnia kell előbb."

        df = pd.read_csv(path)
        detections = []

        # --- DETEKCIÓS SZABÁLYOK ---
        # Egyszerű példa: Port Scan keresése (több mint 10 egyedi célport egy IP-től)
        if 'src_ip' in df.columns and 'dst_port' in df.columns:
            scans = df.groupby('src_ip')['dst_port'].nunique()
            for ip, count in scans[scans > 10].items():
                detections.append({
                    "type": "Port Scan",
                    "severity": "High",
                    "source": ip,
                    "description": f"Gyanús aktivitás: {count} egyedi portot érintett."
                })

        # --- JELENTÉS ÖSSZEÁLLÍTÁSA ---
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_events_analyzed": len(df),
                "incidents_found": len(detections)
            },
            "incidents": detections
        }

        # 2. Mentés a kért helyre: data/processed
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)

        # JSON mentés (Jánosnak - Explainer)
        json_path = os.path.join(output_dir, "detections.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        # Markdown mentés (Zolinak - Reporting)
        md_path = os.path.join(output_dir, "detector_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Detektált Biztonsági Incidensek\n")
            f.write(f"**Időpont:** {report_data['timestamp']}\n\n")
            f.write(f"## Statisztika\n- Elemzett sorok: {len(df)}\n- Talált incidensek: {len(detections)}\n\n")
            if detections:
                for d in detections:
                    f.write(f"### [{d['severity']}] {d['type']}\n- Forrás: {d['source']}\n- {d['description']}\n\n")
            else:
                f.write("Nem észlelhető kritikus incidens a vizsgált mintában.\n")

        # Az Agentnek JSON stringet adunk vissza, hogy tudjon belőle magyarázni
        return json.dumps(report_data, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Hiba a detektálás közben: {str(e)}")
        return f"KRITIKUS HIBA: {str(e)}"