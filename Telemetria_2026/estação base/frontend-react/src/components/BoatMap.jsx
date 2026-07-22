import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Navigation, Compass, MapPin } from 'lucide-react';

function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    map.invalidateSize();
    if (center && center[0] !== 0 && center[1] !== 0) map.setView(center, map.getZoom(), { animate: true });
  }, [center, map]);
  return null;
}

const boatIcon = (proa) => L.divIcon({
  className: '',
  html: `<div style="transform:rotate(${proa}deg);transition:transform 0.5s;width:30px;height:30px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 0 8px rgba(0,242,254,0.8))">
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M12 2L19 21L12 17L5 21L12 2Z" fill="#00f2fe" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/></svg></div>`,
  iconSize: [30, 30], iconAnchor: [15, 15]
});

export default function BoatMap({ telemetryData, history = [] }) {
  const nav = telemetryData?.nav || {};
  const lat = parseFloat(nav.lat) || 0, lon = parseFloat(nav.lon) || 0;
  const proa = parseFloat(nav.proa) || 0, vel = nav.vel || 0, sats = nav.gps_satelites || 0;
  const defaultPos = [-3.119, -60.021];
  const pos = (lat !== 0 && lon !== 0) ? [lat, lon] : defaultPos;
  const track = history.map(i => { const la = parseFloat(i.nav?.lat ?? i.lat), lo = parseFloat(i.nav?.lon ?? i.lon); return la && lo && la !== 0 ? [la, lo] : null; }).filter(Boolean);

  return (
    <div className="card map-card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Navigation style={{ width: 14, height: 14, color: '#00f2fe' }} />
          <span className="card-title">Raia da Prova (GPS)</span>
        </div>
        <div style={{ display: 'flex', gap: 10, fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><Compass style={{ width: 11, height: 11, color: '#ffb703' }} /><strong style={{ color: 'var(--text-main)' }}>{proa}°</strong></span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><MapPin style={{ width: 11, height: 11, color: '#00e676' }} /><strong style={{ color: 'var(--text-main)' }}>{sats} sats</strong></span>
        </div>
      </div>
      <div className="map-body">
        <MapContainer center={pos} zoom={16} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            maxZoom={19}
          />
          <MapRecenter center={pos} />
          {track.length > 1 && <Polyline positions={track} pathOptions={{ color: '#00f2fe', weight: 3, opacity: 0.9 }} />}
          <Marker position={pos} icon={boatIcon(proa)}>
            <Popup><div style={{ fontSize: 11, fontFamily: 'Inter' }}><strong style={{ color: '#0e7490' }}>Barco Leviatã</strong><br />Vel: {vel.toFixed(1)} km/h | Proa: {proa.toFixed(1)}°</div></Popup>
          </Marker>
        </MapContainer>
      </div>
    </div>
  );
}
