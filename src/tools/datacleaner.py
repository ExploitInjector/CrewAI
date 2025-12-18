import pandas as pd # Pandas könyvtár az adatkezeléshez
import os # OS könyvtár a mappák és fájlútvonalak kezeléséhez
from langchain.tools import tool # CrewAI/LangChain dekorátor az eszközhöz

@tool("clean_dataframe")
def clean_dataframe(input_text: str):
    """
    Összetett adattisztító eszköz: beolvassa a nyers adatokat, 
    kezeli a hiányzó értékeket és elmenti a tisztított fájlt.
    """
    try:
        # A te konkrét mappaszerkezeted szerinti forrásfájl útvonala
        source = "data/raw/csv/data.csv" 
        # A kimeneti fájl helye, amit a többi ügynök használni fog
        target = "output/cleaned_data.csv"
        
        # Ellenőrizzük, hogy létezik-e az output mappa, ha nem, létrehozzuk
        os.makedirs("output", exist_ok=True)
        
        # Hibakezelés: Ha nem találjuk a fájlt a megadott helyen
        if not os.path.exists(source):
            return f"HIBA: A forrásfájl nem található: {source}"

        # Adatbeolvasás: Az első 50.000 sor betöltése (memória kímélése céljából)
        df = pd.read_csv(source, nrows=50000, low_memory=False)
        
        # Statisztika készítése a tisztítás előtti állapotról
        initial_count = len(df)
        
        # 1. Lépés: Duplikált sorok eltávolítása
        df = df.drop_duplicates()
        
        # 2. Lépés: Hiányzó (NaN) értékek kitöltése alapértelmezett értékkel
        # A numerikus oszlopokat 0-val, a szövegeseket 'Unknown'-nal töltjük fel
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('Unknown')
            else:
                df[col] = df[col].fillna(0)
        
        # 3. Lépés: Adattípusok egységesítése (minden oszlopnév legyen kisbetűs)
        df.columns = [str(col).lower() for col in df.columns]
        
        # Tisztított adatok elmentése CSV formátumban
        df.to_csv(target, index=False)
        
        # Összetett válasz küldése az Ollama ügynöknek a sikeres folyamatról
        return (f"SIKER: Adattisztítás befejezve.\n"
                f"- Eredeti sorok száma: {initial_count}\n"
                f"- Tisztított sorok száma: {len(df)}\n"
                f"- Mentési hely: {target}")
                
    except Exception as e:
        # Bármilyen hiba esetén részletes hibaüzenet küldése
        return f"Váratlan hiba történt az adattisztítás során: {str(e)}"
