import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    .stApp { background: #f5f7fb; }
    [data-testid="stSidebar"] { background: #101d35; }
    [data-testid="stSidebar"] * { color: #f5f7fb; }
    h1, h2, h3 { color: #14233d; }
    div[data-testid="stMetric"] { background: white; padding: 16px; border-radius: 14px; border: 1px solid #e4e9f2; box-shadow: 0 3px 12px rgba(18,36,64,.05); }
    .stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 650; }
    .status-pill { display:inline-block; padding: 6px 12px; border-radius: 999px; background:#fff2d6; color:#7b4b00; font-weight:700; border:1px solid #f0d28e; margin: 4px 0 12px; }
    </style>
    """, unsafe_allow_html=True)

def metric_card(container, label, value):
    container.metric(label, value)

def status_badge(status):
    st.markdown(f'<span class="status-pill">Status: {status}</span>', unsafe_allow_html=True)
