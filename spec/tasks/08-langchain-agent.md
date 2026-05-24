# Task #8 — LangChain Agent (`ui/agent.py`)

**Status:** pending
**Blocks:** #9
**Blocked by:** #5, #7

## Goal
Build a tool-calling agent that spawns the MCP server over stdio, exposes its tools as LangChain tools, and produces answers that mix prose with chart/HTML blocks.

## Deliverables

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from ui.llm import get_llm

SYSTEM_PROMPT = """You are a data analyst answering questions about a global natural-disasters
dataset (1900–2021, EM-DAT). Always:

1. Call `get_schema` first if you don't know valid filter values.
2. Use the typed tools (aggregate, top_n, time_series, summary_stats, filter_disasters,
   search_events) to fetch data — never invent numbers.
3. Reply with: a) a short prose summary, b) ONE relevant visualization fenced as a code
   block. Pick ONE of:
     ```plotly
     {<Plotly figure JSON: {"data":[...], "layout":{...}}>}
     ```
     ```html
     <div>...self-contained HTML, no external scripts...</div>
     ```
     ```table
     <markdown table>
     ```
4. Numbers in the dataset for damages are in '000 US$ (thousands of US dollars). State units.
5. If the user's question is ambiguous, ask one clarifying question instead of guessing.
"""

async def build_agent():
    client = MultiServerMCPClient({
        "disasters": {
            "command": "python",
            "args": ["-m", "mcp_server.server"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    llm = get_llm()
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
```

- Expose async `run_query(agent, history, user_message) -> str` returning the final text.
- Cache the agent in `st.session_state` to avoid respawning the MCP subprocess on every chat turn.

## Acceptance
- A simple test: `"How many disasters happened in 1900?"` returns a number consistent with `summary_stats({year_from:1900, year_to:1900})`.
- The agent emits a fenced `plotly` / `html` / `table` block for visualization-friendly questions.
