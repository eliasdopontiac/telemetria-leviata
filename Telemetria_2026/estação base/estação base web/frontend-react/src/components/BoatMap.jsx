import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { NavigationArrow, Compass, MapPin } from '@phosphor-icons/react';

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
  html: `<div style="transform:rotate(${proa}deg);transition:transform 0.5s;width:32px;height:32px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 0 10px rgba(255,107,0,0.9))">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M12 2L19 21L12 17L5 21L12 2Z" fill="#ff6b00" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/></svg></div>`,
  iconSize: [32, 32], iconAnchor: [16, 16]
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
                    <NavigationArrow size={14} weight="duotone" color="#ff6b00" />
          <span className="card-title">Raia da Prova (GPS)</span>
        </div>
        <div style={{ display: 'flex', gap: 10, fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><Compass size={11} weight="duotone" color="#ffb703" /><strong style={{ color: 'var(--text-main)' }}>{proa}°</strong></span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}><MapPin size={11} weight="duotone" color="#00e676" /><strong style={{ color: 'var(--text-main)' }}>{sats} sats</strong></span>
        </div>
      </div>
      <div className="map-body">
        <MapContainer center={pos} zoom={16} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />
          <MapRecenter center={pos} />
          {track.length > 1 && <Polyline positions={track} pathOptions={{ color: '#ff6b00', weight: 3.5, opacity: 0.95 }} />}
          <Marker position={pos} icon={boatIcon(proa)}>
            <Popup><div style={{ fontSize: 11, fontFamily: 'Inter' }}><strong style={{ color: '#0e7490' }}>Barco Leviatã</strong><br />Vel: {vel.toFixed(1)} km/h | Proa: {proa.toFixed(1)}°</div></Popup>
          </Marker>
        </MapContainer>
      </div>
    </div>
  );
}
