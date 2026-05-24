# Task #3 — Pydantic Input Schemas (`mcp_server/schema.py`)

**Status:** pending
**Blocks:** #4
**Blocked by:** #1

## Goal
Define typed input models for every MCP tool. The MCP server uses these for validation and the LLM uses them as tool signatures.

## Deliverables

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

AggOp = Literal["sum", "mean", "count", "max", "min", "median"]
Metric = Literal[
    "total_deaths", "no_injured", "no_affected", "no_homeless",
    "total_affected", "insured_damages_kusd", "total_damages_kusd",
    "events"  # synthetic — count of rows
]
GroupBy = Literal[
    "country", "iso", "continent", "region",
    "disaster_type", "disaster_group", "disaster_subgroup", "year"
]

class FilterParams(BaseModel):
    country: Optional[str] = None
    iso: Optional[str] = None
    disaster_type: Optional[str] = None
    disaster_group: Optional[str] = None
    disaster_subgroup: Optional[str] = None
    continent: Optional[str] = None
    region: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class AggregateParams(BaseModel):
    group_by: GroupBy
    metric: Metric
    agg: AggOp = "sum"
    filters: FilterParams = Field(default_factory=FilterParams)
    limit: int = 50

class TopNParams(BaseModel):
    metric: Metric
    by: GroupBy = "country"
    n: int = 10
    agg: AggOp = "sum"
    filters: FilterParams = Field(default_factory=FilterParams)

class TimeSeriesParams(BaseModel):
    metric: Metric
    agg: AggOp = "sum"
    filters: FilterParams = Field(default_factory=FilterParams)

class FilterRowsParams(BaseModel):
    filters: FilterParams = Field(default_factory=FilterParams)
    limit: int = 50

class SearchParams(BaseModel):
    query: str
    fields: list[Literal["event_name", "location", "country"]] = ["event_name", "location"]
    limit: int = 50
```

## Acceptance
- `AggregateParams.model_validate({...})` rejects unknown `metric` / `agg` values.
- `FilterParams()` constructs with no args (all optional).
- All schemas serialize cleanly with `model_dump()`.
