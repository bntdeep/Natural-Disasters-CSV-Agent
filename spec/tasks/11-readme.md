# Task #11 — README

**Status:** pending
**Blocks:** —
**Blocked by:** #10

## Goal
Single entry-point doc covering setup, run, test, and what the bot can do.

## Deliverables — `README.md` sections

1. **Overview** — one paragraph: chat over the EM-DAT 1900–2021 disasters CSV via MCP + LangChain + DIAL + Streamlit.
2. **Architecture** — copy/adapt the diagram from `spec/tasks/PLAN.md`. Emphasize that MCP is the only data API.
3. **Setup**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
   cp .env.example .env  # then fill DIAL credentials
   ```
4. **Run**
   - MCP server alone (debug): `python -m mcp_server.server`
   - Full app: `streamlit run ui/app.py`
   - Switch dataset: set `DISASTERS_CSV_PATH=docs/1900_2021_DISASTERS_FULL.csv`
5. **Tests**
   ```bash
   pytest --cov=mcp_server --cov-report=term-missing --cov-fail-under=80
   ```
6. **Showcase queries** — verbatim list from task #10, grouped by chart type.
7. **Limitations & notes**
   - Damages are in **'000 US$** (per source dataset).
   - HTML blocks emitted by the LLM are rendered via `st.components.html` — be mindful of what model you point at it.
   - Full CSV is loaded into memory once at MCP startup (~4.5 MB, 16k rows).
8. **Project structure** — file tree from `spec/tasks/PLAN.md`.

## Acceptance
- A new dev can clone, set creds, and run the app end-to-end using only the README.
- README references the spec and tasks folder for deeper context.
