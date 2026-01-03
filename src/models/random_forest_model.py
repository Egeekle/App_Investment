"""Random Forest model for TOP/BOTTOM strategy classification"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import mlflow
import mlflow.sklearn
import logging
from typing import Tuple, Optional
import os

logger = logging.getLogger(__name__)


class RandomForestStrategyModel:
    """Random Forest model for classifying investment strategies (TOP/BOTTOM)"""
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,
            min_samples_split=5
        )
        self.feature_columns = [
            "rsi",
            "sma_10",
            "sma_20",
            "volatility",
            "price_position",
            "returns"
        ]
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for model training/prediction
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            DataFrame with feature columns
        """
        # Ensure all required columns exist
        missing_cols = set(self.feature_columns) - set(df.columns)
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}. Filling with 0.")
            for col in missing_cols:
                df[col] = 0
        
        # Select and normalize features
        features = df[self.feature_columns].copy()
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def create_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Create labels for training (TOP=1, BOTTOM=0)
        
        Strategy:
        - TOP (1): RSI < 35 AND price < sma_20 AND volatility > median
        - BOTTOM (0): RSI > 65 AND price > sma_20 AND volatility > median
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            Series with labels (0 or 1)
        """
        labels = pd.Series(0, index=df.index)
        
        # Calculate median volatility
        median_vol = df["volatility"].median() if "volatility" in df.columns else 0
        
        # TOP conditions
        top_conditions = (
            (df["rsi"] < 35) &
            (df["price"] < df["sma_20"]) &
            (df["volatility"] > median_vol)
        )
        
        # BOTTOM conditions
        bottom_conditions = (
            (df["rsi"] > 65) &
            (df["price"] > df["sma_20"]) &
            (df["volatility"] > median_vol)
        )
        
        labels[top_conditions] = 1  # TOP
        labels[bottom_conditions] = 0  # BOTTOM
        
        return labels
    
    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        mlflow_experiment: Optional[str] = None
    ) -> Tuple[float, dict]:
        """
        Train the Random Forest model
        
        Args:
            df: DataFrame with features and labels
            test_size: Proportion of data for testing
            mlflow_experiment: Optional MLflow experiment name
        
        Returns:
            Tuple of (accuracy, classification_report_dict)
        """
        try:
            # Prepare features and labels
            X = self.prepare_features(df)
            y = self.create_labels(df)
            
            # Remove rows where label is ambiguous (not clearly TOP or BOTTOM)
            valid_mask = (y == 0) | (y == 1)
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) == 0:
                raise ValueError("No valid training samples found")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Train model
            logger.info(f"Training model on {len(X_train)} samples")
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            logger.info(f"Model accuracy: {accuracy:.4f}")
            
            # Log to MLflow if experiment name provided
            if mlflow_experiment:
                mlflow.set_experiment(mlflow_experiment)
                with mlflow.start_run():
                    mlflow.log_params({
                        "n_estimators": self.model.n_estimators,
                        "max_depth": self.model.max_depth,
                        "min_samples_split": self.model.min_samples_split
                    })
                    mlflow.log_metric("accuracy", accuracy)
                    mlflow.log_metric("precision", report.get("1", {}).get("precision", 0))
                    mlflow.log_metric("recall", report.get("1", {}).get("recall", 0))
                    mlflow.sklearn.log_model(self.model, "model")
            
            return accuracy, report
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict strategy for given data
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            Array of predictions (0=BOTTOM, 1=TOP)
        """
        try:
            X = self.prepare_features(df)
            predictions = self.model.predict(X)
            return predictions
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
    
    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict strategy probabilities
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            Array of probability predictions [P(BOTTOM), P(TOP)]
        """
        try:
            X = self.prepare_features(df)
            probabilities = self.model.predict_proba(X)
            return probabilities
        except Exception as e:
            logger.error(f"Error making probability predictions: {e}")
            raise
    
    def save(self, filepath: str):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump(self.model, filepath)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load(self, filepath: str):
        """Load model from file"""
        try:
            self.model = joblib.load(filepath)
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

