# Detector Report (correlator schema)

- Input: `data/processed/correlation.parquet`
- Detections: 3

## Példa találatok (max 50)

- **Bruteforce klaszter (sikertelen bejelentkezések)** | severity: `critical` | metric: `25` | group: `{'src_ip': '10.0.0.5', 'dst_ip': '10.0.1.10', 'zone': ''}` | reason: Sikertelen auth események száma=25 (küszöbök: high≥10, critical≥20).
- **Port-szkennelés jellegű viselkedés** | severity: `high` | metric: `79` | group: `{'src_ip': '10.0.0.9', 'dst_ip': '10.0.1.10', 'zone': ''}` | reason: Egyedi portok száma=79 (küszöbök: high≥50, critical≥100).
- **Tiltott/érzékeny protokoll** | severity: `critical` | metric: `1` | group: `{'src_ip': '10.0.0.7', 'dst_ip': '10.0.1.20', 'proto': 'TELNET', 'zone': 'SCADA'}` | reason: Tiltott/érzékeny protokoll észlelve: TELNET, zóna=SCADA → kritikus