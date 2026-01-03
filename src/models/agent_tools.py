"""Tools for the LangGraph agent"""

from typing import Dict, Any, List
import pandas as pd
import logging
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.data_ingestion.alpha_vantage_client import AlphaVantageClient
from src.data_ingestion.technical_indicators import enrich_with_indicators
from src.models.random_forest_model import RandomForestStrategyModel
from src.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class AgentTools:
    """Collection of tools available to the agent"""
    
    def __init__(
        self,
        coingecko_client: CoinGeckoClient,
        alpha_vantage_client: AlphaVantageClient,
        vector_store: VectorStore,
        rf_model: RandomForestStrategyModel
    ):
        self.coingecko_client = coingecko_client
        self.alpha_vantage_client = alpha_vantage_client
        self.vector_store = vector_store
        self.rf_model = rf_model
    
    def get_market_data(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Fetch market data for a symbol
        
        Args:
            symbol: Asset symbol (e.g., 'BTC', 'SPY', 'bitcoin')
            days: Number of days of historical data
        
        Returns:
            Dictionary with market data and indicators
        """
        try:
            # Determine if it's a crypto or ETF
            symbol_lower = symbol.lower()
            is_crypto = symbol_lower in ["bitcoin", "btc", "ethereum", "eth"]
            
            if is_crypto:
                # Map common symbols to CoinGecko IDs
                coin_id_map = {
                    "btc": "bitcoin",
                    "bitcoin": "bitcoin",
                    "eth": "ethereum",
                    "ethereum": "ethereum"
                }
                coin_id = coin_id_map.get(symbol_lower, symbol_lower)
                
                df = self.coingecko_client.get_price_history(
                    coin_id=coin_id,
                    days=days
                )
            else:
                # ETF/Stock via Alpha Vantage
                df = self.alpha_vantage_client.get_time_series_daily(
                    symbol=symbol.upper(),
                    outputsize="compact"
                )
            
            # Enrich with technical indicators
            df = enrich_with_indicators(df)
            
            # Get latest values
            latest = df.iloc[-1].to_dict()
            
            result = {
                "symbol": symbol,
                "data_points": len(df),
                "latest_price": latest.get("price", latest.get("close", 0)),
                "rsi": latest.get("rsi", 0),
                "sma_10": latest.get("sma_10", 0),
                "sma_20": latest.get("sma_20", 0),
                "volatility": latest.get("volatility", 0),
                "price_position": latest.get("price_position", 0),
                "dataframe": df  # Keep for model prediction
            }
            
            logger.info(f"Retrieved market data for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "data_points": 0
            }
    
    def get_news_sentiment(self, symbol: str, query: str = "") -> List[Dict[str, Any]]:
        """
        Search for relevant news and sentiment using RAG
        
        Args:
            symbol: Asset symbol
            query: Optional query string
        
        Returns:
            List of relevant news/sentiment documents
        """
        try:
            # Build search query
            search_query = f"{symbol} {query}" if query else symbol
            
            # Search with metadata filter
            results = self.vector_store.search(
                query=search_query,
                k=5,
                filter_dict={"symbol": symbol} if symbol else None
            )
            
            # Also search general financial knowledge
            general_results = self.vector_store.search(
                query=query or "investment strategy technical analysis",
                k=3
            )
            
            # Combine results
            all_results = results + general_results
            
            logger.info(f"Retrieved {len(all_results)} news/sentiment items for {symbol}")
            return all_results
            
        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")
            return []
    
    def predict_strategy(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict investment strategy using Random Forest model
        
        Args:
            market_data: Dictionary with market data (must include 'dataframe')
        
        Returns:
            Dictionary with prediction results
        """
        try:
            df = market_data.get("dataframe")
            if df is None or len(df) == 0:
                return {
                    "strategy": "UNKNOWN",
                    "confidence": 0.0,
                    "error": "No data available for prediction"
                }
            
            # Get latest row for prediction
            latest_df = df.tail(1)
            
            # Predict
            prediction = self.rf_model.predict(latest_df)[0]
            probabilities = self.rf_model.predict_proba(latest_df)[0]
            
            strategy = "TOP" if prediction == 1 else "BOTTOM"
            confidence = float(max(probabilities))
            
            result = {
                "strategy": strategy,
                "confidence": confidence,
                "probabilities": {
                    "TOP": float(probabilities[1]),
                    "BOTTOM": float(probabilities[0])
                },
                "reasoning": f"Model predicts {strategy} with {confidence:.2%} confidence"
            }
            
            logger.info(f"Predicted strategy: {strategy} (confidence: {confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting strategy: {e}")
            return {
                "strategy": "UNKNOWN",
                "confidence": 0.0,
                "error": str(e)
            }

