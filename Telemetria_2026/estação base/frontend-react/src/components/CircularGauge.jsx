import React from 'react';

export default function CircularGauge({ value = 0, min = 0, max = 100, title, unit, color = '#00f2fe', warningThreshold, dangerThreshold, icon: Icon }) {
  const numVal = typeof value === 'number' && !isNaN(value) ? value : 0;
  const percentage = Math.max(0, Math.min(1, (numVal - min) / (max - min)));

  let activeColor = color;
  if (dangerThreshold !== undefined && numVal >= dangerThreshold) activeColor = '#ff1744';
  else if (warningThreshold !== undefined && numVal >= warningThreshold) activeColor = '#ff9100';

  const r = 50, sw = 8, cx = 60, cy = 60;
  const circ = 2 * Math.PI * r;
  const arc = circ * 0.75;
  const offset = arc - percentage * arc;

  return (
    <div className="gauge-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: 2 }}>
        <span className="gauge-label">{title}</span>
        {Icon && <Icon style={{ width: 13, height: 13, color: 'var(--text-dim)' }} />}
      </div>

      <div className="gauge-svg-wrap">
        <svg viewBox="0 0 120 120" className="transform" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={sw}
            strokeDasharray={`${arc} ${circ}`} strokeLinecap="round" transform={`rotate(135 ${cx} ${cy})`} />
          <circle cx={cx} cy={cy} r={r} fill="none" stroke={activeColor} strokeWidth={sw}
            strokeDasharray={`${arc} ${circ}`} strokeDashoffset={offset} strokeLinecap="round"
            transform={`rotate(135 ${cx} ${cy})`}
            style={{ transition: 'stroke-dashoffset 0.4s ease, stroke 0.3s', filter: `drop-shadow(0 0 6px ${activeColor}80)` }} />
        </svg>
        <div className="gauge-value-overlay">
          <span className="gauge-value" style={{ color: activeColor, textShadow: `0 0 10px ${activeColor}60` }}>
            {numVal % 1 !== 0 ? numVal.toFixed(1) : numVal}
          </span>
          <span className="gauge-unit">{unit}</span>
        </div>
      </div>

      <div className="gauge-range"><span>{min}</span><span>{max} {unit}</span></div>
    </div>
  );
}
