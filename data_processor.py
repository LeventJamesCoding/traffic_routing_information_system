import json
from kafka import KafkaConsumer
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

consumer = KafkaConsumer(
    'raw_traffic_data', 
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🎧 Data Processing Service Active! Processing raw data and writing to Redis...")

try:
    for message in consumer:
        raw_data = message.value
        road_id = raw_data['yol_id']
        
        congestion_status = "NORMAL"
        if raw_data['yogunluk'] > 7:
            congestion_status = "LOCKED"
        elif raw_data['yogunluk'] > 4:
            congestion_status = "HEAVY"

        processed_data = {
            'speed': raw_data['hiz'],
            'congestion_status': congestion_status,
            'current_time': time.strftime("%H:%M:%S")
        }

        redis_client.hset(road_id, mapping=processed_data)
        
        print(f"✅ PROCESSED ({road_id}): Status: {congestion_status} -> Written to Redis.")

except KeyboardInterrupt:
    print("\n🛑 Data Processing Service stopped.")