from __future__ import annotations

import fastmcp
from fastmcp import FastMCP

from mcp_server import tools
from mcp_server.data import get_dataframe
from mcp_server.schema import (
    AggregateParams,
    FilterParams,
    FilterRowsParams,
    SearchParams,
    TimeSeriesParams,
    TopNParams,
)

mcp = FastMCP(
    "disasters",
    instructions=(
        "You have access to a global natural-disasters dataset (1900–2021, EM-DAT). "
        "Call get_schema FIRST to learn valid filter values. "
        "Then use the typed tools to fetch exactly the data you need. "
        "Damage values are in thousands of US dollars (kusd)."
    ),
)


@mcp.tool()
def get_schema() -> dict:
    """Return dataset schema, column names, distinct categorical values (disaster types,
    continents, regions), and year range. Call this FIRST before applying any filters
    to learn which values are valid."""
    return tools.get_schema(get_dataframe())


@mcp.tool()
def filter_disasters(params: FilterRowsParams) -> dict:
    """Return individual disaster rows matching the given filters.
    Use this to inspect raw events or build tables. Results are capped at params.limit
    (default 50, max 200). Returns total_matched so you know if results were truncated."""
    return tools.filter_disasters(params, get_dataframe())


@mcp.tool()
def aggregate(params: AggregateParams) -> dict:
    """Group disasters by a dimension (country, continent, disaster_type, year, etc.)
    and aggregate a metric (total_deaths, total_damages_kusd, events, etc.).
    Use for breakdowns like 'total deaths per continent' or 'event count by disaster type'.
    Results are sorted by value descending."""
    return tools.aggregate(params, get_dataframe())


@mcp.tool()
def top_n(params: TopNParams) -> dict:
    """Return the top N entities ranked by a metric.
    Example: top 10 countries by total_deaths, or top 5 disaster types by total_damages_kusd.
    Combine with filters to scope to a specific continent, year range, or disaster type."""
    return tools.top_n(params, get_dataframe())


@mcp.tool()
def time_series(params: TimeSeriesParams) -> dict:
    """Return a year-by-year time series for a metric.
    Use for trend questions like 'how have flood deaths changed since 1950?'
    or 'number of storms per year worldwide'. Points are sorted by year ascending."""
    return tools.time_series(params, get_dataframe())


@mcp.tool()
def summary_stats(params: FilterParams) -> dict:
    """Return summary statistics for a filter slice: total event count, deaths, injuries,
    affected people, damages, and a breakdown by disaster type. Use as an overview before
    drilling down with other tools."""
    return tools.summary_stats(params, get_dataframe())


@mcp.tool()
def search_events(params: SearchParams) -> dict:
    """Case-insensitive substring search across event_name, location, and/or country fields.
    Use to find specific named events like 'Katrina', 'Tohoku', or events in a specific location."""
    return tools.search_events(params, get_dataframe())


if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        # HTTP mode for Postman / browser testing
        # Stateless: each request is independent, no session management needed
        port = 8000
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        print(f"Starting MCP HTTP server on http://localhost:{port}/mcp")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port, stateless_http=True)
    else:
        mcp.run()
