# Task #7 — DIAL LLM Client (`ui/llm.py`)

**Status:** pending — **BLOCKED on user providing DIAL credentials**
**Blocks:** #8
**Blocked by:** #1

## Goal
Provide a configured LangChain `ChatOpenAI` instance pointed at the EPAM DIAL endpoint. DIAL is OpenAI-compatible.

## Deliverables

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model=os.environ["DIAL_DEPLOYMENT_NAME"],
        api_key=os.environ["DIAL_API_KEY"],
        base_url=os.environ["DIAL_API_BASE"],
        default_headers={"api-key": os.environ["DIAL_API_KEY"]},  # DIAL uses api-key header
        default_query={"api-version": os.environ.get("DIAL_API_VERSION", "2024-02-15-preview")},
        temperature=temperature,
    )
```

## Reference
Mirror auth/headers from the example repo: https://github.com/bntdeep/LLMThreatsAnalysis.git

## Acceptance
- `get_llm().invoke("ping")` returns a non-empty response when valid DIAL creds are in `.env`.
- Missing env vars raise a clear error at construction time.

## Open question for the user
Need from the user before implementing:
- `DIAL_API_KEY`
- `DIAL_API_BASE` (e.g. `https://ai-proxy.lab.epam.com`)
- `DIAL_DEPLOYMENT_NAME` (e.g. `gpt-4o`)
- `DIAL_API_VERSION` (default `2024-02-15-preview` if unknown)
