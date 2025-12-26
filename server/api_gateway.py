from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
from router import TrafficRouter  
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

router_engine = TrafficRouter(redis_client)

class RouteRequest(BaseModel):
    start: str
    end: str

@app.get("/")
def home():
    return {"message": "UrbanPulse API is Running"}

@app.get("/traffic-data")
def get_traffic_data():
    keys = redis_client.keys("*")
    traffic_data = []
    
    for key in keys:
        key_str = key.decode('utf-8')
        if redis_client.hexists(key, "congestion_status"):
            data = redis_client.hgetall(key)
            decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
            decoded_data['road_id'] = key_str
            
            if 'speed' in decoded_data: decoded_data['speed'] = float(decoded_data['speed'])
            if 'timestamp' in decoded_data: decoded_data['timestamp'] = float(decoded_data['timestamp'])
            
            traffic_data.append(decoded_data)
            
    return traffic_data

@app.post("/calculate-route")
def get_route(request: RouteRequest):
    route = router_engine.calculate_fastest_route(request.start, request.end)
    if not route:
        return {"error": "Rota bulunamadı"}
    return route