from __future__ import annotations

import json
import math

import pandas as pd
import pytest

from mcp_server import tools
from mcp_server.schema import (
    AggregateParams,
    FilterParams,
    FilterRowsParams,
    SearchParams,
    TimeSeriesParams,
    TopNParams,
)


def is_json_serializable(obj) -> bool:
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


def has_no_nan(obj) -> bool:
    if isinstance(obj, float):
        return not math.isnan(obj)
    if isinstance(obj, dict):
        return all(has_no_nan(v) for v in obj.values())
    if isinstance(obj, list):
        return all(has_no_nan(v) for v in obj)
    return True


class TestGetSchema:
    def test_returns_year_range(self, df):
        result = tools.get_schema(df)
        yr = result["year_range"]
        assert yr[0] == 1900
        assert yr[1] >= yr[0]

    def test_returns_distinct_disaster_types(self, df):
        result = tools.get_schema(df)
        types = result["distinct_values"]["disaster_type"]
        assert "Flood" in types
        assert "Drought" in types

    def test_returns_total_rows(self, df):
        result = tools.get_schema(df)
        assert result["total_rows"] == 50

    def test_json_serializable(self, df):
        assert is_json_serializable(tools.get_schema(df))


class TestFilterDisasters:
    def test_default_limit(self, df):
        result = tools.filter_disasters(FilterRowsParams(), df)
        assert len(result["rows"]) == 50
        assert result["total_matched"] == 50
        assert result["truncated"] is False

    def test_limit_applied(self, df):
        result = tools.filter_disasters(FilterRowsParams(limit=5), df)
        assert len(result["rows"]) == 5
        assert result["total_matched"] == 50
        assert result["truncated"] is True

    def test_country_filter(self, df):
        params = FilterRowsParams(filters=FilterParams(country="India"))
        result = tools.filter_disasters(params, df)
        assert result["total_matched"] == 4
        assert all(r["country"] == "India" for r in result["rows"])

    def test_empty_filter_result(self, df):
        params = FilterRowsParams(filters=FilterParams(country="Neverland"))
        result = tools.filter_disasters(params, df)
        assert result["rows"] == []
        assert result["total_matched"] == 0

    def test_no_nan_in_output(self, df):
        result = tools.filter_disasters(FilterRowsParams(limit=10), df)
        assert has_no_nan(result)

    def test_json_serializable(self, df):
        assert is_json_serializable(tools.filter_disasters(FilterRowsParams(), df))


class TestAggregate:
    def test_basic_sum(self, df):
        params = AggregateParams(group_by="continent", metric="total_deaths")
        result = tools.aggregate(params, df)
        assert result["group_by"] == "continent"
        assert len(result["rows"]) > 0
        assert "key" in result["rows"][0]
        assert "value" in result["rows"][0]

    def test_count_agg(self, df):
        params = AggregateParams(group_by="disaster_type", metric="events", agg="count")
        result = tools.aggregate(params, df)
        total = sum(r["value"] for r in result["rows"])
        assert total == 50

    def test_sorted_desc(self, df):
        params = AggregateParams(group_by="country", metric="total_deaths")
        result = tools.aggregate(params, df)
        values = [r["value"] for r in result["rows"] if r["value"] is not None]
        assert values == sorted(values, reverse=True)

    def test_empty_filter(self, df):
        params = AggregateParams(
            group_by="country", metric="total_deaths",
            filters=FilterParams(country="Neverland"),
        )
        result = tools.aggregate(params, df)
        assert result["rows"] == []

    def test_limit_respected(self, df):
        params = AggregateParams(group_by="country", metric="events", agg="count", limit=3)
        result = tools.aggregate(params, df)
        assert len(result["rows"]) <= 3

    def test_no_nan(self, df):
        params = AggregateParams(group_by="continent", metric="total_damages_kusd")
        assert has_no_nan(tools.aggregate(params, df))

    def test_json_serializable(self, df):
        params = AggregateParams(group_by="disaster_type", metric="total_deaths")
        assert is_json_serializable(tools.aggregate(params, df))


