import time
import json
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

ROADS = [
    "E5-Beylikduzu-Avcilar", "E5-Avcilar-Kucukcekmece", "E5-Kucukcekmece-Bakirkoy",
    "E5-Bakirkoy-Merter", "E5-Merter-Topkapi", "E5-Topkapi-Halic",
    "E5-Halic-Mecidiyekoy", "E5-Mecidiyekoy-Zincirlikuyu",
    "Tem-Mahmutbey-Seyrantepe", "Tem-Seyrantepe-FSM",
    "Coast-Zeytinburnu-Eminonu", "Coast-Besiktas-Sariyer",
    
    "Bridge-15-July", "Bridge-FSM",
    
    "E5-Altunizade-Uzuncayir", "E5-Uzuncayir-Bostanci", "E5-Bostanci-Pendik",
    "Tem-Kavacik-Umraniye", "Tem-Umraniye-Atasehir",
    "Coast-Uskudar-Harem", "Coast-Kadikoy-Bostanci"
]

current_speeds = {road: random.randint(40, 90) for road in ROADS}
accident_status = {road: False for road in ROADS}

def generate_traffic_data():
    while True:
        for road_id in ROADS:
            if not accident_status[road_id] and random.random() < 0.01:
                accident_status[road_id] = True
                print(f"KAZA OLDU! -> {road_id}")
            elif accident_status[road_id] and random.random() < 0.05:
                accident_status[road_id] = False
                print(f"KAZA KALDIRILDI -> {road_id}")

            if accident_status[road_id]:
                current_speeds[road_id] = max(0, min(15, current_speeds[road_id] + random.randint(-2, 2)))
            else:
                change = random.randint(-5, 5)
                current_speeds[road_id] = max(5, min(110, current_speeds[road_id] + change))

            speed = current_speeds[road_id]
            
            if accident_status[road_id]:
                status = "ACCIDENT"
            elif speed < 30:
                status = "LOCKED"
            elif speed < 60:
                status = "HEAVY"
            else:
                status = "NORMAL"

            traffic_data = {
                "road_id": road_id,
                "speed": speed,
                "congestion_status": status,
                "timestamp": time.time()
            }
            
            producer.send('traffic_sensor_data', traffic_data)
            print(f"SENT -> {traffic_data}")
        
        time.sleep(1)

if __name__ == "__main__":
    print("Smart Traffic Simulator Started with Accident Events...")
    generate_traffic_data()