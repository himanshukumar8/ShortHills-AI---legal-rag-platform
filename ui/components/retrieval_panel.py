import streamlit as st

def render_retrieval_panel(trace: dict):
    st.markdown("---")
    st.markdown("## 3. Supporting Evidence")
    
    results = trace.get("results", [])
    if not results:
        st.warning("No chunks were retrieved from the corpus.")
        return
        
    for i, res in enumerate(results):
        chunk_id = res.get("chunk_id", "Unknown")
        doc_title = res.get("document_title", "Unknown")
        citation = res.get("citation", "Unknown")
        p_start = res.get("page_start", 0)
        p_end = res.get("page_end", 0)
        page_str = f"Page {p_start}" if p_start == p_end else f"Pages {p_start}-{p_end}"
        rrf = res.get("rrf_score", 0.0)
        source = res.get("retrieval_source", "hybrid")
        
        # Note: the actual text might be truncated or mocked in our backend for performance.
        # If text is present in the response, we display it, otherwise a placeholder.
        text = res.get("text", f"Content for {chunk_id} from {doc_title}. [Text not fully transmitted in summary trace]")
        
        with st.expander(f"[{i+1}] {doc_title} ({page_str}) - Score: {rrf:.4f}"):
            st.markdown(f"**Chunk ID**: `{chunk_id}` | **Source**: `{source}` | **Citation**: `{citation}`")
            st.markdown(f"**Text Extract**:")
            st.info(text)
            
    # Optional Trace Panel
    st.markdown("---")
    with st.expander("🔍 Advanced Retrieval Trace (Collapsed by default)"):
        es_count = trace.get("es_candidate_count", 0)
        qd_count = trace.get("qdrant_candidate_count", 0)
        es_lat = trace.get("es_latency", 0.0)
        qd_lat = trace.get("qdrant_latency", 0.0)
        fuse_lat = trace.get("fusion_latency", 0.0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Elasticsearch Hits (BM25)", es_count, f"{es_lat:.3f}s latency")
        with col2:
            st.metric("Qdrant Hits (Dense)", qd_count, f"{qd_lat:.3f}s latency")
        with col3:
            st.metric("RRF Fusion Latency", f"{fuse_lat:.3f}s")
            
        st.json(trace)
