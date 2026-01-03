"""Tests for technical indicators"""

import pytest
import pandas as pd
import numpy as np
from src.data_ingestion.technical_indicators import (
    calculate_rsi,
    calculate_sma,
    enrich_with_indicators
)


def test_calculate_rsi():
    """Test RSI calculation"""
    # Create sample price data
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 5)
    
    rsi = calculate_rsi(prices, period=14)
    
    # RSI should be between 0 and 100
    assert all((rsi >= 0) & (rsi <= 100) | rsi.isna())
    assert len(rsi) == len(prices)


def test_calculate_sma():
    """Test SMA calculation"""
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
    
    sma = calculate_sma(prices, period=5)
    
    # First 4 values should be NaN
    assert pd.isna(sma.iloc[0:4]).all()
    # 5th value should be the mean of first 5
    assert sma.iloc[4] == pytest.approx(prices.iloc[0:5].mean(), rel=1e-5)


def test_enrich_with_indicators():
    """Test indicator enrichment"""
    # Create sample DataFrame
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=30, freq="D"),
        "price": 100 + np.random.randn(30).cumsum()
    })
    
    enriched = enrich_with_indicators(df)
    
    # Check that required columns exist
    assert "rsi" in enriched.columns
    assert "sma_10" in enriched.columns
    assert "sma_20" in enriched.columns
    assert "returns" in enriched.columns
    assert "volatility" in enriched.columns
    
    # Check that NaN values are handled
    assert enriched["rsi"].notna().any()  # At least some non-NaN values

