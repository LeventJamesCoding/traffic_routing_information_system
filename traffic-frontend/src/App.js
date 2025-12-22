import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css'; // Yeni CSS dosyanı çağırır

// Leaflet Marker Fix (Bunu silme, harita ikonları için gerekli)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// --- RENK BELİRLEME FONKSİYONU ---
const getRoadColor = (status) => {
  if (status === 'ACCIDENT') return '#ffffff'; // Kaza: Bembeyaz (CSS ile yanıp sönecek)
  if (status === 'LOCKED') return '#ff0055'; // Kırmızı (Kilit)
  if (status === 'HEAVY') return '#ffcc00';  // Sarı (Yoğun)
  return '#00ff88';                          // Yeşil (Normal)
};

// --- İSTANBUL KOORDİNATLARI ---
const roadCoordinates = {
  "E5-Bridge": [[41.045, 29.025], [41.042, 29.039], [41.030, 29.055]],
  "Tem-Kavacik": [[41.092, 29.055], [41.093, 29.062], [41.091, 29.085]],
  "Besiktas-Coast": [[41.036, 28.995], [41.042, 29.008], [41.048, 29.025]],
  "Kadikoy-Center": [[40.991, 29.021], [40.9905, 29.029], [40.994, 29.038]],
  "E5-Beylikduzu": [[41.002, 28.650], [40.998, 28.680], [40.995, 28.710]],
  "Tem-Seyrantepe": [[41.095, 28.980], [41.100, 28.990], [41.105, 29.000]],
  "Basin-Ekspres": [[41.020, 28.810], [41.040, 28.815], [41.060, 28.820]],
  "Sahil-Kennedy": [[40.995, 28.900], [41.000, 28.950], [41.010, 28.980]],
  "Bagdat-Caddesi": [[40.980, 29.050], [40.970, 29.060], [40.960, 29.070]],
  "Minibus-Yolu": [[40.985, 29.055], [40.975, 29.070], [40.965, 29.090]],
  "Levent-Buyukdere": [[41.070, 29.010], [41.080, 29.015], [41.090, 29.020]],
  "Haliç-Bridge": [[41.040, 28.940], [41.045, 28.945], [41.050, 28.950]]
};

function App() {
  const [trafficData, setTrafficData] = useState([]);
  
  // 1. Veri Çekme Motoru
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/traffic-data');
        setTrafficData(response.data);
      } catch (error) {
        console.error("Connection Error:", error);
      }
    };

    fetchData(); // İlk açılışta çek
    const interval = setInterval(fetchData, 2000); // Her 2 saniyede bir güncelle
    return () => clearInterval(interval);
  }, []);

  // Tahminleri çekip basit bir objeye çevirelim (Haritada göstermek için)
  const predictions = {};
  trafficData.forEach(item => {
    predictions[item.road_id] = item.predicted_speed;
  });

  return (
    <div className="dashboard-container">
      
      {/* --- 1. HEADER (ÜST KISIM) --- */}
      {/* --- 1. HEADER (DÜZELTİLDİ) --- */}
      <header className="header">
        <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
          <span style={{fontSize:'2rem'}}>🚦</span>
          <div>
            <h1 style={{margin:0}}>TRAFFIC CONTROL SYSTEM</h1> 
          </div>
        </div>
      </header>

      {/* --- 2. SOL PANEL (CANLI LOGLAR) --- */}
      <div className="panel">
        <div className="panel-title">📡 LIVE SENSOR STREAM</div>
        <div className="log-container">
          {/* Veriyi ters çevirip (en yeni en üstte) listeliyoruz */}
          {trafficData.slice().reverse().map((data, index) => (
            <div key={index} className={`log-item log-${data.congestion_status}`}>
              <div style={{display:'flex', justifyContent:'space-between', marginBottom:'5px'}}>
                <span style={{fontWeight:'bold', color:'#fff'}}>{data.road_id}</span>
                <span style={{fontSize:'0.8rem', opacity:0.7}}>
                  {new Date(data.timestamp * 1000).toLocaleTimeString()}
                </span>
              </div>
              <div style={{fontSize:'0.9rem', display:'flex', justifyContent:'space-between'}}>
                <span>SPD: {Math.floor(data.speed)} km/h</span>
                <span>AI PRED: {data.predicted_speed} km/h</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* --- 3. ORTA PANEL (HARİTA) --- */}
      <div className="map-container">
        <MapContainer center={[41.045, 29.030]} zoom={12} style={{ height: "100%", width: "100%", background: '#000' }}>
          {/* Karanlık Harita Katmanı */}
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          
          {/* Yolları Çiz */}
          {Object.entries(roadCoordinates).map(([roadName, coords]) => {
            // O yolun verisini bul
            const roadData = trafficData.find(d => d.road_id === roadName);
            // Veri varsa rengini al, yoksa gri yap
            const color = roadData ? getRoadColor(roadData.congestion_status) : '#333';
            // Kaza varsa çizgiyi kalınlaştır
            const weight = roadData && roadData.congestion_status === 'ACCIDENT' ? 8 : 5;

            return (
              <Polyline 
                key={roadName} 
                positions={coords} 
                color={color} 
                weight={weight}
                opacity={0.9} 
              >
                <Popup>
                  <div style={{color:'#000', textAlign:'center'}}>
                    <strong style={{fontSize:'1.1rem'}}>{roadName}</strong><hr/>
                    Current: <b>{roadData ? Math.floor(roadData.speed) : '?'} km/h</b><br/>
                    Status: <b>{roadData ? roadData.congestion_status : 'OFFLINE'}</b><br/>
                    <br/>
                    🤖 AI Prediction (15m):<br/>
                    <b style={{fontSize:'1.2rem', color:'#007bff'}}>
                      {roadData ? roadData.predicted_speed : '?'} km/h
                    </b>
                  </div>
                </Popup>
              </Polyline>
            );
          })}
        </MapContainer>
      </div>

      {/* --- 4. SAĞ PANEL (İSTATİSTİKLER) --- */}
      <div className="panel">
        <div className="panel-title">⚠️ NETWORK STATUS</div>
        
        {/* Ortalama Hız */}
        <div className="stat-card">
          <span className="stat-label">AVG NET SPEED</span>
          <span className="stat-value color-green">
            {trafficData.length > 0 
              ? Math.floor(trafficData.reduce((acc, curr) => acc + curr.speed, 0) / trafficData.length) 
              : 0}
            <span style={{fontSize:'1.5rem', marginLeft:'5px'}}>km/h</span>
          </span>
        </div>

        {/* Kritik Durum Göstergesi */}
        <div className="stat-card">
          <span className="stat-label">CONGESTION LEVEL</span>
          <span className={`stat-value ${
            trafficData.some(d => d.congestion_status === 'LOCKED' || d.congestion_status === 'ACCIDENT') 
            ? 'color-red' 
            : 'color-green'
          }`}>
            {trafficData.some(d => d.congestion_status === 'ACCIDENT') 
              ? 'ACCIDENT!' 
              : trafficData.some(d => d.congestion_status === 'LOCKED') 
                ? 'CRITICAL' 
                : 'STABLE'}
          </span>
        </div>

        {/* Aktif Sensör Sayısı */}
        <div className="stat-card">
          <span className="stat-label">ACTIVE SENSORS</span>
          <span className="stat-value" style={{color:'#fff'}}>
            {trafficData.length} / 12
          </span>
        </div>
      </div>

    </div>
  );
}

export default App;