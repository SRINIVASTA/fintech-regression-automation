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

# Suppress pandas/yfinance FutureWarnings from flooding the UI layout
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="FinTech QA Automation Terminal", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# 1. Initialize Persistent Session Memory States
if "global_session_pnl" not in st.session_state:
    st.session_state.global_session_pnl = 0.0
if "last_price" not in st.session_state:
    st.session_state.last_price = 0.0
if "last_ticker" not in st.session_state:
    st.session_state.last_ticker = ""
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# 2. Sidebar Control Interface (Updates Automatically on Value Selection Shifts)
st.sidebar.header("🎛️ Terminal Configuration")
TICKER_LIST = ["CL=F", "GC=F", "SI=F"]

# Institutional Asset Name Dictionary Mapping
TICKER_FULL_NAMES = {
    "CL=F": "Crude Oil Futures (NYMEX Continuous)",
    "GC=F": "Gold Futures (COMEX Continuous)",
    "SI=F": "Silver Futures (COMEX Continuous)"
}

selected_ticker = st.sidebar.selectbox("Select Target Instrument Ticker:", options=TICKER_LIST, index=0)
full_instrument_name = TICKER_FULL_NAMES.get(selected_ticker, "Unknown Asset")

# Cleanly flush cache memory buffers if switching tracking assets entirely
if selected_ticker != st.session_state.last_ticker:
    st.session_state.last_ticker = selected_ticker
    st.session_state.trade_log = []
    st.session_state.last_price = 0.0

lots_to_trade = st.sidebar.number_input("Trading Size (Lots)", min_value=1, value=5)
multiplier_per_lot = st.sidebar.number_input("Contract Sizing per Lot", min_value=1, value=5000)

# 3. Data Processing Layer
@st.cache_data(ttl=10)
def pull_exchange_feed(symbol: str) -> pd.DataFrame:
    try:
        return yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
    except Exception:
        return pd.DataFrame()

data = pull_exchange_feed(selected_ticker)

# 4. Main Dashboard Screen Layout Rendering
st.title("🎛️ Capital Markets Engine & PyTest Dashboard")
st.caption(f"System Operational Synchronization Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
st.markdown("---")

if not data.empty:
    # CRITICAL MULTI-INDEX RESOLUTION FIX: Flatten columns if structured hierarchically
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Pull metrics values cleanly using pandas indexing best practices
    current_p = float(data['Close'].iloc[-1].item())
    low_p = float(data['Low'].min().item())
    ist_now = datetime.now(IST).strftime('%H:%M:%S')

    # State Machine Logging System
    if st.session_state.last_price == 0.0:
        st.session_state.trade_log.append(f"[{ist_now}] 🟡 INIT | {lots_to_trade} Lot(s) @ {current_p:,.2f} TICKER: {selected_ticker}")
    elif current_p != st.session_state.last_price:
        if current_p < st.session_state.last_price:
            st.session_state.trade_log.append(f"[{ist_now}] 🔴 BUY  | {lots_to_trade} Lot(s) @ {current_p:,.2f} TICKER: {selected_ticker}")
        elif current_p > st.session_state.last_price:
            st.session_state.trade_log.append(f"[{ist_now}] 🟢 SELL | {lots_to_trade} Lot(s) @ {current_p:,.2f} TICKER: {selected_ticker}")
            
    st.session_state.last_price = current_p
    if len(st.session_state.trade_log) > 5:
        st.session_state.trade_log.pop(0)

    # Core Position Calculations
    total_volume = lots_to_trade * multiplier_per_lot
    current_tick_pnl = (current_p - low_p) * total_volume
    
    # Accumulate running total sum calculation across operations
    st.session_state.global_session_pnl += current_tick_pnl

    # Partition Screen Workspace into Two Separate Operational Columns
    left_ui_panel, right_ui_panel = st.columns(2)

    with left_ui_panel:
        st.subheader("📊 Live Trading Position Metrics")
        
        m1, m2 = st.columns(2)
        m1.metric(f"Live Price ({selected_ticker})", f"${current_p:,.2f}")
        m2.metric("Contract Volume Footprint", f"{total_volume:,} Base Units")
        
        # Grand Total Output Box Display
        st.metric("🔥 GRAND TOTAL PROFIT OF ALL TRANSACTIONS COMBINED", f"INR {st.session_state.global_session_pnl:,.2f}")
        
        st.subheader("📈 Intraday Price Trend Matrix")
        st.line_chart(data[['Close']])
        
        st.subheader("📜 Recent Executed Orders Log")
        for log_entry in reversed(st.session_state.trade_log):
            st.write(log_entry)

    with right_ui_panel:
        st.subheader("🧪 Automated PyTest QA Console")
        st.info("Running background infrastructure assertion regressions loops...")
        
        # Intercept background console string messages to print directly inside Streamlit
        pytest_output = io.StringIO()
        with contextlib.redirect_stdout(pytest_output):
            # FIXED: Added --json-report generation capabilities to dump pipeline logs
            pytest.main(["-v", "-W", "ignore", "--json-report", "--json-report-file=qa_metrics.json", "test_trading_suite.py"])
            
        st.code(pytest_output.getvalue(), language="text")
        
        # Display a direct local download hook link for Capgemini review managers
        if os.path.exists("qa_metrics.json"):
            with open("qa_metrics.json", "r") as file:
                st.download_button(label="📥 Download JSON Test Report", data=file.read(), file_name="qa_report.json", mime="application/json")

else:
    st.error("⚠️ Failed to synchronize live exchange feeds. Verify connectivity profiles or configuration inputs.")
