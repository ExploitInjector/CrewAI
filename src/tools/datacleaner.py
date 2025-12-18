import pandas as pd # Adatkezelő könyvtár (DataFrame-ekhez)
import os           # Fájlrendszer műveletekhez
from langchain.tools import tool # CrewAI által értelmezhető eszköz dekorátor

@tool("clean_dataframe")
def clean_dataframe(input_text: str):
    """
    Kifinomult adattisztító eszköz. 
    Beolvassa a nyers hálózati forgalmi adatokat a data/raw/csv/data.csv helyről,
    elvégzi a tisztítást (NaN kezelés, duplikátum szűrés), 
    majd menti a data/processed/cleaned.csv fájlba.
    """
    try:
        # --- ÚTVONALAK MEGHATÁROZÁSA ---
        # A projekt gyökérkönyvtárához viszonyított útvonalak
        source_path = "data/raw/csv/data.csv"
        target_path = "data/processed/cleaned.csv"
        
        # Ellenőrizzük, hogy a célmappa létezik-e (data/processed/)
        os.makedirs("data/processed", exist_ok=True)

        # --- FÁJL ELLENŐRZÉSE ---
        if not os.path.exists(source_path):
            return f"HIBA: A forrásfájl nem található: {source_path}. Kérlek ellenőrizd a mappát!"

        # --- ADATFELDOLGOZÁS ---
        # Csak az első 100.000 sort olvassuk be a sebesség és az Ollama válaszideje miatt
        df = pd.read_csv(source_path, nrows=100000, low_memory=False)
        
        # Eredeti sorok száma statisztikához
        original_count = len(df)

        # 1. Duplikált sorok eltávolítása
        df = df.drop_duplicates()

        # 2. Hiányzó adatok (NaN) intelligens kezelése
        # Számok esetén nullával, szövegnél 'N/A' felirattal pótoljuk
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('N/A')
            else:
                df[col] = df[col].fillna(0)

        # 3. Oszlopnevek tisztítása (szóközök eltávolítása, kisbetűsítés)
        df.columns = [str(col).strip().lower() for col in df.columns]

        # --- MENTÉS ---
        df.to_csv(target_path, index=False)

        # --- VISSZAJELZÉS AZ OLLAMA-NAK ---
        # Ez a szöveg kerül vissza az ágenshez, ebből fog "gondolkodni"
        return (f"SIKER: Az adattisztítás lezajlott.\n"
                f"- Forrás: {source_path}\n"
                f"- Mentve: {target_path}\n"
                f"- Eredeti sorok: {original_count}\n"
                f"- Tisztított sorok: {len(df)}\n"
                f"- Kezelt hiányzó értékek: Igen (NaN -> 0/NA)")

    except Exception as e:
        # Részletes hibaüzenet, ha valami elromlik (pl. jogosultság vagy memória)
        return f"Váratlan hiba az adattisztítás során: {str(e)}"
