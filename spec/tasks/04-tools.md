# Task #4 — Pure Pandas Tool Functions (`mcp_server/tools.py`)

**Status:** pending
**Blocks:** #5, #6
**Blocked by:** #2, #3

## Goal
Implement each MCP tool as a **pure function** of `(params, dataframe) → JSON-serializable dict`. No MCP / LangChain coupling. This makes them trivial to unit-test.

## Deliverables

```python
def get_schema(df) -> dict:
    """Returns columns, dtypes, distinct values for key categoricals,
    and the year range — used by the LLM to ground filter values."""

def filter_disasters(params: FilterRowsParams, df) -> dict:
    """Returns rows matching filters, capped at params.limit (default 50, max 200).
    Output: {"rows": [...], "total_matched": int, "truncated": bool}"""

def aggregate(params: AggregateParams, df) -> dict:
    """Groupby + agg. Output: {"group_by": ..., "metric": ..., "agg": ...,
    "rows": [{"key": ..., "value": ...}, ...]}. Sorted by value desc."""

def top_n(params: TopNParams, df) -> dict:
    """Top N entities by metric. Output: {"rows": [{"key": ..., "value": ...}, ...]}"""

def time_series(params: TimeSeriesParams, df) -> dict:
    """Year-bucketed series. Output: {"metric": ..., "agg": ...,
    "points": [{"year": int, "value": float}, ...]}. Years sorted asc."""

def summary_stats(params: FilterParams, df) -> dict:
    """Count, totals, by-type breakdown for a filter slice.
    Output: {"event_count": int, "total_deaths": int, "total_damages_kusd": float,
             "by_disaster_type": [...], "year_range": [min, max]}"""

def search_events(params: SearchParams, df) -> dict:
    """Substring case-insensitive across selected fields.
    Output: {"rows": [...], "total_matched": int}"""
```

## Implementation notes

- The synthetic metric `"events"` maps to `len(group)` — useful for "how many disasters per year".
- Always replace `NaN` with `None` before returning (JSON cannot encode NaN).
- Cap row outputs to `min(params.limit, 200)`.
- Sort grouped results deterministically (value desc, then key asc) so output is stable across runs.

## Acceptance
- All functions are pure (no globals beyond reading `df`).
- Output is `json.dumps`-able without errors.
- `top_n` with `n > rows` returns all rows, no exception.
- Empty filter result returns `{"rows": [], ...}`, not error.
