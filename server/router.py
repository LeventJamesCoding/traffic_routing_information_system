import networkx as nx
import redis

# Şehir Grafiği: Hangi Nokta (Node) Hangi Yolla (Edge) Bağlı?
CITY_GRAPH = {
    # [Başlangıç, Bitiş, Yol_ID, Mesafe_KM]
    "EDGES": [
        ("Beylikduzu", "Merter", "E5-Beylikduzu", 15),
        ("Merter", "Mecidiyekoy", "Haliç-Bridge", 10),
        ("Merter", "Sahil", "Sahil-Kennedy", 12),
        ("Sahil", "Besiktas", "Besiktas-Coast", 8),
        ("Besiktas", "Levent", "Levent-Buyukdere", 5),
        ("Mecidiyekoy", "Levent", "Levent-Buyukdere", 5),
        ("Mecidiyekoy", "Kadikoy", "E5-Bridge", 7),  # 15 Temmuz Köprüsü
        ("Levent", "Seyrantepe", "Tem-Seyrantepe", 6),
        ("Seyrantepe", "Kavacik", "Tem-Kavacik", 8),   # FSM Köprüsü
        ("Kadikoy", "Bostanci", "Bagdat-Caddesi", 10),
        ("Kadikoy", "Bostanci", "Minibus-Yolu", 10),   # Alternatif yol
        ("Kadikoy", "Kadikoy-Merkez", "Kadikoy-Center", 2),
        ("Merter", "BasinEkspres", "Basin-Ekspres", 12)
    ]
}

class TrafficRouter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.graph = nx.DiGraph()
        # Grafiği başlangıçta oluştur
        for u, v, road_id, dist in CITY_GRAPH["EDGES"]:
            # Çift yönlü ekliyoruz (Gidiş-Dönüş)
            self.graph.add_edge(u, v, road_id=road_id, distance=dist)
            self.graph.add_edge(v, u, road_id=road_id, distance=dist)

    def calculate_fastest_route(self, start_node, end_node):
        # 1. Her yolun güncel ağırlığını (Süre = Yol / Hız) hesapla
        for u, v, data in self.graph.edges(data=True):
            road_id = data['road_id']
            distance = data['distance']
            
            # Redis'ten AI Tahminini Çek
            try:
                predicted_speed_str = self.redis.hget(road_id, "predicted_speed")
                speed = float(predicted_speed_str) if predicted_speed_str else 50.0
            except:
                speed = 50.0 # Varsayılan hız

            # Hız 0 olmasın (Bölen hatası önlemi)
            speed = max(speed, 5.0) 
            
            # Ağırlık = Süre (Dakika cinsinden)
            # Süre = (Mesafe / Hız) * 60
            travel_time = (distance / speed) * 60
            
            # Grafiği güncelle
            self.graph[u][v]['weight'] = travel_time
        
        # 2. Dijkstra ile en hızlı rotayı bul
        try:
            path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight='weight')
            
            # Rota detaylarını topla
            route_details = []
            total_time = 0
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = self.graph[u][v]
                time = edge_data['weight']
                total_time += time
                
                route_details.append({
                    "road_id": edge_data['road_id'],
                    "from": u,
                    "to": v,
                    "time_min": round(time, 1)
                })
                
            return {
                "path": path,
                "segments": route_details,
                "total_time_min": round(total_time, 1)
            }
            
        except nx.NetworkXNoPath:
            return None

if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)
    router = TrafficRouter(r)
    print("Router Modülü Test Modunda Çalıştı.")