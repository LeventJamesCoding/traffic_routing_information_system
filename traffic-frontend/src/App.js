// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import { MapContainer, TileLayer, Polyline, Popup } from 'react-leaflet';
// import 'leaflet/dist/leaflet.css';
// import L from 'leaflet';
// import './App.css';

// // Fix Leaflet Marker Icons
// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
//   iconUrl: require('leaflet/dist/images/marker-icon.png'),
//   shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
// });

// // --- CONSTANTS ---

// // All 12 Road Segments with Coordinates
// // --- UPDATED CONSTANTS (REALISTIC COORDINATES) ---

// const ROAD_COORDINATES = {
//   "E5-Bridge": [
//     [41.048, 29.025], [41.047, 29.028], [41.046, 29.032], [41.045, 29.036], 
//     [41.042, 29.039], [41.038, 29.045], [41.034, 29.050], [41.030, 29.055]
//   ],
//   "Tem-Kavacik": [
//     [41.092, 29.055], [41.093, 29.060], [41.094, 29.065], [41.094, 29.070], 
//     [41.093, 29.075], [41.092, 29.080], [41.091, 29.085]
//   ],
//   "Besiktas-Coast": [
//     [41.040, 29.000], [41.042, 29.005], [41.044, 29.010], [41.046, 29.015], 
//     [41.047, 29.020], [41.048, 29.025]
//   ],
//   "Kadikoy-Center": [
//     [40.991, 29.021], [40.992, 29.025], [40.993, 29.030], [40.994, 29.035], 
//     [40.994, 29.038]
//   ],
//   "E5-Beylikduzu": [
//     [41.002, 28.650], [41.001, 28.660], [41.000, 28.670], [40.999, 28.680], 
//     [40.998, 28.690], [40.996, 28.700], [40.995, 28.710]
//   ],
//   "Tem-Seyrantepe": [
//     [41.095, 28.980], [41.097, 28.985], [41.099, 28.990], [41.101, 28.995], 
//     [41.103, 28.998], [41.105, 29.000]
//   ],
//   "Basin-Ekspres": [
//     [41.020, 28.810], [41.025, 28.812], [41.030, 28.813], [41.035, 28.814], 
//     [41.040, 28.815], [41.045, 28.816], [41.050, 28.818], [41.060, 28.820]
//   ],
//   "Sahil-Kennedy": [
//     [40.995, 28.900], [40.996, 28.910], [40.997, 28.920], [40.998, 28.930], 
//     [40.999, 28.940], [41.000, 28.950], [41.005, 28.965], [41.010, 28.980]
//   ],
//   "Bagdat-Caddesi": [
//     [40.980, 29.050], [40.978, 29.053], [40.975, 29.056], [40.972, 29.059], 
//     [40.970, 29.060], [40.965, 29.065], [40.960, 29.070]
//   ],
//   "Minibus-Yolu": [
//     [40.985, 29.055], [40.982, 29.060], [40.980, 29.065], [40.975, 29.070], 
//     [40.970, 29.080], [40.965, 29.090]
//   ],
//   "Levent-Buyukdere": [
//     [41.070, 29.010], [41.073, 29.012], [41.076, 29.013], [41.080, 29.015], 
//     [41.085, 29.018], [41.090, 29.020]
//   ],
//   "Haliç-Bridge": [
//     [41.040, 28.940], [41.042, 28.942], [41.044, 28.944], [41.045, 28.945], 
//     [41.047, 28.947], [41.050, 28.950]
//   ]
// };

// const LOCATION_LIST = Object.keys(ROAD_COORDINATES);

// // Helper: Determine Color based on Congestion Status
// const getRoadColor = (status) => {
//   switch (status) {
//     case 'ACCIDENT': return '#ff0000'; // Bright Red for visibility on light map
//     case 'LOCKED': return '#d90429';   // Dark Red
//     case 'HEAVY': return '#ff8c00';    // Dark Orange
//     default: return '#2dcc70';         // Green (Normal)
//   }
// };

