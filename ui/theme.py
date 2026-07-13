import streamlit as st

def apply_theme():
    """Applies clean, minimal, production-ready enterprise styling."""
    st.markdown("""
        <style>
        /* Base typography and background */
        .stApp {
            background-color: #FFFFFF;
            color: #1A202C;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #F7FAFC;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Minimal headers */
        h1, h2, h3, h4, h5, h6 {
            color: #2D3748;
            font-weight: 600;
        }
        
        /* Metric cards */
        .css-1wivap2 {
            background-color: #F7FAFC;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #E2E8F0;
        }
        
        /* Blue accents for primary buttons */
        .stButton>button {
            background-color: #3182CE;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #2B6CB0;
            color: white;
            border: none;
        }
        
        /* Secondary outline buttons (like in sidebar) */
        .sidebar-btn>button {
            background-color: transparent !important;
            color: #4A5568 !important;
            border: 1px solid #CBD5E0 !important;
        }
        .sidebar-btn>button:hover {
            background-color: #F7FAFC !important;
            border-color: #A0AEC0 !important;
        }
        
        /* Expander/Cards with rounded corners */
        .streamlit-expanderHeader {
            background-color: #F7FAFC;
            border-radius: 6px;
            border: 1px solid #E2E8F0;
        }
        .streamlit-expanderContent {
            border: 1px solid #E2E8F0;
            border-top: none;
            border-bottom-left-radius: 6px;
            border-bottom-right-radius: 6px;
        }
        
        /* Clean text input */
        .stTextInput>div>div>input {
            border-radius: 6px;
            border: 1px solid #CBD5E0;
        }
        .stTextInput>div>div>input:focus {
            border-color: #3182CE;
            box-shadow: 0 0 0 1px #3182CE;
        }
        
        /* Badges */
        .badge-green {
            background-color: #C6F6D5;
            color: #22543D;
            padding: 0.2rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-yellow {
            background-color: #FEFCBF;
            color: #744210;
            padding: 0.2rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-red {
            background-color: #FED7D7;
            color: #742A2A;
            padding: 0.2rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding-top: 3rem;
            padding-bottom: 1rem;
            color: #718096;
            font-size: 0.875rem;
            border-top: 1px solid #E2E8F0;
            margin-top: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)
