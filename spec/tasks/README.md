# Tasks Index

High-level plan: see [`PLAN.md`](./PLAN.md).

## Order of execution

| # | File | Depends on | Summary |
|---|------|------------|---------|
| 1 | [`01-setup.md`](./01-setup.md) | — | `pyproject.toml`, dirs, `.env.example`, `.gitignore` |
| 2 | [`02-data-loader.md`](./02-data-loader.md) | #1 | CSV load + column normalization + filters (`mcp_server/data.py`) |
| 3 | [`03-schemas.md`](./03-schemas.md) | #1 | Pydantic input models (`mcp_server/schema.py`) |
| 4 | [`04-tools.md`](./04-tools.md) | #2, #3 | Pure pandas tool functions (`mcp_server/tools.py`) |
| 5 | [`05-mcp-server.md`](./05-mcp-server.md) | #4 | FastMCP server, stdio (`mcp_server/server.py`) |
| 6 | [`06-tests.md`](./06-tests.md) | #4 | pytest ≥80% coverage of `mcp_server/` |
| 7 | [`07-dial-client.md`](./07-dial-client.md) | #1 | DIAL `ChatOpenAI` factory (`ui/llm.py`) — **needs DIAL creds** |
| 8 | [`08-langchain-agent.md`](./08-langchain-agent.md) | #5, #7 | LangChain agent over MCP (`ui/agent.py`) |
| 9 | [`09-streamlit-ui.md`](./09-streamlit-ui.md) | #8 | Streamlit chat + chart/HTML/table rendering (`ui/app.py`) |
| 10 | [`10-smoke-test.md`](./10-smoke-test.md) | #9 | Run on FULL CSV, capture showcase queries |
| 11 | [`11-readme.md`](./11-readme.md) | #10 | Repo README |

## Parallelizable groups
- After #1: **#2 ‖ #3 ‖ #7**
- After #4: **#5 ‖ #6**
