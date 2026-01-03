"""MLflow configuration"""

import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

# Set MLflow tracking URI
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Set experiment
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "investment_assistant")
mlflow.set_experiment(EXPERIMENT_NAME)

print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
print(f"MLflow experiment: {EXPERIMENT_NAME}")

