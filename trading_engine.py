import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

def calculate_transaction_metrics(ticker: str, lots: int, multiplier: int) -> dict:
    """Fetches real-time exchange data and checks column matrix levels."""
    data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
    if data.empty:
        raise ConnectionError(f"Market data stream unreachable for Ticker: {ticker}")
        
    # Standardize column index arrays to avoid MultiIndex structure bugs
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
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
