import pandas as pd
import os
from langchain.tools import tool

@tool("clean_dataframe")
def clean_dataframe(input_path: str, output_path: str):
    """Beolvassa az IDS naplót, eltávolítja a zajt és kiegyensúlyozott mintát ment el."""
    try:
        if not os.path.exists(input_path):
            return f"Hiba: A fájl nem található: {input_path}"

        # 5GB miatt csak az elejét olvassuk teszteléshez
        df = pd.read_csv(input_path, nrows=100000, low_memory=False)
        
        df = df.drop_duplicates()
        df.columns = df.columns.str.strip()

        if 'Label' in df.columns:
            df_cleaned = df.groupby('Label').apply(lambda x: x.sample(n=min(len(x), 1000), random_state=42)).reset_index(drop=True)
        else:
            df_cleaned = df.sample(n=min(len(df), 5000), random_state=42)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        df_cleaned.to_csv(output_path, index=False)
        
        return f"Siker! Tisztított adatok mentve: {output_path}"
    except Exception as e:
        return f"Hiba: {str(e)}"﻿
