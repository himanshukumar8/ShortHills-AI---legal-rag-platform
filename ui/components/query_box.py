import streamlit as st
from config import UIConfig
from api_client import api_client

def render_query_box():
    st.markdown("### Ask a Legal Question")
    
    # Form to handle "Enter" key submits
    with st.form("query_form", clear_on_submit=False):
        query_input = st.text_input("Query", value=st.session_state.query, placeholder="E.g. What expenses are deductible under Section 162?", label_visibility="collapsed")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("Search", use_container_width=True)
            
        if submitted and query_input.strip():
            st.session_state.query = query_input
            st.session_state.is_loading = True
            
            # Show a spinner while querying
            with st.spinner("Executing RAG Pipeline..."):
                response = api_client.execute_query(query_input)
                
            st.session_state.is_loading = False
            if response:
                st.session_state.current_response = response
                # Add to history
                if query_input not in st.session_state.history:
                    st.session_state.history.append(query_input)
            else:
                st.error("Failed to fetch response. Please ensure the backend is online.")
            
            # Rerun to update panels below
            st.rerun()

    # Examples underneath
    st.markdown("**Examples:**")
    cols = st.columns(len(UIConfig.EXAMPLE_QUERIES))
    for i, ex in enumerate(UIConfig.EXAMPLE_QUERIES):
        with cols[i]:
            if st.button(ex, key=f"ex_{i}", help="Click to use this example query"):
                st.session_state.query = ex
                st.rerun()
                
    # History section
    if st.session_state.history:
        with st.expander("Session History"):
            for h in reversed(st.session_state.history):
                if st.button(h, key=f"hist_{h}"):
                    st.session_state.query = h
                    st.rerun()
