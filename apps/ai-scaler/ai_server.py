from fastapi import FastAPI
import math
import pandas as pd
import mlflow.prophet
from mlflow.tracking import MlflowClient
import os

app = FastAPI()
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-service.mlops.svc.cluster.local:5000")
mlflow.set_tracking_uri(MLFLOW_URI)
PREDICT_MINUTES = int(os.getenv("PREDICT_MINUTES", 15))

client = MlflowClient()
experiment = client.get_experiment_by_name("Proactive_Scaling")
runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=1)

latest_run_id = runs[0].info.run_id
MODEL_URI = f"runs:/{latest_run_id}/prophet_model"

model = mlflow.prophet.load_model(MODEL_URI)

@app.get("/api/forecast")
def get_forecast():
    target_time = pd.Timestamp.now() + pd.Timedelta(minutes=PREDICT_MINUTES)
    future = pd.DataFrame({'ds': [target_time]})
    forecast = model.predict(future)
    res = round(float(forecast['yhat'].iloc[-1]), 2)
    return {"predicted_rps": max(0, res)}
