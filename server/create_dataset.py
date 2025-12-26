import pandas as pd
import random
import joblib
from sklearn.preprocessing import LabelEncoder

# 1. Genişletilmiş Yol Listesi (12 Yol)
ROADS = [
    "E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center",
    "E5-Beylikduzu", "Tem-Seyrantepe", "Basin-Ekspres", "Sahil-Kennedy",
    "Bagdat-Caddesi", "Minibus-Yolu", "Levent-Buyukdere", "Haliç-Bridge"
]

data = []

print("Generating Synthetic Traffic Data with Correct Columns...")

# 2. 10.000 Satırlık Veri Üret
for _ in range(10000):
    road = random.choice(ROADS)
    hour = random.randint(0, 23)
    
    # Mantıklı Trafik Kuralları (Sabah/Akşam yoğunluğu)
    if (7 <= hour <= 10) or (17 <= hour <= 20):
        # %70 ihtimalle yoğun
        if random.random() < 0.7:
            speed = random.randint(5, 30)
            status = random.choice(['LOCKED', 'HEAVY'])
        else:
            speed = random.randint(30, 60)
            status = 'NORMAL'
    else:
        # Gece/Öğlen genelde açık
        if random.random() < 0.1: # Arada kaza vs. olsun
            speed = random.randint(10, 40)
            status = 'HEAVY'
        else:
            speed = random.randint(70, 120)
            status = 'NORMAL'
            
    # train_model.py'nin beklediği SÜTUN İSİMLERİ BURADA:
    data.append({
        "road_id": road,
        "hour": hour,
        "speed": speed,
        "congestion_status": status  # <-- İşte aranan sütun bu!
    })

# 3. DataFrame Oluştur ve Kaydet
df = pd.DataFrame(data)
df.to_csv('traffic_dataset.csv', index=False)
print("✅ traffic_dataset.csv created successfully!")

# 4. Encoder'ı da burada oluşturup kaydedelim (Garanti olsun)
encoder = LabelEncoder()
df['road_encoded'] = encoder.fit_transform(df['road_id'])
joblib.dump(encoder, 'road_encoder.pkl')
print("✅ road_encoder.pkl updated!")