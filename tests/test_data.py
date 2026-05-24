from __future__ import annotations

import pandas as pd
import pytest

from mcp_server.data import apply_filters, get_dataframe, get_distinct, load_dataset


class TestLoadDataset:
    def test_row_count(self, df):
        assert len(df) == 50

    def test_column_count(self, df):
        assert len(df.columns) == 45

    def test_snake_case_columns(self, df):
        for col in df.columns:
            assert " " not in col, f"Column '{col}' still has spaces"
            assert "(" not in col, f"Column '{col}' still has parentheses"

    def test_key_columns_present(self, df):
        required = [
            "year", "country", "disaster_type", "continent", "region",
            "total_deaths", "total_damages_kusd", "insured_damages_kusd",
        ]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_numeric_coercion(self, df):
        assert df["total_deaths"].dtype == float
        assert df["total_damages_kusd"].dtype == float
        # year has no blanks in the fixture, so pandas infers int64 — both numeric types are correct
        assert df["year"].dtype in (float, int)

    def test_blank_becomes_nan_not_zero(self, df):
        """Blank strings in numeric cols must be NaN, never 0."""
        # India 1900 row has NaN for total_damages_kusd (blank in source)
        sample = df[df["country"] == "India"].iloc[0]
        assert pd.isna(sample["total_damages_kusd"])

    def test_singleton(self):
        df1 = get_dataframe()
        df2 = get_dataframe()
        assert df1 is df2


class TestApplyFilters:
    def test_country_case_insensitive(self, df):
        result = apply_filters(df, {"country": "india"})
        assert len(result) == 4
        assert all(result["country"] == "India")

    def test_country_exact_case(self, df):
        result = apply_filters(df, {"country": "India"})
        assert len(result) == 4

    def test_unknown_country_returns_empty(self, df):
        result = apply_filters(df, {"country": "Neverland"})
        assert len(result) == 0

    def test_year_from(self, df):
        result = apply_filters(df, {"year_from": 1910})
        assert (result["year"] >= 1910).all()

    def test_year_to(self, df):
        result = apply_filters(df, {"year_to": 1905})
        assert (result["year"] <= 1905).all()

    def test_year_range_inclusive(self, df):
        result = apply_filters(df, {"year_from": 1900, "year_to": 1900})
        assert (result["year"] == 1900).all()

    def test_multi_key_and(self, df):
        result = apply_filters(df, {"continent": "Asia", "disaster_type": "Drought"})
        assert all(result["continent"] == "Asia")
        assert all(result["disaster_type"] == "Drought")

    def test_empty_filters_returns_all(self, df):
        result = apply_filters(df, {})
        assert len(result) == len(df)

    def test_iso_filter(self, df):
        result = apply_filters(df, {"iso": "IND"})
        assert len(result) > 0
        assert all(result["iso"] == "IND")


class TestGetDistinct:
    def test_returns_sorted_list(self, df):
        vals = get_distinct(df, "disaster_type")
        assert vals == sorted(vals)

    def test_no_nulls(self, df):
        vals = get_distinct(df, "disaster_type")
        assert None not in vals
        assert "" not in vals

    def test_unknown_column_returns_empty(self, df):
        vals = get_distinct(df, "nonexistent_column")
        assert vals == []
