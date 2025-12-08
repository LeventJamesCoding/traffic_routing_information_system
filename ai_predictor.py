import time
import redis
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from datetime import datetime

# 1. Load the Trained Brain & Tools
print("🧠 Loading AI Model and Scalers...")
model = load_model('traffic_model.h5')
scaler_features = joblib.load('scaler_features.pkl')
scaler_target = joblib.load('scaler_target.pkl')
encoder = joblib.load('road_encoder.pkl')

# 2. Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Road segments to monitor
road_segments = ["E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center"]

print("🔮 AI Predictor Service Started! Watching Blackboard...")

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
            # A. Get Real-Time Data from Redis
            redis_data = redis_client.hgetall(road)
            
            if not redis_data:
                continue # No data yet for this road
            
            # Decode Redis bytes to strings/ints
            try:
                # We need 'density' for prediction.
                # Note: 'congestion_status' is text, we need the raw density number if possible.
                # In data_processor, we didn't save raw density to Redis, only status.
                # Let's fix this logic by estimating density from status OR 
                # BETTER: Update data_processor to save 'density' too.
                # FOR NOW: Let's assume we can map status back to a number for simplicity
                status = redis_data.get(b'congestion_status').decode('utf-8')
                
                if status == 'LOCKED': density = 9
                elif status == 'HEAVY': density = 6
                else: density = 2
                
                # B. Prepare Feature Vector
                input_features = prepare_input(road, current_hour, density)
                
                # C. Update History Buffer (We need 3 steps)
                history_buffer[road].append(input_features)
                
                # Keep only last 3 steps
                if len(history_buffer[road]) > 3:
                    history_buffer[road].pop(0)
                
                # If we don't have 3 steps yet, duplicate the current one to fill
                input_seq = list(history_buffer[road])
                while len(input_seq) < 3:
                    input_seq.append(input_features)
                
                # D. Scale and Reshape for LSTM
                # Shape must be (1, 3, 3) -> (Batch, TimeSteps, Features)
                input_scaled = scaler_features.transform(input_seq)
                input_reshaped = np.array([input_scaled])
                
                # E. PREDICT!
                prediction_scaled = model.predict(input_reshaped, verbose=0)
                
                # Inverse scale to get real speed (km/h)
                predicted_speed = scaler_target.inverse_transform(prediction_scaled)[0][0]
                
                # F. Write Prediction back to Redis
                redis_client.hset(road, "predicted_speed", f"{predicted_speed:.1f}")
                
                print(f"🔮 ({road}) Current Status: {status} -> AI Predicts Speed in 15min: {predicted_speed:.1f} km/h")
                
            except Exception as e:
                print(f"Error processing {road}: {e}")

        time.sleep(5) # Predict every 5 seconds

except KeyboardInterrupt:
    print("\n🛑 AI Predictor stopped.")