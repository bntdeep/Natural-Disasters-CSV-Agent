# Task #5 — MCP Server (`mcp_server/server.py`)

**Status:** pending
**Blocks:** #8
**Blocked by:** #4

## Goal
Expose the pure tool functions over the MCP protocol via FastMCP, stdio transport.

## Deliverables

- `mcp_server/server.py` with FastMCP app:
  ```python
  from fastmcp import FastMCP
  from mcp_server.data import get_dataframe
  from mcp_server import tools, schema

  mcp = FastMCP("disasters")

  @mcp.tool()
  def get_schema() -> dict:
      """Return dataset schema, distinct categorical values, and year range.
      Call this FIRST to learn valid filter values before other tools."""
      return tools.get_schema(get_dataframe())

  @mcp.tool()
  def aggregate(params: schema.AggregateParams) -> dict:
      """Group disasters by a column and aggregate a metric. Use for breakdowns
      like 'total deaths per disaster type' or 'event count per continent'."""
      return tools.aggregate(params, get_dataframe())

  # ... one wrapper per tool, with rich docstrings (LLM reads them)

  if __name__ == "__main__":
      mcp.run()  # stdio transport by default
  ```
- Entrypoint: `python -m mcp_server.server`.
- Each tool docstring must be **prescriptive** — tell the LLM when to call it and how to chain calls. Docstrings ARE the tool description for the LLM.

## Acceptance
- `python -m mcp_server.server` starts and waits on stdio.
- Manual MCP client (e.g., the inspector or a quick LangChain test) lists 7 tools with non-empty descriptions.
- Each tool returns valid JSON when invoked with sample params.
