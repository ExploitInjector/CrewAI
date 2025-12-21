from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ExplainInput(BaseModel):
    input_text: str = Field(..., description="Findings to map to MITRE ATT&CK.")


class ExplainAttackVectorTool(BaseTool):
    name: str = "explain_attack_vector"
    description: str = "Provides technical mapping to MITRE ATT&CK and strategic mitigations."
    args_schema: Type[BaseModel] = ExplainInput

    def _run(self, input_text: str) -> str:
        try:
            detect_path = Path("data/processed/detection_report.md")
            output_path = Path("data/processed/explanation_report.md")
            with open(detect_path, "r") as f:
                content = f.read().upper()

            explanations = ["# Technical Risk Analysis & MITRE Mapping\n"]

            mapping = {
                "RECONNAISSANCE": "## [T1595] Active Scanning\n**Impact**: Surface mapping.\n**Mitigation**: Implement IP-based rate limiting.",
                "DOS_ATTACK": "## [T1498] Network DoS\n**Impact**: Service outage.\n**Mitigation**: Deploy anti-DDoS traffic scrubbing.",
                "BRUTE_FORCE": "## [T1110] Brute Force\n**Impact**: Credential theft.\n**Mitigation**: Enable Account Lockout policies and MFA.",
                "EXFILTRATION": "## [T1048] Exfiltration Over Alternative Protocol\n**Impact**: Data breach.\n**Mitigation**: Monitor outbound traffic volume and implement DLP."
            }

            for key, text in mapping.items():
                if key in content:
                    explanations.append(text)

            with open(output_path, "w") as f:
                f.write("\n\n".join(explanations))
            return f"EXPLANATION SUCCESS: Mapping saved to {output_path}"
        except Exception as e:
            return f"EXPLANATION ERROR: {str(e)}"