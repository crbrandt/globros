import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="Globros Geography Game Scorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Earth/Globe theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .score-card {
        background: linear-gradient(135deg, #4a90e2, #52c41a);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .winner-announcement {
        background: linear-gradient(45deg, #ff7f0e, #ffb347);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #2ca02c, #1f77b4);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #f0f8ff;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header"><h1>🌍 Globros Geography Game Scorer 🌍</h1><p>Track your daily geography game performance</p></div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🗺️ Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Daily Score Submission", "Historical Records", "Player Statistics"]
)

# Import page modules
if page == "Daily Score Submission":
    from pages import daily_submission
    daily_submission.show()
elif page == "Historical Records":
    from pages import historical_view
    historical_view.show()
elif page == "Player Statistics":
    from pages import player_stats
    player_stats.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🌍 **Globros Scoring System**")
st.sidebar.markdown("Built with Streamlit")
