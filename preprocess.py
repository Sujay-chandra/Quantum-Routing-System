# team_a_core/preprocess.py
import joblib
import numpy as np
from sklearn.preprocessing import MinMaxScaler

INPUT_FILE = "data/processed/labeled_dataset.joblib"
OUTPUT_FILE = "data/processed/preprocessed_data.joblib"
SCALER_FILE = "data/processed/scaler.joblib"

dataset = joblib.load(INPUT_FILE)
X, y = [], []
for instance in dataset:
    X.extend(instance["features"])
    y.extend(instance["labels"])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = X_scaled * 2 * np.pi

joblib.dump(scaler, SCALER_FILE)
joblib.dump({"X": X_scaled, "y": y}, OUTPUT_FILE)
print(f"✅ Preprocessed data saved to {OUTPUT_FILE}")