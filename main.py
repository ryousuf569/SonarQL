import streamlit as st
import sqlite3 as sq
import pandas as pd

from app.simulation.simulation import monte_carlo_sim
from app.query.query_parser import parse_query
from app.feature_selection.top3 import get_top3_indicators

st.set_page_config(
    page_title="SonarQL",
    layout="centered"
)

st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    :root {
        --font: "Courier New", monospace;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: var(--font) !important;
        background-color: #0b0b0b;
        color: #d0d0d0;
        font-size: 14px;
    }

    /* ---------- MAIN CONTENT ---------- */
    [data-testid="stMain"] * {
        font-family: var(--font) !important;
    }

    /* ---------- METRICS ---------- */
    [data-testid="stMetric"] {
        background: #000;
        border: 1px solid #444;
        border-radius: 0;
        padding: 6px;
    }

    [data-testid="stMetricLabel"] {
        color: #aaa;
        font-size: 12px;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetricValue"] {
        color: #e0e0e0;
        font-size: 22px;
        font-weight: normal;
    }

    /* ---------- ALERTS ---------- */
    [data-testid="stAlert"] {
        background-color: #111 !important;
        border: 1px solid #666 !important;
        border-radius: 0 !important;
        color: #ddd !important;
    }

    /* ---------- INPUTS ---------- */
    input, textarea {
        background-color: #000 !important;
        color: #e0e0e0 !important;
        border: 1px solid #555 !important;
        border-radius: 0 !important;
        font-family: var(--font) !important;
    }

    /* ---------- BUTTONS ---------- */
    button {
        background-color: #111 !important;
        color: #ddd !important;
        border: 1px solid #555 !important;
        border-radius: 0 !important;
        font-family: var(--font) !important;
    }

    /* ---------- HEADERS ---------- */
    h1, h2, h3 {
        font-weight: normal;
        letter-spacing: 1px;
    }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #333;
    }

    [data-testid="stSidebar"] * {
        font-family: var(--font) !important;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("SonarQL Monte Carlo Simulator")

st.sidebar.header("Available Indicators")

st.sidebar.markdown("""
• SMA5  
• SMA20  
• EMA5  
• EMA20  
• RSI14  
• ATR14  
• OBV 
• Boll_%B20  
• Z20  
• ADX14  
• VOL20  
""")

st.sidebar.caption("Indicators shown are asset-agnostic.\n"
                   "Strength varies by market regime.\n"
                   "\n"
                   "All data from yfinance")

@st.cache_data
def load_data():
    conn = sq.connect("app/db/sonarql.db")
    return {
        "NQ": pd.read_sql("SELECT * FROM NQ_RAW", conn),
        "ES": pd.read_sql("SELECT * FROM ES_RAW", conn),
        "YM": pd.read_sql("SELECT * FROM YM_RAW", conn),
    }

data = load_data()

st.subheader("Asset")

st.subheader("Available Markets")

st.markdown(""" **NQ** – NASDAQ 100  
                **ES** – E-Mini S&P 500  
                **YM** – Mini Dow Jones """)


query = st.text_input("Query", placeholder="e.g. SELECT SMA20 FROM NQ WHERE CHANGE=20 SIM=1000")

run = st.button("Run Simulation")

if run and query:
    try:
        parsed = parse_query(query)
        df = data[parsed["asset"]]

        result = monte_carlo_sim(df, parsed["indicator"], parsed["change"], parsed["sim"])

        if parsed["asset"] == "NQ":
            top3 = get_top3_indicators("app/data/nq_price_info.csv")
        elif parsed["asset"] == "ES":
            top3 = get_top3_indicators("app/data/es_price_info.csv")
        elif parsed["asset"] == "YM":
            top3 = get_top3_indicators("app/data/ym_price_info.csv")

        st.subheader("Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean % Change", f"{result['mean_pct_change']:.4f}")
        col1.metric("Median % Change", f"{result['median_pct_change']:.4f}")
        col1.metric("5th / 95th %", f"{result['p5']:.4f} / {result['p95']:.4f}")

        col2.metric("Sample Size", result["sample_size"])
        col2.metric("P-Value", f"{result['p_value']:.4f}")

        with col3:
            if result["dangerous"]:
                col3.warning("P-hack value is dangerous.\nProceed with caution.")
            else:
                col3.success("P-hack value looks safe.")
                col3.caption("Markets are inherently unpredictable. "
                            "Always apply risk management.")

        col4.subheader(f"Strongest Indicators for {parsed['asset']}")
        col4.caption("Based on Correlation and R²")

        for ind in top3:
            col4.markdown(f"• **{ind}**")


    except Exception as e:
        st.error(str(e))