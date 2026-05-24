# Task #9 — Streamlit Chat UI (`ui/app.py`)

**Status:** pending
**Blocks:** #10
**Blocked by:** #8

## Goal
A chat UI that calls the LangChain agent and renders the response: prose + interactive chart/HTML/table.

## Deliverables

- `ui/app.py`:
  - `st.set_page_config(page_title="Disasters Chat", layout="wide")`
  - Sidebar:
    - dataset path indicator
    - "Sample queries" — clickable list (populated from task #10)
    - "Reset chat" button
  - Main area: `st.chat_message` history loop + `st.chat_input`.
  - On user input → call agent → parse response → render.
- Response parser: regex over fenced blocks. For each block:
  | Lang | Renderer |
  |------|----------|
  | `plotly` | `plotly.io.from_json(block_text)` → `st.plotly_chart(fig, use_container_width=True)` |
  | `html` | `st.components.v1.html(block_text, height=500, scrolling=True)` |
  | `table` | `st.markdown(block_text)` (markdown tables) |
  | other | render as markdown code block (fallback) |
  - Non-fenced text → `st.markdown`.
- Persist chat history in `st.session_state["messages"]`.
- Spawn the agent ONCE in `st.session_state["agent"]` (lazy init in an async helper using `asyncio.run`).
- Run command: `streamlit run ui/app.py`.

## Acceptance
- Chat history persists across turns within a session.
- A query like "Top 10 countries by total deaths" yields prose + an interactive Plotly bar chart.
- A query like "Show me a table of the deadliest events" yields a rendered markdown table.
- Reset clears the history and the agent state cleanly.
