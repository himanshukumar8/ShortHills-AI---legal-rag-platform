import streamlit as st

def render_footer():
    st.markdown("""
        <div class="footer">
            Powered by Hybrid Retrieval (BM25 + Dense Vectors + RRF)
        </div>
    """, unsafe_allow_html=True)
