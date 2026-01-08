from crewai import Task


def build_detector_smith_task(cleaned_path: str, corr_path: str,
                              output_json_path: str, output_md_path: str) -> Task:
    description = f"""
Feladat: azonosítsd a legfontosabb biztonsági detekciókat a CLEANED és CORR adatok alapján.

Kimenetek:
- JSON lista, minden elem mint:
    {{"id": 1, "type": "...", "severity": "low|medium|high|critical", "evidence": "..."}}
- Rövid magyar nyelvű szöveges magyarázat Markdownban.

Legyél tömör, strukturált, ne írj felesleges szöveget.
Ha nem tudsz érvényes JSON-t adni: adj üres listát ([]), és külön rövid magyarázatot.
"""

    expected_output = "Detekciók JSON + magyar magyarázat Markdown."

    return Task(
        description=description,
        expected_output=expected_output,
        verbose=True  # vagy verbose=False ha nem akarod kiíratni
    )