// function App() {
//   // --- STATE ---
//   const [trafficData, setTrafficData] = useState([]);
//   const [searchTerm, setSearchTerm] = useState('');
  
//   // Route Planner State
//   const [startPoint, setStartPoint] = useState('Beylikduzu');
//   const [endPoint, setEndPoint] = useState('Kavacik');
//   const [calculatedRoute, setCalculatedRoute] = useState(null);
//   const [routeError, setRouteError] = useState(null);

//   // --- DATA FETCHING ---
//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const response = await axios.get('http://127.0.0.1:8000/traffic-data');
//         setTrafficData(response.data);
//       } catch (error) {
//         console.error("API Connection Error:", error);
//       }
//     };
    
//     fetchData(); 
//     const interval = setInterval(fetchData, 2000); 
//     return () => clearInterval(interval);
//   }, []);

//   // --- HANDLERS ---
//   const handleCalculateRoute = async () => {
//     setRouteError(null);
//     setCalculatedRoute(null);
    
//     try {
//       const response = await axios.post('http://127.0.0.1:8000/calculate-route', {
//         start: startPoint,
//         end: endPoint
//       });
      
//       if (response.data.error) {
//         setRouteError("No suitable route found.");
//       } else {
//         setCalculatedRoute(response.data);
//       }
//     } catch (error) {
//       console.error("Routing Error:", error);
//       setRouteError("Connection failed.");
//     }
//   };

//   // Filter Road List based on Search
//   const displayRoads = LOCATION_LIST.filter(road => 
//     road.toLowerCase().includes(searchTerm.toLowerCase())
//   );

//   return (
//     <div className="dashboard-container">
      
//       {/* HEADER */}
//       <header className="header">
//         <div className="brand-wrapper">
//           <span className="brand-icon">🚦</span>
//           <div className="brand-text">
//             <h1>TRAFFIC CONTROL SYSTEM</h1> 
//             <span className="subtitle">AI POWERED ANALYTICS</span>
//           </div>
//         </div>
//       </header>

//       {/* --- LEFT PANEL: ROUTE PLANNER --- */}
//       <div className="panel left-panel">
//         <div className="panel-header">
//           <span className="panel-icon">🗺️</span>
//           <h2>ROUTE PLANNER</h2>
//         </div>
        
//         <div className="route-form">
//           <label className="input-label">FROM</label>
//           <select 
//             className="route-select" 
//             value={startPoint} 
//             onChange={e => setStartPoint(e.target.value)}
//           >
//             {LOCATION_LIST.map(loc => <option key={loc} value={loc.split('-')[0]}>{loc}</option>)}
//           </select>
          
//           <div className="route-arrow">⬇️</div>
          
//           <label className="input-label">TO</label>
//           <select 
//             className="route-select" 
//             value={endPoint} 
//             onChange={e => setEndPoint(e.target.value)}
//           >
//             {LOCATION_LIST.map(loc => <option key={loc} value={loc.split('-')[0]}>{loc}</option>)}
//           </select>

//           <button className="primary-btn" onClick={handleCalculateRoute}>
//             FIND ROUTE 🚀
//           </button>

//           {/* Result Area */}
//           {calculatedRoute && (
//             <div className="route-result-card success">
//               <div className="result-header">
//                 <span className="result-label">TOTAL TIME</span>
//                 <span className="result-value">{calculatedRoute.total_time_min} min</span>
//               </div>
//               <div className="result-path">
//                 <ul>
//                   {calculatedRoute.segments.map((s, i) => (
//                     <li key={i}>{s.from} ➝ {s.to}</li>
//                   ))}
//                 </ul>
//               </div>
//             </div>
//           )}
//           {routeError && <div className="route-result-card error">⚠️ {routeError}</div>}
//         </div>
//       </div>

//       {/* --- MIDDLE: MAP (LIGHT THEME) --- */}
//       <div className="map-wrapper">
//         <MapContainer center={[41.045, 29.030]} zoom={11} style={{ height: "100%", width: "100%" }}>
//           {/* LIGHT THEME TILE LAYER */}
//           <TileLayer
//             url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
//             attribution='&copy; <a href="https://carto.com/">CARTO</a>'
//           />
          
