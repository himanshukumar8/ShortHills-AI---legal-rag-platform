# Streamlit UI

## Objective
Construct a professional, enterprise-grade presentation layer for users to interact with the Legal RAG system.

----------------------------------------------------

## Representative Prompt

```text
Objective: Build a professional Streamlit frontend for the Legal RAG system.

Requirements:
- Connect securely to the FastAPI backend using `requests`.
- Manage query history strictly using `st.session_state` to prevent accidental re-runs.
- Override default Streamlit aesthetics using custom CSS in `ui/theme.py` (clean white, blue accents, rounded corners).
- Construct modular UI widgets in `ui/components/`: Sidebar (Metrics), Query Box, Answer Panel, and Citation verification badges.
- Do NOT duplicate backend logic in the UI.
```

----------------------------------------------------

## Outcome
- Delivered the `ui/` module functioning perfectly as a lightweight client.
- Produced a visually appealing interface that organizes dense legal traces into hierarchical, readable sections.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Streamlit is notorious for tightly coupling logic and UI. By abstracting the `APIClient` and enforcing pure UI component rendering, we circumvent Streamlit's typical performance bottlenecks.
- **Review Steps:** Validated that CSS injections correctly mapped `FAILED` citations to red badges and `PASSED` citations to green.
- **Validation Approach:** `test_ui_client.py` generated `reports/ui_validation.json` proving the API connector handled serialization seamlessly.
