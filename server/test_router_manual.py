import redis
from router import TrafficRouter
import time

# 1. Redis Bağlantısı
print("🔌 Redis'e Bağlanılıyor...")
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✅ Redis Bağlantısı Başarılı!")
except Exception as e:
    print(f"❌ Redis Hatası: {e}")
    exit()

# 2. Router Motorunu Başlat
print("🗺️ Şehir Haritası Yükleniyor...")
router = TrafficRouter(r)

# 3. Senaryo Testi: Beylikdüzü -> Kavacık
start = "Beylikduzu"
end = "Kavacik"

print(f"\n🧪 TEST: {start} -> {end} arası en hızlı rota hesaplanıyor...")
start_time = time.time()

route = router.calculate_fastest_route(start, end)
duration = time.time() - start_time

if route:
    print(f"\n🚀 SONUÇ BULUNDU ({duration:.4f} sn):")
    print(f"   ⏱️ Toplam Tahmini Süre: {route['total_time_min']} dakika")
    print("   📍 Rota Adımları:")
    for step in route['segments']:
        print(f"      - {step['from']} -> {step['to']} ({step['road_id']}) : {step['time_min']} dk")
else:
    print("❌ Rota Bulunamadı! Grafiği veya yol isimlerini kontrol et.")