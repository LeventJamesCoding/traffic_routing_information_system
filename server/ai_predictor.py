import time
import redis
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from keras.models import load_model 

print("Loading Hybrid AI Models and Scalers...")

# --- UPDATE: BETTER ERROR HANDLING ---
try:
    model_lstm = load_model('lstm_model.h5')
    model_gru = load_model('gru_model.h5')
    print("✅ LSTM & GRU Models Loaded Successfully.")
except Exception as e:
    # Print the REAL error message
    print(f"❌ CRITICAL ERROR: Could not load models.")
    print(f"Details: {e}")
    print("👉 HINT: Run 'python train_model.py' to regenerate model files.")
    exit()

scaler_features = joblib.load('scaler_features.pkl')
scaler_target = joblib.load('scaler_target.pkl')
encoder = joblib.load('road_encoder.pkl')

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# --- GÜNCELLEME: TÜM YOLLAR (12 ADET) ---
road_segments = [
    "E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center",
    "E5-Beylikduzu", "Tem-Seyrantepe", "Basin-Ekspres", "Sahil-Kennedy",
    "Bagdat-Caddesi", "Minibus-Yolu", "Levent-Buyukdere", "Haliç-Bridge"
]

print("🧠 AI Hybrid Predictor Service Started! Watching Blackboard...")

history_buffer = {road: [] for road in road_segments}

def prepare_input(road_id, hour, density):
    try:
        road_encoded = encoder.transform([road_id])[0]
    except ValueError:
        road_encoded = 0 
    return [hour, road_encoded, density]

try:
    while True:
        current_time = datetime.now()
        current_hour = current_time.hour
        
        for road in road_segments:
            redis_data = redis_client.hgetall(road)
            
            if not redis_data:
                continue 
            
            try:
                status = redis_data.get(b'congestion_status').decode('utf-8')
                
                # Kaza durumunu da yoğunluk olarak algılasın
                if status == 'ACCIDENT': density = 10
                elif status == 'LOCKED': density = 9
                elif status == 'HEAVY': density = 6
                else: density = 2
                
                input_features = prepare_input(road, current_hour, density)
                
                history_buffer[road].append(input_features)
                
                if len(history_buffer[road]) > 3:
                    history_buffer[road].pop(0)
                
                input_seq = list(history_buffer[road])
                while len(input_seq) < 3:
                    input_seq.append(input_features)
                
                input_scaled = scaler_features.transform(input_seq)
                input_reshaped = np.array([input_scaled])
                
                # --- HİBRİT TAHMİN (ENSEMBLE) ---
                pred_lstm = model_lstm.predict(input_reshaped, verbose=0)
                pred_gru = model_gru.predict(input_reshaped, verbose=0)
                
                # İki modelin ortalamasını al (Daha güvenilir sonuç)
                avg_prediction = (pred_lstm + pred_gru) / 2
                
                predicted_speed = scaler_target.inverse_transform(avg_prediction)[0][0]
                
                redis_client.hset(road, "predicted_speed", f"{predicted_speed:.1f}")
                
                print(f"({road}) Status: {status} -> Hybrid AI Predicts: {predicted_speed:.1f} km/h")
                
            except Exception as e:
                print(f"Error processing {road}: {e}")

        time.sleep(2) # Tahmin sıklığı

except KeyboardInterrupt:
    print("\nAI Predictor stopped.")