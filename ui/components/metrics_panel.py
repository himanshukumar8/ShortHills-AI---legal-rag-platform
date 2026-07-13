import streamlit as st

def render_metrics_panel(response: dict):
    st.markdown("---")
    st.markdown("## Live Request Metrics")
    
    trace = response.get("retrieval_trace", {})
    total_lat = trace.get("total_latency", 0.0)
    # LLM time is total - retrieval
    ret_lat = trace.get("es_latency", 0.0) + trace.get("qdrant_latency", 0.0) + trace.get("fusion_latency", 0.0)
    llm_time = total_lat - ret_lat if total_lat > ret_lat else 0.0
    
    # Calculate mock scores based on confidence/citations
    citations = response.get("citations", [])
    verified_count = sum(1 for c in citations if c.get("status") == "VERIFIED")
    cit_score = (verified_count / len(citations) * 100) if citations else 0.0
    
    # We map Confidence to a faithfulness proxy for display
    conf = response.get("confidence", "UNKNOWN")
    faith_score = 100 if conf == "HIGH" else (50 if conf == "MEDIUM" else 0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Latency", f"{total_lat:.2f} s")
    with col2:
        st.metric("Retrieval Time", f"{ret_lat:.2f} s")
    with col3:
        st.metric("LLM Time", f"{llm_time:.2f} s")
    with col4:
        st.metric("Faithfulness Proxy", f"{faith_score}%")
        
    if citations:
        st.metric("Citation Verification Score", f"{cit_score:.1f}%")
