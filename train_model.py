import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
import joblib

# 1. Veri Setini Yükle
print("Loading Dataset...")
df = pd.read_csv('traffic_dataset.csv')

# Veriyi Hazırla
scaler_features = MinMaxScaler(feature_range=(0, 1))
scaler_target = MinMaxScaler(feature_range=(0, 1))
road_encoder = joblib.load('road_encoder.pkl') # Encoder'ı önceden oluşturmuştuk

# Feature Engineering
df['road_encoded'] = road_encoder.transform(df['road_id'])
df['congestion_level'] = df['congestion_status'].map({'LOCKED': 9, 'HEAVY': 6, 'NORMAL': 2})

features = df[['hour', 'road_encoded', 'congestion_level']].values
target = df[['speed']].values

features_scaled = scaler_features.fit_transform(features)
target_scaled = scaler_target.fit_transform(target)

# Scalerları kaydet (Predictor bunları kullanacak)
joblib.dump(scaler_features, 'scaler_features.pkl')
joblib.dump(scaler_target, 'scaler_target.pkl')

# Zaman Serisi Oluştur (Lookback = 3)
X, y = [], []
look_back = 3

for i in range(len(features_scaled) - look_back):
    X.append(features_scaled[i:i+look_back])
    y.append(target_scaled[i+look_back])

X, y = np.array(X), np.array(y)

# --- MODEL 1: LSTM (Eski Dostumuz) ---
print("Building LSTM Model...")
model_lstm = Sequential()
model_lstm.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model_lstm.add(Dropout(0.2))
model_lstm.add(LSTM(units=50))
model_lstm.add(Dropout(0.2))
model_lstm.add(Dense(units=1))
model_lstm.compile(optimizer='adam', loss='mean_squared_error')
model_lstm.fit(X, y, epochs=5, batch_size=32)
model_lstm.save('lstm_model.h5') # <-- İsim değişti!

# --- MODEL 2: GRU (Yeni Kardeş) ---
print("Building GRU Model (Hybrid Layer)...")
model_gru = Sequential()
model_gru.add(GRU(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model_gru.add(Dropout(0.2))
model_gru.add(GRU(units=50))
model_gru.add(Dropout(0.2))
model_gru.add(Dense(units=1))
model_gru.compile(optimizer='adam', loss='mean_squared_error')
model_gru.fit(X, y, epochs=5, batch_size=32)
model_gru.save('gru_model.h5') # <-- Yeni dosya!

print("✅ Hybrid Training Completed! Models saved: lstm_model.h5 & gru_model.h5")