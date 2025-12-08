import json
from kafka import KafkaConsumer
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

consumer = KafkaConsumer(
    'raw_traffic_data', 
    bootstrap_servers=['localhost:9092'],
    api_version=(0, 10, 1), 
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Data Processing Service Active! Processing raw data and writing to Redis...")

try:
    for message in consumer:
        raw_data = message.value
        
        road_id = raw_data['road_id']
        density = raw_data['density']
        speed = raw_data['speed']
        
        status = "NORMAL"
        if density > 7:
            status = "LOCKED"
        elif density > 4:
            status = "HEAVY"

        processed_data = {
            'speed': speed,
            'congestion_status': status,
            'last_updated': time.strftime("%H:%M:%S")
        }

        redis_client.hset(road_id, mapping=processed_data)
        
        print(f"PROCESSED ({road_id}): Status: {status} -> Written to Redis.")

except KeyboardInterrupt:
    print("\n🛑 Data Processing Service stopped.")