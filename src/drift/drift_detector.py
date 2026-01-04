"""
Drift Detection Module
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional
import logging
import json
import os

logger = logging.getLogger(__name__)

class DriftDetector:
    """Detects drift in model predictions and agent actions"""
    
    def __init__(self, reference_data_path: str = "./data/drift_reference.json"):
        self.reference_data_path = reference_data_path
        self.reference_data = self._load_reference_data()
        
    def _load_reference_data(self) -> Dict[str, Any]:
        """Load reference distributions"""
        if os.path.exists(self.reference_data_path):
            try:
                with open(self.reference_data_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading drift reference: {e}")
        return {"predictions": [], "actions": []}

    def update_reference(self, new_prediction: float, new_action: str):
        """Update reference data (simple sliding window or append)"""
        # In a real system, we'd have a separate training set reference.
        # Here we collect data to build a baseline if empty.
        self.reference_data["predictions"].append(new_prediction)
        self.reference_data["actions"].append(new_action)
        
        # Keep window size manageable
        if len(self.reference_data["predictions"]) > 1000:
            self.reference_data["predictions"] = self.reference_data["predictions"][-1000:]
            self.reference_data["actions"] = self.reference_data["actions"][-1000:]
            
        self._save_reference()

    def _save_reference(self):
        try:
            os.makedirs(os.path.dirname(self.reference_data_path), exist_ok=True)
            with open(self.reference_data_path, 'w') as f:
                json.dump(self.reference_data, f)
        except Exception as e:
            logger.error(f"Error saving drift reference: {e}")

    def detect_prediction_drift(self, current_predictions: List[float]) -> Dict[str, Any]:
        """
        Detect drift in model confidence predictions using KS Test
        """
        if len(self.reference_data["predictions"]) < 50 or len(current_predictions) < 10:
            return {"drift_detected": False, "reason": "Insufficient data"}
            
        # Kolmogorov-Smirnov test
        statistic, p_value = stats.ks_2samp(self.reference_data["predictions"], current_predictions)
        
        drift_detected = p_value < 0.05
        
        return {
            "drift_detected": drift_detected,
            "p_value": p_value,
            "statistic": statistic,
            "method": "KS Test"
        }

    def detect_action_drift(self, current_actions: List[str]) -> Dict[str, Any]:
        """
        Detect drift in agent actions (categorical) using Chi-Square
        """
        if len(self.reference_data["actions"]) < 50 or len(current_actions) < 10:
            return {"drift_detected": False, "reason": "Insufficient data"}
            
        # simple distribution comparison
        ref_counts = pd.Series(self.reference_data["actions"]).value_counts(normalize=True)
        curr_counts = pd.Series(current_actions).value_counts(normalize=True)
        
        # Calculate divergence (e.g., max difference in proportions)
        all_actions = set(ref_counts.index) | set(curr_counts.index)
        max_diff = 0
        for action in all_actions:
            diff = abs(ref_counts.get(action, 0) - curr_counts.get(action, 0))
            if diff > max_diff:
                max_diff = diff
                
        # Threshold for action distribution change
        drift_detected = max_diff > 0.2
        
        return {
            "drift_detected": drift_detected,
            "max_difference": max_diff,
            "method": "Proportion Difference"
        }
