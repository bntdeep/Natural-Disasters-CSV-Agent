# Disasters Chat Bot

A natural-language chatbot over the **EM-DAT global disasters dataset (1900–2021)**.
Ask any question in plain English and get a prose answer plus an interactive chart or table — powered by an MCP data server, a LangChain agent, and EPAM DIAL (GPT-4o).

## Architecture

```
┌──────────────┐  chat   ┌──────────────────────────┐  MCP/stdio  ┌────────────────┐
│ Streamlit UI │ ──────▶ │ LangChain agent + DIAL   │ ──────────▶ │  MCP server    │
│  ui/app.py   │ ◀────── │  ui/agent.py + llm.py    │ ◀────────── │ mcp_server/    │
└──────┬───────┘ text+viz└──────────────────────────┘  tool calls └───────┬────────┘
       │ renders Plotly / HTML / tables                                    │ pandas
       ▼                                                                   ▼
   browser                                                          docs/*.csv
```

**Key constraint:** MCP is the only data API. The frontend never reads the CSV directly — all data flows through the LangChain agent using MCP tools.

### Request lifecycle

1. **Streamlit** (`ui/app.py`) receives user input and calls `run_query()`.
2. **LangGraph ReAct agent** (`ui/agent.py`) enters a loop:
   - GPT-4o decides which MCP tool to call based on the question and the system prompt.
   - It may call **multiple tools in sequence** (e.g. `get_schema` → `top_n` → `aggregate`) until it has enough data.
   - Each tool result is appended to the message history and the model reasons again.
   - The loop exits when the model produces a final answer with no further tool calls.
3. **MCP server** (`mcp_server/server.py`) exposes tools via FastMCP over stdio. Each tool accepts a **Pydantic model** as input — FastMCP converts these to JSON Schema so GPT-4o sees exact enum values and types, preventing hallucinated field names.
4. **tools.py** executes pandas queries (filter → groupby → aggregate) and returns a plain `dict`.
5. **GPT-4o** formats the final answer as markdown with a fenced code block tagged by output type:
   - ` ```plotly ` — Plotly figure JSON → rendered via `st.plotly_chart`
   - ` ```html ` — self-contained HTML with inline CSS → rendered via `st.components.html`
   - ` ```table ` — markdown table → rendered via `st.markdown`
   - plain prose → rendered via `st.markdown`
6. **`_render_response()`** in `app.py` parses the fenced blocks and routes each one to the correct Streamlit renderer.

### MCP tools

| Tool | Purpose |
|---|---|
| `get_schema` | Columns, distinct categories, year range |
| `filter_disasters` | Raw rows for a filter slice (max 200) |
| `aggregate` | Groupby + sum/mean/count/max/min/median |
| `top_n` | Top N entities by a metric |
| `time_series` | Year-bucketed series for line charts |
| `summary_stats` | Count, deaths, damages, type breakdown |
| `search_events` | Substring search by event name / location / country |

## Project structure

```
├── docs/                       # CSV datasets
│   ├── 1900_2021_DISASTERS_Example.csv   # 50 rows — for dev & tests
│   └── 1900_2021_DISASTERS_FULL.csv      # 16 126 rows — production
├── mcp_server/
│   ├── server.py               # FastMCP entrypoint (stdio)
│   ├── data.py                 # CSV loading, normalization, filter helpers
│   ├── tools.py                # Pure pandas tool functions
│   └── schema.py               # Pydantic input models
├── ui/
│   ├── app.py                  # Streamlit chat
│   ├── agent.py                # LangChain ReAct agent over MCP
│   └── llm.py                  # EPAM DIAL AzureChatOpenAI factory
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   └── test_tools.py
├── pyproject.toml
├── .env.example
└── spec/tasks/                 # Implementation plan and task files
```

## Setup

**Requirements:** Python 3.11+ (uses `python3.11` from Homebrew if system Python is older).

```bash
# 1. Create virtual environment
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Configure credentials
cp .env.example .env
# Edit .env and fill in your EPAM DIAL credentials
```

### `.env` variables

| Variable | Description | Default |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | DIAL endpoint URL | — |
| `AZURE_OPENAI_API_KEY` | DIAL API key | — |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-12-01-preview` |
| `DISASTERS_CSV_PATH` | Path to the CSV file | `docs/1900_2021_DISASTERS_Example.csv` |

## Run

```bash
# Start the full app
streamlit run ui/app.py

# To use the full 16k-row dataset, set in .env:
# DISASTERS_CSV_PATH=docs/1900_2021_DISASTERS_FULL.csv

# Start MCP server standalone (debug / inspector)
python -m mcp_server.server
```

## Tests

```bash
pytest --cov=mcp_server --cov-report=term-missing --cov-fail-under=80
```

Current coverage: **83%** (64 tests, all passing). Tests use `docs/1900_2021_DISASTERS_Example.csv` only — no network required.

## Showcase queries

These queries were verified on the full 16 126-row dataset and produce both prose and a chart.

### Bar charts
- **"Top 10 countries by total deaths from all disasters since 1900"**
  → China 12.5M, India 9.1M, Soviet Union 3.9M … Bar chart, sorted descending.

- **"Number of disaster events per continent"**
  → Asia 6490, Americas 3971, Africa 2946 … Coloured bar chart.

- **"Most damaging storms (by total damages) since 2000, top 10"**
  → Dominated by US hurricanes; total >$1.35 trillion in damages.

### Line charts
- **"Show trend of flood events per year since 1970"**
  → Steady rise from 31 events (1970) to peak 226 (2006); clear upward trend after 1990s.

### Pie charts
- **"What share of all disasters belong to each disaster type?"**
  → Floods 34%, Storms 28%, Earthquakes 10%, Epidemics 9% …

### Tables
- **"Find events related to Katrina"**
  → Returns 2 events: Katrina/Beulah/Fern (1967, Mexico) and Hurricane Katrina (2005, USA, $125B damages).

### Specific lookups
- **"What was the deadliest single disaster event in India?"**
  → 1920 Bubonic Plague epidemic — 2,000,000 deaths.

- **"Summary stats for disasters in Asia"**
  → 6490 events, breakdown by type, total deaths and damages.

## Notes

- **Damage values** in the dataset are in **thousands of US dollars** (kusd). The LLM converts to millions/billions when quoting.
- **HTML blocks** generated by the LLM are rendered via `st.components.html` — sandboxed in an iframe.
- The full CSV (~4.5 MB, 16k rows) is loaded into memory once at MCP server startup.
- The MCP subprocess is spawned once per Streamlit session and reused across chat turns.
