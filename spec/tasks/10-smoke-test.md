# Task #10 — End-to-End Smoke Test on FULL CSV + Showcase Queries

**Status:** pending
**Blocks:** #11
**Blocked by:** #9

## Goal
Validate the whole stack on the full 16k-row dataset and harvest the queries that best showcase the bot for the README.

## Deliverables

1. Switch `DISASTERS_CSV_PATH` to `docs/1900_2021_DISASTERS_FULL.csv`.
2. Run the Streamlit app and try at least these query categories:
   - **Top-N**: "Top 10 countries by total deaths from earthquakes since 1980"
   - **Time-series**: "Trend of floods per year worldwide since 1970"
   - **Breakdown / pie**: "What share of disasters are climatological vs geophysical vs hydrological?"
   - **Filtered ranking**: "Most damaging hurricanes (in US$ damages) since 2000"
   - **Geographic**: "Number of disasters per continent in the last decade"
   - **Specific event lookup**: "Find the deadliest event in India"
   - **Comparison**: "Compare flood deaths between Asia and Africa over time"
3. For each working query, capture:
   - the user prompt (verbatim)
   - which chart type the LLM chose
   - whether numbers match a manual pandas check on the FULL CSV
4. Identify any tools that fail or return useless output → file follow-up notes inline.

## Acceptance
- At least 5 queries run cleanly end-to-end with both prose and a chart/table.
- At least one query of each chart type (bar, line, pie/donut, table) is captured.
- A `showcase_queries.md` (or section in the README) is drafted with the verbatim queries.
