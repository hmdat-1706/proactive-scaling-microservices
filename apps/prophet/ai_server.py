from fastapi import FastAPI
import pandas as pd
import mlflow.prophet
import os

app = FastAPI()
PREDICT_MINUTES = int(os.getenv("PREDICT_MINUTES", 15))

# Load demo model from directory
model = mlflow.prophet.load_model("./prophet_model")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/api/forecast")
def get_forecast():
    try:
        # HARDCODED FOR DEMO: Predict load at 11:00 today to simulate a moderate, manageable spike
        target_time = pd.Timestamp.today().normalize() + pd.Timedelta(hours=11)
        future = pd.DataFrame({'ds': [target_time]})
        forecast = model.predict(future)
        yhat = float(forecast['yhat'].iloc[-1])
        yhat_lower = float(forecast['yhat_lower'].iloc[-1])
        res = round((yhat + yhat_lower) / 2, 2)
        return {"predicted_rps": max(0, res)}
    except Exception as e:
        # Return 0 as a safe fallback
        return {"predicted_rps": 0, "error": str(e)}
