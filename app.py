import streamlit as st
import pandas as pd
import pytest
import io
import contextlib
from trading_engine import calculate_transaction_metrics

st.set_page_config(page_title="QA Automation & MM Terminal", layout="wide")

# Persistent balance tracker across screen updates
if "global_session_pnl" not in st.session_state:
    st.session_state.global_session_pnl = 0.0

st.title("🎛️ Capital Markets Engine & PyTest Dashboard")
st.markdown("---")

# Setup Sidebar Component Controls
st.sidebar.header("⚙️ Terminal Controls")
ticker_selection = st.sidebar.selectbox("Select Target Ticker:", ["GC=F", "SI=F", "CL=F"])
lots = st.sidebar.number_input("Trading Lots:", min_value=1, value=5)
multiplier = st.sidebar.number_input("Contract Sizing:", min_value=1, value=5000)

# Execute core processing
try:
    metrics = calculate_transaction_metrics(ticker_selection, lots, multiplier)
    
    # Split layout into two separate columns
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("📊 Live Trading Position Metrics")
        
        # Display Live Cards
        m1, m2 = st.columns(2)
        m1.metric("Live Execution Spot Price", f"${metrics['current_price']:,.2f}")
        m2.metric("Total Transacted Volume Size", f"{metrics['total_volume']:,} Units")
        
        # Accumulate to master pool on refresh clicks
        st.session_state.global_session_pnl += metrics['tick_pnl']
        st.metric("🔥 GRAND TOTAL PROFIT (ALL TRANSACTIONS)", f"INR {st.session_state.global_session_pnl:,.2f}")
        
        # Render Trend Chart
        st.subheader("📈 Intraday Price Trend Matrix")
        st.line_chart(metrics['data_frame'][['Close']])
        
    with right_col:
        st.subheader("🧪 Automated PyTest QA Console")
        st.info("Running background framework assertion regression loops...")
        
        # Capture PyTest terminal output string variables to display directly in the dashboard
        pytest_output = io.StringIO()
        with contextlib.redirect_stdout(pytest_output):
            pytest.main(["-v", "test_trading_suite.py"])
            
        # Print clean test framework log inside a UI text block code component
        st.code(pytest_output.getvalue(), language="text")

except Exception as e:
    st.error(f"Failed to synchronize live exchange feeds: {e}")
