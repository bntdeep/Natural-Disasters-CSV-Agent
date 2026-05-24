from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

AggOp = Literal["sum", "mean", "count", "max", "min", "median"]

Metric = Literal[
    "total_deaths",
    "no_injured",
    "no_affected",
    "no_homeless",
    "total_affected",
    "insured_damages_kusd",
    "total_damages_kusd",
    "events",  # synthetic: count of rows
]

GroupBy = Literal[
    "country",
    "iso",
    "continent",
    "region",
    "disaster_type",
    "disaster_group",
    "disaster_subgroup",
    "year",
]

SearchField = Literal["event_name", "location", "country"]


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
    fields: list[SearchField] = ["event_name", "location"]
    limit: int = 50
