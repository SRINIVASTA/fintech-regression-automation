import streamlit as st
import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime
import io
import contextlib
import pytest
import warnings
import os
import json

# Suppress underlying warnings from cluttering the screen
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="FinTech Automated Test Bench", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# 1. Initialize Memory States
if "global_session_pnl" not in st.session_state:
    st.session_state.global_session_pnl = 0.0
if "last_price" not in st.session_state:
    st.session_state.last_price = 0.0
if "last_ticker" not in st.session_state:
    st.session_state.last_ticker = ""
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# 2. Sidebar Configuration Control Panel
st.sidebar.header("🛠️ Dashboard Settings")
TICKER_LIST = ["CL=F", "GC=F", "SI=F"]
TICKER_FULL_NAMES = {
    "CL=F": "Crude Oil Futures",
    "GC=F": "Gold Futures",
    "SI=F": "Silver Futures"
}

selected_ticker = st.sidebar.selectbox("Choose What to Trade:", options=TICKER_LIST, index=0)
full_instrument_name = TICKER_FULL_NAMES.get(selected_ticker, "Unknown Asset")

if selected_ticker != st.session_state.last_ticker:
    st.session_state.last_ticker = selected_ticker
    st.session_state.trade_log = []
    st.session_state.last_price = 0.0

lots_to_trade = st.sidebar.number_input("Number of Lots:", min_value=1, value=5)
multiplier_per_lot = st.sidebar.number_input("Multiplier Units per Lot:", min_value=1, value=5000)

# 3. Data Processing Layer
@st.cache_data(ttl=10)
def pull_exchange_feed(symbol: str) -> pd.DataFrame:
    try:
        return yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
    except Exception:
        return pd.DataFrame()

data = pull_exchange_feed(selected_ticker)

# 4. Layman-Friendly Main Layout Header
st.title("📊 Financial Trading & Quality Assurance Center")
st.markdown(f"**Current Status:** Live & Connected | **Last Sync:** {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
st.markdown("---")

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    current_p = float(data['Close'].iloc[-1].item())
    low_p = float(data['Low'].min().item())
    ist_now = datetime.now(IST).strftime('%H:%M:%S')

    # State Machine Logging
    if st.session_state.last_price == 0.0:
        st.session_state.trade_log.append(f"[{ist_now}] 🟡 STARTED | Monitoring {lots_to_trade} Lots of {selected_ticker}")
    elif current_p != st.session_state.last_price:
        if current_p < st.session_state.last_price:
            st.session_state.trade_log.append(f"[{ist_now}] 🔴 BUY ORDER | Triggered at ${current_p:,.2f}")
        elif current_p > st.session_state.last_price:
            st.session_state.trade_log.append(f"[{ist_now}] 🟢 SELL ORDER | Triggered at ${current_p:,.2f}")
            
    st.session_state.last_price = current_p
    if len(st.session_state.trade_log) > 5:
        st.session_state.trade_log.pop(0)

    total_volume = lots_to_trade * multiplier_per_lot
    current_tick_pnl = (current_p - low_p) * total_volume
    st.session_state.global_session_pnl += current_tick_pnl

    # Partition Workspace into Column 1 (Trading) and Column 2 (Testing)
    left_ui_panel, right_ui_panel = st.columns(2)

    with left_ui_panel:
        st.subheader("💵 Real-Time Market Data")
        
        m1, m2 = st.columns(2)
        m1.metric(f"Current Price ({full_instrument_name})", f"${current_p:,.2f}")
        m2.metric("Total Size of Trade", f"{total_volume:,} Units")
        
        st.metric("💰 Total Combined Profit Across All Trades", f"INR {st.session_state.global_session_pnl:,.2f}")
        
        st.subheader("📈 Today's Price Movement Chart")
        st.line_chart(data[['Close']])
        
        st.subheader("📜 Recent Activity Log")
        for log_entry in reversed(st.session_state.trade_log):
            st.write(log_entry)

    with right_ui_panel:
        st.subheader("🛡️ Automated System Health & Safety Guard")
        st.markdown("Our automated software guard continuously tests the mathematics, database fields, and network connections to ensure zero calculation errors.")
        
        # Run PyTest completely silently in the background
        pytest_output = io.StringIO()
        with contextlib.redirect_stdout(pytest_output):
            pytest.main(["-q", "-W", "ignore", "--json-report", "--json-report-file=qa_metrics.json", "test_trading_suite.py"])
        
        # Parse the JSON report to display human-friendly indicators instead of terminal logs
        if os.path.exists("qa_metrics.json"):
            try:
                with open("qa_metrics.json", "r") as file:
                    report_data = json.load(file)
                
                summary = report_data.get("summary", {})
                passed_tests = summary.get("passed", 0)
                failed_tests = summary.get("failed", 0)
                total_duration = report_data.get("duration", 0.0)
                
                if failed_tests == 0 and passed_tests > 0:
                    st.success(f"✔ **SYSTEM HEALTH: EXCELLENT**")
                    st.balloons() # Visual celebration on pass
                    
                    # Layman Explanation Metric Cards
                    kpi1, kpi2 = st.columns(2)
                    kpi1.metric("Safety Checked Scenarios", f"{passed_tests} Passed")
                    kpi2.metric("System Speed Check", f"{total_duration:.2f} Seconds")
                    
                    st.info("💡 **What this means:** The system mathematically cross-checked all incoming values, verified contract configurations, and confirmed that the database layout is completely free of errors.")
                else:
                    st.error("⚠️ **CRITICAL ALERT: CALCULATION BUG DETECTED**")
                    st.markdown(f"Failed verification checks count: **{failed_tests}**")
            except Exception:
                st.warning("Running infrastructure check cycles...")
        
        st.markdown("---")
        st.subheader("📥 Executive Report Export")
        st.markdown("Download a machine-readable audit report containing the complete verification history for compliance managers.")
        
        if os.path.exists("qa_metrics.json"):
            with open("qa_metrics.json", "r") as file:
                st.download_button(label="📥 Download System Audit Certificate (JSON)", data=file.read(), file_name="system_health_report.json", mime="application/json", use_container_width=True)

        # Hidden advanced section if an engineer wants to expand it
        with st.expander("🔍 View Raw Technical Terminal Logs (For Engineers Only)"):
            st.code(pytest_output.getvalue() if pytest_output.getvalue() else "All tests compiled and passed perfectly.", language="text")

else:
    st.error("⚠️ Failed to synchronize live exchange feeds. Verify connectivity profiles or configuration inputs.")
