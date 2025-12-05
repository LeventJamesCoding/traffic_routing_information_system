import time
import json
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("Traffic Simulator Started! (Press CTRL+C to exit)")

road_segments = ["E5-Kopru", "Tem-Kavacik", "Besiktas-Sahil", "Kadikoy-Merkez"]

try:
    while True:
        data = {
            "yol_id": random.choice(road_segments),
            "hiz": random.randint(10, 120),       
            "yogunluk": random.randint(1, 10),    
            "timestamp": time.time()
        }
        
        producer.send('raw_traffic_data', value=data)
        
        print(f"SENT -> {data}")
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped.")