//           {Object.entries(ROAD_COORDINATES).map(([roadName, coords]) => {
//             const roadData = trafficData.find(d => d.road_id === roadName);
//             const isPartOfRoute = calculatedRoute?.segments.some(s => s.road_id === roadName);
            
//             // Logic: If data exists, use status color. If no data, gray.
//             let color = roadData ? getRoadColor(roadData.congestion_status) : '#999';
//             if (isPartOfRoute) color = '#2980b9'; // Blue for Route

//             let weight = isPartOfRoute ? 8 : 6;
//             let opacity = isPartOfRoute ? 1 : 0.8;

//             // ... (önceki kodlar aynı)

//             // --- DEĞİŞİKLİK BURADA: pathOptions KULLANILIYOR ---
//             return (
//               <Polyline 
//                 key={roadName} 
//                 positions={coords} 
//                 pathOptions={{ 
//                   color: color, 
//                   weight: weight, 
//                   opacity: opacity,
//                   lineCap: 'round', // Çizgi uçlarını yuvarlatır (Daha estetik)
//                   lineJoin: 'round' // Köşeleri yuvarlatır
//                 }}
//               >
//                 <Popup>
//                   <div className="popup-content">
//                     <strong>{roadName}</strong>
//                     <hr/>
//                     <div>Speed: {roadData ? Math.floor(roadData.speed) : 'N/A'} km/h</div>
//                     <div>Status: {roadData ? roadData.congestion_status : 'Offline'}</div>
//                   </div>
//                 </Popup>
//               </Polyline>
//             );
//           })}
//         </MapContainer>
//       </div>

//       {/* --- RIGHT PANEL: LIVE STATUS (FIXED LIST) --- */}
//       <div className="panel right-panel">
//         <div className="panel-header">
//           <span className="panel-icon">📡</span>
//           <h2>LIVE STATUS MONITOR</h2>
//         </div>

//         <div className="search-box">
//           <input 
//             type="text" 
//             placeholder="Filter Roads..." 
//             value={searchTerm}
//             onChange={(e) => setSearchTerm(e.target.value)}
//           />
//         </div>

//         <div className="log-container">
//           {displayRoads.map((roadName) => {
//             // Find live data for this specific road
//             const data = trafficData.find(d => d.road_id === roadName);
//             const status = data ? data.congestion_status : 'OFFLINE';

//             return (
//               <div key={roadName} className={`log-item status-${status}`}>
//                 <div className="log-header">
//                   <span className="log-id">{roadName}</span>
//                   <span className="log-status">{status}</span>
//                 </div>
//                 <div className="log-details">
//                   <div className="detail-box">
//                     <span className="label">SPEED</span>
//                     <span className="value">{data ? Math.floor(data.speed) : '-'} <small>km/h</small></span>
//                   </div>
//                   <div className="detail-box">
//                     <span className="label">AI PRED</span>
//                     <span className="value">{data ? data.predicted_speed : '-'}</span>
//                   </div>
//                 </div>
//               </div>
//             );
//           })}
//         </div>
//       </div>

//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css';

