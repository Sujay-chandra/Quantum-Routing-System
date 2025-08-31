# team_a_core/inference.py
import joblib
import numpy as np

def predict_assignments(customers, demands):
    vqc = joblib.load("data/models/vqc_model.joblib")
    scaler = joblib.load("data/processed/scaler.joblib")
    X = np.array([[c[0], c[1], d] for c, d in zip(customers, demands)])
    X = scaler.transform(X) * 2 * np.pi
    return vqc.predict(X).tolist()