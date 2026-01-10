
# src/tools/schema_probe.py
import pandas as pd

def probe_parquet(path="data/processed/correlation.parquet", n=1000):
    df = pd.read_parquet(path)
    print("\n=== Oszlopok ===")
    print(list(df.columns))

    print("\n=== Típusok ===")
    print(df.dtypes)

    print("\n=== Mintaértékek (max 3 per oszlop) ===")
    for col in df.columns:
        sample = df[col].head(3).to_list()
        print(f"- {col}: {sample}")

if __name__ == "__main__":
    probe_parquet()
