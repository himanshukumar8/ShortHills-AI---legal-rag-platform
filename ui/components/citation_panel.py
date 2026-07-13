import streamlit as st
from ui.utils import get_badge_class

def render_citation_panel(citations: list):
    st.markdown("---")
    st.markdown("## 2. Verified Citations")
    
    if not citations:
        st.info("No explicit citations were extracted from the answer.")
        return
        
    for i, cit in enumerate(citations):
        status = cit.get("status", "UNVERIFIED")
        badge_cls = get_badge_class(status)
        
        doc = cit.get("document", "Unknown Document")
        page = cit.get("page", 0)
        section = cit.get("section", "N/A")
        conf = cit.get("confidence", 0.0)
        msg = cit.get("message", "")
        
        st.markdown(f"""
            <div class="css-1wivap2" style="margin-bottom: 1rem; border-left: 4px solid #3182CE;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="margin: 0;">{doc} (Page {page})</h5>
                    <span class="{badge_cls}">{status}</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #4A5568;">
                    <strong>Section:</strong> {section} | <strong>Verification Confidence:</strong> {conf:.2f}
                </div>
                <div style="margin-top: 0.25rem; font-size: 0.9rem; color: #718096;">
                    <em>{msg}</em>
                </div>
            </div>
        """, unsafe_allow_html=True)
