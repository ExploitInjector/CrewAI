import pandas as pd
import json
import os
import logging
from crewai.tools import tool
from datetime import datetime

# Naplózás beállítása
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@tool("detect_attacks")
def detect_incidents(input_path: str = "data/processed/cleaned.csv") -> str:
    """
    Összetett biztonsági incidens detektálás (DDoS, Bruteforce, Port Scan, Tiltott protokollok).
    JSON és MD jelentést generál az Explainer és Reporting AI-nak a data/processed mappába.
    """
    try:
        # 1. Bemeneti útvonal kezelése
        path = input_path if input_path else "data/processed/cleaned.csv"
        if not os.path.exists(path):
            return f"HIBA: A fájl nem található: {path}. Andrásnak (DataCleaner) futnia kell előbb!"

        df = pd.read_csv(path, low_memory=False)
        detections = []

        # Oszlopnevek normalizálása a biztonság kedvéért
        df.columns = [col.lower() for col in df.columns]
        src_ip = next((c for c in ['src_ip', 'source_ip'] if c in df.columns), 'src_ip')
        dst_ip = next((c for c in ['dst_ip', 'destination_ip'] if c in df.columns), 'dst_ip')
        dst_port = next((c for c in ['dst_port', 'destination_port', 'port'] if c in df.columns), 'dst_port')
        label_col = next((c for c in ['label', 'attack_type', 'type'] if c in df.columns), 'label')

        # --- 1. SZABÁLY: DDoS Detektálás (Cél IP elárasztása) ---
        if dst_ip in df.columns:
            counts = df[dst_ip].value_counts()
            for target, count in counts[counts > 1000].items():
                detections.append({
                    "type": "DDoS Attack Suspected",
                    "severity": "CRITICAL",
                    "source": "Multiple/Distributed",
                    "description": f"Célzott elárasztás észlelhető a(z) {target} címen. Kérések száma: {count}"
                })

        # --- 2. SZABÁLY: Bruteforce Detektálás ---
        if label_col in df.columns and src_ip in df.columns:
            bf_mask = df[label_col].str.contains('BruteForce|SSH|FTP', case=False, na=False)
            bf_attempts = df[bf_mask][src_ip].value_counts()
            for ip, count in bf_attempts[bf_attempts > 5].items():
                detections.append({
                    "type": "Bruteforce Attempt",
                    "severity": "HIGH",
                    "source": ip,
                    "description": f"Sokszoros sikertelen bejelentkezési kísérlet ({count} db) azonosítható."
                })

        # --- 3. SZABÁLY: Port Scan Detektálás ---
        if src_ip in df.columns and dst_port in df.columns:
            scans = df.groupby(src_ip)[dst_port].nunique()
            for ip, count in scans[scans > 15].items():
                detections.append({
                    "type": "Port Scan",
                    "severity": "MEDIUM",
                    "source": ip,
                    "description": f"Gyanús port-szkennelés: {count} egyedi portot próbált elérni."
                })

        # --- 4. SZABÁLY: Tiltott/Veszélyes Protokollok ---
        forbidden_ports = {21: "FTP", 23: "TELNET", 445: "SMB/WannaCry-risk"}
        if dst_port in df.columns:
            for port, name in forbidden_ports.items():
                if port in df[dst_port].values:
                    affected_ips = df[df[dst_port] == port][src_ip].unique()
                    detections.append({
                        "type": "Forbidden Protocol Usage",
                        "severity": "HIGH",
                        "source": str(list(affected_ips[:3])),
                        "description": f"Veszélyes protokoll használata észlelve a(z) {port}-as porton ({name})."
                    })

        # --- EREDMÉNYEK MENTÉSE ---
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {"total_events": len(df), "incidents_found": len(detections)},
            "incidents": detections
        }

        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)

        # JSON Jánosnak
        with open(os.path.join(output_dir, "detections.json"), "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        # MD Zolinak
        with open(os.path.join(output_dir, "detector_report.md"), "w", encoding="utf-8") as f:
            f.write(f"# Biztonsági Jelentés - Detector AI\n\n## Összegzés\nAnalizált sorok: {len(df)}\nTalált incidensek: {len(detections)}\n\n")
            for d in detections:
                f.write(f"### [{d['severity']}] {d['type']}\n- Forrás: {d['source']}\n- Leírás: {d['description']}\n\n")

        return json.dumps(report_data, ensure_ascii=False)

    except Exception as e:
        return f"KRITIKUS HIBA: {str(e)}"