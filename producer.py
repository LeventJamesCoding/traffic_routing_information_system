import time
import json
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    api_version=(0, 10, 1), 
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚦 Traffic Simulator Started! (Press CTRL+C to exit)")

road_segments = ["E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center"]

try:
    while True:
        data = {
            "road_id": random.choice(road_segments),
            "speed": random.randint(10, 120),       
            "density": random.randint(1, 10),    
            "timestamp": time.time()
        }

        producer.send('raw_traffic_data', value=data)
        
        print(f"SENT -> {data}")
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped.")