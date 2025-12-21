import datetime
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class FinalInput(BaseModel):
    input_text: str = Field(..., description="Final request to generate report.")


class GenerateFinalReportTool(BaseTool):
    name: str = "generate_final_report"
    description: str = "Generates the final Executive SOC Report for management."
    args_schema: Type[BaseModel] = FinalInput

    def _run(self, input_text: str) -> str:
        try:
            processed = Path("data/processed")
            report_file = Path("report.md")

            final_output = [
                f"# SOC Security Assessment Report\n**Timestamp:** {datetime.datetime.now()}\n",
                "## 1. Executive Summary\nAutomated analysis of the network telemetry has concluded. Below are the identified risks.\n"
            ]

            for section, file in [("Threat Findings", "detection_report.md"),
                                  ("Risk Mapping", "explanation_report.md")]:
                path = processed / file
                if path.exists():
                    with open(path, "r") as f:
                        final_output.append(f"## {section}\n" + f.read().replace("# ", "### "))

            with open(report_file, "w") as f:
                f.write("\n\n".join(final_output))
            return f"FINAL SUCCESS: Report generated at {report_file.absolute()}"
        except Exception as e:
            return f"REPORT ERROR: {str(e)}"