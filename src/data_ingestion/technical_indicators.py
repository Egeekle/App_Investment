"""Technical indicators calculation module"""

import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: Series of closing prices
        period: Period for RSI calculation (default: 14)
    
    Returns:
        Series with RSI values
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: Series of prices
        period: Period for SMA calculation
    
    Returns:
        Series with SMA values
    """
    return prices.rolling(window=period).mean()


def calculate_volatility(returns: pd.Series, period: int = 30) -> pd.Series:
    """
    Calculate volatility (standard deviation of returns)
    
    Args:
        returns: Series of returns
        period: Rolling window period
    
    Returns:
        Series with volatility values
    """
    return returns.rolling(window=period).std() * np.sqrt(252)  # Annualized


def calculate_price_position(df: pd.DataFrame, period: int = 30) -> pd.Series:
    """
    Calculate price position in range (0-100)
    
    Args:
        df: DataFrame with 'high', 'low', 'close' columns
        period: Period for range calculation
    
    Returns:
        Series with position values (0 = bottom, 100 = top)
    """
    high_max = df["high"].rolling(window=period).max()
    low_min = df["low"].rolling(window=period).min()
    
    position = ((df["close"] - low_min) / (high_max - low_min)) * 100
    return position


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate daily returns
    
    Args:
        prices: Series of prices
    
    Returns:
        Series with returns
    """
    return prices.pct_change()


def enrich_with_indicators(
    df: pd.DataFrame,
    rsi_period: int = 14,
    sma_short: int = 10,
    sma_long: int = 20
) -> pd.DataFrame:
    """
    Enrich DataFrame with technical indicators
    
    Args:
        df: DataFrame with 'price' or 'close' column
        rsi_period: Period for RSI calculation
        sma_short: Period for short SMA
        sma_long: Period for long SMA
    
    Returns:
        Enriched DataFrame
    """
    df = df.copy()
    
    # Use 'price' if available, otherwise 'close'
    price_col = "price" if "price" in df.columns else "close"
    prices = df[price_col]
    
    # Calculate returns
    df["returns"] = calculate_returns(prices)
    
    # Calculate RSI
    df["rsi"] = calculate_rsi(prices, period=rsi_period)
    
    # Calculate SMAs
    df[f"sma_{sma_short}"] = calculate_sma(prices, period=sma_short)
    df[f"sma_{sma_long}"] = calculate_sma(prices, period=sma_long)
    
    # Calculate volatility
    df["volatility"] = calculate_volatility(df["returns"])
    
    # Calculate price position if we have high/low data
    if all(col in df.columns for col in ["high", "low", "close"]):
        df["price_position"] = calculate_price_position(df)
    elif "price" in df.columns:
        # Approximate using price range
        df["high"] = df["price"]
        df["low"] = df["price"]
        df["close"] = df["price"]
        df["price_position"] = calculate_price_position(df)
    
    # Clean up NaN values
    df = df.dropna(subset=["rsi", f"sma_{sma_short}", f"sma_{sma_long}"])
    
    logger.info(f"Enriched DataFrame with technical indicators. Shape: {df.shape}")
    return df

