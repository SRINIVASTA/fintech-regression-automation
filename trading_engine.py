import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

def calculate_transaction_metrics(ticker: str, lots: int, multiplier: int) -> dict:
    """Fetches live exchange data and processes structural volume and profit logic."""
    data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
    if data.empty:
        raise ConnectionError(f"Market data stream unreachable for Ticker: {ticker}")
        
    current_price = float(data['Close'].iloc[-1].item())
    low_price = float(data['Low'].min().item())
    
    total_volume = lots * multiplier
    tick_pnl = (current_price - low_price) * total_volume
    
    return {
        "current_price": current_price,
        "low_price": low_price,
        "total_volume": total_volume,
        "tick_pnl": tick_pnl,
        "data_frame": data
    }
