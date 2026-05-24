from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from ui.llm import get_llm

SYSTEM_PROMPT = """You are a data analyst specializing in natural disasters worldwide (1900–2021).
You have access to tools that query the EM-DAT global disasters dataset.

## Workflow
1. Call `get_schema` FIRST if you are unsure which filter values are valid (disaster types, continents, regions, year range).
2. Use the typed tools to fetch data — NEVER invent numbers.
3. Compose your answer as:
   a. A short prose summary (2–4 sentences with key numbers and context).
   b. ONE relevant visualization in a fenced code block.

## Visualization format — choose the most appropriate ONE:

For charts (bar, line, pie, scatter):
```plotly
{"data": [...], "layout": {...}}
```
Use Plotly figure JSON. Examples:
- Bar chart: {"data": [{"type": "bar", "x": [...], "y": [...], "name": "..."}], "layout": {"title": "..."}}
- Line chart: {"data": [{"type": "scatter", "mode": "lines+markers", "x": [...], "y": [...]}], "layout": {"title": "..."}}
- Pie chart: {"data": [{"type": "pie", "labels": [...], "values": [...]}], "layout": {"title": "..."}}

For tabular data:
```table
| Col1 | Col2 | Col3 |
|------|------|------|
| val  | val  | val  |
```

## Important notes
- Damage values are in **thousands of US dollars** (kusd). Convert to millions/billions when quoting.
- Use the `events` metric to count the number of disaster events.
- If the user's question is ambiguous, ask ONE clarifying question instead of guessing.
- Do not add a visualization if the data is not suitable for one.
"""


def _get_server_command() -> list[str]:
    python = sys.executable
    server_module = "mcp_server.server"
    return [python, "-m", server_module]


async def build_agent() -> Any:
    cwd = str(Path(__file__).parent.parent)
    client = MultiServerMCPClient(
        {
            "disasters": {
                "command": _get_server_command()[0],
                "args": _get_server_command()[1:],
                "transport": "stdio",
                "env": {**os.environ, "PYTHONPATH": cwd},
            }
        }
    )
    tools = await client.get_tools()
    llm = get_llm()
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


async def run_query(agent: Any, history: list[BaseMessage], user_message: str) -> str:
    messages = history + [HumanMessage(content=user_message)]
    result = await agent.ainvoke({"messages": messages})
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    return ai_messages[-1].content if ai_messages else ""
