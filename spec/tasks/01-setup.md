# Task #1 — Project Setup

**Status:** pending
**Blocks:** #2, #3
**Blocked by:** —

## Goal
Create the project skeleton: dependency manifest, folder layout, environment template.

## Deliverables

- `pyproject.toml` with dependencies:
  - Runtime: `mcp`, `fastmcp`, `pandas`, `pydantic>=2`, `langchain`, `langchain-openai`, `langchain-mcp-adapters`, `streamlit`, `plotly`, `python-dotenv`
  - Dev: `pytest`, `pytest-cov`, `pytest-asyncio`
- Empty package dirs with `__init__.py`: `mcp_server/`, `ui/`, `tests/`
- `.env.example`:
  ```
  DIAL_API_KEY=
  DIAL_API_BASE=
  DIAL_DEPLOYMENT_NAME=
  DIAL_API_VERSION=
  DISASTERS_CSV_PATH=docs/1900_2021_DISASTERS_Example.csv
  ```
- `.gitignore`: `.env`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `*.egg-info/`, `.venv/`

## Acceptance
- `pip install -e .` succeeds in a fresh venv.
- `python -c "import mcp_server, ui"` succeeds.
