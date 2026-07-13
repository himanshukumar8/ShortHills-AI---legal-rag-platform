import streamlit as st
from ui.config import UIConfig
from ui.api_client import api_client
from ui.state import clear_session
from ui.utils import format_latency

def render_sidebar():
    with st.sidebar:
        st.header("System Information")
        
        # Check Backend
        is_healthy = api_client.check_health()
        status_color = "🟢 Online" if is_healthy else "🔴 Offline"
        st.markdown(f"**Backend Status**: {status_color}")
        st.markdown(f"**Version**: {UIConfig.APP_VERSION}")
        
        st.divider()
        
        st.subheader("Architecture")
        st.markdown(f"**Embedding Model**: {UIConfig.EMBEDDING_MODEL}")
        st.markdown(f"**Retrieval Mode**: {UIConfig.RETRIEVAL_MODE}")
        st.markdown(f"**LLM Provider**: {UIConfig.LLM_PROVIDER}")
        
        st.divider()
        
        st.subheader("Corpus Statistics")
        st.markdown(f"**Documents**: {UIConfig.TOTAL_DOCUMENTS:,}")
        st.markdown(f"**Chunks Indexed**: {UIConfig.TOTAL_CHUNKS:,}")
        
        st.divider()
        
        st.subheader("Live Metrics")
        metrics = api_client.get_metrics()
        if metrics:
            st.markdown(f"**Avg Latency**: {format_latency(metrics['average_latency_s'])}")
            st.markdown(f"**Total Requests**: {metrics['total_requests']}")
        else:
            st.markdown("Metrics unavailable")
            
        st.divider()
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Refresh Status", key="btn_refresh", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("Clear Session", key="btn_clear", use_container_width=True):
                clear_session()
                st.rerun()
