import time
import json
from prophet.serialize import model_from_json
from prometheus_client import start_http_server, Gauge
import os
import warnings

warnings.filterwarnings('ignore')

SHARED_DIR = "/shared-data"
MODEL_PATH = f"{SHARED_DIR}/prophet_model.json"

# Cổng phát sóng cho KEDA
PREDICTED_RPS = Gauge('prophet_predicted_rps', 'AI dự báo lượng RPS trong 15 phút tới')

def predict_and_serve():
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Chưa tìm thấy mô hình. Đang đợi AI Trainer làm việc...")
        return

    try:
        # 1. Đọc mô hình từ kho chung
        with open(MODEL_PATH, 'r') as fin:
            m = model_from_json(json.load(fin))
            
        # 2. Dự báo tương lai
        future = m.make_future_dataframe(periods=15, freq='min')
        forecast = m.predict(future)
        
        future_rps = forecast['yhat'].tail(15).max()
        future_rps = max(0, future_rps) 
        
        # 3. Phát sóng
        PREDICTED_RPS.set(future_rps)
        print(f"📡 ĐÃ PHÁT SÓNG: Dự báo đỉnh tải sắp tới là {future_rps:.2f} RPS")
        
    except Exception as e:
        print(f"❌ Lỗi khi dự báo: {e}")

if __name__ == '__main__':
    start_http_server(8000)
    print("🚀 Trạm phát sóng AI Server đã khởi động trên cổng 8000!")
    
    while True:
        predict_and_serve()
        time.sleep(60) # Cứ 60 giây dự báo lại 1 lần
