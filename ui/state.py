import streamlit as st

def init_session_state():
    """Initialize all session state variables."""
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_response" not in st.session_state:
        st.session_state.current_response = None
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False

def clear_session():
    """Clear the session state."""
    st.session_state.query = ""
    st.session_state.history = []
    st.session_state.current_response = None
    st.session_state.is_loading = False
