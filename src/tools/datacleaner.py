import pandas as pd
import os
import logging
from langchain.tools import tool

# Naplózás beállítása, hogy lássuk a folyamatot a konzolon
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@tool("clean_dataframe")
def clean_dataframe(input_text: str):
    """
    Hálózati IDS logok professzionális tisztítása, normalizálása és validálása.
    Forrás: data/raw/csv/data.csv | Cél: data/processed/cleaned.csv
    """
    try:
        # Útvonalak meghatározása
        source = "data/raw/csv/data.csv"
        target_dir = "data/processed"
        target_file = os.path.join(target_dir, "cleaned.csv")

        # Ellenőrizzük, hogy létezik-e a forrásfájl, mielőtt belekezdünk
        if not os.path.exists(source):
            return f"HIBA: A forrásállomány nem található a megadott helyen: {source}"

        # Adatok betöltése (az első 100.000 sor, hogy ne fogyjon el a memória)
        logging.info("Adatok betöltése folyamatban...")
        df = pd.read_csv(source, nrows=100000, low_memory=False)

        # 1. LÉPÉS: Duplikátumok eltávolítása (megtartjuk az első előfordulást)
        initial_count = len(df)
        df = df.drop_duplicates()
        removed_dupes = initial_count - len(df)

        # 2. LÉPÉS: Oszlopnevek szabványosítása (kisbetű, szóközök cseréje alulvonásra)
        df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

        # 3. LÉPÉS: Üres (NaN) értékek kezelése
        # A szöveges oszlopoknál 'unknown', a számoknál 0 értéket adunk meg
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('unknown')
            else:
                df[col] = df[col].fillna(0)

        # 4. LÉPÉS: Adattípusok kényszerítése a pontosság érdekében
        # Például biztosítjuk, hogy a portok egész számok (int) legyenek, ha léteznek
        if 'destination_port' in df.columns:
            df['destination_port'] = pd.to_numeric(df['destination_port'], errors='coerce').fillna(0).astype(int)

        # 5. LÉPÉS: Extrém értékek (outlierek) alapvető szűrése
        # Például: negatív csomagméretek törlése, ami mérési hiba lehetne
        if 'packet_length' in df.columns:
            df = df[df['packet_length'] >= 0]

        # 6. LÉPÉS: Célkönyvtár létrehozása, ha még nem létezne
        os.makedirs(target_dir, exist_ok=True)

        # 7. LÉPÉS: A megtisztított adat mentése standard CSV formátumban
        df.to_csv(target_file, index=False)

        # Részletes visszajelzés az AI ügynök számára
        return (f"SIKER: Tisztítás befejezve.\n"
                f"- Eredeti sorok: {initial_count}\n"
                f"- Törölt duplikátumok: {removed_dupes}\n"
                f"- Jelenlegi sorok: {len(df)}\n"
                f"- Mentési útvonal: {target_file}")

    except Exception as e:
        # Hiba esetén részletes naplózás
        logging.error(f"Kritikus hiba az adattisztítás során: {str(e)}")
        return f"KRITIKUS HIBA: {str(e)}"
