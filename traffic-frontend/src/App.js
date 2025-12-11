import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Clock, Map as MapIcon } from 'lucide-react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Popup, Marker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // Harita stillerini yükle
import L from 'leaflet';
import './App.css';

// Marker ikonlarını düzeltmek için (Leaflet React bug'ı için fix)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function App() {
  const [trafficData, setTrafficData] = useState([]);
  const [logs, setLogs] = useState([]);
  const [systemStatus, setSystemStatus] = useState("OFFLINE");

  // 1. Veri Çekme Motoru
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/traffic-data');
        const data = response.data;
        setTrafficData(data);
        setSystemStatus("ONLINE");
        
        if (data.length > 0) {
          const latest = data[Math.floor(Math.random() * data.length)];
          addLog(`${latest.road_id}: ${latest.congestion_status} (${latest.speed} km/h)`);
        }
      } catch (error) {
        setSystemStatus("CONNECTION ERROR");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const addLog = (message) => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [`[${time}] ${message}`, ...prev.slice(0, 9)]);
  };

  const getRoadColor = (status) => {
    if (status === 'LOCKED') return '#ff0055'; // Kırmızı
    if (status === 'HEAVY') return '#ffcc00';  // Sarı
    return '#00ff88';                          // Yeşil
  };

  // GERÇEK İSTANBUL KOORDİNATLARI (Enlem, Boylam)
  const roadCoordinates = {
    "E5-Bridge": [
      [41.0665, 29.0140], // Zincirlikuyu Sapağı
      [41.0600, 29.0220], // Balmumcu
      [41.0490, 29.0300], // Ortaköy Viyadüğü
      [41.0450, 29.0340], // 15 Temmuz Köprüsü (Avrupa)
      [41.0420, 29.0390], // 15 Temmuz Köprüsü (Asya)
      [41.0380, 29.0450], // Beylerbeyi Çıkışı
      [41.0300, 29.0550]  // Altunizade
    ],
    "Tem-Kavacik": [
      [41.0900, 29.0400], // Baltalimanı
      [41.0920, 29.0550], // FSM Köprüsü Giriş
      [41.0930, 29.0620], // FSM Köprüsü Orta
      [41.0920, 29.0700], // FSM Çıkış
      [41.0910, 29.0850], // Kavacık Sapağı
      [41.0950, 29.1000]  // Beykoz Yolu
    ],
    "Besiktas-Coast": [
      [41.0360, 28.9950], // Dolmabahçe Sarayı
      [41.0400, 29.0020], // Beşiktaş İskelesi
      [41.0430, 29.0090], // Çırağan Sarayı
      [41.0460, 29.0160], // Yıldız Parkı Altı
      [41.0480, 29.0250]  // Ortaköy Meydan
    ],
    "Kadikoy-Center": [
      [40.9910, 29.0210], // Kadıköy Rıhtım
      [40.9900, 29.0250], // Çarşı İçi
      [40.9905, 29.0290], // Boğa Heykeli
      [40.9920, 29.0330], // Söğütlüçeşme Caddesi
      [40.9940, 29.0380]  // Metrobüs Durağı
    ]
  };

  // İstatistikler
  const avgSpeed = trafficData.length > 0 
    ? Math.floor(trafficData.reduce((acc, curr) => acc + curr.speed, 0) / trafficData.length) 
    : 0;
  const mainStatus = trafficData.some(d => d.congestion_status === 'LOCKED') ? 'CRITICAL' : 'NORMAL';

  return (  
    <div className="dashboard-container">
      {/* HEADER */}
      <header className="top-bar">
        <div className="logo-section">
          <Activity className="icon-pulse" color={systemStatus === 'ONLINE' ? "#00ff88" : "red"} />
          <h1>TRAFFIC CONTROL SYSTEM</h1>
        </div>
        <div style={{color: systemStatus === 'ONLINE' ? '#00ff88' : 'red', fontWeight: 'bold'}}>
          {systemStatus}
        </div>
      </header>

      {/* MAIN CONTENT */}
      <div className="main-content">
        
        {/* LEFT PANEL */}
        <div className="panel left-panel">
          <div className="panel-header"><Clock size={18} /> LIVE DATA STREAM</div>
          <div className="log-container">
            {logs.map((log, index) => (
              <p key={index} className="log-item" style={{color: log.includes('LOCKED') ? '#ff0055' : '#ccc'}}>
                {log}
              </p>
            ))}
          </div>
        </div>

        {/* MIDDLE PANEL: LIVE MAP */}
        <div className="panel map-panel">
          <MapContainer center={[41.045, 29.030]} zoom={12} style={{ height: "100%", width: "100%", background: '#0a0a12' }}>
            
            {/* Dark Mode Harita Katmanı (CartoDB Dark Matter) */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Yolları Çiz */}
            {trafficData.map((road) => (
              roadCoordinates[road.road_id] && (
                <Polyline 
                  key={road.road_id}
                  positions={roadCoordinates[road.road_id]}
                  pathOptions={{ 
                    color: getRoadColor(road.congestion_status), 
                    weight: 6, // Çizgi kalınlığı
                    opacity: 0.8 
                  }}
                >
                  <Popup>
                    <div style={{color: 'black'}}>
                      <strong>{road.road_id}</strong><br/>
                      Speed: {road.speed} km/h<br/>
                      Status: {road.congestion_status}<br/>
                      AI Prediction: {road.predicted_speed} km/h
                    </div>
                  </Popup>
                </Polyline>
              )
            ))}
          </MapContainer>
        </div>

        {/* RIGHT PANEL */}
        <div className="panel right-panel">
          <div className="panel-header"><AlertTriangle size={18} /> NETWORK STATUS</div>
          <div className="stat-card">
            <h4>AVG SPEED</h4>
            <div className="stat-value">{avgSpeed} <span className="unit">km/h</span></div>
          </div>
          <div className="stat-card">
            <h4>CONGESTION</h4>
            <div className={`stat-value ${mainStatus === 'CRITICAL' ? 'critical' : ''}`} style={{color: mainStatus==='CRITICAL' ? '#ff0055' : '#00ff88'}}>
              {mainStatus}
            </div>
          </div>
          <div className="stat-card">
            <h4>ACTIVE SENSORS</h4>
            <div className="stat-value">{trafficData.length}</div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;