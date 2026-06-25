import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle
import os

# ──────────────────────────────────────────────────────
#  STEP 1 — Generate a proper 500-row dataset
#
#  Your original dataset had only 7 rows.
#  7 rows is like trying to learn cricket
#  by watching 7 balls. Not enough.
#  We generate 500 realistic synthetic cases.
# ──────────────────────────────────────────────────────
np.random.seed(42)
n = 500

distance = np.random.randint(1, 20, n)   # 1–19 km :   total 500 values 
traffic  = np.random.randint(1, 4, n)    # 1=clear, 2=moderate, 3=heavy
urgency  = np.random.randint(1, 4, n)    # 1=mild, 2=moderate, 3=severe

# Response time formula:
# farther distance  → more time
# heavier traffic   → more time
# higher urgency    → slightly more time (complex handling)
# + small random noise to make it realistic
response_time = (
    (distance * 2.0) +
    (traffic  * 3.0) +
    (urgency  * 1.5) +
    np.random.normal(0, 1.5, n)
)
response_time = np.clip(response_time, 3, 60).round(1)

df = pd.DataFrame({
    'Distance':      distance,
    'Traffic':       traffic,
    'Urgency':       urgency,
    'Response_Time': response_time
})

df.to_csv('emergency_dataset.csv', index=False)
print(f"Dataset generated: {len(df)} rows")
print(df.head(10))
print()


# ──────────────────────────────────────────────────────
#  STEP 2 — Split into X (inputs) and y (output)  why ? because its regression- supervised ML model .
#
#  X = Distance, Traffic, Urgency  → what we KNOW
#  y = Response_Time               → what we PREDICT
#
#  Think: X = question, y = answer
#  Model studies question+answer pairs
#  so it can answer new questions on its own
# ──────────────────────────────────────────────────────
X = df[['Distance', 'Traffic', 'Urgency']]
y = df['Response_Time']


# ──────────────────────────────────────────────────────
#  STEP 3 — Train the model
#
#  RandomForestRegressor = 100 decision trees
#  all voting together → average answer
#
#  Like asking 100 experienced dispatchers:
#  "How long will this take?"
#  Take the average of all their answers.
# ──────────────────────────────────────────────────────
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
print("Model trained successfully on 500 cases.")
print()


# ──────────────────────────────────────────────────────
#  STEP 4 — Test with 3 different cases
#  to verify the model is working correctly
# ──────────────────────────────────────────────────────
test_cases = pd.DataFrame({
    'Distance': [2,  8,  15],
    'Traffic':  [1,  2,  3],
    'Urgency':  [3,  2,  1]
})

preds = model.predict(test_cases).round(1)
print("Test predictions:")
print(f"  Nearby + clear roads  → {preds[0]} mins  (expect ~8-10)")
print(f"  Mid distance + moderate → {preds[1]} mins (expect ~20-25)")
print(f"  Far + heavy traffic   → {preds[2]} mins  (expect ~40-45)")
print()


# ──────────────────────────────────────────────────────
#  STEP 5 — Save trained model as model.pkl
#
#  pickle = freeze the trained brain into a file
#  Flask loads this file — no retraining needed
#
#  Game analogy: model.py = playing the game
#                model.pkl = save file
#  app.py just loads the save file every time
# ──────────────────────────────────────────────────────
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model saved as model.pkl")
print("Now run: python app.py")
