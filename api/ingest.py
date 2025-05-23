#!/usr/bin/env python3
# ingest.py

from pathlib import Path
import pandas as pd

def main():
    DATA = Path(__file__).parent / "data"
    # 1) Load building & energy
    bld_cols  = ["PNU","지번주소명","도로명대지위치","건물명","시군구코드"]
    eng_cols  = ["PNU","사용년월","사용량(KWh)"]
    bld       = pd.read_csv(DATA/"building_daegu.csv", usecols=bld_cols, low_memory=False)
    eng       = pd.read_csv(DATA/"energy_daegu.csv",    usecols=eng_cols, low_memory=False)
    merged    = eng.merge(bld, on="PNU", how="left")

    # 2) Parse & rename
    merged["month"] = pd.to_datetime(merged["사용년월"].astype(str) + "01",
                                     format="%Y%m%d")
    merged = merged.rename(columns={
        "사용량(KWh)": "kwh",
        "건물명":       "name",
        "지번주소명":   "addr"
    })

    # 3) Save normalized merged data
    out = Path(__file__).parent / "merged.parquet"
    merged.to_parquet(out, index=False)
    print(f"Wrote merged data to {out}")

    # 4) Build pop_long for per-capita lookups
    pop = pd.read_csv(DATA/"population.csv", low_memory=False)
    # only district-level rows where 법정동코드 == 0
    pop = pop[pop["법정동코드"] == 0]
    pop_cols = [c for c in pop.columns if c.endswith("_총인구수")]
    pop_long = pop[["시군구코드"] + pop_cols].melt(
        id_vars=["시군구코드"],
        value_vars=pop_cols,
        var_name="period",
        value_name="population"
    )
    pop_long["period"] = (
        pop_long["period"]
        .str.replace("년", "", regex=False)
        .str.replace("월_총인구수", "", regex=False)
    )
    pop_long["population"] = (
        pop_long["population"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(int)
    )

    out2 = Path(__file__).parent / "pop_long.parquet"
    pop_long.to_parquet(out2, index=False)
    print(f"Wrote population data to {out2}")

if __name__ == "__main__":
    main()
