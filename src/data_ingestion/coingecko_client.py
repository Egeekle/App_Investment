"""CoinGecko API client for cryptocurrency data"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """Client for fetching cryptocurrency data from CoinGecko API"""
    
    def __init__(self, base_url: str = "https://api.coingecko.com/api/v3", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get_price_history(
        self, 
        coin_id: str, 
        days: int = 30,
        vs_currency: str = "usd"
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data
            vs_currency: Currency to compare against (default: usd)
        
        Returns:
            DataFrame with columns: date, price, market_cap, volume
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                "vs_currency": vs_currency,
                "days": days,
                "interval": "daily"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extract price data
            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            volumes = data.get("total_volumes", [])
            
            # Create DataFrame
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            # Add market cap and volume
            if market_caps:
                df_mc = pd.DataFrame(market_caps, columns=["timestamp", "market_cap"])
                df = df.merge(df_mc[["timestamp", "market_cap"]], on="timestamp", how="left")
            
            if volumes:
                df_vol = pd.DataFrame(volumes, columns=["timestamp", "volume"])
                df = df.merge(df_vol[["timestamp", "volume"]], on="timestamp", how="left")
            
            # Select and reorder columns
            df = df[["date", "price", "market_cap", "volume"]].copy()
            df = df.sort_values("date").reset_index(drop=True)
            
            logger.info(f"Fetched {len(df)} days of data for {coin_id}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing CoinGecko data: {e}")
            raise
    
    def get_current_price(self, coin_id: str, vs_currency: str = "usd") -> Dict:
        """Get current price for a cryptocurrency"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": vs_currency,
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return data.get(coin_id, {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current price: {e}")
            raise

