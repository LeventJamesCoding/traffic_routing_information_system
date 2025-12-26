import json
import redis
import time
from kafka import KafkaConsumer

redis_client = redis.Redis(host='localhost', port=6379, db=0)

consumer = KafkaConsumer(
    'traffic_sensor_data', 
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Data Processing Service Active Listening to 'traffic_sensor_data'...")

try:
    for message in consumer:
        traffic_data = message.value
        
        road_id = traffic_data['road_id']
        speed = traffic_data['speed']
        status = traffic_data['congestion_status']
        timestamp = traffic_data['timestamp']

        processed_data = {
            'speed': speed,
            'congestion_status': status,
            'timestamp': timestamp,
            'last_updated': time.strftime("%H:%M:%S")
        }

        redis_client.hset(road_id, mapping=processed_data)
        print(f"💾 SAVED TO REDIS -> {road_id} | Spd: {speed} | Sts: {status}")

except KeyboardInterrupt:
    print("\nData Processing Service stopped.")
except Exception as e:
    print(f"❌ Error: {e}")