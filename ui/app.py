from __future__ import annotations

import asyncio
import json
import re

import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="Disasters Chat", layout="wide", page_icon="🌍")

SAMPLE_QUERIES = [
    "Top 10 countries by total deaths from all disasters",
    "Trend of floods per year since 1970",
    "Share of disasters by type (pie chart)",
    "Most damaging storms since 2000",
    "Compare earthquake deaths by continent",
    "Summary stats for disasters in Asia",
    "Find events related to Katrina",
    "How many disasters happened per year in the 20th century?",
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_blocks(text: str) -> list[tuple[str, str]]:
    """Return list of (lang, content) for fenced blocks, plus ('text', ...) for prose."""
    pattern = re.compile(r"```(\w+)\s*\n(.*?)```", re.DOTALL)
    parts: list[tuple[str, str]] = []
    last = 0
    for m in pattern.finditer(text):
        prose = text[last : m.start()].strip()
        if prose:
            parts.append(("text", prose))
        parts.append((m.group(1).lower(), m.group(2).strip()))
        last = m.end()
    tail = text[last:].strip()
    if tail:
        parts.append(("text", tail))
    return parts or [("text", text)]


def _render_response(text: str) -> None:
    for lang, content in _extract_blocks(text):
        if lang == "plotly":
            try:
                fig = pio.from_json(content)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart render error: {e}")
                st.code(content, language="json")
        elif lang == "html":
            components.html(content, height=500, scrolling=True)
        elif lang == "table":
            st.markdown(content)
        elif lang == "text":
            st.markdown(content)
        else:
            st.code(content, language=lang)


# ── agent init ────────────────────────────────────────────────────────────────

def _get_agent():
    if "agent" not in st.session_state:
        from ui.agent import build_agent
        with st.spinner("Connecting to MCP server…"):
            st.session_state.agent = asyncio.run(build_agent())
    return st.session_state.agent


def _ask(user_input: str) -> str:
    from ui.agent import run_query
    history = [
        HumanMessage(content=m["content"]) if m["role"] == "user"
        else AIMessage(content=m["content"])
        for m in st.session_state.messages[:-1]  # exclude last (just-added) user message
    ]
    return asyncio.run(run_query(_get_agent(), history, user_input))


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🌍 Disasters Chat")
    st.caption("EM-DAT global disasters dataset, 1900–2021")
    st.divider()

    st.subheader("Sample queries")
    for q in SAMPLE_QUERIES:
        if st.button(q, use_container_width=True, key=f"sq_{q[:20]}"):
            st.session_state.pending_query = q

    st.divider()
    if st.button("🗑 Reset chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("agent", None)
        st.rerun()


# ── chat history ──────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            _render_response(msg["content"])
        else:
            st.markdown(msg["content"])


# ── input ─────────────────────────────────────────────────────────────────────

user_input = st.chat_input("Ask about natural disasters…")

# Handle sidebar sample query click
if "pending_query" in st.session_state and st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                response = _ask(user_input)
            except Exception as e:
                response = f"❌ Error: {e}"
        _render_response(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
