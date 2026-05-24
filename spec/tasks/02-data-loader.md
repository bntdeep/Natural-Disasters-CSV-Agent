# Task #2 — CSV Loader & Normalization (`mcp_server/data.py`)

**Status:** pending
**Blocks:** #4
**Blocked by:** #1

## Goal
Load the CSV once at process start and expose helpers for filtering and column lookup.

## Deliverables

- `load_dataset(path: str | None = None) -> pd.DataFrame`
  - Reads the CSV from `DISASTERS_CSV_PATH` env or argument.
  - Normalizes column names: `Total Damages ('000 US$)` → `total_damages_kusd`, `Disaster Type` → `disaster_type`, etc. Build a stable mapping table (do not auto-derive — explicit dict).
  - Coerces numeric columns with `errors='coerce'`: `total_deaths`, `no_injured`, `no_affected`, `no_homeless`, `total_affected`, `insured_damages_kusd`, `total_damages_kusd`, `dis_mag_value`, `latitude`, `longitude`, `cpi`, `year`, `start_year`, `end_year`, etc.
- `apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame`
  - Supported keys: `country`, `iso`, `disaster_type`, `disaster_group`, `disaster_subgroup`, `continent`, `region`, `year_from`, `year_to`.
  - Case-insensitive equality for strings; range for years.
- `get_distinct(df, column) -> list[str]` — sorted unique non-null values.
- Module-level cache: `get_dataframe()` returns a singleton; idempotent.

## Acceptance
- Loading `1900_2021_DISASTERS_Example.csv` returns a DataFrame with 50 rows and snake_case columns.
- Numeric coercion turns blank strings into `NaN` (not `0`).
- `apply_filters(df, {"country": "india"})` matches rows where `country == "India"`.
