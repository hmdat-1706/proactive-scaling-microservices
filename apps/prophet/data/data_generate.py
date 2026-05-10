import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_pro_traffic_data():
    print("⏳ Đang sinh dữ liệu bão traffic trong 3 tháng...")
    
    # 1. Khởi tạo dải thời gian: 90 ngày, mỗi 5 phút 1 dòng (đủ chi tiết nhưng file không bị quá nặng để train)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    df = pd.DataFrame({'ds': pd.date_range(start=start_date, end=end_date, freq='5min')})
    
    # 2. TĂNG TRƯỞNG DẦN (Trend): Lượng user gốc tăng dần từ đầu tháng 1 đến tháng 3
    total_steps = len(df)
    df['trend'] = np.linspace(100, 300, total_steps) # Nền tảng tăng trưởng dần
    
    # 3. CHU KỲ TRONG NGÀY (Daily Seasonality)
    def get_daily_multiplier(hour):
        if 0 <= hour < 6: return 0.15    # Giờ ngủ: Đáy
        elif 6 <= hour < 8: return 0.4   # Dậy, đi làm
        elif 8 <= hour < 11: return 0.6  # Giờ hành chính sáng (Vắng)
        elif 11 <= hour < 13: return 1.2 # Nghỉ trưa lướt đt (Đông)
        elif 13 <= hour < 17: return 0.5 # Giờ hành chính chiều (Vắng)
        elif 17 <= hour < 19: return 1.0 # Tan làm
        elif 19 <= hour < 23: return 1.8 # Tối ở nhà (Đỉnh trong ngày)
        else: return 0.3
    
    df['daily_mult'] = df['ds'].dt.hour.apply(get_daily_multiplier)
    
    # (Làm mượt đường cong hàng ngày để không bị giật cục)
    df['daily_mult'] = df['daily_mult'].rolling(window=12, min_periods=1, center=True).mean()
    
    # 4. CHU KỲ CUỐI TUẦN (Weekly Seasonality)
    df['is_weekend'] = df['ds'].dt.dayofweek >= 5 # Thứ 7, CN
    df['weekly_mult'] = np.where(df['is_weekend'], 1.4, 1.0) # Cuối tuần đông hơn 40%
    
    # Tính RPS cơ sở
    df['y'] = df['trend'] * df['daily_mult'] * df['weekly_mult']
    
    # 5. NGÀY ĐÔI (Sale Double Days: 4/4, 5/5, 6/6...)
    is_double_day = df['ds'].dt.day == df['ds'].dt.month
    df.loc[is_double_day, 'y'] *= 1.6 # Gấp 1.6 lần bình thường
    
    # 6. FLASH SALE CUỐI TUẦN (20h - 22h T7, CN)
    flash_sale_mask = (df['is_weekend']) & (df['ds'].dt.hour >= 20) & (df['ds'].dt.hour < 22)
    df.loc[flash_sale_mask, 'y'] += 150 # Nhồi thêm thẳng 150 RPS
    
    # 7. NHIỄU NGẪU NHIÊN (Noise: Làm cho dữ liệu chân thực)
    noise = np.random.normal(0, df['y'] * 0.08) # 8% độ nhiễu
    df['y'] = df['y'] + noise
    
    # 8. CHUẨN HÓA ĐỈNH VỀ ĐÚNG 600 RPS
    current_max = df['y'].max()
    scale_factor = 600 / current_max
    df['y'] = df['y'] * scale_factor
    
    # Làm tròn và không cho phép rớt dưới 5 RPS
    df['y'] = df['y'].clip(lower=15).astype(int)
    
    # Lưu file
    final_df = df[['ds', 'y']]
    final_df.to_csv('mock_dataset.csv', index=False)
    print(f"✅ Đã tạo xong! {len(final_df)} bản ghi. Đỉnh cao nhất đạt: {final_df['y'].max()} RPS.")

if __name__ == "__main__":
    generate_pro_traffic_data()
