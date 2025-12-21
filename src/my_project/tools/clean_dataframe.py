import pandas as pd
import os
from pathlib import Path
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CleanInput(BaseModel):
    input_text: Optional[str] = Field(None, description="Request text (optional).")


class CleanDataFrameTool(BaseTool):
    name: str = "clean_dataframe"
    description: str = "Standardizes and cleans large scale network logs from data/raw/data.csv."
    args_schema: Type[BaseModel] = CleanInput

    def _run(self, input_text: Optional[str] = None) -> str:
        try:
            # Fix útvonalak használata, mert az ügynök hajlamos elgépelni őket
            source = Path("data/raw/data.csv")
            target_file = Path("data/processed/cleaned.csv")

            if not source.exists():
                return f"ERROR: Source file missing at {source.absolute()}"

            # Memóriahatékony beolvasás
            df = pd.read_csv(source, nrows=100000, low_memory=False)

            # Oszlopnevek normalizálása (Szóköz -> Alulvonás, Kisbetű)
            df.columns = [col.strip().lower().replace(' ', '_').replace('.', '_') for col in df.columns]

            # Tisztítási logika
            df = df.drop_duplicates()

            # Biztosítjuk a könyvtár létezését
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Mentés
            df.to_csv(target_file, index=False)

            return f"SUCCESS: {len(df)} rows cleaned and saved to {target_file}"
        except Exception as e:
            return f"CLEANING ERROR: {str(e)}"