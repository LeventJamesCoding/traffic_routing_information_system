import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, GRU, Dense, Dropout
import joblib

print("Loading Dataset...")
# Veri setini yükle
try:
    df = pd.read_csv('traffic_dataset.csv')
except FileNotFoundError:
    print("❌ HATA: 'traffic_dataset.csv' bulunamadı! Lütfen önce 'create_dataset.py' çalıştırın.")
    exit()

scaler_features = MinMaxScaler(feature_range=(0, 1))
scaler_target = MinMaxScaler(feature_range=(0, 1))

# Encoder'ı yükle
try:
    road_encoder = joblib.load('road_encoder.pkl')
except FileNotFoundError:
    print("❌ HATA: 'road_encoder.pkl' bulunamadı! Lütfen önce 'create_dataset.py' çalıştırın.")
    exit()

# --- HATA BURADAYDI (DÜZELTİLDİ: rad_id -> road_id) ---
df['road_encoded'] = road_encoder.transform(df['road_id'])
# -----------------------------------------------------

df['congestion_level'] = df['congestion_status'].map({'LOCKED': 9, 'HEAVY': 6, 'NORMAL': 2})

features = df[['hour', 'road_encoded', 'congestion_level']].values
target = df[['speed']].values

features_scaled = scaler_features.fit_transform(features)
target_scaled = scaler_target.fit_transform(target)

joblib.dump(scaler_features, 'scaler_features.pkl')
joblib.dump(scaler_target, 'scaler_target.pkl')

X, y = [], []
look_back = 3

for i in range(len(features_scaled) - look_back):
    X.append(features_scaled[i:i+look_back])
    y.append(target_scaled[i+look_back])

X, y = np.array(X), np.array(y)

# LSTM
print("Training LSTM Model...")
model_lstm = Sequential()
model_lstm.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model_lstm.add(Dropout(0.2))
model_lstm.add(LSTM(units=50))
model_lstm.add(Dropout(0.2))
model_lstm.add(Dense(units=1))
model_lstm.compile(optimizer='adam', loss='mean_squared_error')
model_lstm.fit(X, y, epochs=5, batch_size=32)
model_lstm.save('lstm_model.h5')

# GRU
print("Training GRU Model...")
model_gru = Sequential()
model_gru.add(GRU(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model_gru.add(Dropout(0.2))
model_gru.add(GRU(units=50))
model_gru.add(Dropout(0.2))
model_gru.add(Dense(units=1))
model_gru.compile(optimizer='adam', loss='mean_squared_error')
model_gru.fit(X, y, epochs=5, batch_size=32)
model_gru.save('gru_model.h5')

print("✅ Training completed successfully. Models saved!")