# Streamlit UI Presentation Layer

The Legal RAG platform includes a production-ready, enterprise-grade Streamlit frontend. This serves as a "thin client" that relies entirely on the internal FastAPI service layer for business logic, retrieval, and generation.

## Running the UI

```bash
# Ensure the backend is running first
python -m api.app

# In a new terminal, launch the Streamlit frontend
streamlit run ui/app.py
```

## Architecture & State Management
The UI strictly isolates concerns:
- `api_client.py`: Uses `requests` to securely wrap backend calls to FastAPI (`/health`, `/query`, `/metrics`).
- `state.py`: Safely manages Session State without leaking between queries. It tracks the query history, the current trace response, and loading indicators.
- `theme.py`: Overrides Streamlit's default CSS to apply a clean, minimal "white and blue" enterprise motif with rounded corners.
- `components/`: Modular UI widgets. 
    - The Sidebar (`sidebar.py`) polls the API for live metrics.
    - The Answer Panel (`answer_panel.py`) renders the generated text.
    - The Citation Panel (`citation_panel.py`) builds the Green/Yellow/Red Verification Badges natively using CSS classes.

## Testing & Validation
The UI layer relies strictly on the `api_client.py`. We successfully executed `test_ui_client.py` to assert that the components can fetch traces from the backend synchronously. The output of this test is logged into `reports/ui_validation.json`.
