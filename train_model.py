import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# 1. Load Dataset
print("⏳ Loading dataset...")
df = pd.read_csv('traffic_dataset.csv')

# 2. Preprocessing (Data Cleaning)
# AI works with numbers. Convert 'road_id' to numbers.
encoder = LabelEncoder()
df['road_id_encoded'] = encoder.fit_transform(df['road_id'])

# We need to predict 'speed' (to calculate travel time).
# Features: Hour, Road ID, Density -> Target: Speed
features = df[['hour', 'road_id_encoded', 'density']].values
target = df['speed'].values.reshape(-1, 1)

# Scale data to 0-1 range (Best for LSTM)
scaler_features = MinMaxScaler()
scaler_target = MinMaxScaler()

features_scaled = scaler_features.fit_transform(features)
target_scaled = scaler_target.fit_transform(target)

# 3. Create Sequences (Time Series Logic)
# Look back 3 steps (15 mins) to predict the next step.
X, y = [], []
look_back = 3 

for i in range(len(features_scaled) - look_back):
    X.append(features_scaled[i:i+look_back])
    y.append(target_scaled[i+look_back])

X, y = np.array(X), np.array(y)

# 4. Build LSTM Model
print("🧠 Building AI Model...")
model = Sequential()
# Layer 1: LSTM Memory Layer
model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2)) # Prevent overfitting

# Layer 2: LSTM Memory Layer
model.add(LSTM(units=50))
model.add(Dropout(0.2))

# Layer 3: Output Layer (Predict Speed)
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# 5. Train Model
print("🚀 Training Started... This might take a minute.")
model.fit(X, y, epochs=10, batch_size=32)

# 6. Save Artifacts
model.save('traffic_model.h5')
joblib.dump(scaler_features, 'scaler_features.pkl')
joblib.dump(scaler_target, 'scaler_target.pkl')
joblib.dump(encoder, 'road_encoder.pkl')

print("✅ Training Complete!")
print("💾 Model saved as 'traffic_model.h5'")
print("💾 Utilities saved as .pkl files")