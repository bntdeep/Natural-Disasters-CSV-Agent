from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Explicit mapping: original CSV column → snake_case internal name
COLUMN_MAP: dict[str, str] = {
    "Year": "year",
    "Seq": "seq",
    "Glide": "glide",
    "Disaster Group": "disaster_group",
    "Disaster Subgroup": "disaster_subgroup",
    "Disaster Type": "disaster_type",
    "Disaster Subtype": "disaster_subtype",
    "Disaster Subsubtype": "disaster_subsubtype",
    "Event Name": "event_name",
    "Country": "country",
    "ISO": "iso",
    "Region": "region",
    "Continent": "continent",
    "Location": "location",
    "Origin": "origin",
    "Associated Dis": "associated_dis",
    "Associated Dis2": "associated_dis2",
    "OFDA Response": "ofda_response",
    "Appeal": "appeal",
    "Declaration": "declaration",
    "Aid Contribution": "aid_contribution",
    "Dis Mag Value": "dis_mag_value",
    "Dis Mag Scale": "dis_mag_scale",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Local Time": "local_time",
    "River Basin": "river_basin",
    "Start Year": "start_year",
    "Start Month": "start_month",
    "Start Day": "start_day",
    "End Year": "end_year",
    "End Month": "end_month",
    "End Day": "end_day",
    "Total Deaths": "total_deaths",
    "No Injured": "no_injured",
    "No Affected": "no_affected",
    "No Homeless": "no_homeless",
    "Total Affected": "total_affected",
    "Insured Damages ('000 US$)": "insured_damages_kusd",
    "Total Damages ('000 US$)": "total_damages_kusd",
    "CPI": "cpi",
    "Adm Level": "adm_level",
    "Admin1 Code": "admin1_code",
    "Admin2 Code": "admin2_code",
    "Geo Locations": "geo_locations",
}

NUMERIC_COLUMNS = [
    "year", "seq", "dis_mag_value", "latitude", "longitude",
    "start_year", "start_month", "start_day",
    "end_year", "end_month", "end_day",
    "total_deaths", "no_injured", "no_affected", "no_homeless", "total_affected",
    "insured_damages_kusd", "total_damages_kusd", "cpi",
]

FILTER_STRING_COLUMNS = {
    "country", "iso", "disaster_type", "disaster_group",
    "disaster_subgroup", "continent", "region",
}


def load_dataset(path: str | None = None) -> pd.DataFrame:
    csv_path = path or os.getenv("DISASTERS_CSV_PATH", "docs/1900_2021_DISASTERS_Example.csv")
    df = pd.read_csv(csv_path, dtype=str)
    df = df.rename(columns=COLUMN_MAP)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@lru_cache(maxsize=1)
def get_dataframe() -> pd.DataFrame:
    return load_dataset()


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    result = df.copy()

    for key in FILTER_STRING_COLUMNS:
        val = filters.get(key)
        if not val:
            continue
        val_lower = val.lower()
        col = result[key].str.lower()

        # 1. Exact match (fast path — covers most cases)
        exact = result[col == val_lower]
        if not exact.empty:
            result = exact
            continue

        # 2. Word-boundary regex fallback
        # Handles "United States" → "United States of America (the)"
        # while avoiding "Niger" matching "Nigeria"
        import re
        pattern = r"\b" + re.escape(val_lower) + r"\b"
        result = result[col.str.contains(pattern, regex=True)]

    year_from = filters.get("year_from")
    year_to = filters.get("year_to")
    if year_from is not None:
        result = result[result["year"] >= year_from]
    if year_to is not None:
        result = result[result["year"] <= year_to]

    return result


def get_distinct(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().unique().tolist())
