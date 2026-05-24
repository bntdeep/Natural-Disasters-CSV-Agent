# Implementation Plan

## Goal
Build a chatbot that answers natural-language questions about natural disasters from a CSV dataset (1900–2021). The chatbot must return both a textual description and a graphical representation (chart/table/HTML) chosen by the LLM.

## Architecture

```
┌──────────────┐     chat      ┌──────────────────────────┐    MCP/stdio   ┌────────────────┐
│ Streamlit UI │ ────────────▶ │ LangChain agent + DIAL   │ ─────────────▶ │  MCP server    │
│  (ui/app.py) │ ◀──────────── │  (ui/agent.py + llm.py)  │ ◀───────────── │ (mcp_server/)  │
└──────┬───────┘   text + viz  └──────────────────────────┘   tool calls   └────────┬───────┘
       │                                                                            │ pandas
       │ renders Plotly JSON / HTML / tables                                         ▼
       ▼                                                                       CSV dataset
   user view                                                                  (docs/*.csv)
```

**Constraints from spec:**
- MCP is the **only** API. Frontend talks to data exclusively via the LangChain agent that uses MCP tools.
- Backend (MCP) — Python. UI — any language; we picked Streamlit (Python) for a single-language stack.
- LLM provider: EPAM DIAL (OpenAI-compatible).

## Project Structure

```
final_task_csv_chat_bot/
├── docs/                     # CSVs (existing)
│   ├── 1900_2021_DISASTERS_Example.csv
│   └── 1900_2021_DISASTERS_FULL.csv
├── spec/
│   ├── SPEC.md               # original spec
│   └── tasks/                # this folder
├── mcp_server/
│   ├── __init__.py
│   ├── server.py             # FastMCP entrypoint, stdio transport
│   ├── data.py               # CSV loading, normalization, filter helpers
│   ├── tools.py              # pure pandas tool functions
│   └── schema.py             # pydantic input models
├── ui/
│   ├── __init__.py
│   ├── app.py                # Streamlit chat
│   ├── agent.py              # LangChain agent + MCP adapter
│   └── llm.py                # DIAL ChatOpenAI factory
├── tests/
│   ├── conftest.py           # fixtures (Example CSV)
│   ├── test_data.py
│   └── test_tools.py
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## MCP Tool Surface (typed)

| Tool | Purpose |
|---|---|
| `get_schema` | Columns, dtypes, distinct values for key categoricals (disaster_type, continent, region), year range. Helps the LLM ground filters. |
| `filter_disasters` | Returns rows matching filters (capped at N=200) for inspection / table rendering. |
| `aggregate` | Groupby + agg (sum/mean/count/max/min) over a metric. |
| `top_n` | Top N entities by a metric (e.g. countries by total_deaths). |
| `time_series` | Year-bucketed series for line charts. |
| `summary_stats` | Counts, totals, breakdowns for an optional filter slice. |
| `search_events` | Substring/case-insensitive search over Event Name / Location / Country. |

All tools accept pydantic-validated parameters and return JSON-serializable dicts. They are **pure functions** of `(params, dataframe)` — no MCP coupling — so they are unit-testable.

## Charting / HTML strategy

Per user choice: the LLM emits HTML/Plotly code blocks inline with its text answer. The Streamlit layer parses fenced blocks:

- ` ```plotly ` → `st.plotly_chart(plotly.io.from_json(...))`
- ` ```html ` → `st.components.html(...)` (XSS surface — see Risks)
- ` ```table ` → markdown table or DataFrame JSON → `st.dataframe`

Plain text rendered via `st.markdown`.

## Test Strategy

- `pytest` + `pytest-cov`, fixture loads `docs/1900_2021_DISASTERS_Example.csv`.
- Per-tool happy path + edge cases (empty filters, unknown country, year out of bounds, top_n > rows, NaN-heavy metric column).
- `pytest --cov=mcp_server --cov-fail-under=80` enforced in CI / README.

## Risks & Open Questions

1. **DIAL credentials**: need `DIAL_API_KEY`, `DIAL_API_BASE`, deployment name from the user. Task #7 blocked until provided.
2. **HTML from LLM = XSS surface**: user accepted; recommendation noted to narrow to Plotly JSON only if needed.
3. **FULL CSV size**: 16 126 rows × 45 cols ≈ 4.5 MB — fits in memory comfortably; loaded once at MCP startup.
4. **Column names with spaces / special chars** (e.g. `Total Damages ('000 US$)`): normalized to snake_case internally; human-readable names preserved in `get_schema` output for the LLM.

## Task Dependency Graph

```
#1 setup
 ├── #2 data loader ─┐
 └── #3 schemas    ──┴── #4 tool functions ──┬── #5 MCP server ──┐
                                              └── #6 tests       │
                                                                  ├── #8 LC agent ── #9 UI ── #10 smoke ── #11 README
                                              #7 DIAL client ────┘
```

## Execution Order

1. **#1** Project skeleton
2. **#2** + **#3** in parallel (data loader + schemas)
3. **#4** Pure tool functions
4. **#5** + **#6** + **#7** in parallel (MCP server, tests, DIAL client)
5. **#8** LangChain agent
6. **#9** Streamlit UI
7. **#10** Smoke test on FULL CSV, capture showcase queries
8. **#11** README
