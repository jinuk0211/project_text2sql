-- file: create_view.sql
DROP MATERIALIZED VIEW IF EXISTS district_percapita;

CREATE MATERIALIZED VIEW district_percapita AS
SELECT
    district_code,
    month,                          -- YYYY-MM date column
    SUM(kwh)                AS total_kwh,
    SUM(population)         AS population,
    ROUND(SUM(kwh)::numeric / NULLIF(SUM(population),0), 2)
                            AS kwh_per_person
FROM energy_merged
WHERE district_code IS NOT NULL
GROUP BY district_code, month;

CREATE INDEX ON district_percapita (month);


DROP VIEW IF EXISTS district_month_pop;
CREATE VIEW district_month_pop AS
SELECT
    p."시군구코드"      AS district_code,
    to_date(period, 'YYYYMM')::date AS month,
    population
FROM population_long p;        -- ← your melted population table






CREATE MATERIALIZED VIEW public.district_percapita AS
SELECT
    district_code,
    month,
    ROUND(SUM(kwh)::numeric,2)          AS kwh_total,
    SUM(population)                     AS population_total,
    ROUND(SUM(kwh)::numeric / NULLIF(SUM(population),0), 2)
                                         AS kwh_per_person
FROM   energy_merged
WHERE  district_code IS NOT NULL
GROUP  BY district_code, month;

-- optional: indexes for speed
CREATE INDEX ON public.district_percapita (month);
CREATE INDEX ON public.district_percapita (district_code);

-- populate immediately
REFRESH MATERIALIZED VIEW public.district_percapita;