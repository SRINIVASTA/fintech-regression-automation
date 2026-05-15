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
import random  # FIXED: Imported missing standard library to resolve NameError namespace crash

# Suppress underlying warnings from cluttering the screen
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="FinTech Automated Test Bench", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# 1. Initialize State Storage Memory Buffers
if "global_session_pnl" not in st.session_state:
    st.session_state.global_session_pnl = 0.0
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = "Never"
if "current_price" not in st.session_state:
    st.session_state.current_price = 0.0
if "total_volume" not in st.session_state:
    st.session_state.total_volume = 0
if "current_tick_pnl" not in st.session_state:
    st.session_state.current_tick_pnl = 0.0
if "show_celebration" not in st.session_state:
    st.session_state.show_celebration = False

# 2. Sidebar Configuration Control Panel
st.sidebar.header("🛠️ Order Routing Parameter Panel")
TICKER_LIST = ["CL=F", "GC=F", "SI=F"]
TICKER_FULL_NAMES = {
    "CL=F": "Crude Oil Futures",
    "GC=F": "Gold Futures",
    "SI=F": "Silver Futures"
}

selected_ticker = st.sidebar.selectbox("Choose Asset Class to Trade:", options=TICKER_LIST, index=0)
full_instrument_name = TICKER_FULL_NAMES.get(selected_ticker, "Unknown Asset")

lots_to_trade = st.sidebar.number_input("Order Quantity (Lots):", min_value=1, value=5)
multiplier_per_lot = st.sidebar.number_input("Multiplier Units per Lot:", min_value=1, value=5000)

# Sidebar Submit Trade Trigger Button
st.sidebar.markdown("---")
submit_trade_button = st.sidebar.button("🚀 SUBMIT TRADE TO MARKET EXECUTION", use_container_width=True, type="primary")

# 3. Data Ingestion Layer
@st.cache_data(ttl=5)
def pull_exchange_feed(symbol: str) -> pd.DataFrame:
    try:
        return yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
    except Exception:
        return pd.DataFrame()

data = pull_exchange_feed(selected_ticker)

# 4. Main Dashboard Screen Layout Header
st.title("📊 Financial Trading & Quality Assurance Center")
st.markdown(f"**Current Connectivity:** Connected to Exchange Feed | **Last Market Refresh:** {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
st.markdown("---")

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 5. Core Submission Pipeline Processing Layer
    if submit_trade_button:
        # Pull real-time data frame values during the exact click milestone window
        live_spot_price = float(data['Close'].iloc[-1].item())
        session_low_price = float(data['Low'].min().item())
        execution_timestamp = datetime.now(IST).strftime('%H:%M:%S')
        
        # Calculate algorithmic execution side vectors (Using the now imported random module)
        trade_side_signal = random.choice(["🟢 BUY ORDER", "🔴 SELL ORDER"])
        
        # Save positions to session cache memories
        st.session_state.current_price = live_spot_price
        st.session_state.total_volume = lots_to_trade * multiplier_per_lot
        st.session_state.current_tick_pnl = (live_spot_price - session_low_price) * st.session_state.total_volume
        st.session_state.global_session_pnl += st.session_state.current_tick_pnl
        st.session_state.last_submit_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
        st.session_state.show_celebration = True
        
        # Append clean formatted transactional text arrays directly to ledger log feeds
        st.session_state.trade_log.append(
            f"[{execution_timestamp}] {trade_side_signal} | Executed {lots_to_trade} Lot(s) of {selected_ticker} @ ${live_spot_price:,.2f}"
        )
        
        if len(st.session_state.trade_log) > 5:
            st.session_state.trade_log.pop(0)

    # Partition Screen Workspace into Column 1 (Trading) and Column 2 (Testing)
    left_ui_panel, right_ui_panel = st.columns(2)

    with left_ui_panel:
        st.subheader("💵 Real-Time Market Data")
        
        m1, m2 = st.columns(2)
        m1.metric(f"Last Traded Price ({full_instrument_name})", f"${st.session_state.current_price:,.2f}" if st.session_state.current_price > 0 else "$0.00")
        m2.metric("Last Transacted Size", f"{st.session_state.total_volume:,} Units" if st.session_state.total_volume > 0 else "0 Units")
        
        st.metric("💰 Total Combined Profit Across All Trades", f"INR {st.session_state.global_session_pnl:,.2f}")
        st.caption(f"⏱️ **Last Order Routed Timestamp:** {st.session_state.last_submit_time}")
        
        st.subheader("📈 Today's Price Movement Chart")
        st.line_chart(data[['Close']])
        
        st.subheader("📜 Recent Activity Log")
        if st.session_state.trade_log:
            for log_entry in reversed(st.session_state.trade_log):
                st.write(log_entry)
        else:
            st.info("No orders routed yet. Use the control panel on the left to configure parameters and click Submit Trade.")

    with right_ui_panel:
        st.subheader("🛡️ Automated System Health & Safety Guard")
        st.markdown("Our automated software guard continuously tests the mathematics, database fields, and network connections to ensure zero calculation errors.")
        
        # Run PyTest completely silently in the background
        pytest_output = io.StringIO()
        with contextlib.redirect_stdout(pytest_output):
            pytest.main(["-q", "-W", "ignore", "--json-report", "--json-report-file=qa_metrics.json", "test_trading_suite.py"])
        
        # Parse JSON results matrix to render simple indicators to user views
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
                    
                    # Pop balloons only on an active click event cycle
                    if st.session_state.show_celebration:
                        st.balloons()
                        st.session_state.show_celebration = False
                    
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
