import streamlit as st

from config import UIConfig
from state import init_session_state
from theme import apply_theme
from api_client import api_client

from components.sidebar import render_sidebar
from components.query_box import render_query_box
from components.answer_panel import render_answer_panel
from components.citation_panel import render_citation_panel
from components.retrieval_panel import render_retrieval_panel
from components.metrics_panel import render_metrics_panel
from components.footer import render_footer

def main():
    st.set_page_config(
        page_title=UIConfig.APP_TITLE,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    apply_theme()
    
    # Render Sidebar
    render_sidebar()
    
    # Main Header
    st.title(UIConfig.APP_TITLE)
    st.markdown(f"#### {UIConfig.APP_SUBTITLE}")
    
    # Check Backend Status
    if not api_client.check_health():
        st.error("Backend Offline. The FastAPI service layer is currently unreachable.")
        if st.button("Retry Connection", type="primary"):
            st.rerun()
        st.stop()
        
    # Render Query Input
    render_query_box()
    
    # Render Results if available
    response = st.session_state.current_response
    if response:
        # Exact order: Answer -> Citations -> Evidence -> Metrics
        render_answer_panel(response)
        
        citations = response.get("citations", [])
        render_citation_panel(citations)
        
        trace = response.get("retrieval_trace", {})
        render_retrieval_panel(trace)
        
        render_metrics_panel(response)
        
    render_footer()

if __name__ == "__main__":
    main()
