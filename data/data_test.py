import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# CÔNG TẮC DEMO (ĐACN): 
# Đổi thành True -> Ép tất cả các giờ đều 600 RPS (Demo scale 10 Pod tức thì)
# Đổi thành False -> Data thực tế (Đêm thấp, ngày cao, 20h có bão sale)
GOD_MODE = True 
# ==========================================

def generate_mock_data():
    print("🚀 Bắt đầu sinh dữ liệu huấn luyện...")
    
    # Tạo chuỗi thời gian 7 ngày qua, mỗi phút 1 sample (giống KEDA lấy mẫu)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    date_rng = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    df = pd.DataFrame(date_rng, columns=['ds'])
    
    if GOD_MODE:
        # HACK DEMO: Giữ RPS luôn ở ngưỡng kích hoạt kịch trần
        print("🔥 CẢNH BÁO: Đang bật GOD MODE (Ép bão 600 RPS toàn thời gian)!")
        df['y'] = np.random.randint(580, 620, size=len(df))
    else:
        # DATA THỰC TẾ CÓ CHU KỲ
        print("🌍 Đang tạo dữ liệu chu kỳ thực tế...")
        base_rps = 40
        
        # 1. Thêm nhiễu ngẫu nhiên
        noise = np.random.normal(0, 5, len(df))
        
        # 2. Tạo sóng hình sin (Chu kỳ ngày đêm)
        time_seconds = (df['ds'] - df['ds'].min()).dt.total_seconds()
        daily_wave = 20 * np.sin(2 * np.pi * time_seconds / (24 * 3600))
        
        df['y'] = base_rps + daily_wave + noise
        
        # 3. Ép đỉnh Flash Sale (20h - 22h tối)
        flash_sale_mask = (df['ds'].dt.hour >= 20) & (df['ds'].dt.hour <= 22)
        df.loc[flash_sale_mask, 'y'] += np.random.randint(400, 550, size=flash_sale_mask.sum())

    # Đảm bảo không có số âm và làm tròn
    df['y'] = df['y'].clip(lower=10).round().astype(int)

    # Lưu ra file CSV (Nhớ copy vào thư mục data/ nếu cần)
    df.to_csv('mock_dataset.csv', index=False)
    
    print(f"✅ Đã lưu thành công {len(df)} dòng dữ liệu vào 'mock_dataset.csv'")
    print(f"📊 RPS Trung bình: {df['y'].mean():.2f} | RPS Cao nhất: {df['y'].max()}")

if __name__ == "__main__":
    generate_mock_data()