// Fix Leaflet Marker Icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// --- HD REALISTIC ISTANBUL ROAD NETWORK ---
const ROAD_COORDINATES = {
  // --- EUROPEAN SIDE (AVRUPA YAKASI) ---
  
  // E5 LINE (WEST TO EAST)
  "E5-Beylikduzu-Avcilar": [
    [41.002, 28.650], [41.001, 28.660], [41.000, 28.670], [40.998, 28.680], 
    [40.995, 28.700], [40.990, 28.715], [40.985, 28.725]
  ],
  "E5-Avcilar-Kucukcekmece": [
    [40.985, 28.725], [40.982, 28.735], [40.980, 28.750], [40.985, 28.765], 
    [40.990, 28.775], [40.995, 28.785]
  ],
  "E5-Kucukcekmece-Bakirkoy": [
    [40.995, 28.785], [40.998, 28.800], [41.000, 28.820], [40.998, 28.840], 
    [40.995, 28.860], [40.992, 28.880] // Merter Girişi
  ],
  "E5-Bakirkoy-Merter": [
    [40.992, 28.880], [41.000, 28.890], [41.010, 28.895], [41.015, 28.900]
  ],
  "E5-Merter-Topkapi": [
    [41.015, 28.900], [41.020, 28.910], [41.025, 28.920], [41.028, 28.930]
  ],
  "E5-Topkapi-Halic": [
    [41.028, 28.930], [41.035, 28.935], [41.040, 28.940], [41.044, 28.945] // Haliç Köprüsü Ortası
  ],
  "E5-Halic-Mecidiyekoy": [
    [41.044, 28.945], [41.050, 28.955], [41.055, 28.965], [41.060, 28.975], 
    [41.065, 28.985], [41.068, 28.995]
  ],
  "E5-Mecidiyekoy-Zincirlikuyu": [
    [41.068, 28.995], [41.065, 29.005], [41.062, 29.015]
  ],

  // TEM (O-2) LINE
  "Tem-Mahmutbey-Seyrantepe": [
    [41.055, 28.800], [41.060, 28.820], [41.065, 28.850], [41.070, 28.880], 
    [41.080, 28.920], [41.090, 28.950], [41.095, 28.980]
  ],
  "Tem-Seyrantepe-FSM": [
    [41.095, 28.980], [41.092, 29.000], [41.090, 29.020], [41.092, 29.040], 
    [41.091, 29.055] // FSM Giriş
  ],

  // COASTAL ROAD (KENNEDY CAD.)
  "Coast-Zeytinburnu-Eminonu": [
    [40.985, 28.900], [40.990, 28.920], [40.995, 28.940], [41.000, 28.960], 
    [41.005, 28.975], [41.015, 28.980]
  ],
  "Coast-Besiktas-Sariyer": [
    [41.040, 29.000], [41.045, 29.015], [41.050, 29.030], [41.060, 29.040], // Ortaköy
    [41.075, 29.045], [41.090, 29.050], [41.110, 29.055] // Sarıyer Yönü
  ],

  // --- BRIDGES (KÖPRÜLER) ---
  
  "Bridge-15-July": [
    [41.045, 29.025], [41.046, 29.032], [41.047, 29.038], [41.045, 29.042]
  ],
  "Bridge-FSM": [
    [41.091, 29.055], [41.092, 29.065], [41.091, 29.075], [41.090, 29.085]
  ],

  // --- ASIAN SIDE (ANADOLU YAKASI) ---

  // E5 CONNECTIONS
  "E5-Altunizade-Uzuncayir": [
    [41.045, 29.042], [41.035, 29.045], [41.020, 29.050], [41.010, 29.052], 
    [41.000, 29.055] // Uzunçayır
  ],
  "E5-Uzuncayir-Bostanci": [
    [41.000, 29.055], [40.990, 29.065], [40.980, 29.080], [40.970, 29.095], 
    [40.960, 29.110]
  ],
  "E5-Bostanci-Pendik": [
    [40.960, 29.110], [40.950, 29.130], [40.930, 29.160], [40.910, 29.200], 
    [40.880, 29.230]
  ],

  // TEM CONNECTIONS
  "Tem-Kavacik-Umraniye": [
    [41.090, 29.085], [41.085, 29.095], [41.070, 29.110], [41.050, 29.120], 
    [41.020, 29.130]
  ],
  "Tem-Umraniye-Atasehir": [
    [41.020, 29.130], [41.000, 29.125], [40.990, 29.120]
  ],

  // ASIAN COAST
  "Coast-Uskudar-Harem": [
    [41.025, 29.015], [41.020, 29.010], [41.010, 29.008], [41.000, 29.012]
  ],
  "Coast-Kadikoy-Bostanci": [
    [40.990, 29.025], [40.980, 29.030], [40.970, 29.040], [40.960, 29.060], 
    [40.955, 29.080]
  ]
};

const LOCATION_LIST = Object.keys(ROAD_COORDINATES);

