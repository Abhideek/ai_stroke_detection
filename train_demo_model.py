# train_demo_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib

# Synthetic small dataset (same features your app expects)
N = 1000
np.random.seed(42)
age = np.random.randint(30, 80, size=N)
sex = np.random.choice([0,1], size=N)
bp = np.random.normal(130, 15, size=N).astype(int)
chol = np.random.normal(240, 40, size=N).astype(int)
maxhr = np.random.normal(150, 20, size=N).astype(int)
angina = np.random.choice([0,1], size=N)

X = pd.DataFrame({
    "age": age,
    "sex": sex,
    "bp": bp,
    "cholesterol": chol,
    "maxhr": maxhr,
    "angina": angina
})
# simple target rule for demo only
y = ((chol > 250).astype(int) + (bp > 140).astype(int) + (angina==1).astype(int)) >= 2
y = y.astype(int)

# scaler + model
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# save files
import joblib
joblib.dump(scaler, "scaler.pkl")
joblib.dump(model, "model.pkl")
print("Saved scaler.pkl and model.pkl")
