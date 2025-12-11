from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI()

# 1. Enable CORS (React'in bağlanabilmesi için izin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Redis Bağlantısı
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/")
def read_root():
    return {"status": "UrbanPulse API is Running 🚀"}

@app.get("/traffic-data")
def get_traffic_data():
    """
    Redis'teki tüm yol verilerini çeker ve JSON listesi olarak döner.
    """
    try:
        keys = redis_client.keys("*") 
        traffic_list = []
        
        for key in keys:
            road_id = key.decode('utf-8')
            
            # Redis'ten veriyi çek
            raw_data = redis_client.hgetall(road_id)
            
            # Veriyi temizle ve formata sok
            clean_data = {
                "road_id": road_id,
                "speed": int(raw_data.get(b'speed', 0)),
                "congestion_status": raw_data.get(b'congestion_status', b'UNKNOWN').decode('utf-8'),
                "predicted_speed": float(raw_data.get(b'predicted_speed', 0)),
                # last_updated yoksa boş string ver
                "last_updated": raw_data.get(b'last_updated', b'').decode('utf-8')
            }
            traffic_list.append(clean_data)
            
        return traffic_list

    except Exception as e:
        print(f"Error: {e}")
        return []