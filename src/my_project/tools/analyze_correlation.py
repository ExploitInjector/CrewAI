import pandas as pd
import os
import logging
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnalyzeCorrelationInput(BaseModel):
    """Input schema for AnalyzeCorrelationTool."""
    input_text: str = Field(..., description="A placeholder input text for the correlation analysis request.")

class AnalyzeCorrelationTool(BaseTool):
    name: str = "analyze_correlation"
    description: str = (
        "Advanced statistical correlation analysis for network traffic. Identifies "
        "suspicious Source-Destination relationships, high-frequency port access, "
        "and payload anomalies. Source: data/processed/cleaned.csv | Target: data/processed/correlation_report.md"
    )
    args_schema: Type[BaseModel] = AnalyzeCorrelationInput

    def _run(self, input_text: str) -> str:
        try:
            source_file = Path("data/processed/cleaned.csv")
            target_dir = Path("data/processed")
            report_file = target_dir / "correlation_report.md"

            if not source_file.exists():
                return f"ERROR: Cleaned data file not found at: {source_file}. Please run data cleaning first."

            logging.info(f"Starting professional correlation analysis on {source_file}")
            df = pd.read_csv(source_file, low_memory=False)

            if df.empty:
                return "WARNING: Dataset is empty. Correlation analysis aborted."

            # 1. Traffic Intensity Analysis (Potential DoS/DDoS Indicators)
            # Grouping by Source and Destination to find heavy talkers
            intensity = df.groupby(['src_ip', 'dst_ip']).size().reset_index(name='connection_count')
            top_intensity = intensity.sort_values(by='connection_count', ascending=False).head(10)

            # 2. Port Diversity Analysis (Scanning Indicators)
            # Identifying IPs hitting the most unique ports
            port_diversity = df.groupby('src_ip')['dst_port'].nunique().reset_index(name='unique_ports_hit')
            top_scanners = port_diversity.sort_values(by='unique_ports_hit', ascending=False).head(10)

            # 3. Payload Anomaly Analysis
            # Looking for unusually high average packet lengths relative to protocol
            payload_stats = df.groupby('protocol')['total_length_of_fwd_packet'].agg(['mean', 'max', 'count']).round(2)

            # 4. Label/Traffic Type Distribution (If columns exist in your dataset)
            traffic_summary = ""
            if 'label' in df.columns:
                label_counts = df['label'].value_counts().to_markdown()
                traffic_summary = f"### Dataset Label Distribution\n\n{label_counts}\n\n"

            # Building the Professional Report
            report_content = (
                "# Professional Network Correlation Report\n\n"
                f"**Analysis Scope:** {len(df)} network flows processed.\n\n"
                "## 1. Traffic Intensity (Heavy Talkers)\n"
                "High connection counts between specific IP pairs may indicate DoS activity or automated data exfiltration.\n\n"
                f"{top_intensity.to_markdown(index=False)}\n\n"
                "## 2. Scanning Activity (Port Diversity)\n"
                "Sources contacting a high number of unique destination ports are likely performing reconnaissance/port scanning.\n\n"
                f"{top_scanners.to_markdown(index=False)}\n\n"
                "## 3. Protocol & Payload Statistics\n"
                "Summary of data volume distributed across protocols.\n\n"
                f"{payload_stats.to_markdown()}\n\n"
                f"{traffic_summary}"
                "--- \n"
                "*Generated automatically by the AnalyzeCorrelationTool for SOC analysis.*"
            )

            if 'label' in df.columns:
                label_summary = df['label'].value_counts().to_markdown()
                report_content += f"## Traffic Label Distribution\n\n{label_summary}\n\n"

            # Save the report
            target_dir.mkdir(parents=True, exist_ok=True)
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            return (f"SUCCESS: Advanced correlation analysis finished.\n"
                    f"- Flows Analyzed: {len(df)}\n"
                    f"- Indicators: Top talkers, port scanning, and payload stats calculated.\n"
                    f"- File Saved: {report_file}")

        except Exception as e:
            logging.error(f"Critical error during professional correlation: {str(e)}")
            return f"CRITICAL ERROR: {str(e)}"