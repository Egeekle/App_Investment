"""Script to train the Random Forest model"""

import sys
import os
import pandas as pd
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.random_forest_model import RandomForestStrategyModel
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.data_ingestion.alpha_vantage_client import AlphaVantageClient
from src.data_ingestion.technical_indicators import enrich_with_indicators
from dotenv import load_dotenv
import mlflow

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_training_data():
    """Collect training data from multiple sources"""
    logger.info("Collecting training data...")
    
    coingecko = CoinGeckoClient()
    alpha_vantage = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""))
    
    all_data = []
    
    # Collect crypto data
    crypto_symbols = ["bitcoin", "ethereum"]
    for symbol in crypto_symbols:
        try:
            df = coingecko.get_price_history(symbol, days=90)
            df = enrich_with_indicators(df)
            df["symbol"] = symbol
            all_data.append(df)
            logger.info(f"Collected {len(df)} rows for {symbol}")
        except Exception as e:
            logger.warning(f"Error collecting data for {symbol}: {e}")
    
    # Collect ETF data
    etf_symbols = ["SPY", "QQQ"]
    for symbol in etf_symbols:
        try:
            df = alpha_vantage.get_time_series_daily(symbol, outputsize="compact")
            df = enrich_with_indicators(df)
            df["symbol"] = symbol
            all_data.append(df)
            logger.info(f"Collected {len(df)} rows for {symbol}")
        except Exception as e:
            logger.warning(f"Error collecting data for {symbol}: {e}")
    
    if not all_data:
        raise ValueError("No training data collected")
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Total training data: {len(combined_df)} rows")
    
    return combined_df


def main():
    """Main training function"""
    try:
        # Initialize MLflow
        from mlflow_config import EXPERIMENT_NAME
        mlflow.set_experiment(EXPERIMENT_NAME)
        
        # Collect data
        df = collect_training_data()
        
        # Initialize and train model
        model = RandomForestStrategyModel()
        
        logger.info("Training model...")
        accuracy, report = model.train(
            df=df,
            test_size=0.2,
            mlflow_experiment=EXPERIMENT_NAME
        )
        
        logger.info(f"Training completed. Accuracy: {accuracy:.4f}")
        
        # Save model
        model_path = os.getenv("MODEL_PATH", "./models/random_forest_model.pkl")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        model.save(model_path)
        
        logger.info(f"Model saved to {model_path}")
        
    except Exception as e:
        logger.error(f"Error in training: {e}")
        raise


if __name__ == "__main__":
    main()

