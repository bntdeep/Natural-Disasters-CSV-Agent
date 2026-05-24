from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd

from mcp_server.data import apply_filters, get_distinct
from mcp_server.schema import (
    AggregateParams,
    FilterParams,
    FilterRowsParams,
    SearchParams,
    TimeSeriesParams,
    TopNParams,
)

_MAX_ROWS = 200


def _clean(val: Any) -> Any:
    """Replace NaN/Inf with None for JSON safety."""
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


def _rows_to_records(df: pd.DataFrame) -> list[dict]:
    records = df.to_dict(orient="records")
    return [{k: _clean(v) for k, v in row.items()} for row in records]


def get_schema(df: pd.DataFrame) -> dict:
    """Return dataset schema, distinct categorical values, and year range."""
    year_min = int(df["year"].min()) if not df["year"].isna().all() else None
    year_max = int(df["year"].max()) if not df["year"].isna().all() else None

    return {
        "total_rows": len(df),
        "year_range": [year_min, year_max],
        "columns": {col: str(df[col].dtype) for col in df.columns},
        "distinct_values": {
            "disaster_group": get_distinct(df, "disaster_group"),
            "disaster_subgroup": get_distinct(df, "disaster_subgroup"),
            "disaster_type": get_distinct(df, "disaster_type"),
            "continent": get_distinct(df, "continent"),
            "region": get_distinct(df, "region"),
        },
        "metrics_note": (
            "Damage values (insured_damages_kusd, total_damages_kusd) are in "
            "thousands of US dollars. Use 'events' as metric to count rows."
        ),
    }


def filter_disasters(params: FilterRowsParams, df: pd.DataFrame) -> dict:
    """Return rows matching filters, capped at params.limit (max 200)."""
    filtered = apply_filters(df, params.filters.model_dump())
    total = len(filtered)
    limit = min(params.limit, _MAX_ROWS)
    truncated = total > limit
    return {
        "rows": _rows_to_records(filtered.head(limit)),
        "total_matched": total,
        "truncated": truncated,
    }


def _compute_metric(group: pd.core.groupby.DataFrameGroupBy, metric: str, agg: str) -> pd.Series:
    if metric == "events":
        return group.size()
    col = group[metric]
    ops = {
        "sum": col.sum,
        "mean": col.mean,
        "count": col.count,
        "max": col.max,
        "min": col.min,
        "median": col.median,
    }
    return ops[agg]()


def aggregate(params: AggregateParams, df: pd.DataFrame) -> dict:
    """Group by a column and aggregate a metric."""
    filtered = apply_filters(df, params.filters.model_dump())
    if filtered.empty:
        return {"group_by": params.group_by, "metric": params.metric, "agg": params.agg, "rows": []}

    grp = filtered.groupby(params.group_by, dropna=True)
    series = _compute_metric(grp, params.metric, params.agg)
    result = (
        series.reset_index()
        .rename(columns={series.name or 0: "value", params.group_by: "key"})
        .sort_values(["value", "key"], ascending=[False, True])
        .head(params.limit)
    )
    result["value"] = result["value"].apply(_clean)
    return {
        "group_by": params.group_by,
        "metric": params.metric,
        "agg": params.agg,
        "rows": result.to_dict(orient="records"),
    }


def top_n(params: TopNParams, df: pd.DataFrame) -> dict:
    """Return top N entities by a metric."""
    filtered = apply_filters(df, params.filters.model_dump())
    if filtered.empty:
        return {"metric": params.metric, "by": params.by, "rows": []}

    grp = filtered.groupby(params.by, dropna=True)
    series = _compute_metric(grp, params.metric, params.agg)
    result = (
        series.reset_index()
        .rename(columns={series.name or 0: "value", params.by: "key"})
        .sort_values("value", ascending=False)
        .head(params.n)
    )
    result["value"] = result["value"].apply(_clean)
    return {
        "metric": params.metric,
        "by": params.by,
        "agg": params.agg,
        "rows": result.to_dict(orient="records"),
    }


def time_series(params: TimeSeriesParams, df: pd.DataFrame) -> dict:
    """Return year-bucketed series sorted ascending."""
    filtered = apply_filters(df, params.filters.model_dump())
    if filtered.empty:
        return {"metric": params.metric, "agg": params.agg, "points": []}

    grp = filtered.groupby("year", dropna=True)
    series = _compute_metric(grp, params.metric, params.agg)
    result = series.reset_index().rename(columns={series.name or 0: "value", "year": "year"})
    result = result.sort_values("year")
    result["year"] = result["year"].apply(lambda y: int(y) if not _is_nan(y) else None)
    result["value"] = result["value"].apply(_clean)
    return {
        "metric": params.metric,
        "agg": params.agg,
        "points": result.to_dict(orient="records"),
    }


def _is_nan(v: Any) -> bool:
    try:
        return math.isnan(v)
    except TypeError:
        return False


def summary_stats(params: FilterParams, df: pd.DataFrame) -> dict:
    """Return aggregate stats for a filter slice."""
    filtered = apply_filters(df, params.model_dump())

    def safe_sum(col: str) -> float | None:
        s = filtered[col].sum() if col in filtered.columns else 0.0
        return _clean(float(s))

    by_type: list[dict] = []
    if "disaster_type" in filtered.columns:
        counts = (
            filtered.groupby("disaster_type", dropna=True)
            .size()
            .reset_index()
            .rename(columns={0: "count"})
            .sort_values("count", ascending=False)
        )
        by_type = counts.to_dict(orient="records")

    year_col = filtered["year"].dropna()
    return {
        "event_count": len(filtered),
        "total_deaths": safe_sum("total_deaths"),
        "no_injured": safe_sum("no_injured"),
        "total_affected": safe_sum("total_affected"),
        "total_damages_kusd": safe_sum("total_damages_kusd"),
        "by_disaster_type": by_type,
        "year_range": [
            int(year_col.min()) if not year_col.empty else None,
            int(year_col.max()) if not year_col.empty else None,
        ],
    }


def search_events(params: SearchParams, df: pd.DataFrame) -> dict:
    """Case-insensitive substring search across selected text fields."""
    query_lower = params.query.lower()
    mask = pd.Series([False] * len(df), index=df.index)
    for field in params.fields:
        if field in df.columns:
            mask |= df[field].fillna("").str.lower().str.contains(query_lower, regex=False)

    matched = df[mask]
    total = len(matched)
    limit = min(params.limit, _MAX_ROWS)
    return {
        "query": params.query,
        "total_matched": total,
        "rows": _rows_to_records(matched.head(limit)),
    }
