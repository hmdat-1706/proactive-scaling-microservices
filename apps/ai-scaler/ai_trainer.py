import pandas as pd
from prophet import Prophet
import mlflow
import mlflow.prophet
import os
import requests
from datetime import datetime

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://kube-prom-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/api/v1/query")

def fetch_metrics_and_append(data_path):
    print("Fetching latest RPS from Prometheus...")
    query = 'sum(rate(http_requests_total[1m]))'
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query}, timeout=10)
        data = response.json()
        if data.get('status') == 'success' and data['data']['result']:
            current_rps = float(data['data']['result'][0]['value'][1])
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_row = pd.DataFrame({'ds': [current_time], 'y': [current_rps]})
            
            # Check if file exists to decide whether to write the header
            file_exists = os.path.isfile(data_path)
            new_row.to_csv(data_path, mode='a', header=not file_exists, index=False)
            
            print(f"[OK] New data added to {data_path}: {current_time} - {current_rps:.2f} RPS")
        else:
            print("[WARN] Query successfully but new data not found.")
            
    except Exception as e:
        print(f"[ERROR] failed to connect with Prometheus: {e}. Keep current dataset.")

def train_and_push():
    data_path = os.getenv("DATASET_PATH", "mock_dataset.csv")
    data_interval = int(os.getenv("DATA_INTERVAL", "5")) 

    fetch_metrics_and_append(data_path)

    if not os.path.exists(data_path):
        print(f"Dataset not found: {data_path}")
        return

    print("Reading dataset...")
    df = pd.read_csv(data_path)

    # Ensure we have enough data points to train Prophet (e.g., minimum 5 rows)
    if len(df) < 5:
        print(f"[SKIP] Not enough data to train Prophet (current rows: {len(df)}). Need at least 5.")
        return

    # Convert to datetime format
    df['ds'] = pd.to_datetime(df['ds'])

    # Preprocessing: Resample time-series data to ensure uniform intervals
    df.set_index('ds', inplace=True)
    df = df.resample(f'{data_interval}T').mean()
    
    # Forward fill to handle missing values
    df = df.ffill().reset_index()

    # Double check after resampling in case data was squashed into too few rows
    if len(df) < 2:
         print("[SKIP] Not enough data points after resampling. Waiting for more data.")
         return

    print("Training Prophet...")
    m = Prophet(daily_seasonality=20)
    m.fit(df)

    print(f"Pushing to MLflow ({MLFLOW_URI})...")
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("Proactive_Scaling")
    
    with mlflow.start_run():
        mlflow.prophet.log_model(pr_model=m, artifact_path="prophet_model")
    print("Saved on MLflow successfully.")

if __name__ == "__main__":
    train_and_push()
