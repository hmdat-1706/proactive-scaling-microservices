import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_pro_traffic_data():
    print("⏳ Generating 3 months of traffic data...")
    
    # 1. Initialize time range: 90 days, 1 row per 5 minutes (detailed but not too heavy for training)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    df = pd.DataFrame({'ds': pd.date_range(start=start_date, end=end_date, freq='5min')})
    
    # 2. TREND: Baseline user count gradually increases from Jan to March
    total_steps = len(df)
    df['trend'] = np.linspace(100, 300, total_steps) # Growing baseline
    
    # 3. DAILY SEASONALITY
    def get_daily_multiplier(hour):
        if 0 <= hour < 6: return 0.15    # Sleeping hours: Bottom
        elif 6 <= hour < 8: return 0.4   # Waking up, commuting
        elif 8 <= hour < 11: return 0.6  # Morning office hours (Low)
        elif 11 <= hour < 13: return 1.2 # Lunch break (High)
        elif 13 <= hour < 17: return 0.5 # Afternoon office hours (Low)
        elif 17 <= hour < 19: return 1.0 # After work
        elif 19 <= hour < 23: return 1.8 # Evening at home (Daily Peak)
        else: return 0.3
    
    df['daily_mult'] = df['ds'].dt.hour.apply(get_daily_multiplier)
    
    # (Smooth the daily curve to prevent sudden spikes)
    df['daily_mult'] = df['daily_mult'].rolling(window=12, min_periods=1, center=True).mean()
    
    # 4. WEEKLY SEASONALITY
    df['is_weekend'] = df['ds'].dt.dayofweek >= 5 # Saturday, Sunday
    df['weekly_mult'] = np.where(df['is_weekend'], 1.4, 1.0) # Weekends are 40% higher
    
    # Calculate base RPS
    df['y'] = df['trend'] * df['daily_mult'] * df['weekly_mult']
    
    # 5. DOUBLE DAY SALES (4/4, 5/5, 6/6...)
    is_double_day = df['ds'].dt.day == df['ds'].dt.month
    df.loc[is_double_day, 'y'] *= 1.6 # 1.6x multiplier
    
    # 6. WEEKEND FLASH SALE (20h - 22h Sat, Sun)
    flash_sale_mask = (df['is_weekend']) & (df['ds'].dt.hour >= 20) & (df['ds'].dt.hour < 22)
    df.loc[flash_sale_mask, 'y'] += 150 # Directly inject 150 RPS
    
    # 7. RANDOM NOISE (Make data look realistic)
    noise = np.random.normal(0, df['y'] * 0.08) # 8% noise
    df['y'] = df['y'] + noise
    
    # 8. NORMALIZE PEAK TO EXACTLY 600 RPS
    current_max = df['y'].max()
    scale_factor = 600 / current_max
    df['y'] = df['y'] * scale_factor
    
    # Round and prevent dropping below 5 RPS
    df['y'] = df['y'].clip(lower=15).astype(int)
    
    # Save file
    final_df = df[['ds', 'y']]
    final_df.to_csv('mock_dataset.csv', index=False)
    print(f"✅ Generation complete! {len(final_df)} records. Highest peak reached: {final_df['y'].max()} RPS.")

if __name__ == "__main__":
    generate_pro_traffic_data()
