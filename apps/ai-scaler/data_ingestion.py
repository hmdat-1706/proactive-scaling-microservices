import os
import requests
import pandas as pd
from datetime import datetime
import time

# Configurations
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090/api/v1/query_range")
PROMETHEUS_QUERY = os.getenv("PROMETHEUS_QUERY", "sum(rate(http_requests_total[1m]))")
DATA_PATH = os.getenv("DATA_PATH", "/mlflow/artifacts/data_lake/test_dataset.csv")
DATA_INTERVAL = int(os.getenv("DATA_INTERVAL", "5"))
DATA_DIR = os.path.dirname(DATA_PATH)

def fetch_daily_metrics():
    print(f"[{datetime.now()}] [INFO] Starting data ingestion from Prometheus...")
    os.makedirs(DATA_DIR, exist_ok=True)

    # Calculate time range (Last 24h)
    end_time = int(time.time())
    start_time = end_time - (24 * 3600)
    step_seconds = DATA_INTERVAL * 60 # Tự động tính step (VD: 5 * 60 = 300s)

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

            # Append to Data Lake (test_dataset.csv)
            file_exists = os.path.isfile(DATA_PATH)
            df_new.to_csv(DATA_PATH, mode='a', header=not file_exists, index=False)
            
            print(f"[{datetime.now()}] [SUCCESS] Appended {len(df_new)} rows to {DATA_PATH}")
        else:
            print(f"[{datetime.now()}] [WARN] Query successful but no data returned from Prometheus.")
            
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Prometheus connection failed: {e}")

if __name__ == "__main__":
    fetch_daily_metrics()
