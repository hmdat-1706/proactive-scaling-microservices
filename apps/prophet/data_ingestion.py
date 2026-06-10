import os
import requests
import pandas as pd
from datetime import datetime
import time

# Configurations
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090/api/v1/query_range")
PROMETHEUS_QUERY = os.getenv("PROMETHEUS_QUERY", "sum(rate(traefik_service_requests_total[1m]))")
DATA_PATH = os.getenv("DATA_PATH", "/mlflow/artifacts/data_lake/test_dataset.csv")
DATA_INTERVAL = int(os.getenv("DATA_INTERVAL", "5"))
DATA_DIR = os.path.dirname(DATA_PATH)

def fetch_daily_metrics():
    print(f"[{datetime.now()}] [INFO] Starting 24h data ingestion from Prometheus...")
    os.makedirs(DATA_DIR, exist_ok=True)

    # Calculate time range (Last 24h)
    end_time = int(time.time())
    start_time = end_time - (24 * 3600)
    step_seconds = DATA_INTERVAL * 60 # Automatically calculate step (e.g., 5 * 60 = 300s)

    try:
        response = requests.get(PROMETHEUS_URL, params={
            'query': PROMETHEUS_QUERY,
            'start': start_time,
            'end': end_time,
            'step': f'{step_seconds}s'
        }, timeout=15)
        
        data = response.json()
        if data.get('status') == 'success' and data['data']['result']:
            values = data['data']['result'][0]['values']
            
            # Convert to Pandas DataFrame
            df_new = pd.DataFrame(values, columns=['ds', 'y'])
            df_new['ds'] = pd.to_datetime(df_new['ds'], unit='s')
            df_new['y'] = df_new['y'].astype(float)

            # Deduplicate with existing data
            if os.path.isfile(DATA_PATH):
                df_existing = pd.read_csv(DATA_PATH)
                df_existing['ds'] = pd.to_datetime(df_existing['ds'])
                df_combined = pd.concat([df_existing, df_new])
                df_combined = df_combined.drop_duplicates(subset=['ds'], keep='last')
                df_combined.to_csv(DATA_PATH, index=False)
            else:
                df_new.to_csv(DATA_PATH, index=False)
            
            print(f"[{datetime.now()}] [SUCCESS] Appended {len(df_new)} rows to {DATA_PATH}")
        else:
            print(f"[{datetime.now()}] [WARN] Data ingestion successful but none data returned from Prometheus.")
            
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Prometheus connection failed: {e}")

if __name__ == "__main__":
    fetch_daily_metrics()
