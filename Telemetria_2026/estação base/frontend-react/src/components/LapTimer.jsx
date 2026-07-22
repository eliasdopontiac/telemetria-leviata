import React, { useState, useEffect } from 'react';
import { Timer, Flag, Play, Square, RotateCcw } from 'lucide-react';

export default function LapTimer({ history = [], currentTelemetry }) {
  const [isRunning, setIsRunning] = useState(false);
  const [timeMs, setTimeMs] = useState(0);
  const [laps, setLaps] = useState([]);

  useEffect(() => {
    let interval = null;
    if (isRunning) { interval = setInterval(() => setTimeMs(p => p + 100), 100); }
    return () => clearInterval(interval);
  }, [isRunning]);

  const fmt = (ms) => {
    const s = Math.floor(ms / 1000); const m = Math.floor(s / 60);
    return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}.${Math.floor((ms % 1000) / 100)}`;
  };

  const speeds = history.map(h => h.nav?.vel ?? h.vel).filter(v => typeof v === 'number' && !isNaN(v));
  const maxVel = speeds.length > 0 ? Math.max(...speeds) : 0;
  const avgVel = speeds.length > 0 ? (speeds.reduce((a, b) => a + b, 0) / speeds.length) : 0;
  const bestLap = laps.length > 0 ? Math.min(...laps) : null;

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Timer style={{ width: 16, height: 16, color: '#ffb703' }} />
          <span style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 0.8, color: 'var(--text-main)' }}>Cronômetro</span>
        </div>
        <span className="card-badge" style={{ background: 'rgba(255,183,3,0.08)', color: '#ffb703', borderColor: 'rgba(255,183,3,0.2)' }}>PIT WALL</span>
      </div>

      <div className="timer-display">
        <div className="timer-value">{fmt(timeMs)}</div>
        <div className="timer-label">
          {laps.length > 0 ? `Volta ${laps.length + 1} em andamento` : 'tempo de volta em andamento'}
        </div>
      </div>

      <div className="timer-controls">
        <button className="btn" onClick={() => setIsRunning(!isRunning)}
          style={isRunning ? { borderColor: 'rgba(255,23,68,0.4)', color: '#fca5a5' } : { borderColor: 'rgba(0,230,118,0.4)', color: '#86efac' }}>
          {isRunning ? <><Square style={{ width: 12, height: 12, fill: 'currentColor' }} />Pausar</> : <><Play style={{ width: 12, height: 12, fill: 'currentColor' }} />Iniciar</>}
        </button>
        <button className="btn" onClick={() => isRunning && timeMs > 0 && setLaps(p => [timeMs, ...p])} style={{ opacity: isRunning ? 1 : 0.4 }}>
          <Flag style={{ width: 12, height: 12, color: '#ffb703' }} />Marcar Volta
        </button>
        <button className="btn" onClick={() => { setIsRunning(false); setTimeMs(0); setLaps([]); }}>
          <RotateCcw style={{ width: 12, height: 12 }} />Zerar
        </button>
      </div>

      <div style={{ marginTop: 6, fontSize: 9, textTransform: 'uppercase', letterSpacing: 0.8, color: 'var(--text-dim)', textAlign: 'center' }}>
        Estatísticas Gerais da Sessão
      </div>

      <div className="timer-stats">
        <div className="timer-stat">
          <div className="timer-stat-label">Vel. Máxima</div>
          <div className="timer-stat-value">{maxVel.toFixed(1)} km/h</div>
        </div>
        <div className="timer-stat" style={{ borderLeft: '1px solid rgba(255,255,255,0.06)', borderRight: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="timer-stat-label">Vel. Média</div>
          <div className="timer-stat-value" style={{ color: '#00f2fe' }}>{avgVel.toFixed(1)} km/h</div>
        </div>
        <div className="timer-stat">
          <div className="timer-stat-label">Best Lap</div>
          <div className="timer-stat-value" style={{ color: '#ffb703' }}>{bestLap ? fmt(bestLap) : '--:--'}</div>
        </div>
      </div>
    </div>
  );
}
