#!/usr/bin/env python3
# load_sql.py – parquet → Postgres  +  (re)build materialised-view
# ---------------------------------------------------------------

import pandas as pd
from sqlalchemy import create_engine, text

PG_URI = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
engine = create_engine(PG_URI)

# ───────────────────────────────────────────────────────── TABLES ──
print("⏳ loading parquet …")
df  = pd.read_parquet("merged.parquet")[["PNU", "month", "kwh",
                                         "name", "addr", "시군구코드"]]
df  = df.rename(columns={"시군구코드": "district_code"})
pop = pd.read_parquet("pop_long.parquet")          \
        .rename(columns={"시군구코드": "district_code",
                         "period"     : "month"})
pop["month"] = pd.to_datetime(pop["month"] + "01", format="%Y%m%d")

with engine.begin() as conn:            # one autocommit block
    # ── 0) make sure *nothing* depends on the tables  ──────────────
    conn.exec_driver_sql("DROP MATERIALIZED VIEW IF EXISTS district_percapita CASCADE;")

    # ── 1) write / overwrite the base tables  ─────────────────────
    df.to_sql ("energy_merged",    conn, if_exists="replace", index=False)
    pop.to_sql("population_long",  conn, if_exists="replace", index=False)
    print(f"✅ loaded {len(df):,} rows  ->  energy_merged")
    print(f"✅ loaded {len(pop):,} rows ->  population_long")

    # ── 2) rebuild the materialised view  ─────────────────────────
    conn.exec_driver_sql("""
        CREATE TABLE district_percapita AS
        SELECT
            e.district_code,
            e.month,
            SUM(e.kwh)                         AS total_kwh,
            SUM(p.population)                  AS population,
            ROUND(
                SUM(e.kwh)::numeric
                / NULLIF(SUM(p.population),0), 2
            ) AS kwh_per_person
        FROM   energy_merged     e
        JOIN   population_long   p USING (district_code, month)
        WHERE  e.district_code IS NOT NULL
        GROUP  BY e.district_code, e.month;

        CREATE INDEX ON district_percapita (month);
    """)
    print("✅ materialised view district_percapita rebuilt")

print("🚀 done.")
