
from crewai import Task

def build_detector_smith_task(cleaned_path: str, corr_path: str,
                              output_json_path: str, output_md_path: str) -> Task:
    """
    Minimalista, CrewAI 0.7x kompatibilis Task.
    A bemeneteket és a várt kimenetet egyértelműen leírjuk.
    (Az agentet NEM adjuk át a konstruktorban – a main-ben task.agent = agent.)
    """
    description = f"""
Feladat: Általános detekciós riport készítése domainfüggetlen adathalmazra.

Források (kontextus):
- CLEANED (parquet): {cleaned_path}
- CORR (parquet, ha elérhető): {corr_path}

Feladatod:
1) Azonosítsd a releváns detekciókat / eseményeket a rendelkezésre álló adatok alapján.
2) Állíts elő JSON kimenetet, amit a rendszer fájlba ment:
   - Mentési útvonal: {output_json_path}
   - Struktúra javaslat: list[object], minden elem: {{
       "id": str/int,
       "type": str,               # pl. "burst", "range_violation", "stat_outlier", stb.
       "severity": "low|medium|high|critical",
       "evidence": str            # tömör magyar leírás, mire alapozod a detekciót
     }}
   - Ha nem tudsz szabályos JSON-t adni, adj nyers szöveget (artefakt), hogy a pipeline ne álljon le.
3) Adj rövid magyar nyelvű magyarázatot Markdown formában:
   - Mentési útvonal: {output_md_path}
   - Fogalmazz tömören, a detekciókhoz rendelt indoklással.

Megjegyzés:
- A pipeline minimum-mentést alkalmaz: ha nincs érvényes JSON, üres listát ment ([]) és külön Markdown magyarázatot.
- A Detektor célja: működő artefaktok előállítása, amire a Magyarázó és Tudósító rá tud építeni.
"""
    expected_output = "Detekciók JSON + magyar magyarázat Markdown."

    return Task(
        description=description,
        expected_output=expected_output,
        verbose=True
    )
