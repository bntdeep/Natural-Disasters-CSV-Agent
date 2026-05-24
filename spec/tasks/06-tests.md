# Task #6 — Pytest Suite for `mcp_server` (≥80% coverage)

**Status:** pending
**Blocks:** —
**Blocked by:** #4

## Goal
Cover the MCP backend with unit tests. Target ≥80% line coverage on `mcp_server/`.

## Deliverables

- `tests/conftest.py`:
  ```python
  import pytest
  from mcp_server.data import load_dataset

  @pytest.fixture(scope="session")
  def df():
      return load_dataset("docs/1900_2021_DISASTERS_Example.csv")
  ```
- `tests/test_data.py`:
  - column normalization keeps all columns, snake_cases them, handles `'000 US$` suffix
  - numeric coercion: blank strings → `NaN`, not `0`
  - `apply_filters` — country (case-insensitive), year_from/year_to inclusive bounds, multi-key AND
  - `get_distinct` returns sorted unique non-null
  - singleton `get_dataframe()` returns same instance twice
- `tests/test_tools.py` — one test class per tool:
  - **get_schema**: returns expected categoricals, year range
  - **filter_disasters**: respects limit, sets `truncated=True` when matched > limit, empty filter returns all rows
  - **aggregate**: sum/mean/count produce correct values for known fixture; unknown filter returns empty rows
  - **top_n**: n > rows returns all rows, n=0 returns empty, sorted desc by value
  - **time_series**: years are sorted asc, missing-year buckets handled
  - **summary_stats**: totals match manual calculation on fixture
  - **search_events**: case-insensitive, multiple fields, no match returns empty
- Run command in README: `pytest --cov=mcp_server --cov-report=term-missing --cov-fail-under=80`

## Acceptance
- All tests pass.
- Coverage report shows ≥80% on `mcp_server/`.
- No tests depend on the FULL CSV — Example CSV only.
