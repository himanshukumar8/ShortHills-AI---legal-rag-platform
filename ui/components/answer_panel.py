import streamlit as st

def render_answer_panel(response: dict):
    st.markdown("---")
    st.markdown("## 1. Generated Answer")
    
    # Extract data
    answer = response.get("answer", "No answer generated.")
    confidence = response.get("confidence", "UNKNOWN")
    limitations = response.get("limitations", "None provided.")
    
    # Get generation time from trace if available
    trace = response.get("retrieval_trace", {})
    gen_time = trace.get("total_latency", 0.0)
    
    st.markdown(f"""
        <div class="css-1wivap2">
            <h4>Answer</h4>
            <p style="font-size: 1.1rem; line-height: 1.6;">{answer}</p>
            <hr style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; color: #718096; font-size: 0.9rem;">
                <span><strong>Confidence:</strong> {confidence}</span>
                <span><strong>Generation Time:</strong> {gen_time:.3f} s</span>
            </div>
            <div style="margin-top: 0.5rem; color: #718096; font-size: 0.9rem;">
                <strong>Limitations:</strong> {limitations}
            </div>
        </div>
    """, unsafe_allow_html=True)
