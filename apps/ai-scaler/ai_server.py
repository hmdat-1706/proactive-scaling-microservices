from fastapi import FastAPI
import pandas as pd
import mlflow.prophet
import os

app = FastAPI()
PREDICT_MINUTES = int(os.getenv("PREDICT_MINUTES", 15))

# Đọc model demo từ thư mục
model = mlflow.prophet.load_model("./prophet_model")

@app.get("/api/forecast")
def get_forecast():
    target_time = pd.Timestamp.now() + pd.Timedelta(minutes=PREDICT_MINUTES)
    future = pd.DataFrame({'ds': [target_time]})
    forecast = model.predict(future)
    res = round(float(forecast['yhat'].iloc[-1]), 2)
    return {"predicted_rps": max(0, res)}
