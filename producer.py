import time
import json
import random
from kafka import KafkaProducer

# 1. Kafka Producer Ayarları
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 2. Genişletilmiş İstanbul Yol Ağı
ROADS = [
    "E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center",
    "E5-Beylikduzu", "Tem-Seyrantepe", "Basin-Ekspres", "Sahil-Kennedy",
    "Bagdat-Caddesi", "Minibus-Yolu", "Levent-Buyukdere", "Haliç-Bridge"
]

# Her yolun o anki hızını hafızada tutuyoruz (Gerçekçi geçişler için)
current_speeds = {road: random.randint(40, 90) for road in ROADS}
# Kaza durumlarını tutuyoruz
accident_status = {road: False for road in ROADS}

def generate_traffic_data():
    while True:
        for road_id in ROADS:
            
            # --- ÖZELLİK 1: KAZA SENARYOSU (ACCIDENT EVENT) ---
            # %1 ihtimalle kaza olur, %5 ihtimalle kaza çözülür
            if not accident_status[road_id] and random.random() < 0.01:
                accident_status[road_id] = True
                print(f"💥 KAZA OLDU! -> {road_id}")
            elif accident_status[road_id] and random.random() < 0.05:
                accident_status[road_id] = False
                print(f"✅ KAZA KALDIRILDI -> {road_id}")

            # --- ÖZELLİK 2: GERÇEKÇİ VERİ GEÇİŞİ (SMOOTH TRANSITION) ---
            if accident_status[road_id]:
                # Kaza varsa hız 0-15 km/s arasında sürünür
                current_speeds[road_id] = max(0, min(15, current_speeds[road_id] + random.randint(-2, 2)))
            else:
                # Kaza yoksa hız, önceki hızına göre azıcık değişir (+-5 değişim)
                change = random.randint(-5, 5)
                # Trafik yoğunluğu simülasyonu (Akşam saati gibi davran)
                current_speeds[road_id] = max(5, min(110, current_speeds[road_id] + change))

            speed = current_speeds[road_id]
            
            # Durum Belirleme
            if accident_status[road_id]:
                status = "ACCIDENT" # Yeni Durum!
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
        
        time.sleep(1) # Her saniye tüm yollar için veri bas

if __name__ == "__main__":
    print("🚦 Smart Traffic Simulator Started with Accident Events...")
    generate_traffic_data()