// Helper: Determine Color based on Congestion Status
const getRoadColor = (status) => {
  switch (status) {
    case 'ACCIDENT': return '#ff0000'; // Bright Red
    case 'LOCKED': return '#d90429';   // Deep Red
    case 'HEAVY': return '#ff8c00';    // Orange
    default: return '#2dcc70';         // Green
  }
};

function App() {
  // --- STATE ---
  const [trafficData, setTrafficData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Route Planner State
  const [startPoint, setStartPoint] = useState('E5-Beylikduzu-Avcilar');
  const [endPoint, setEndPoint] = useState('E5-Bostanci-Pendik');
  const [calculatedRoute, setCalculatedRoute] = useState(null);
  const [routeError, setRouteError] = useState(null);

  // --- DATA FETCHING ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/traffic-data');
        setTrafficData(response.data);
      } catch (error) {
        console.error("API Connection Error:", error);
      }
    };
    
    fetchData(); 
    const interval = setInterval(fetchData, 2000); 
    return () => clearInterval(interval);
  }, []);

  // --- HANDLERS ---
  const handleCalculateRoute = async () => {
    setRouteError(null);
    setCalculatedRoute(null);
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/calculate-route', {
        start: startPoint,
        end: endPoint
      });
      
      if (response.data.error) {
        setRouteError("No suitable route found.");
      } else {
        setCalculatedRoute(response.data);
      }
    } catch (error) {
      console.error("Routing Error:", error);
      setRouteError("Connection failed.");
    }
  };

  // Filter Road List based on Search
  const displayRoads = LOCATION_LIST.filter(road => 
    road.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="dashboard-container">
      
      {/* HEADER */}
      <header className="header">
        <div style={{display:'flex', alignItems:'center', gap:'15px'}}>
          <span style={{fontSize:'2rem'}}>🚦</span>
          <div>
            <h1 style={{margin:0}}>TRAFFIC CONTROL SYSTEM</h1> 
            <span style={{fontSize:'0.8rem', color:'#aaa', letterSpacing:'3px'}}>ISTANBUL LIVE MONITOR</span>
          </div>
        </div>
        <div className="status-badge">
          SYSTEM ONLINE
        </div>
      </header>

      {/* --- LEFT PANEL: ROUTE PLANNER --- */}
      <div className="panel">
        <div className="panel-title">🗺️ ROUTE PLANNER</div>
        
        <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
          <div>
            <label style={{fontSize:'0.7rem', color:'#888'}}>START POINT</label>
            <select 
              className="route-select" 
              style={{width:'100%', padding:'10px', background:'#151525', color:'white', border:'1px solid #444', borderRadius:'8px'}}
              value={startPoint} 
              onChange={e => setStartPoint(e.target.value)}
            >
              {LOCATION_LIST.map(loc => <option key={loc} value={loc}>{loc}</option>)}
            </select>
          </div>
          
          <div style={{textAlign:'center', color:'#555'}}>⬇️</div>
          
          <div>
            <label style={{fontSize:'0.7rem', color:'#888'}}>DESTINATION</label>
            <select 
              className="route-select" 
              style={{width:'100%', padding:'10px', background:'#151525', color:'white', border:'1px solid #444', borderRadius:'8px'}}
              value={endPoint} 
              onChange={e => setEndPoint(e.target.value)}
            >
              {LOCATION_LIST.map(loc => <option key={loc} value={loc}>{loc}</option>)}
            </select>
          </div>

          <button 
            style={{
              background: 'linear-gradient(90deg, #00f260, #0575e6)',
              border: 'none', padding: '15px', color: 'white', fontWeight: 'bold',
              borderRadius: '8px', cursor: 'pointer', marginTop: '10px'
            }}
            onClick={handleCalculateRoute}
          >
            CALCULATE ROUTE 🚀
          </button>

          {/* Result Area */}
          {calculatedRoute && (
            <div style={{marginTop:'20px', padding:'15px', background:'rgba(0,255,136,0.1)', borderLeft:'4px solid #00ff88', borderRadius:'8px'}}>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                <span style={{fontSize:'0.9rem', color:'#aaa'}}>EST. TIME</span>
                <span style={{fontSize:'1.5rem', fontWeight:'bold', color:'#fff'}}>{calculatedRoute.total_time_min} min</span>
              </div>
              <div style={{marginTop:'10px', fontSize:'0.8rem', color:'#ddd', maxHeight:'100px', overflowY:'auto'}}>
                <strong>Path:</strong>
                <ul style={{paddingLeft:'20px', margin:'5px 0'}}>
                  {calculatedRoute.segments.map((s, i) => (
                    <li key={i}>{s.road_id}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          {routeError && <div style={{marginTop:'20px', padding:'15px', background:'rgba(255,0,0,0.1)', borderLeft:'4px solid red', color:'#ffcccc'}}>{routeError}</div>}
        </div>
      </div>

      {/* --- MIDDLE: MAP --- */}
      <div className="map-container">
        <MapContainer center={[41.025, 28.970]} zoom={11} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            attribution='&copy; CARTO'
          />
          
          {Object.entries(ROAD_COORDINATES).map(([roadName, coords]) => {
            const roadData = trafficData.find(d => d.road_id === roadName);
            const isPartOfRoute = calculatedRoute?.segments.some(s => s.road_id === roadName);
            
            // Logic: Data varsa renk ver, yoksa gri. Route ise mavi.
            let color = roadData ? getRoadColor(roadData.congestion_status) : '#999';
            if (isPartOfRoute) color = '#2980b9'; 

            let weight = isPartOfRoute ? 8 : 6;
            let opacity = isPartOfRoute ? 1 : 0.8;

            return (
              <Polyline 
                key={roadName} 
                positions={coords} 
                pathOptions={{ 
                  color: color, 
                  weight: weight, 
                  opacity: opacity,
                  lineCap: 'round',
                  lineJoin: 'round'
                }}
              >
                <Popup>
                  <div style={{textAlign:'center', color:'black'}}>
                    <strong>{roadName}</strong>
                    <hr/>
                    <div>Speed: {roadData ? Math.floor(roadData.speed) : 'N/A'} km/h</div>
                    <div>Status: {roadData ? roadData.congestion_status : 'Offline'}</div>
                  </div>
                </Popup>
                <Tooltip sticky>{roadName}</Tooltip>
              </Polyline>
            );
          })}
        </MapContainer>
      </div>

      {/* --- RIGHT PANEL: LIVE STATUS --- */}
      <div className="panel">
        <div className="panel-title">📡 LIVE NETWORK STATUS</div>

        <input 
          type="text" 
          placeholder="Search Road Segment..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width:'100%', padding:'12px', background:'#111', border:'1px solid #333',
            color:'white', borderRadius:'8px', marginBottom:'15px', boxSizing: 'border-box'
          }}
        />

        <div className="log-container">
          {displayRoads.map((roadName) => {
            const data = trafficData.find(d => d.road_id === roadName);
            const status = data ? data.congestion_status : 'OFFLINE';

            return (
              <div key={roadName} className={`log-item log-${status}`}>
                <div style={{display:'flex', justifyContent:'space-between', marginBottom:'5px'}}>
                  <span style={{fontWeight:'bold', fontSize:'0.85rem'}}>{roadName}</span>
                  <span className="log-status" style={{background:'#000', padding:'2px 6px', borderRadius:'4px', fontSize:'0.7rem'}}>{status}</span>
                </div>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                   <div style={{display:'flex', flexDirection:'column'}}>
                      <span style={{fontSize:'0.65rem', color:'#aaa'}}>SPEED</span>
                      <span style={{fontSize:'1.1rem', fontWeight:'bold'}}>{data ? Math.floor(data.speed) : '-'} <small>km/h</small></span>
                   </div>
                   <div style={{display:'flex', flexDirection:'column', textAlign:'right'}}>
                      <span style={{fontSize:'0.65rem', color:'#aaa'}}>AI PRED</span>
                      <span style={{fontSize:'1.1rem', fontWeight:'bold'}}>{data ? data.predicted_speed : '-'}</span>
                   </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}

export default App;