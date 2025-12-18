import pandas as pd
import os
from langchain.tools import tool

@tool("clean_dataframe")
def clean_dataframe(input_text: str):
    """
    Összetett adattisztító folyamat. 
    A data/raw/csv/data.csv fájlt dolgozza fel és menti a data/processed/cleaned.csv-be.
    """
    try:
        # Relatív útvonalak meghatározása a projekt gyökeréhez képest
        source = "data/raw/csv/data.csv"
        target_dir = "data/processed"
        target_file = os.path.join(target_dir, "cleaned.csv")

        # Ellenőrzés: Létezik-e a célmappa, ha nem, létrehozás
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        # Ellenőrzés: Megtalálható-e a forrásfájl
        if not os.path.exists(source):
            return f"HIBA: A forrásfájl nem található: {source}"

        # Adatbeolvasás: Az első 100.000 sor betöltése a memória védelme érdekében
        df = pd.read_csv(source, nrows=100000, low_memory=False)
        
        # Tisztítás 1: Duplikált sorok eltávolítása
        df = df.drop_duplicates()

        # Tisztítás 2: Hiányzó értékek kitöltése (szövegnél 'N/A', számnál 0)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('N/A')
            else:
                df[col] = df[col].fillna(0)

        # Tisztítás 3: Oszlopnevek szabványosítása (kisbetű, szóközmentesítés)
        df.columns = [str(col).strip().lower() for col in df.columns]

        # Eredmény mentése CSV formátumban
        df.to_csv(target_file, index=False)

        # Visszajelzés az ügynöknek a sikeres lefutásról
        return f"SIKER: Az adatok tisztítása befejeződött. Új fájl: {target_file}"

    except Exception as e:
        # Hiba esetén a pontos hibaüzenet továbbítása
        return f"HIBA a tisztítás során: {str(e)}"
