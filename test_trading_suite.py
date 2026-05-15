import pytest
from trading_engine import calculate_transaction_metrics

def test_financial_matrix_volume_multipliers():
    """Asserts that the system handles lots and multiplier parameters accurately."""
    result = calculate_transaction_metrics("GC=F", 5, 5000)
    assert result["total_volume"] == 25000
    assert result["current_price"] > 0.0

def test_dataframe_ingestion_integrity():
    """Validates that the pricing dataframe schema complies with standard rules."""
    result = calculate_transaction_metrics("CL=F", 1, 100)
    df = result["data_frame"]
    assert "Close" in df.columns
    assert "Low" in df.columns
