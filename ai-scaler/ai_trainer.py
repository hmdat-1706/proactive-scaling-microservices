import pandas as pd
import requests
import json
from datetime import datetime, timezone, timedelta
from prophet import Prophet
from prophet.serialize import model_to_json
import os
import warnings

warnings.filterwarnings('ignore')

# 1. Cấu hình
MIMIR_URL = "http://mimir.monitoring.svc.cluster.local:9009/prometheus/api/v1/query_range"
# Đường dẫn ổ cứng chung (PVC) trong Pod
SHARED_DIR = "/shared-data"
MODEL_PATH = f"{SHARED_DIR}/prophet_model.json"

def fetch_and_train():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ BẮT ĐẦU QUÁ TRÌNH HUẤN LUYỆN...")
    try:
        # Đảm bảo thư mục dùng chung tồn tại
        os.makedirs(SHARED_DIR, exist_ok=True)

        # 1. Kéo dữ liệu 1 giờ qua
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=60)
        
        params = {
            "query": "sum(nginx_ingress_controller_nginx_process_requests_total)",
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "30s"
        }
        
        response = requests.get(MIMIR_URL, params=params)
        results = response.json()['data']['result'][0]['values']
        
        # 2. Xử lý dữ liệu
        df = pd.DataFrame(results, columns=['timestamp', 'total_requests'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s') + timedelta(hours=7)
        df['total_requests'] = df['total_requests'].astype(float)
        df['rps'] = df['total_requests'].diff() / 30.0
        df['rps'] = df['rps'].fillna(0).clip(lower=0)
        
        start_t = df['timestamp'].min()
        df['ds'] = start_t + (df['timestamp'] - start_t) * 30 
        df['y'] = df['rps']
        
        # 3. Huấn luyện mô hình
        print("🧠 Đang cập nhật kiến thức cho mô hình Prophet...")
        m = Prophet(daily_seasonality=True, weekly_seasonality=False, yearly_seasonality=False)
        m.fit(df[['ds', 'y']])
        
        # 4. Lưu mô hình (Serialize) ra ổ cứng chung
        with open(MODEL_PATH, 'w') as fout:
            json.dump(model_to_json(m), fout)
            
        print(f"✅ Đã lưu mô hình thành công tại {MODEL_PATH}")
        print("💤 Thợ rèn AI Trainer xin phép đi ngủ!")

    except Exception as e:
        print(f"❌ Lỗi trong quá trình huấn luyện: {e}")

if __name__ == '__main__':
    fetch_and_train()