class TestTopN:
    def test_top3_deaths(self, df):
        result = tools.top_n(TopNParams(metric="total_deaths", by="country", n=3), df)
        assert len(result["rows"]) == 3
        assert result["rows"][0]["key"] == "India"

    def test_n_greater_than_rows(self, df):
        result = tools.top_n(TopNParams(metric="total_deaths", by="country", n=1000), df)
        assert len(result["rows"]) <= 50

    def test_n_zero_returns_empty(self, df):
        result = tools.top_n(TopNParams(metric="total_deaths", by="country", n=0), df)
        assert result["rows"] == []

    def test_empty_filter(self, df):
        result = tools.top_n(
            TopNParams(metric="total_deaths", by="country", filters=FilterParams(country="Neverland")),
            df,
        )
        assert result["rows"] == []

    def test_events_metric(self, df):
        result = tools.top_n(TopNParams(metric="events", by="continent", n=5), df)
        assert len(result["rows"]) > 0

    def test_no_nan(self, df):
        assert has_no_nan(tools.top_n(TopNParams(metric="total_deaths", by="country"), df))

    def test_json_serializable(self, df):
        assert is_json_serializable(tools.top_n(TopNParams(metric="total_deaths", by="country"), df))


class TestTimeSeries:
    def test_points_sorted_asc(self, df):
        result = tools.time_series(TimeSeriesParams(metric="events", agg="count"), df)
        years = [p["year"] for p in result["points"]]
        assert years == sorted(years)

    def test_years_are_ints(self, df):
        result = tools.time_series(TimeSeriesParams(metric="events", agg="count"), df)
        for p in result["points"]:
            assert isinstance(p["year"], int)

    def test_sum_matches_total(self, df):
        result = tools.time_series(TimeSeriesParams(metric="events", agg="count"), df)
        total = sum(p["value"] for p in result["points"])
        assert total == 50

    def test_empty_filter(self, df):
        result = tools.time_series(
            TimeSeriesParams(metric="total_deaths", filters=FilterParams(country="Neverland")),
            df,
        )
        assert result["points"] == []

    def test_no_nan(self, df):
        assert has_no_nan(tools.time_series(TimeSeriesParams(metric="total_deaths"), df))

    def test_json_serializable(self, df):
        assert is_json_serializable(tools.time_series(TimeSeriesParams(metric="total_deaths"), df))


class TestSummaryStats:
    def test_event_count(self, df):
        result = tools.summary_stats(FilterParams(), df)
        assert result["event_count"] == 50

    def test_total_deaths_positive(self, df):
        result = tools.summary_stats(FilterParams(), df)
        assert result["total_deaths"] > 0

    def test_by_type_breakdown(self, df):
        result = tools.summary_stats(FilterParams(), df)
        assert len(result["by_disaster_type"]) > 0
        types = [r["disaster_type"] for r in result["by_disaster_type"]]
        assert "Flood" in types

    def test_by_type_counts_sum(self, df):
        result = tools.summary_stats(FilterParams(), df)
        total = sum(r["count"] for r in result["by_disaster_type"])
        assert total == 50

    def test_filtered_subset(self, df):
        result = tools.summary_stats(FilterParams(country="India"), df)
        assert result["event_count"] == 4

    def test_empty_filter_result(self, df):
        result = tools.summary_stats(FilterParams(country="Neverland"), df)
        assert result["event_count"] == 0
        assert result["total_deaths"] == 0.0

    def test_no_nan(self, df):
        assert has_no_nan(tools.summary_stats(FilterParams(), df))

    def test_json_serializable(self, df):
        assert is_json_serializable(tools.summary_stats(FilterParams(), df))


class TestSearchEvents:
    def test_finds_country(self, df):
        result = tools.search_events(SearchParams(query="India", fields=["country"]), df)
        assert result["total_matched"] == 4

    def test_case_insensitive(self, df):
        result = tools.search_events(SearchParams(query="india", fields=["country"]), df)
        assert result["total_matched"] == 4

    def test_no_match_returns_empty(self, df):
        result = tools.search_events(SearchParams(query="xyznotfound"), df)
        assert result["rows"] == []
        assert result["total_matched"] == 0

    def test_limit_applied(self, df):
        result = tools.search_events(
            SearchParams(query="a", fields=["country"], limit=2), df
        )
        assert len(result["rows"]) <= 2

    def test_multiple_fields(self, df):
        result = tools.search_events(
            SearchParams(query="Bengal", fields=["event_name", "location", "country"]), df
        )
        assert result["total_matched"] > 0

    def test_no_nan(self, df):
        assert has_no_nan(
            tools.search_events(SearchParams(query="flood", fields=["location"]), df)
        )

    def test_json_serializable(self, df):
        assert is_json_serializable(
            tools.search_events(SearchParams(query="storm"), df)
        )
