import pandas as pd
from prophet import Prophet
import mlflow
import mlflow.prophet
import os
from datetime import datetime, timedelta

# Configurations
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-service.boutique.svc.cluster.local:5000")
DATA_PATH = os.getenv("DATA_PATH", "/mlflow/artifacts/data_lake/test_dataset.csv")
WINDOW_DAYS = int(os.getenv("RETRAIN_WINDOW_DAYS", "90"))
DATA_INTERVAL = os.getenv("DATA_INTERVAL", "5")

def retrain_model():
    print(f"[{datetime.now()}] [INFO] Initiating Sliding Window Retraining Pipeline...")

    if not os.path.exists(DATA_PATH):
        print(f"[{datetime.now()}] [ERROR] Data Lake not found at {DATA_PATH}")
        return

    print(f"[{datetime.now()}] [INFO] Loading dataset from Data Lake...")
    df = pd.read_csv(DATA_PATH)
    df['ds'] = pd.to_datetime(df['ds'])

    # Extract sliding window
    cutoff_date = datetime.now() - timedelta(days=WINDOW_DAYS)
    df_window = df[df['ds'] >= cutoff_date].copy()
    
    print(f"[{datetime.now()}] [INFO] Total historical records: {len(df)}. Sliding window ({WINDOW_DAYS} days): {len(df_window)} records.")

    if len(df_window) < 288: 
        print(f"[{datetime.now()}] [SKIP] Insufficient data points ({len(df_window)}). Minimum 288 required.")
        return

    # Data Preprocessing
    df_window.set_index('ds', inplace=True)
    df_window = df_window.resample(f'{DATA_INTERVAL}T').mean().ffill().reset_index()

    print(f"[{datetime.now()}] [INFO] Fitting Prophet model...")
    m = Prophet(daily_seasonality=True, weekly_seasonality=True)
    m.fit(df_window)

    print(f"[{datetime.now()}] [INFO] Pushing new model to MLflow Tracking Server ({MLFLOW_URI})...")
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("Proactive_Scaling")
    
    with mlflow.start_run() as run:
        mlflow.prophet.log_model(pr_model=m, artifact_path="prophet_model")
        mlflow.log_param("window_days", WINDOW_DAYS)
        mlflow.log_param("data_points", len(df_window))
        mlflow.set_tag("status", "drift_quarantine") 
        print(f"[{datetime.now()}] [SUCCESS] Model registered successfully. Run ID: {run.info.run_id}")

if __name__ == "__main__":
    retrain_model()
