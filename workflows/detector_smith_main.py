
# workflows/detector_smith_main.py
from __future__ import annotations

import sys
import json
import logging
from pathlib import Path
from typing import Optional, List

import pyarrow.parquet as pq
import pandas as pd
# PyYAML a confighoz
import yaml
from crewai import Crew

from agents.detector_smith_agent import build_detector_smith_agent
from tasks.detector_smith_task import build_detector_smith_task

# --- Logging beállítás ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("detector_main")

# --- Project ROOT a sys.path-ban (opcionális) ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Alapértelmezett path-ok (YAML felülírhatja) ---
DEFAULT_CLEANED = Path("data/processed/cleaned.parquet")
DEFAULT_CORR = Path("data/processed/correlation.parquet")
OUT_JSON = Path("data/processed/detections.json")
OUT_MD = Path("data/processed/detector_report.md")

CFG_PATH = Path("configs/detector.yaml")


def _load_cfg() -> Optional[dict]:
    """Betölti a configs/detector.yaml-t, ha létezik."""
    if CFG_PATH.exists():
        try:
            return yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            logger.warning("YAML betöltési hiba (%s), folytatás defaulttal.", e)
            return None
    return None


def _ensure_output_dir() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)


def _schema_columns(parquet_path: Path) -> List[str]:
    """Parquet schema oszlopok gyors kiolvasása; pandas fallback."""
    try:
        pf = pq.ParquetFile(parquet_path)
        return list(pf.schema.names)
    except Exception as e:  # egyes környezetekben több Arrow kivétel lehet
        logger.warning("pyarrow schema olvasás nem sikerült (%s), fallback pandas-ra: %s", parquet_path, e)
        # Fallback: pandas (ha a fájl tényleg olvasható Parquet)
        try:
            return list(pd.read_parquet(parquet_path).columns)
        except Exception as e2:
            logger.error("pandas read_parquet sem sikerült (%s): %s", parquet_path, e2)
            raise


def main() -> None:
    _ensure_output_dir()

    # --- Config beolvasása ---
    cfg = _load_cfg()

    # --- Path-ok a YAML-ból vagy defaultból ---
    cleaned_path = Path(cfg["data"]["cleaned_path"]) if (cfg and "data" in cfg and cfg["data"].get("cleaned_path")) else DEFAULT_CLEANED
    corr_path = Path(cfg["data"]["corr_path"]) if (cfg and "data" in cfg and cfg["data"].get("corr_path")) else DEFAULT_CORR

    if not cleaned_path.exists():
        raise RuntimeError(f"A CLEANED fájl nem található: {cleaned_path}")

    corr_exists = corr_path.exists()
    if not corr_exists:
        logger.info("CORR fájl nincs megadva vagy nem található (%s) — correlator nélkül futunk.", corr_path)

    # --- Oszlopséma kiolvasás ---
    cleaned_cols = _schema_columns(cleaned_path)
    corr_cols: List[str] = []
    if corr_exists:
        try:
            corr_cols = _schema_columns(corr_path)
        except Exception as e:
            logger.warning("CORR schema olvasás sikertelen (%s): %s", corr_path, e)
            corr_cols = []

    # --- Minimális validálás ---
    if not cleaned_cols:
        raise RuntimeError("A CLEANED Parquet fájl üres vagy nem olvasható oszlopokkal.")
    # corr_cols lehet üres, ez nem fatális

    # --- Agent (Ollama/mistral) ---
    agent = build_detector_smith_agent()

    # --- Task (agent később hozzárendelve) ---
    task = build_detector_smith_task(
        cleaned_path=str(cleaned_path),
        corr_path=str(corr_path) if corr_exists else None,
        output_json_path=str(OUT_JSON),
        output_md_path=str(OUT_MD),
    )
    task.agent = agent

    # --- Crew és kickoff ---
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()

    # --- Kimenet feldolgozás ---
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
            md_part = result  # ha nem JSON, mehet Markdownba
    else:
        # Bizonyos CrewAI verziók AgentResult-szerű objektumot adhatnak
        text = getattr(result, "raw", None) or getattr(result, "output", None) or str(result)
        try:
            parsed = json.loads(text)
            json_part = parsed
        except Exception:
            md_part = text

    # --- JSON mentés ---
    try:
        if json_part is not None:
            if isinstance(json_part, str):
                # Nyers szöveg fallback — legyen artefakt
                OUT_JSON.write_text(json_part, encoding="utf-8")
            else:
                OUT_JSON.write_text(json.dumps(json_part, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            # Ha nincs JSON, legalább üres lista
            OUT_JSON.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning("JSON mentés nem sikerült (%s): %s", OUT_JSON, e)
        OUT_JSON.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")

    # --- MD mentés ---
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
