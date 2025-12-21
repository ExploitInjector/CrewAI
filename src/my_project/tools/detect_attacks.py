import pandas as pd
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DetectInput(BaseModel):
    input_text: str = Field(..., description="Identify attacks in large cleaned dataset.")


class DetectAttacksTool(BaseTool):
    name: str = "detect_attacks"
    description: str = "Detects DDoS, Scanning, and Brute Force in high-volume traffic."
    args_schema: Type[BaseModel] = DetectInput

    def _run(self, input_text: str) -> str:
        try:
            df = pd.read_csv("data/processed/cleaned.csv")
            findings = []

            # 1. DDoS Detektálás: Ha egy IP a forgalom több mint 5%-át adja (100k sornál >5000 csomag)
            ddos_threshold = len(df) * 0.05
            heavy_talkers = df['src_ip'].value_counts()
            for ip, count in heavy_talkers[heavy_talkers > ddos_threshold].items():
                findings.append(
                    f"### [DDoS_POTENTIAL] IP `{ip}` responsible for {count} flows ({round(count / len(df) * 100, 2)}%).")

            # 2. Port Scan: Egy IP több mint 50 különböző portot próbál elérni
            recon = df.groupby('src_ip')['dst_port'].nunique()
            for ip, count in recon[recon > 50].items():
                findings.append(f"### [RECONNAISSANCE] IP `{ip}` scanned {count} unique ports.")

            # 3. Brute Force: SSH (22) vagy RDP (3389) portokon kiugró forgalom
            brute = df[df['dst_port'].isin([22, 3389])].groupby('src_ip').size()
            for ip, count in brute[brute > 200].items():
                findings.append(f"### [BRUTE_FORCE] Excessive auth attempts from `{ip}` on sensitive ports.")

            report_path = Path("data/processed/detection_report.md")
            with open(report_path, "w") as f:
                f.write("# High-Volume Security Detection Report\n\n" + "\n".join(findings))

            return f"DETECTION SUCCESS: Processed {len(df)} rows. Found {len(findings)} incidents."
        except Exception as e:
            return f"ERROR: {str(e)}"