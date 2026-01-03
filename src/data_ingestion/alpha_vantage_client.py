"""Alpha Vantage API client for ETF and stock data"""

import requests
import pandas as pd
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Client for fetching ETF and stock data from Alpha Vantage API"""
    
    def __init__(self, api_key: str, base_url: str = "https://www.alphavantage.co/query", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
    
    def get_time_series_daily(
        self, 
        symbol: str,
        outputsize: str = "compact"
    ) -> pd.DataFrame:
        """
        Fetch daily time series data for an ETF or stock
        
        Args:
            symbol: Stock/ETF symbol (e.g., 'SPY', 'QQQ')
            outputsize: 'compact' (last 100 data points) or 'full' (full history)
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": outputsize,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
            if "Note" in data:
                raise ValueError(f"Alpha Vantage API Rate Limit: {data['Note']}")
            
            # Extract time series data
            time_series = data.get("Time Series (Daily)", {})
            
            if not time_series:
                raise ValueError(f"No time series data found for symbol {symbol}")
            
            # Convert to DataFrame
            records = []
            for date_str, values in time_series.items():
                records.append({
                    "date": pd.to_datetime(date_str),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"])
                })
            
            df = pd.DataFrame(records)
            df = df.sort_values("date").reset_index(drop=True)
            
            # Use close as price for consistency
            df["price"] = df["close"]
            
            logger.info(f"Fetched {len(df)} days of data for {symbol}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing Alpha Vantage data: {e}")
            raise
    
    def get_technical_indicators(
        self,
        symbol: str,
        indicator: str = "RSI",
        interval: str = "daily",
        time_period: int = 14
    ) -> pd.DataFrame:
        """
        Fetch technical indicators from Alpha Vantage
        
        Args:
            symbol: Stock/ETF symbol
            indicator: Technical indicator (RSI, SMA, EMA, etc.)
            interval: Time interval (daily, weekly, monthly)
            time_period: Period for the indicator
        
        Returns:
            DataFrame with indicator values
        """
        try:
            function_map = {
                "RSI": "RSI",
                "SMA": "SMA",
                "EMA": "EMA"
            }
            
            function = function_map.get(indicator.upper(), "RSI")
            
            params = {
                "function": function,
                "symbol": symbol,
                "interval": interval,
                "time_period": time_period,
                "series_type": "close",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if "Error Message" in data or "Note" in data:
                logger.warning(f"Could not fetch {indicator} for {symbol}")
                return pd.DataFrame()
            
            # Extract indicator data
            key = f"Technical Analysis: {function}"
            if key not in data:
                return pd.DataFrame()
            
            indicator_data = data[key]
            records = []
            for date_str, values in indicator_data.items():
                records.append({
                    "date": pd.to_datetime(date_str),
                    indicator.lower(): float(values[function])
                })
            
            df = pd.DataFrame(records)
            df = df.sort_values("date").reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.warning(f"Error fetching technical indicator {indicator}: {e}")
            return pd.DataFrame()

