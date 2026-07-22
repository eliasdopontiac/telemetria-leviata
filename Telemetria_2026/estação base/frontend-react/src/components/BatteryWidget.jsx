import React from 'react';
import { Battery, Sun, Zap, ArrowRight, Clock, ShieldCheck } from 'lucide-react';

export default function BatteryWidget({ telemetryData }) {
  const b = telemetryData?.bateria || {};
  const s = telemetryData?.solar || {};
  const p = telemetryData?.prop || {};

  const soc = b.soc ?? telemetryData?.soc ?? 0;
  const vBat = b.tensao_bat ?? telemetryData?.v_bat ?? 0;
  const potSolar = s.pot ?? telemetryData?.pot_solar ?? 0;
  const iMotor = p.i_motor ?? telemetryData?.i_motor ?? 0;
  const potMotor = iMotor * vBat;
  const potSaldo = potSolar - potMotor;

  let estimativaHoras = '--';
  if (potSaldo < 0 && Math.abs(potSaldo) > 10 && soc > 0) {
    const horas = (2500 * (soc / 100)) / Math.abs(potSaldo);
    estimativaHoras = horas > 10 ? '> 10h' : `${horas.toFixed(1)}h`;
  } else if (potSaldo >= 0) {
    estimativaHoras = '∞';
  }

  return (
    <div className="card" style={{ flex: 1 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Battery style={{ width: 16, height: 16, color: '#00e676' }} />
          <span style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 0.8, color: 'var(--text-main)' }}>Fluxo de Energia</span>
        </div>
        <span className="card-badge">LiFePO4 51.2V</span>
      </div>

      {/* Barra de Carga */}
      <div style={{ marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, fontFamily: 'var(--font-mono)', marginBottom: 4 }}>
          <span style={{ color: 'var(--text-dim)' }}>Carga Útil</span>
          <span style={{ color: '#00e676', fontWeight: 700 }}>{soc.toFixed(1)}% ({vBat.toFixed(1)}V)</span>
        </div>
        <div className="battery-bar-grid">
          {Array.from({ length: 10 }).map((_, i) => {
            const rangeMin = i * 10;
            const rangeMax = (i + 1) * 10;
            const filled = soc >= rangeMax - 5;
            const isLow = rangeMax <= 20;
            const tooltipText = isLow
              ? `Faixa Crítica (${rangeMin}% - ${rangeMax}%): Nível mínimo para proteção dos módulos LiFePO4`
              : `Nível de Carga (${rangeMin}% - ${rangeMax}%)`;

            return (
              <div key={i} className="battery-cell" title={tooltipText} style={{
                background: filled ? (isLow ? '#ff1744' : '#00e676') : 'rgba(255,255,255,0.04)',
                boxShadow: filled ? `0 0 6px ${isLow ? 'rgba(255,23,68,0.5)' : 'rgba(0,230,118,0.5)'}` : 'none',
              }} />
            );
          })}
        </div>
      </div>

      {/* Fluxo Solar -> Motor */}
      <div className="battery-flow-grid">
        <div>
          <Sun style={{ width: 14, height: 14, color: '#ffb703', margin: '0 auto 3px' }} />
          <div style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>Solar</div>
          <div style={{ fontSize: 13, fontWeight: 900, fontFamily: 'var(--font-mono)', color: '#ffb703' }}>+{potSolar.toFixed(0)} W</div>
        </div>
        <div className="energy-flow-arrow">
          <ArrowRight style={{ width: 16, height: 16, color: potSaldo >= 0 ? '#00e676' : '#ff1744' }} />
        </div>
        <div>
          <Zap style={{ width: 14, height: 14, color: '#00f2fe', margin: '0 auto 3px' }} />
          <div style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>Motor</div>
          <div style={{ fontSize: 13, fontWeight: 900, fontFamily: 'var(--font-mono)', color: '#00f2fe' }}>-{potMotor.toFixed(0)} W</div>
        </div>
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8, paddingTop: 6, borderTop: '1px solid rgba(255,255,255,0.06)', fontSize: 10, fontFamily: 'var(--font-mono)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-dim)' }}>
          <Clock style={{ width: 12, height: 12, color: '#00f2fe' }} />
          Autonomia: <strong style={{ color: 'var(--text-main)' }}>{estimativaHoras}</strong>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <ShieldCheck style={{ width: 12, height: 12, color: '#00e676' }} />
          <span style={{ color: potSaldo >= 0 ? '#00e676' : '#ff1744', fontWeight: 700 }}>
            {potSaldo >= 0 ? `+${potSaldo.toFixed(0)}` : potSaldo.toFixed(0)} W
          </span>
        </div>
      </div>
    </div>
  );
}
