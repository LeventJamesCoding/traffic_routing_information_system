import time
import redis
import joblib
import numpy as np
import pandas as pd
from tensorflow import load_model
from datetime import datetime

print("Loading AI Model and Scalers...")
model = load_model('traffic_model.h5')
scaler_features = joblib.load('scaler_features.pkl')
scaler_target = joblib.load('scaler_target.pkl')
encoder = joblib.load('road_encoder.pkl')

redis_client = redis.Redis(host='localhost', port=6379, db=0)

road_segments = ["E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center"]

print("AI Predictor Service Started! Watching Blackboard...")

# Helper to maintain history for LSTM (We need 3 past steps)
# Dictionary format: {'E5-Bridge': [[hour, road, density], ...]}
history_buffer = {road: [] for road in road_segments}

def prepare_input(road_id, hour, density):
    # Convert 'road_id' to number using the saved encoder
    # Note: We use a try-except block in case of unseen labels, but here we cover all roads.
    try:
        road_encoded = encoder.transform([road_id])[0]
    except ValueError:
        road_encoded = 0 # Fallback
        
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
                
                if status == 'LOCKED': density = 9
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
                
                prediction_scaled = model.predict(input_reshaped, verbose=0)
                
                predicted_speed = scaler_target.inverse_transform(prediction_scaled)[0][0]
                
                redis_client.hset(road, "predicted_speed", f"{predicted_speed:.1f}")
                
                print(f"({road}) Current Status: {status} -> AI Predicts Speed in 15min: {predicted_speed:.1f} km/h")
                
            except Exception as e:
                print(f"Error processing {road}: {e}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nAI Predictor stopped.")