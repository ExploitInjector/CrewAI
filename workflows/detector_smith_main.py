
# workflows/detector_smith_main.py
from __future__ import annotations

import sys
import json
import logging
from pathlib import Path
from typing import Optional, List

import pyarrow.parquet as pq
import pandas as pd
import yaml
from crewai import Crew

from agents.detector_smith_agent import build_detector_smith_agent
from tasks.detector_smith_task import build_detector_smith_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("detector_main")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#rugalmas defaultok (CSV preferencia, de bármely formátum mehet)
DEFAULT_CLEANED_CANDIDATES = [
    Path("data/processed/cleaned.parquet"),
    Path("data/processed/cleaned.csv"),
    Path("data/processed/cleaned.json"),
]
DEFAULT_CORR_CANDIDATES = [
    Path("data/processed/correlation.csv"),
    Path("data/processed/correlation.json"),
    Path("data/processed/correlation.parquet"),
    Path("data/processed/correlation_report.md"),
]

OUT_JSON = Path("data/processed/detections.json")
OUT_MD = Path("data/processed/detector_report.md")

CFG_PATH = Path("config/detector.yaml")


def _load_cfg() -> Optional[dict]:
    if CFG_PATH.exists():
        try:
            return yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            logger.warning("YAML betöltési hiba (%s), folytatás defaulttal.", e)
            return None
    return None


def _ensure_output_dir() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)


def _schema_columns_any(path: Optional[Path]) -> List[str]:
    """CSV/Parquet esetén oszlopok; JSON/MD/TXT esetén üres lista (szöveges/rekordos input)."""
    if not path or not path.exists():
        return []
    suf = path.suffix.lower()
    try:
        if suf == ".parquet":
            try:
                pf = pq.ParquetFile(path)
                return list(pf.schema.names)
            except Exception:
                return list(pd.read_parquet(path).columns)
        elif suf == ".csv":
            return list(pd.read_csv(path, nrows=0).columns)
        elif suf == ".json":
            # JSON nem feltétlen táblás; a Detektor agent kontextusként kapja
            return []
        elif suf in (".md", ".txt"):
            return []  # szöveges riport
        else:
            # Fallback: próbáljuk meg CSV-nek
            return list(pd.read_csv(path, nrows=0).columns)
    except Exception as e:
        logger.warning("Schema olvasás sikertelen (%s): %s", path, e)
        return []


def _first_existing(paths: List[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None


def main() -> None:
    _ensure_output_dir()
    cfg = _load_cfg()

    # --- CLEANED kiválasztása ---
    # Ha YAML-ban megadott path van, azt használjuk; ha nincs, próbáljuk a jelölteket.
    cleaned_path: Optional[Path] = None
    if cfg and "data" in cfg and cfg["data"].get("cleaned_path"):
        cleaned_path = Path(cfg["data"]["cleaned_path"])
    else:
        cleaned_path = _first_existing(DEFAULT_CLEANED_CANDIDATES)

    # CLEANED nem kötelező a korrelátor-only üzemmódban, de ha van Parquet/CSV, validáljuk a sémát.
    cleaned_cols = _schema_columns_any(cleaned_path)
    if cleaned_path and not cleaned_cols and cleaned_path.suffix.lower() in (".csv", ".parquet"):
        raise RuntimeError(f"A CLEANED fájl olvashatatlan vagy üres sémával: {cleaned_path}")

    # --- CORR kiválasztása (AUTOMATIKUS FALLBACK) ---
    corr_path: Optional[Path] = None
    if cfg and "data" in cfg and cfg["data"].get("corr_path"):
        corr_path = Path(cfg["data"]["corr_path"])
        if not corr_path.exists():
            logger.info("YAML-ban megadott CORR fájl nem létezik (%s), fallback lista indul.", corr_path)
            corr_path = _first_existing(DEFAULT_CORR_CANDIDATES)
    else:
        corr_path = _first_existing(DEFAULT_CORR_CANDIDATES)

    corr_exists = bool(corr_path and corr_path.exists())
    corr_cols = _schema_columns_any(corr_path) if corr_exists else []

    if not corr_exists:
        logger.info("CORR fájl nincs megadva vagy nem található — Detektor korrelátor nélkül fut.")
    else:
        logger.info("CORR input: %s (cols=%s)", corr_path, len(corr_cols) if corr_cols else 0)

    # --- Agent és Task ---
    agent = build_detector_smith_agent()
    task = build_detector_smith_task(
        cleaned_path=str(cleaned_path) if cleaned_path else "",
        corr_path=str(corr_path) if corr_exists else "",
        output_json_path=str(OUT_JSON),
        output_md_path=str(OUT_MD),
    )
    task.agent = agent

    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()

    # --- Kimenet feldolgozás (változatlan logika) ---
    json_part = None
    md_part = None

    if isinstance(result, dict):
        json_part = result.get("json")
        md_part = result.get("md")
    elif isinstance(result, str):
        try:
            parsed = json.loads(result)
            json_part = parsed
        except Exception:
            md_part = result
    else:
        text = getattr(result, "raw", None) or getattr(result, "output", None) or str(result)
        try:
            parsed = json.loads(text)
            json_part = parsed
        except Exception:
            md_part = text

    try:
        if json_part is not None:
            if isinstance(json_part, str):
                OUT_JSON.write_text(json_part, encoding="utf-8")
            else:
                OUT_JSON.write_text(json.dumps(json_part, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            OUT_JSON.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning("JSON mentés nem sikerült (%s): %s", OUT_JSON, e)
        OUT_JSON.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")

    try:
        if md_part:
            OUT_MD.write_text(md_part, encoding="utf-8")
        else:
            OUT_MD.write_text("# Detektor riport\n\n(Nem érkezett külön magyarázat.)", encoding="utf-8")
    except Exception as e:
        logger.warning("MD mentés nem sikerült (%s): %s", OUT_MD, e)

    logger.info("Detektor befejezve. JSON: %s | MD: %s", OUT_JSON, OUT_MD)


if __name__ == "__main__":
    main()
