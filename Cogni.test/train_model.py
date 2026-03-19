import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

# Step 1: Generate Synthetic Dataset
np.random.seed(42)

data_size = 1000

wpm = np.random.normal(35, 10, data_size)
accuracy = np.random.normal(85, 10, data_size)
pauses = np.random.randint(0, 10, data_size)
backspaces = np.random.randint(0, 15, data_size)

# REAL numeric load score
load_score = (
    (100 - accuracy) * 0.5 +
    (pauses * 3) +
    (backspaces * 2) +
    (40 - wpm) * 0.7
)

df = pd.DataFrame({
    "wpm": wpm,
    "accuracy": accuracy,
    "pauses": pauses,
    "backspaces": backspaces,
    "load_score": load_score
})

# Step 2: Prepare Data
X = df[["wpm", "accuracy", "pauses", "backspaces"]]
y = df["load_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Step 3: Train Model
model = RandomForestRegressor(n_estimators=200)
model.fit(X_train, y_train)

# Step 4: Evaluate
predictions = model.predict(X_test)
print("R2 Score:", r2_score(y_test, predictions))

# Step 5: Save Model
joblib.dump(model, "cognitive_model.pkl")

print("Regression model trained and saved successfully.")
